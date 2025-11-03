#!/usr/bin/env python3
"""
CLI entry point for the Meeting Summarizer.
Reads a conversation from a .txt file and outputs a summary.
"""

import sys
import os
import logging
from summarize import summarize_conversation
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def print_usage():
    """Print usage instructions."""
    print("Usage: python main.py <path/to/conversation.txt>")
    print("\nExample:")
    print("  python main.py conversation.txt")


def main():
    """Main CLI function."""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Error: Invalid number of arguments\n")
        print_usage()
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Validate file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Validate file is readable
    if not os.path.isfile(file_path):
        print(f"Error: Path is not a file: {file_path}")
        sys.exit(1)
    
    # Read the conversation file
    try:
        logger.info(f"Reading conversation from: {file_path}")
        print(f"Reading conversation from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation_text = f.read()
        
        if not conversation_text.strip():
            logger.error("File is empty")
            print("Error: File is empty")
            sys.exit(1)
        
        print("-" * 60)
        
        # Summarize the conversation
        summary = summarize_conversation(conversation_text)
        
        # Output the final summary
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        print(summary)
        print("=" * 60)
        
        logger.info("Summary generated successfully")
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {str(e)}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(f"Error processing file: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
