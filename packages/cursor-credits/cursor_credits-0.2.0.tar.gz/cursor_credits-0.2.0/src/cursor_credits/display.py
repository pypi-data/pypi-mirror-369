from colorama import Fore, Style

EMOJI = {
    "USER": "👤",
    "FAST": "⭐",
    "SLOW": "📝",
    "ERROR": "❌",
    "WARNING": "⚠️"
}

def display_account_info(email, usage_info, user_id=None):
    """Prints the account and usage information to the console."""
    if email:
        print(f"{Fore.GREEN}{EMOJI['USER']} Email: {Fore.WHITE}{email}{Style.RESET_ALL}")
    elif user_id:
        print(f"{Fore.CYAN}{EMOJI['USER']} User ID: {Fore.WHITE}{user_id}{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}{EMOJI['USER']} Account: {Fore.WHITE}Authenticated{Style.RESET_ALL}")

    if not usage_info:
        print(f"{Fore.RED}{EMOJI['ERROR']} Could not retrieve usage information.{Style.RESET_ALL}")
        return

    # Premium (Fast) model display logic
    premium_usage = usage_info.get('premium_usage', 0)
    max_premium_usage = usage_info.get('max_premium_usage', "No Limit")
    if max_premium_usage == "No Limit" or max_premium_usage == 0:
        premium_display = f"{premium_usage}/{max_premium_usage}"
    else:
        premium_percentage = (premium_usage / max_premium_usage) * 100
        premium_display = f"{premium_usage}/{max_premium_usage} ({premium_percentage:.1f}%)"
    
    print(f"{Fore.YELLOW}{EMOJI['FAST']} Fast: {Fore.WHITE}{premium_display}{Style.RESET_ALL}")

    # Basic (Slow) model display logic - GPT-3.5 data often not available
    basic_usage = usage_info.get('basic_usage', 0)
    max_basic_usage = usage_info.get('max_basic_usage', "No Limit")
    
    # Handle case where slow model data is not available (common)
    if basic_usage == 0 and (max_basic_usage == "No Limit" or max_basic_usage is None):
        basic_display = "Not available"
    else:
        basic_display = f"{basic_usage}/{max_basic_usage}"
    
    print(f"{Fore.BLUE}{EMOJI['SLOW']} Slow: {Fore.WHITE}{basic_display}{Style.RESET_ALL}")