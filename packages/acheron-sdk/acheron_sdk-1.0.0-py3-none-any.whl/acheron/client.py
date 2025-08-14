"""
Acheron Python SDK - Main Client
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import websocket
import threading

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AcheronConfig:
    """Configuration for Acheron client"""
    endpoint: str
    api_key: str
    timeout: int = 10
    retries: int = 3
    debug: bool = False
    websocket: bool = False
    verify_ssl: bool = True

@dataclass
class PolicyEvaluationRequest:
    """Policy evaluation request"""
    policy: str
    input: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

@dataclass
class PolicyEvaluationResult:
    """Policy evaluation result"""
    decision: str  # 'ALLOW' | 'DENY' | 'LOG' | 'MODIFY'
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    violations: Optional[List[str]] = None
    latency: float = 0.0
    timestamp: float = 0.0
    trace_id: Optional[str] = None

@dataclass
class PolicyInfo:
    """Policy information"""
    name: str
    version: str
    framework: str
    description: str
    rules: int
    last_modified: str

@dataclass
class SystemStatus:
    """System status information"""
    status: str  # 'healthy' | 'degraded' | 'down'
    version: str
    uptime: float
    components: Dict[str, Dict[str, Any]]
    metrics: Dict[str, Any]

class AcheronError(Exception):
    """Base exception for Acheron SDK"""
    pass

class AcheronAPIError(AcheronError):
    """API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class AcheronConnectionError(AcheronError):
    """Connection-related errors"""
    pass

