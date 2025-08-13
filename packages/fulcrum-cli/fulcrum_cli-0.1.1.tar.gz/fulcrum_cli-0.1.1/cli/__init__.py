#!/usr/bin/env python3
"""Main CLI interface for Fulcrum tools."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .uploader import upload_inspect_log


def upload_inspect_command(args):
    """Handle the upload-inspect subcommand."""
    path = Path(args.log_file).expanduser().resolve()
    
    if args.recursive:
        if not path.is_dir():
            print(f"Error: {path} is not a directory. --recursive requires a directory path.", file=sys.stderr)
            sys.exit(1)
        
        # Find all .eval files recursively
        eval_files = list(path.glob("**/*.eval"))
        
        if not eval_files:
            print(f"No .eval files found in {path}")
            return
        
        print(f"Found {len(eval_files)} .eval file(s) to upload:")
        for i, eval_file in enumerate(eval_files, 1):
            print(f"  [{i}/{len(eval_files)}] {eval_file.relative_to(path)}")
        
        print()  # Empty line for readability
        
        # Upload each file sequentially
        for i, eval_file in enumerate(eval_files, 1):
            print(f"\n{'='*60}")
            print(f"Uploading file {i}/{len(eval_files)}: {eval_file.name}")
            print(f"{'='*60}")
            
            try:
                upload_inspect_log(
                    log_file=str(eval_file),
                    api=args.api,
                    batch_size=args.batch_size,
                    env_name=args.env_name,
                )
            except Exception as e:
                print(f"Error uploading {eval_file}: {e}", file=sys.stderr)
                continue
        
        print(f"\n{'='*60}")
        print(f"Completed uploading {len(eval_files)} file(s)")
        print(f"{'='*60}")
    else:
        # Single file upload
        upload_inspect_log(
            log_file=args.log_file,
            api=args.api,
            batch_size=args.batch_size,
            env_name=args.env_name,
        )


def main():
    """Main entry point for the Fulcrum CLI."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        prog="fulcrum",
        description="Fulcrum CLI - Tools for agent observability and analysis",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )
    
    # upload-inspect subcommand
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload Inspect AI log files to Fulcrum",
        description="Upload evaluation logs from Inspect AI to Fulcrum for analysis",
    )
    upload_parser.add_argument(
        "log_file",
        type=str,
        help="Path to Inspect .eval or .json log file",
    )
    upload_parser.add_argument(
        "--api",
        default="http://localhost:8000",
        help="Backend API root URL (default: http://localhost:8000)",
    )
    upload_parser.add_argument(
        "--batch-size",
        type=int,
        default=400,
        help="Number of trajectories to upload in each batch (default: 400)",
    )
    upload_parser.add_argument(
        "--env-name",
        type=str,
        help="Override the environment name (defaults to sanitized task name from log)",
    )
    upload_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively find and upload all .eval files in the given directory",
    )
    upload_parser.set_defaults(func=upload_inspect_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
