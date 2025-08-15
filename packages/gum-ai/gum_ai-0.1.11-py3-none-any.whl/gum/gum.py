# gum.py

from __future__ import annotations

import asyncio
import json
import logging
import os
from uuid import uuid4
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Callable, List
from .models import observation_proposition
import traceback

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from .db_utils import (
    get_related_observations,
    search_propositions_bm25,
)
from .models import Observation, Proposition, init_db
from .observers import Observer
from .schemas import (
    PropositionItem,
    PropositionSchema,
    RelationSchema,
    Update,
    get_schema,
    AuditSchema
)
from gum.prompts.gum import AUDIT_PROMPT, PROPOSE_PROMPT, REVISE_PROMPT, SIMILAR_PROMPT
from .batcher import ObservationBatcher

class gum:
    """A class for managing general user models.

    This class provides functionality for observing user behavior, generating and managing
    propositions about user behavior, and maintaining relationships between observations
    and propositions.

    Args:
        user_name (str): The name of the user being modeled.
        *observers (Observer): Variable number of observer instances to track user behavior.
        propose_prompt (str, optional): Custom prompt for proposition generation.
        similar_prompt (str, optional): Custom prompt for similarity analysis.
        revise_prompt (str, optional): Custom prompt for proposition revision.
        audit_prompt (str, optional): Custom prompt for auditing.
        data_directory (str, optional): Directory for storing data. Defaults to "~/.cache/gum".
        db_name (str, optional): Name of the database file. Defaults to "gum.db".

        verbosity (int, optional): Logging verbosity level. Defaults to logging.INFO.
        audit_enabled (bool, optional): Whether to enable auditing. Defaults to False.
    """

    def __init__(
        self,
        user_name: str,
        model: str,
        *observers: Observer,
        propose_prompt: str | None = None,
        similar_prompt: str | None = None,
        revise_prompt: str | None = None,
        audit_prompt: str | None = None,
        data_directory: str = "~/.cache/gum",
        db_name: str = "gum.db",
        verbosity: int = logging.INFO,
        audit_enabled: bool = False,
        api_base: str | None = None,
        api_key: str | None = None,
        batch_interval_minutes: float = 2,
        max_batch_size: int = 50,
    ):
        # basic paths
        data_directory = os.path.expanduser(data_directory)
        os.makedirs(data_directory, exist_ok=True)

        # runtime
        self.user_name = user_name
        self.observers: list[Observer] = list(observers)
        self.model = model
        self.audit_enabled = audit_enabled

        # batching configuration
        self.batch_interval_minutes = batch_interval_minutes
        self.max_batch_size = max_batch_size

        # logging
        self.logger = logging.getLogger("gum")
        self.logger.setLevel(verbosity)
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(h)

        # prompts
        self.propose_prompt = propose_prompt or PROPOSE_PROMPT
        self.similar_prompt = similar_prompt or SIMILAR_PROMPT
        self.revise_prompt = revise_prompt or REVISE_PROMPT
        self.audit_prompt = audit_prompt or AUDIT_PROMPT

        self.client = AsyncOpenAI(
            base_url=api_base or os.getenv("GUM_LM_API_BASE"), 
            api_key=api_key or os.getenv("GUM_LM_API_KEY") or os.getenv("OPENAI_API_KEY") or "None"
        )

        self.engine = None
        self.Session = None
        self._db_name        = db_name
        self._data_directory = data_directory

        # Initialize batcher if enabled
        self.batcher = ObservationBatcher(
            data_directory=data_directory,
            batch_interval_minutes=batch_interval_minutes,
            max_batch_size=max_batch_size
        )

        self._loop_task: asyncio.Task | None = None
        self._batch_task: asyncio.Task | None = None
        self._batch_processing_lock = asyncio.Lock()
        self.update_handlers: list[Callable[[Observer, Update], None]] = []

    def start_update_loop(self):
        """Start the asynchronous update loop for processing observer updates."""
        if self._loop_task is None:
            self._loop_task = asyncio.create_task(self._update_loop())
            
        # Start batch processing if enabled
        if self._batch_task is None:
            self._batch_task = asyncio.create_task(self._batch_processing_loop())

    async def stop_update_loop(self):
        """Stop the asynchronous update loop and clean up resources."""
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None
            
        # Stop batch processing if enabled
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
            
        if self.batcher:
            await self.batcher.stop()

    async def connect_db(self):
        """Initialize the database connection if not already connected."""
        if self.engine is None:
            self.engine, self.Session = await init_db(
                self._db_name, self._data_directory
            )

    async def __aenter__(self):
        """Async context manager entry point.
        
        Returns:
            gum: The instance of the gum class.
        """
        await self.connect_db()
        self.start_update_loop()
        
        # Start batcher if enabled
        if self.batcher:
            await self.batcher.start()
            
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit point.
        
        Args:
            exc_type: The type of exception if any.
            exc: The exception instance if any.
            tb: The traceback if any.
        """
        await self.stop_update_loop()

        # stop observers
        for obs in self.observers:
            await obs.stop()

    async def _update_loop(self):
        """Efficiently wait for any observer to produce an Update and dispatch it.
        
        This method continuously monitors all observers for updates and processes them
        through the semaphore-guarded handler.
        """
        while True:
            gets = {
                asyncio.create_task(obs.update_queue.get()): obs
                for obs in self.observers
            }

            done, _ = await asyncio.wait(
                gets.keys(), return_when=asyncio.FIRST_COMPLETED
            )

            for fut in done:
                upd: Update = fut.result()
                obs = gets[fut]

                asyncio.create_task(self._default_handler(obs, upd))

    async def _batch_processing_loop(self):
        """Process batched observations periodically to reduce API calls."""
        while True:
            try:
                # Wait for the batch interval
                await asyncio.sleep(self.batch_interval_minutes * 60)
                
                # Get pending observations
                batch = self.batcher.pop_batch()
                if batch:
                    self.logger.info(f"Processing batch of {len(batch)} observations")
                    # Use lock to ensure batch processing runs synchronously
                    async with self._batch_processing_lock:
                        await self._process_batch(batch)
                else:
                    self.logger.debug("No observations to process in this batch")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in batch processing loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def _process_batch(self, batched_observations):
        """Process a batch of observations together to reduce API calls."""
        if not batched_observations:
            return
            
        self.logger.info(f"Processing {len(batched_observations)} observations in batch")
        
        # Combine all observations into a single content for analysis
        combined_content = []
        observation_ids = []
        
        for obs in batched_observations:
            combined_content.append(f"[{obs['observer_name']}] {obs['content']}")
            observation_ids.append(obs['id'])
            
        combined_text = "\n\n".join(combined_content)
        
        # Create a combined update
        combined_update = Update(
            content=combined_text,
            content_type="input_text"
        )
        
        try:
            async with self._session() as session:
                # Create observations in database
                observations = []
                for obs in batched_observations:
                    observation = Observation(
                        observer_name=obs['observer_name'],
                        content=obs['content'],
                        content_type=obs['content_type'],
                    )
                    session.add(observation)
                    observations.append(observation)
                
                await session.flush()
                
                # Process the combined content
                pool = await self._generate_and_search(session, combined_update)
                identical, similar, different = await self._filter_propositions(pool)

                self.logger.info("Applying proposition updates for batch...")
                await self._handle_identical(session, identical, observations)
                await self._handle_similar(session, similar, observations)
                await self._handle_different(session, different, observations)
                
                # Observations are already removed from queue by pop_batch()
                self.logger.info(f"Completed processing batch of {len(batched_observations)} observations")
                
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.logger.error(f"Batch size: {len(batched_observations)}")
            if batched_observations:
                self.logger.error(f"First observation type: {type(batched_observations[0])}")
                self.logger.error(f"First observation: {batched_observations[0]}")
            # Put failed items back in queue for retry
            for obs in batched_observations:
                self.batcher.push(obs['observer_name'], obs['content'], obs['content_type'])

    async def _construct_propositions(self, update: Update) -> list[PropositionItem]:
        """Generate propositions from an update.
        
        Args:
            update (Update): The update to generate propositions from.
            
        Returns:
            list[PropositionItem]: List of generated propositions.
        """
        prompt = (
            self.propose_prompt.replace("{user_name}", self.user_name)
            .replace("{inputs}", update.content)
        )

        schema = PropositionSchema.model_json_schema()
        rsp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=get_schema(schema),
        )

        return json.loads(rsp.choices[0].message.content)["propositions"]

    async def _build_relation_prompt(self, all_props) -> str:
        """Build a prompt for analyzing relationships between propositions.
        
        Args:
            all_props: List of propositions to analyze.
            
        Returns:
            str: The formatted prompt for relationship analysis.
        """
        blocks = [
            f"[id={p['id']}] {p['proposition']}\n    Reasoning: {p['reasoning']}"
            for p in all_props
        ]
        body = "\n\n".join(blocks)
        return self.similar_prompt.replace("{body}", body)

    async def _filter_propositions(
        self, rel_props: list[Proposition]
    ) -> tuple[list[Proposition], list[Proposition], list[Proposition]]:
        """Filter propositions into identical, similar, and unrelated groups.
        
        Args:
            rel_props (list[Proposition]): List of propositions to filter.
            
        Returns:
            tuple[list[Proposition], list[Proposition], list[Proposition]]: Three lists containing
                identical, similar, and unrelated propositions respectively.
        """
        if not rel_props:
            return [], [], []

        payload = [
            {"id": p.id, "proposition": p.text, "reasoning": p.reasoning or ""}
            for p in rel_props
        ]
        prompt_text = await self._build_relation_prompt(payload)

        rsp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt_text}],
            response_format=get_schema(RelationSchema.model_json_schema()),
        )

        data = RelationSchema.model_validate_json(rsp.choices[0].message.content)

        id_to_prop = {p.id: p for p in rel_props}
        ident, sim, unrel = set(), set(), set()

        for r in data.relations:
            if r.label == "IDENTICAL":
                ident.add(r.source)
                ident.update(r.target or [])
            elif r.label == "SIMILAR":
                sim.add(r.source)
                sim.update(r.target or [])
            else:
                unrel.add(r.source)

        # only keep IDs we actually know about
        valid_ids = set(id_to_prop.keys())
        ident &= valid_ids
        sim &= valid_ids
        unrel &= valid_ids

        return (
            [id_to_prop[i] for i in ident],
            [id_to_prop[i] for i in sim - ident],
            [id_to_prop[i] for i in unrel - ident - sim],
        )

    async def _build_revision_body(
        self, similar: List[Proposition], related_obs: List[Observation]
    ) -> str:
        """Build the body text for proposition revision.
        
        Args:
            similar (List[Proposition]): List of similar propositions.
            related_obs (List[Observation]): List of related observations.
            
        Returns:
            str: The formatted body text for revision.
        """
        blocks = [
            f"Proposition {idx}: {p.text}\nReasoning: {p.reasoning}"
            for idx, p in enumerate(similar, 1)
        ]
        if related_obs:
            blocks.append("\nSupporting observations:")
            blocks.extend(f"- {o.content}" for o in related_obs[:10])
        return "\n".join(blocks)

    async def _revise_propositions(
        self,
        related_obs: list[Observation],
        similar_cluster: list[Proposition],
    ) -> list[dict]:
        """Revise propositions based on related observations and similar propositions.
        
        Args:
            related_obs (list[Observation]): List of related observations.
            similar_cluster (list[Proposition]): List of similar propositions.
            
        Returns:
            list[dict]: List of revised propositions.
        """
        body = await self._build_revision_body(similar_cluster, related_obs)
        prompt = self.revise_prompt.replace("{body}", body)
        rsp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=get_schema(PropositionSchema.model_json_schema()), 
        )
        return json.loads(rsp.choices[0].message.content)["propositions"]

    async def _generate_and_search(
        self, session: AsyncSession, update: Update
    ) -> list[Proposition]:

        drafts_raw = await self._construct_propositions(update)
        drafts: list[Proposition] = []
        pool: dict[int, Proposition] = {}

        for itm in drafts_raw:
            draft = Proposition(
                text=itm["proposition"],
                reasoning=itm["reasoning"],
                confidence=itm.get("confidence"),
                decay=itm.get("decay"),
                revision_group=str(uuid4()),
                version=1,
            )
            drafts.append(draft)

            # search existing persisted props
            with session.no_autoflush:
                hits = await search_propositions_bm25(
                    session, f"{draft.text}\n{draft.reasoning}", mode="OR",
                    include_observations=False,
                    enable_mmr=False,
                    enable_decay=True
                )
                
            for prop, _score in hits:
                pool[prop.id] = prop

        session.add_all(drafts)
        await session.flush()

        for draft in drafts:
            pool[draft.id] = draft

        return list(pool.values())

    async def _handle_identical(
        self, session, identical: list[Proposition], observations: list[Observation]
    ) -> None:
        for p in identical:
            for obs in observations:
                await self._attach_obs_if_missing(p, obs, session)

    async def _handle_similar(
        self,
        session: AsyncSession,
        similar: list[Proposition],
        observations: list[Observation],
    ) -> None:

        if not similar:
            return

        # Collect all observations from similar propositions
        rel_obs = {
            o
            for p in similar
            for o in await get_related_observations(session, p.id)
        }
        # Add all the batched observations
        rel_obs.update(observations)

        # Generate revised propositions
        revised_items = await self._revise_propositions(list(rel_obs), similar)
        
        # Delete all old similar propositions
        for prop in similar:
            await session.delete(prop)
        
        # Create new propositions to replace them
        revision_group = str(uuid4())
        for item in revised_items:
            new_prop = Proposition(
                text=item["proposition"],
                reasoning=item["reasoning"],
                confidence=item.get("confidence"),
                decay=item.get("decay"),
                version=1,  # Start fresh with version 1
                revision_group=revision_group,
                observations=rel_obs,
            )
            session.add(new_prop)

        await session.flush()

    async def _handle_different(
        self, session, different: list[Proposition], observations: list[Observation]
    ) -> None:
        for p in different:
            for obs in observations:
                await self._attach_obs_if_missing(p, obs, session)

    async def _handle_audit(self, obs: Observation) -> bool:
        if not self.audit_enabled:
            return False

        hits = await self.query(obs.content, limit=10, mode="OR")

        if not hits:
            past_interaction = "*None*"
        else:
            ctx_chunks: list[str] = []
            async with self._session() as session:
                for prop, score in hits:
                    chunk = [f"• {prop.text}"]
                    if prop.reasoning:
                        chunk.append(f"  Reasoning: {prop.reasoning}")
                    if prop.confidence is not None:
                        chunk.append(f"  Confidence: {prop.confidence}")
                    chunk.append(f"  Relevance Score: {score:.2f}")

                    obs_list = await get_related_observations(session, prop.id)
                    if obs_list:
                        chunk.append("  Supporting Observations:")
                        for rel_obs in obs_list:
                            preview = rel_obs.content.replace("\n", " ")[:120]
                            chunk.append(f"    - [{rel_obs.observer_name}] {preview}")

                    ctx_chunks.append("\n".join(chunk))

            past_interaction = "\n\n".join(ctx_chunks)

        prompt = (
            self.audit_prompt
            .replace("{past_interaction}", past_interaction)
            .replace("{user_input}", obs.content)
            .replace("{user_name}", self.user_name)
        )

        rsp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=get_schema(AuditSchema.model_json_schema()),
            temperature=0.0,
        )
        decision = json.loads(rsp.choices[0].message.content)

        if not decision["transmit_data"]:
            self.logger.warning(
                "Audit blocked transmission (data_type=%s, subject=%s)",
                decision["data_type"],
                decision["subject"],
            )
            return True

        return False

    async def _default_handler(self, observer: Observer, update: Update) -> None:
        self.logger.info(f"Processing update from {observer.name}")

        # add to batch
        observation_id = self.batcher.push(
            observer_name=observer.name,
            content=update.content,
            content_type=update.content_type
        )
        self.logger.info(f"Added observation {observation_id} to queue (size: {self.batcher.size()})")

    @asynccontextmanager
    async def _session(self):
        async with self.Session() as s:
            async with s.begin():
                yield s

    @staticmethod
    async def _attach_obs_if_missing(prop: Proposition, obs: Observation, session):
        await session.execute(
            insert(observation_proposition)
            .prefix_with("OR IGNORE")
            .values(observation_id=obs.id, proposition_id=prop.id)
        )
        prop.updated_at = datetime.now(timezone.utc)

    def add_observer(self, observer: Observer):
        """Add an observer to track user behavior.
        
        Args:
            observer (Observer): The observer to add.
        """
        self.observers.append(observer)

    def remove_observer(self, observer: Observer):
        """Remove an observer from tracking.
        
        Args:
            observer (Observer): The observer to remove.
        """
        if observer in self.observers:
            self.observers.remove(observer)

    def register_update_handler(self, fn: Callable[[Observer, Update], None]):
        """Register a custom update handler function.
        
        Args:
            fn (Callable[[Observer, Update], None]): The handler function to register.
        """
        self.update_handlers.append(fn)

    async def query(
        self,
        user_query: str,
        *,
        limit: int = 3,
        mode: str = "OR",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[tuple[Proposition, float]]:
        """Query the database for propositions matching the user query.
        
        Args:
            user_query (str): The query string to search for.
            limit (int, optional): Maximum number of results to return. Defaults to 3.
            mode (str, optional): Search mode ("OR" or "AND"). Defaults to "OR".
            start_time (datetime, optional): Start time for filtering results. Defaults to None.
            end_time (datetime, optional): End time for filtering results. Defaults to None.
            
        Returns:
            list[tuple[Proposition, float]]: List of tuples containing propositions and their relevance scores.
        """
        async with self._session() as session:
            return await search_propositions_bm25(
                session,
                user_query,
                limit=limit,
                mode=mode,
                start_time=start_time,
                end_time=end_time,
            )
