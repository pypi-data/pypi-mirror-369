import os
import json
import sqlite3
import logging
import jwt
from . import paths # Relative import

logger = logging.getLogger(__name__)

def get_token_from_storage(storage_path):
    """Extract authentication token from storage.json file."""
    try:
        if not os.path.exists(storage_path):
            logger.debug(f"Storage file not found: {storage_path}")
            return None
            
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Look for authentication token in common locations
        for key in ['auth.token', 'cursor.auth.token', 'token', 'authToken']:
            if key in data:
                token = data[key]
                if token and isinstance(token, str):
                    logger.info("Token found in storage.json")
                    return _process_jwt_token(token)
                    
        logger.debug("No valid token found in storage.json")
        return None
        
    except Exception as e:
        logger.debug(f"Failed to read token from storage: {e}")
        return None


def get_token_from_sqlite(sqlite_path):
    """Extract authentication token from SQLite database."""
    try:
        if not os.path.exists(sqlite_path):
            logger.debug(f"SQLite file not found: {sqlite_path}")
            return None
            
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Look for the specific Cursor auth token key
        try:
            cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursorAuth/accessToken'")
            result = cursor.fetchone()
            if result and result[0]:
                token = result[0]
                if isinstance(token, str) and len(token) > 10:
                    logger.info("Token found in SQLite database")
                    conn.close()
                    return _process_jwt_token(token)
        except sqlite3.Error as e:
            logger.debug(f"SQLite query failed: {e}")
                
        conn.close()
        logger.debug("No valid token found in SQLite database")
        return None
        
    except Exception as e:
        logger.error(f"Failed to read token from SQLite: {e}")
        return None


def _process_jwt_token(jwt_token):
    """Process JWT token to create session token format."""
    try:
        # Decode JWT to extract user ID
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        
        if not decoded or 'sub' not in decoded:
            logger.error("Invalid JWT structure")
            return None
            
        # Extract user ID from JWT subject
        sub = decoded['sub']
        user_id = sub.split('|')[1] if '|' in sub else sub
        
        # Create session token in the format: userId%3A%3AjwtToken
        session_token = f"{user_id}%3A%3A{jwt_token}"
        logger.info(f"Created session token for user ID: {user_id}")
        return session_token
        
    except Exception as e:
        logger.error(f"Error processing JWT token: {e}")
        return None




def get_credentials():
    """Find the user's authentication token."""
    cursor_paths = paths.get_cursor_paths()
    if not cursor_paths:
        return None, None

    storage_path = cursor_paths['storage_path']
    sqlite_path = cursor_paths['sqlite_path']

    # Get session token (try SQLite first as it's the primary source)
    token = get_token_from_sqlite(sqlite_path) or get_token_from_storage(storage_path)
    
    # Email extraction is currently not reliable, so we return None for email
    # The app handles this gracefully by showing user ID instead
    email = None

    return email, token