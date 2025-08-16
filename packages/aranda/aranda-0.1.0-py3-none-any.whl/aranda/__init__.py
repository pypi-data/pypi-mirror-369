#!/usr/bin/env python3
"""
aranda - Personal website redirector
"""
import webbrowser
import sys

__version__ = "0.1.0"


def main():
    """Open personal website in default browser"""
    website_url = "https://antoara.com"  # Replace with your actual website URL
    
    try:
        print(f"Opening {website_url} in your default browser...")
        webbrowser.open(website_url)
    except Exception as e:
        print(f"Error opening website: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
