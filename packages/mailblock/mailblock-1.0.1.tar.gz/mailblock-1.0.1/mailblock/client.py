"""
MailBlock Python SDK Client

This module provides the main MailBlock client class for sending emails.
"""

import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .email_builder import EmailBuilder
from .exceptions import (
    MailBlockError, ValidationError, AuthenticationError, 
    AuthorizationError, RateLimitError, ServerError, 
    NetworkError, TimeoutError
)
from .types import EmailData, APIResponse, ClientConfig
from .utils import (
    generate_request_id, categorize_http_error, get_error_suggestion,
    setup_logger, redact_sensitive_data, calculate_retry_delay
)


class MailBlock:
    """
    MailBlock Python SDK Client
    
    Main client class for interacting with the MailBlock API.
    Provides methods for sending emails with comprehensive error handling,
    logging, and retry mechanisms.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://sdk-backend-production-20e1.up.railway.app",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        debug: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize MailBlock client.
        
        Args:
            api_key: Your MailBlock API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            debug: Enable debug logging
            logger: Custom logger instance
            
        Raises:
            ValidationError: If API key is invalid
        """
        self.config = ClientConfig(
            api_key=api_key,
            base_url=base_url.rstrip('/'),
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            debug=debug,
            logger=logger
        )
        
        self.logger = logger or setup_logger("mailblock", debug)
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Set up requests session with retry strategy."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "MailBlock-Python-SDK/1.0.0"
        })

    def _log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal logging method.
        
        Args:
            level: Log level (info, debug, error, warning)
            message: Log message
            data: Additional data to log
        """
        if not self.config.debug and level == 'debug':
            return
        
        log_method = getattr(self.logger, level, self.logger.info)
        
        if data:
            # Redact sensitive information
            safe_data = redact_sensitive_data(data)
            log_method(f"{message} - {safe_data}")
        else:
            log_method(message)

    def email(self) -> EmailBuilder:
        """
        Create a new email builder instance.
        
        Returns:
            EmailBuilder instance for fluent email construction
        """
        return EmailBuilder(self)

    def send_email_sync(self, email_data: EmailData) -> APIResponse:
        """
        Send an email synchronously.
        
        Args:
            email_data: Email data to send
            
        Returns:
            APIResponse with the result
            
        Raises:
            MailBlockError: If sending fails
        """
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()

        self._log('info', 'Initiating email send request', {
            'request_id': request_id,
            'to': email_data.to,
            'from': email_data.from_email,
            'subject': email_data.subject[:50] + '...' if len(email_data.subject) > 50 else email_data.subject,
            'scheduled': email_data.scheduled_at is not None
        })

        try:
            # Prepare payload
            payload = self._prepare_payload(email_data)
            endpoint = f"{self.config.base_url}/v1/send-email"
            
            self._log('debug', 'Sending API request', {
                'request_id': request_id,
                'endpoint': endpoint,
                'payload': redact_sensitive_data(payload)
            })

            # Make the request
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.config.timeout,
                headers={"X-Request-ID": request_id}
            )
            
            duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            self._log('debug', 'API response received', {
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': f"{duration}ms",
                'success': response.ok
            })

            # Handle response
            if response.ok:
                result = response.json()
                
                self._log('info', f"Email {'scheduled' if email_data.scheduled_at else 'sent'} successfully", {
                    'request_id': request_id,
                    'duration': f"{duration}ms",
                    'email_id': result.get('id')
                })

                return APIResponse.success_response(
                    data=result,
                    message="Email scheduled successfully" if email_data.scheduled_at else "Email sent successfully",
                    request_id=request_id,
                    duration=duration,
                    timestamp=timestamp
                )
            else:
                return self._handle_error_response(response, request_id, duration, timestamp, endpoint)

        except requests.exceptions.Timeout as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Request timed out', {
                'request_id': request_id,
                'timeout': self.config.timeout,
                'duration': f"{duration}ms"
            })
            
            raise TimeoutError(
                f"Request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e

        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Connection error occurred', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise NetworkError(
                f"Failed to connect to MailBlock API: {str(e)}",
                request_id=request_id
            ) from e

        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Request failed with exception', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Request failed: {str(e)}",
                error_type="REQUEST_ERROR",
                request_id=request_id
            ) from e

    async def send_email(self, email_data: EmailData) -> APIResponse:
        """
        Send an email asynchronously.
        
        Note: This method requires aiohttp to be installed.
        
        Args:
            email_data: Email data to send
            
        Returns:
            APIResponse with the result
            
        Raises:
            MailBlockError: If sending fails
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
            import asyncio
        except ImportError as e:
            raise ImportError(
                "aiohttp is required for async operations. Install with: pip install aiohttp"
            ) from e

        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()

        self._log('info', 'Initiating async email send request', {
            'request_id': request_id,
            'to': email_data.to,
            'from': email_data.from_email,
            'subject': email_data.subject[:50] + '...' if len(email_data.subject) > 50 else email_data.subject
        })

        try:
            payload = self._prepare_payload(email_data)
            endpoint = f"{self.config.base_url}/v1/send-email"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Request-ID": request_id,
                "User-Agent": "MailBlock-Python-SDK/1.0.0"
            }

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    duration = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        self._log('info', f"Email {'scheduled' if email_data.scheduled_at else 'sent'} successfully", {
                            'request_id': request_id,
                            'duration': f"{duration}ms",
                            'email_id': result.get('id')
                        })

                        return APIResponse.success_response(
                            data=result,
                            message="Email scheduled successfully" if email_data.scheduled_at else "Email sent successfully",
                            request_id=request_id,
                            duration=duration,
                            timestamp=timestamp
                        )
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        return self._create_error_response_from_async(
                            response.status, error_data, request_id, duration, timestamp, endpoint
                        )

        except asyncio.TimeoutError as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Async request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Async request failed', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Async request failed: {str(e)}",
                error_type="ASYNC_ERROR",
                request_id=request_id
            ) from e

    def _prepare_payload(self, email_data: EmailData) -> Dict[str, Any]:
        """
        Prepare email payload for API request.
        
        Args:
            email_data: Email data to convert
            
        Returns:
            Dictionary payload for API request
        """
        payload = {
            "to": email_data.to,
            "from": email_data.from_email,  # 'from' is valid in dict keys
            "subject": email_data.subject
        }
        
        if email_data.text:
            payload["text"] = email_data.text
        
        if email_data.html:
            payload["html"] = email_data.html
        
        if email_data.scheduled_at:
            payload["scheduled_at"] = email_data.scheduled_at.isoformat()
        
        return payload

    def _handle_error_response(
        self, 
        response: requests.Response, 
        request_id: str, 
        duration: int, 
        timestamp: datetime,
        endpoint: str
    ) -> APIResponse:
        """Handle error response from API."""
        try:
            error_data = response.json()
            error_message = error_data.get('error', f'HTTP error! status: {response.status_code}')
        except (json.JSONDecodeError, ValueError):
            error_message = f'HTTP error! status: {response.status_code}'

        error_type = categorize_http_error(response.status_code)
        suggestion = get_error_suggestion(response.status_code)

        self._log('error', 'API request failed', {
            'request_id': request_id,
            'error': error_message,
            'status_code': response.status_code,
            'error_type': error_type,
            'suggestion': suggestion
        })

        # Raise appropriate exception
        if response.status_code == 401:
            raise AuthenticationError(error_message, request_id=request_id)
        elif response.status_code == 403:
            raise AuthorizationError(error_message, request_id=request_id)
        elif response.status_code == 429:
            raise RateLimitError(error_message, request_id=request_id)
        elif 500 <= response.status_code < 600:
            raise ServerError(error_message, status_code=response.status_code, request_id=request_id)

        return APIResponse.error_response(
            error=error_message,
            error_type=error_type,
            suggestion=suggestion,
            status_code=response.status_code,
            request_id=request_id,
            duration=duration,
            endpoint=endpoint,
            timestamp=timestamp
        )

    def _create_error_response_from_async(
        self,
        status_code: int,
        error_data: Dict[str, Any],
        request_id: str,
        duration: int,
        timestamp: datetime,
        endpoint: str
    ) -> APIResponse:
        """Create error response from async request."""
        error_message = error_data.get('error', f'HTTP error! status: {status_code}')
        error_type = categorize_http_error(status_code)
        suggestion = get_error_suggestion(status_code)

        self._log('error', 'Async API request failed', {
            'request_id': request_id,
            'error': error_message,
            'status_code': status_code,
            'error_type': error_type
        })

        return APIResponse.error_response(
            error=error_message,
            error_type=error_type,
            suggestion=suggestion,
            status_code=status_code,
            request_id=request_id,
            duration=duration,
            endpoint=endpoint,
            timestamp=timestamp
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, 'session'):
            self.session.close()

    def __repr__(self) -> str:
        """String representation of MailBlock client."""
        return f"MailBlock(base_url='{self.config.base_url}', debug={self.config.debug})"