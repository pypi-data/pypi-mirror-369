import argparse
import logging
from colorama import init, Fore, Style
from .auth import get_credentials
from .api import UsageManager
from .display import display_account_info

def extract_user_id_from_token(token):
    """Extract user ID from session token for display."""
    try:
        return token.split('%3A%3A')[0] if token and '%3A%3A' in token else None
    except:
        return None

def run_check(verbose=False):
    """Main function to check and display Cursor credits usage."""
    try:
        # Get credentials (email and token)
        email, token = get_credentials()
        
        if not token:
            print("❌ Error: Could not find Cursor authentication token.")
            print("Please make sure:")
            print("1. Cursor is installed and you're logged in")
            print("2. Cursor application has been opened at least once")
            return False
        
        # Extract user ID for display
        user_id = extract_user_id_from_token(token)
        
        # Fetch usage information
        usage_info = UsageManager.get_usage(token)
        
        if not usage_info:
            print("❌ Error: Could not retrieve usage information.")
            print("Please check your internet connection and try again.")
            return False
        
        # Display the results
        display_account_info(email, usage_info, user_id)
        return True
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    """The main entry point for the command-line tool."""
    parser = argparse.ArgumentParser(
        description="Check your Cursor AI credits usage",
        prog="cursor-credits"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output with detailed logging"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 0.2.0"
    )
    
    args = parser.parse_args()
    
    # Initialize colorama
    init()
    
    # Configure logging based on verbosity
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(levelname)s: %(message)s'
        )
    else:
        # Only show errors and warnings in non-verbose mode
        logging.basicConfig(
            level=logging.ERROR, 
            format='%(levelname)s: %(message)s'
        )

    try:
        success = run_check(verbose=args.verbose)
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        exit(1)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()