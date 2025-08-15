from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

import os
import argparse
import asyncio
import shutil  
from gum import gum
from gum.observers import Screen

class QueryAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, '')
        else:
            setattr(namespace, self.dest, values)

def parse_args():
    parser = argparse.ArgumentParser(description='GUM - A Python package with command-line interface')
    parser.add_argument('--user-name', '-u', type=str, help='The user name to use')
    
    parser.add_argument(
        '--query', '-q',
        nargs='?',
        action=QueryAction,
        help='Query the GUM with an optional query string',
    )
    
    parser.add_argument('--limit', '-l', type=int, help='Limit the number of results', default=10)
    parser.add_argument('--model', '-m', type=str, help='Model to use')
    parser.add_argument('--reset-cache', action='store_true', help='Reset the GUM cache and exit')  # Add this line
    
    # Batching configuration arguments
    parser.add_argument('--batch-interval-minutes', type=float, help='Minutes between batch processing')
    parser.add_argument('--max-batch-size', type=int, help='Maximum number of observations per batch')

    args = parser.parse_args()

    if not hasattr(args, 'query'):
        args.query = None

    return args

async def main():
    args = parse_args()

    # Handle --reset-cache before anything else
    if getattr(args, 'reset_cache', False):
        cache_dir = os.path.expanduser('~/.cache/gum/')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Deleted cache directory: {cache_dir}")
        else:
            print(f"Cache directory does not exist: {cache_dir}")
        return

    model = args.model or os.getenv('MODEL_NAME') or 'gpt-4o-mini'
    user_name = args.user_name or os.getenv('USER_NAME')

    # Batching configuration - follow same pattern as other args    
    batch_interval_minutes = args.batch_interval_minutes or float(os.getenv('BATCH_INTERVAL_MINUTES', '2'))
    max_batch_size = args.max_batch_size or int(os.getenv('MAX_BATCH_SIZE', '50'))

    # you need one or the other
    if user_name is None and args.query is None:
        print("Please provide a user name (as an argument, -u, or as an env variable) or a query (as an argument, -q)")
        return
    
    if args.query is not None:
        gum_instance = gum(user_name, model)
        await gum_instance.connect_db()
        result = await gum_instance.query(args.query, limit=args.limit)
        
        # confidences / propositions / number of items returned
        print(f"\nFound {len(result)} results:")
        for prop, score in result:
            print(f"\nProposition: {prop.text}")
            if prop.reasoning:
                print(f"Reasoning: {prop.reasoning}")
            if prop.confidence is not None:
                print(f"Confidence: {prop.confidence:.2f}")
            print(f"Relevance Score: {score:.2f}")
            print("-" * 80)
    else:
        print(f"Listening to {user_name} with model {model}")
            
        async with gum(
            user_name, 
            model, 
            Screen(model),
            batch_interval_minutes=batch_interval_minutes,
            max_batch_size=max_batch_size
        ) as gum_instance:
            await asyncio.Future()  # run forever (Ctrl-C to stop)

def cli():
    asyncio.run(main())

if __name__ == '__main__':
    cli()