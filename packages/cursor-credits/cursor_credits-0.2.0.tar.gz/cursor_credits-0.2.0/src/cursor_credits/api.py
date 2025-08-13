import requests
import logging

logger = logging.getLogger(__name__)


class UsageManager:
    CURSOR_API_URL = "https://cursor.com/api/usage"
    
    @staticmethod
    def get_usage(session_token):
        """Fetch usage information from Cursor API."""
        if not session_token:
            logger.error("No session token provided")
            return None
            
        # Extract user ID from session token
        try:
            user_id = session_token.split('%3A%3A')[0]
        except (IndexError, AttributeError):
            logger.error("Invalid session token format")
            return None
            
        headers = {
            "Cookie": f"WorkosCursorSessionToken={session_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        params = {"user": user_id}
        
        try:
            response = requests.get(
                UsageManager.CURSOR_API_URL, 
                headers=headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"API response: {data}")
            
            # Extract usage information from response based on actual API structure
            gpt4_data = data.get('gpt-4', {})
            gpt35_data = data.get('gpt-3.5-turbo', {})
            
            usage_info = {
                'premium_usage': gpt4_data.get('numRequests', 0),
                'max_premium_usage': gpt4_data.get('maxRequestUsage', 500),  # Default limit
                'basic_usage': gpt35_data.get('numRequests', 0),
                'max_basic_usage': gpt35_data.get('maxRequestUsage', 'No Limit')
            }
            
            logger.info("Successfully retrieved usage information")
            return usage_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch usage data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching usage: {e}")
            return None