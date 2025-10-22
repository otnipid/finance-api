import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)

class SimpleFinError(Exception):
    """Base exception for SimpleFin client errors."""
    pass

class SimpleFinClient:
    def __init__(self, access_url: str = None):
        """Initialize the SimpleFin client.
        
        Args:
            access_url: The SimpleFin access URL or None to use environment variables
            
        Raises:
            ValueError: If access_url is not provided and not in environment variables
            SimpleFinError: If there's an error initializing the client
        """
        try:
            if not access_url:
                access_url = os.getenv('SIMPLEFIN_ACCESS_URL')
                if not access_url:
                    raise ValueError(
                        "SimpleFIN access URL is required. "
                        "Set SIMPLEFIN_ACCESS_URL environment variable or pass it to the constructor."
                    )
            
            self.access_url = access_url
            
            # Parse the access URL
            try:
                parsed_url = urlparse(self.access_url)
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    raise ValueError("Invalid access URL format")
            except Exception as e:
                raise ValueError(f"Invalid access URL: {str(e)}")
            
            # Extract credentials from the URL
            try:
                if '@' in parsed_url.netloc:
                    # Format: https://username:password@host/path
                    auth_part, host_part = parsed_url.netloc.split('@', 1)
                    self.username, self.password = auth_part.split(':', 1)
                    self.base_url = f"{parsed_url.scheme}://{host_part}{parsed_url.path.rstrip('/')}"
                else:
                    # Format: https://host/path (no auth in URL)
                    self.username = os.getenv('SIMPLEFIN_USERNAME')
                    self.password = os.getenv('SIMPLEFIN_PASSWORD')
                    self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rstrip('/')}"
                
                if not (self.username and self.password):
                    raise ValueError(
                        "SimpleFIN credentials not found. Set SIMPLEFIN_USERNAME and "
                        "SIMPLEFIN_PASSWORD environment variables or include them in the access URL."
                    )
                    
            except ValueError as e:
                raise ValueError(f"Invalid authentication format: {str(e)}")
            
            # Set up session with basic auth
            self.session = requests.Session()
            self.session.auth = (self.username, self.password)
                
        except Exception as e:
            logger.error(f"Failed to initialize SimpleFinClient: {str(e)}", exc_info=True)
            if isinstance(e, (ValueError, SimpleFinError)):
                raise
            raise SimpleFinError(f"Failed to initialize client: {str(e)}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Union[Dict, List]:
        """Helper method to make API requests.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            The parsed JSON response as a dictionary or list
        """
        try:
            # Remove leading slash from endpoint if present
            endpoint = endpoint.lstrip('/')
            url = f"{self.base_url}/{endpoint}"
            
            logger.debug(f"Making request to: {url} with params: {params}")
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                error_msg = f"Request to {url} timed out after 30 seconds"
                logger.error(error_msg)
                raise SimpleFinError(error_msg)
                
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP error occurred: {str(e)}"
                if e.response is not None:
                    error_msg += f"\nStatus Code: {e.response.status_code}"
                    try:
                        error_data = e.response.json()
                        error_msg += f"\nError Details: {error_data}"
                    except ValueError:
                        error_msg += f"\nResponse: {e.response.text[:500]}"
                logger.error(error_msg)
                raise SimpleFinError(error_msg)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed: {str(e)}"
                logger.error(error_msg)
                raise SimpleFinError(error_msg)
                
            except ValueError as e:
                error_msg = f"Failed to parse JSON response: {str(e)}"
                logger.error(f"{error_msg}\nResponse: {response.text[:500]}" if 'response' in locals() else error_msg)
                raise SimpleFinError(error_msg)
                
        except Exception as e:
            if not isinstance(e, SimpleFinError):
                error_msg = f"Unexpected error making request: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise SimpleFinError(error_msg)
            raise
    
    def get_accounts(self, include_transactions: bool = False, days_back: int = 7) -> List[Dict]:
        """Get list of all accounts with optional transactions.
        
        Args:
            include_transactions: Whether to include transactions
            days_back: Number of days to look back for transactions
            
        Returns:
            List of accounts
        """
        try:
            params = {}
            if include_transactions:
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days_back)
                    params = {
                        'start-date': int(start_date.timestamp()),
                        'end-date': int(end_date.timestamp())
                    }
                except Exception as e:
                    logger.error(f"Error calculating date range: {str(e)}")
                    raise SimpleFinError(f"Invalid date range parameters: {str(e)}")
            
            response = self._make_request('accounts', params=params)
            
            if not isinstance(response, dict):
                error_msg = f"Unexpected response format: {type(response).__name__}"
                logger.error(error_msg)
                raise SimpleFinError(error_msg)
                
            if 'error' in response:
                raise SimpleFinError(f"Error from SimpleFIN: {response.get('error')}")
                
            if 'accounts' not in response:
                error_msg = f"No 'accounts' key in response: {response}"
                logger.error(error_msg)
                raise SimpleFinError(error_msg)
                
            return response['accounts']
            
        except Exception as e:
            if not isinstance(e, SimpleFinError):
                error_msg = f"Failed to get accounts: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise SimpleFinError(error_msg)
            raise
    
    def get_transactions(self, days_back: int = 7, end_date: Optional[datetime] = None) -> List[Dict]:
        """Get transactions within a date range.
        
        Args:
            days_back: Number of days to look back from end_date
            end_date: End date as datetime object. Defaults to now.
            
        Returns:
            List of transactions
        """
        try:
            if end_date is None:
                end_date = datetime.now()
                
            if not isinstance(days_back, int) or days_back < 1:
                raise ValueError("days_back must be a positive integer")
                
            start_date = end_date - timedelta(days=days_back)
            
            logger.info(
                f"Fetching transactions from {start_date.strftime('%Y-%m-%d')} "
                f"to {end_date.strftime('%Y-%m-%d')}"
            )
            
            accounts = self.get_accounts(include_transactions=True, days_back=days_back)
            
            all_transactions = []
            for account in accounts:
                account_id = account.get('id')
                if not account_id:
                    logger.warning("Account missing ID, skipping")
                    continue
                    
                transactions = account.get('transactions', [])
                for tx in transactions:
                    tx['account_id'] = account_id
                    
                all_transactions.extend(transactions)
            
            return all_transactions
            
        except Exception as e:
            if not isinstance(e, SimpleFinError):
                error_msg = f"Failed to get transactions: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise SimpleFinError(error_msg)
            raise