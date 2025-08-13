#!/usr/bin/env python3
"""
Entry point for Clivid (CLI Video Assistant) command-line interface.
"""

import sys
import os

def main():
    """Main entry point for the clivid command."""
    try:
        from clivid.main import AIVideoChatInterface
        
        # Initialize and run the application
        app = AIVideoChatInterface()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Clivid: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