class AcheronClient:
    """
    Main Acheron client for AI governance and policy evaluation.
    
    Example:
        >>> client = AcheronClient(AcheronConfig(
        ...     endpoint="https://api.acheron.ai",
        ...     api_key="your-api-key"
        ... ))
        >>> result = client.evaluate_policy(PolicyEvaluationRequest(
        ...     policy="gdpr-pii-protection",
        ...     input={"llm_response": "Hello, my name is John Doe"}
        ... ))
        >>> print(result.decision)  # 'DENY'
    """
    
    def __init__(self, config: AcheronConfig):
        self.config = config
        self._session = self._create_session()
        self._ws = None
        self._ws_thread = None
        self._ws_callbacks = []
        
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug(f"Initialized Acheron client for {config.endpoint}")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.config.retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Acheron-Python-SDK/1.0.0'
        })
        
        return session
    
    def evaluate_policy(self, request: PolicyEvaluationRequest) -> PolicyEvaluationResult:
        """
        Evaluate a policy against input data.
        
        Args:
            request: Policy evaluation request
            
        Returns:
            Policy evaluation result
            
        Raises:
            AcheronAPIError: If the API request fails
            AcheronConnectionError: If connection fails
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Evaluating policy: {request.policy}")
            
            response = self._session.post(
                urljoin(self.config.endpoint, '/v1/evaluate'),
                json=asdict(request),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            
            result_data = response.json()
            result = PolicyEvaluationResult(
                **result_data,
                latency=time.time() - start_time,
                timestamp=time.time()
            )
            
            logger.debug(f"Policy evaluation completed: {result.decision} ({result.latency:.3f}s)")
            return result
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Connection failed: {str(e)}")
    
    def evaluate_batch(self, requests: List[PolicyEvaluationRequest]) -> List[PolicyEvaluationResult]:
        """
        Evaluate multiple policies in batch.
        
        Args:
            requests: List of policy evaluation requests
            
        Returns:
            List of policy evaluation results
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Evaluating batch of {len(requests)} policies")
            
            response = self._session.post(
                urljoin(self.config.endpoint, '/v1/evaluate/batch'),
                json={'requests': [asdict(req) for req in requests]},
                timeout=self.config.timeout * 2,  # Longer timeout for batch
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            
            results_data = response.json()
            batch_latency = time.time() - start_time
            
            results = [
                PolicyEvaluationResult(
                    **result_data,
                    latency=batch_latency,
                    timestamp=time.time()
                ) for result_data in results_data
            ]
            
            logger.debug(f"Batch evaluation completed ({batch_latency:.3f}s)")
            return results
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Batch evaluation failed: {str(e)}")
    
    def list_policies(self) -> List[PolicyInfo]:
        """
        List all available policies.
        
        Returns:
            List of policy information
        """
        try:
            response = self._session.get(
                urljoin(self.config.endpoint, '/v1/policies'),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            
            policies_data = response.json()
            return [PolicyInfo(**policy) for policy in policies_data]
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to list policies: {str(e)}")
    
    def get_policy(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific policy.
        
        Args:
            name: Policy name
            
        Returns:
            Policy details including rules
        """
        try:
            response = self._session.get(
                urljoin(self.config.endpoint, f'/v1/policies/{name}'),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to get policy {name}: {str(e)}")
    
    def deploy_policy(self, policy: Dict[str, Any]) -> None:
        """
        Deploy a new policy or update an existing one.
        
        Args:
            policy: Policy definition
        """
        try:
            response = self._session.post(
                urljoin(self.config.endpoint, '/v1/policies'),
                json=policy,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            logger.debug(f"Policy deployed: {policy.get('metadata', {}).get('name', 'unknown')}")
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to deploy policy: {str(e)}")
    
    def delete_policy(self, name: str) -> None:
        """
        Delete a policy.
        
        Args:
            name: Policy name to delete
        """
        try:
            response = self._session.delete(
                urljoin(self.config.endpoint, f'/v1/policies/{name}'),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            logger.debug(f"Policy deleted: {name}")
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to delete policy {name}: {str(e)}")
    
    def get_status(self) -> SystemStatus:
        """
        Get system status and health information.
        
        Returns:
            System status
        """
        try:
            response = self._session.get(
                urljoin(self.config.endpoint, '/v1/status'),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            return SystemStatus(**response.json())
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to get system status: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics.
        
        Returns:
            System metrics
        """
        try:
            response = self._session.get(
                urljoin(self.config.endpoint, '/v1/metrics'),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            self._handle_response_errors(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise AcheronConnectionError(f"Failed to get metrics: {str(e)}")
    
    def stream_evaluations(self, callback: Callable[[PolicyEvaluationResult], None]) -> None:
        """
        Stream real-time policy evaluations via WebSocket.
        
        Args:
            callback: Function to call for each evaluation result
        """
        if not self.config.websocket:
            raise AcheronError("WebSocket not enabled. Set websocket=True in config.")
        
        self._ws_callbacks.append(callback)
        
        if not self._ws or not self._ws_thread:
            self._initialize_websocket()
    
    def test_connection(self) -> bool:
        """
        Test connection to Acheron.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._session.get(
                urljoin(self.config.endpoint, '/health'),
                timeout=5,
                verify=self.config.verify_ssl
            )
            return response.status_code == 200
        except:
            return False
    
    def disconnect(self) -> None:
        """Close WebSocket connection and cleanup resources."""
        if self._ws:
            self._ws.close()
            self._ws = None
        
        if self._ws_thread:
            self._ws_thread.join(timeout=5)
            self._ws_thread = None
        
        self._ws_callbacks.clear()
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle HTTP response errors"""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get('error', f'HTTP {response.status_code}')
            except:
                message = f'HTTP {response.status_code}: {response.reason}'
            
            raise AcheronAPIError(message, response.status_code)
    
    def _initialize_websocket(self) -> None:
        """Initialize WebSocket connection"""
        parsed_url = urlparse(self.config.endpoint)
        ws_scheme = 'wss' if parsed_url.scheme == 'https' else 'ws'
        ws_url = f"{ws_scheme}://{parsed_url.netloc}/ws"
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'evaluation':
                    result = PolicyEvaluationResult(**data['data'])
                    for callback in self._ws_callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error(f"WebSocket callback error: {e}")
            except Exception as e:
                logger.error(f"WebSocket message processing error: {e}")
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.debug("WebSocket connection closed")
        
        def on_open(ws):
            logger.debug("WebSocket connection opened")
        
        def run_websocket():
            self._ws = websocket.WebSocketApp(
                ws_url,
                header=[f"Authorization: Bearer {self.config.api_key}"],
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            self._ws.run_forever(sslopt={"cert_reqs": 2 if self.config.verify_ssl else 0})
        
        self._ws_thread = threading.Thread(target=run_websocket, daemon=True)
        self._ws_thread.start()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect() 