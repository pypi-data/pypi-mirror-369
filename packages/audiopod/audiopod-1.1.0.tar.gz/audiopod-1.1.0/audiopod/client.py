"""
AudioPod API Client
Main client classes for synchronous and asynchronous API access
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
import aiohttp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ClientConfig
from .exceptions import AuthenticationError, APIError, RateLimitError
from .services import (
    VoiceService,
    MusicService, 
    TranscriptionService,
    TranslationService,
    SpeakerService,
    DenoiserService,
    KaraokeService,
    CreditService,
    StemExtractionService
)

logger = logging.getLogger(__name__)


class BaseClient:
    """Base client with common functionality"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        """
        Initialize the AudioPod API client
        
        Args:
            api_key: Your AudioPod API key. If None, will try to read from AUDIOPOD_API_KEY env var
            base_url: API base URL. Defaults to production endpoint
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            verify_ssl: Whether to verify SSL certificates
            debug: Enable debug logging
        """
        # Set up logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            
        # Get API key
        self.api_key = api_key or os.getenv("AUDIOPOD_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass it as 'api_key' parameter or set AUDIOPOD_API_KEY environment variable."
            )
            
        # Validate API key format
        if not self.api_key.startswith("ap_"):
            raise AuthenticationError("Invalid API key format. AudioPod API keys start with 'ap_'")
            
        # Configuration
        self.config = ClientConfig(
            base_url=base_url or "https://api.audiopod.ai",
            timeout=timeout,
            max_retries=max_retries,
            verify_ssl=verify_ssl,
            debug=debug
        )
        
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"audiopod-python/{self.config.version}",
            "Accept": "application/json"
        }
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("detail", str(e))
                except:
                    message = str(e)
                raise APIError(f"API request failed: {message}", status_code=response.status_code)
            else:
                raise APIError(f"Unexpected HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")


class Client(BaseClient):
    """
    Synchronous AudioPod API Client
    
    Provides access to all AudioPod services through a simple Python interface.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Initialize services
        self.voice = VoiceService(self)
        self.music = MusicService(self)
        self.transcription = TranscriptionService(self)
        self.translation = TranslationService(self)
        self.speaker = SpeakerService(self)
        self.denoiser = DenoiserService(self)
        self.karaoke = KaraokeService(self)
        self.credits = CreditService(self)
        self.stem_extraction = StemExtractionService(self)
        
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request to the AudioPod API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data to send
            files: Files to upload
            params: URL parameters
            **kwargs: Additional requests parameters
            
        Returns:
            API response data
        """
        url = urljoin(self.config.base_url, endpoint)
        headers = self._get_headers()
        
        # Handle file uploads (don't set Content-Type for multipart)
        if files:
            headers.pop("Content-Type", None)
            
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                files=files,
                params=params,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                **kwargs
            )
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise
            
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return self.request("GET", "/api/v1/auth/me")
        
    def check_health(self) -> Dict[str, Any]:
        """Check API health status"""
        return self.request("GET", "/api/v1/health")
        
    def close(self):
        """Close the client session"""
        self.session.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncClient(BaseClient):
    """
    Asynchronous AudioPod API Client
    
    Provides async/await support for better performance in async applications.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Initialize async services
        self.voice = VoiceService(self, async_mode=True)
        self.music = MusicService(self, async_mode=True)
        self.transcription = TranscriptionService(self, async_mode=True)
        self.translation = TranslationService(self, async_mode=True)
        self.speaker = SpeakerService(self, async_mode=True)
        self.denoiser = DenoiserService(self, async_mode=True)
        self.karaoke = KaraokeService(self, async_mode=True)
        self.credits = CreditService(self, async_mode=True)
        self.stem_extraction = StemExtractionService(self, async_mode=True)
        
    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_headers()
            )
        return self._session
        
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an async request to the AudioPod API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data to send
            files: Files to upload
            params: URL parameters
            **kwargs: Additional aiohttp parameters
            
        Returns:
            API response data
        """
        url = urljoin(self.config.base_url, endpoint)
        
        try:
            if files:
                # Handle file uploads
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, str(value))
                for key, file_data in files.items():
                    form_data.add_field(key, file_data)
                data = form_data
                
            async with self.session.request(
                method=method,
                url=url,
                json=data if not files else None,
                data=data if files else None,
                params=params,
                **kwargs
            ) as response:
                return await self._handle_async_response(response)
                
        except Exception as e:
            logger.error(f"Async request failed: {method} {url} - {e}")
            raise
            
    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle async API response and raise appropriate exceptions"""
        try:
            response.raise_for_status()
            return await response.json()
        except aiohttp.ClientResponseError as e:
            if response.status == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status >= 400:
                try:
                    error_data = await response.json()
                    message = error_data.get("detail", str(e))
                except:
                    message = str(e)
                raise APIError(f"API request failed: {message}", status_code=response.status)
            else:
                raise APIError(f"Unexpected HTTP error: {e}")
        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {e}")
            
    async def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return await self.request("GET", "/api/v1/auth/me")
        
    async def check_health(self) -> Dict[str, Any]:
        """Check API health status"""
        return await self.request("GET", "/api/v1/health")
        
    async def close(self):
        """Close the async client session"""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
