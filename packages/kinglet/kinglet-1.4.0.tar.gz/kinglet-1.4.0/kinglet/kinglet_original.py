"""
Kinglet - A lightweight routing framework for Python Workers
Single-file version for easy deployment and distribution
"""
import json
import re
import time
import functools
from typing import Dict, List, Callable, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from abc import ABC, abstractmethod

__version__ = "1.4.0"
__author__ = "Mitchell Currie"

def generate_request_id() -> str:
    """Generate a unique request ID for tracing"""
    import secrets
    return secrets.token_hex(8)

class HTTPError(Exception):
    """HTTP error with status code and message"""
    def __init__(self, status_code: int, message: str, detail: str = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(message)


class GeoRestrictedError(HTTPError):
    """Geographic restriction error"""
    def __init__(self, country_code: str, allowed_countries: List[str]):
        message = f"Access denied from {country_code}. Allowed: {', '.join(allowed_countries)}"
        super().__init__(451, message)  # HTTP 451 Unavailable For Legal Reasons
        self.country_code = country_code
        self.allowed_countries = allowed_countries


class DevOnlyError(HTTPError):
    """Development-only endpoint error"""
    def __init__(self):
        super().__init__(403, "This endpoint is only available in development mode")

# Testing support  
class _KingletTestClient:
    """Simple sync wrapper for testing Kinglet apps without HTTP/Wrangler overhead"""
    __test__ = False  # Tell pytest this is not a test class
    
    def __init__(self, app, base_url="http://testserver", env=None):
        self.app = app
        self.base_url = base_url.rstrip('/')
        self.env = env or {}
        
        # Enable test mode on the app if it's a Kinglet instance
        if hasattr(app, 'test_mode'):
            app.test_mode = True
    
    def request(self, method: str, path: str, json=None, data=None, headers=None, **kwargs):
        """Make a test request and return (status, headers, body)"""
        import asyncio
        return asyncio.run(self._async_request(method, path, json, data, headers, **kwargs))
    
    async def _async_request(self, method: str, path: str, json=None, data=None, headers=None, **kwargs):
        """Internal async request handler"""
        # Build full URL
        url = f"{self.base_url}{path}"
        
        # Prepare headers
        test_headers = {"content-type": "application/json"} if json else {}
        if headers:
            test_headers.update({k.lower(): v for k, v in headers.items()})
        
        # Prepare body
        body_content = ""
        if json is not None:
            body_content = json.dumps(json)
            test_headers["content-type"] = "application/json"
        elif data is not None:
            body_content = str(data)
        
        # Create mock request object matching Workers format
        mock_request = MockRequest(method, url, test_headers, body_content)
        
        # Create mock env with test defaults
        mock_env = MockEnv(self.env)
        
        try:
            # Call the app
            response = await self.app(mock_request, mock_env)
            
            # Handle Kinglet Response objects
            if hasattr(response, 'status') and hasattr(response, 'content'):
                status = response.status
                headers = response.headers
                content = response.content
                
                # Serialize content for test consumption
                if isinstance(content, (dict, list)):
                    import json
                    body = json.dumps(content)
                else:
                    body = str(content) if content is not None else ""
                    
                return status, headers, body
            
            # Handle raw response objects (dict, string, etc.)
            elif isinstance(response, dict):
                return 200, {}, json.dumps(response)
            elif isinstance(response, str):
                return 200, {}, response
            else:
                return 200, {}, str(response)
            
        except Exception as e:
            # Return error response format
            error_body = json.dumps({"error": str(e)})
            return 500, {}, error_body


class MockRequest:
    """Mock request object for testing that matches Workers request interface"""
    
    def __init__(self, method: str, url: str, headers: dict, body: str = ""):
        self.method = method
        self.url = url
        self.headers = MockHeaders(headers)
        self._body = body
    
    async def text(self):
        return self._body
    
    async def json(self):
        if self._body:
            import json
            return json.loads(self._body)
        return None


class MockHeaders:
    """Mock headers object that matches Workers headers interface"""
    
    def __init__(self, headers_dict):
        self._headers = {k.lower(): v for k, v in (headers_dict or {}).items()}
    
    def get(self, key, default=None):
        return self._headers.get(key.lower(), default)
    
    def items(self):
        return self._headers.items()
    
    def __iter__(self):
        return iter(self._headers.items())


class MockEnv:
    """Mock environment object for testing"""
    
    def __init__(self, env_dict):
        # Set defaults for common Cloudflare bindings
        self.DB = env_dict.get('DB', MockDatabase())
        self.ENVIRONMENT = env_dict.get('ENVIRONMENT', 'test')
        self.JWT_SECRET = env_dict.get('JWT_SECRET', 'test-secret')
        
        # Add any additional env vars
        for key, value in env_dict.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class MockDatabase:
    """Mock D1 database for testing"""
    
    def prepare(self, query):
        return MockQuery(query)
    
    async def exec(self, query):
        return {"success": True, "meta": {"changes": 1}}


class MockQuery:
    """Mock D1 prepared statement"""
    
    def __init__(self, query):
        self.query = query
        self._bindings = []
    
    def bind(self, *args):
        self._bindings.extend(args)
        return self
    
    async def first(self):
        return MockResult({"id": 1, "test": "data"})
    
    async def all(self):
        return {"results": [{"id": 1, "test": "data"}], "success": True}
    
    async def run(self):
        return {"success": True, "meta": {"changes": 1}}


class MockResult:
    """Mock D1 query result"""
    
    def __init__(self, data):
        self._data = data
    
    def to_py(self):
        return self._data


class Request:
    """Wrapper around Workers request with convenient methods"""
    
    def __init__(self, raw_request, env):
        self.raw_request = raw_request
        self.env = env
        
        # Generate unique request ID for tracing
        self.request_id = generate_request_id()
        
        # Parse URL components
        self.url = str(raw_request.url)
        parsed_url = urlparse(self.url)
        
        self.method = raw_request.method
        self.path = parsed_url.path
        self.query_string = parsed_url.query
        
        # Parse query parameters
        self._query_params = parse_qs(parsed_url.query)
        
        # Headers (converted to dict for easier access)
        self._headers = {}
        if hasattr(raw_request, 'headers'):
            try:
                # Try dictionary-style access first
                for key, value in raw_request.headers.items():
                    self._headers[key.lower()] = value
            except AttributeError:
                # Headers might be in a different format in Workers
                try:
                    # Try iterating over headers directly
                    for header in raw_request.headers:
                        self._headers[header[0].lower()] = header[1]
                except:
                    # If all else fails, just continue without headers
                    pass
        
        # Path parameters (set by router)
        self.path_params: Dict[str, str] = {}
        
        # Cached request body
        self._body_cache = None
        self._json_cache = None
        self._bytes_cache = None
    
    def query(self, key: str, default: Any = None) -> Optional[str]:
        """Get single query parameter value"""
        values = self._query_params.get(key, [])
        return values[0] if values else default
    
    def query_int(self, key: str, default: int = None) -> Optional[int]:
        """Get query parameter as integer (returns 400 error on invalid)"""
        value = self.query(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise HTTPError(400, f"Query parameter '{key}' must be an integer")
    
    def query_bool(self, key: str, default: bool = False) -> bool:
        """Get query parameter as boolean"""
        value = self.query(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off", ""):
            return default if value == "" else False
        else:
            return default
    
    def query_all(self, key: str) -> List[str]:
        """Get all values for a query parameter"""
        return self._query_params.get(key, [])
    
    def path_param(self, key: str, default: Any = None) -> Any:
        """Get path parameter value"""
        return self.path_params.get(key, default)
    
    def path_param_int(self, key: str, default: int = None) -> Optional[int]:
        """Get path parameter as integer (returns 400 error on invalid)"""
        value = self.path_param(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise HTTPError(400, f"Path parameter '{key}' must be an integer")
    
    def path_param_uuid(self, key: str, default: str = None) -> Optional[str]:
        """Get path parameter as UUID (validates format)"""
        import re
        value = self.path_param(key)
        if value is None:
            return default
        
        # UUID4 regex pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, value.lower()):
            raise HTTPError(400, f"Path parameter '{key}' must be a valid UUID")
        return value
    
    def header(self, key: str, default: Any = None) -> Optional[str]:
        """Get header value (case-insensitive)"""
        return self._headers.get(key.lower(), default)
    
    def bearer_token(self) -> Optional[str]:
        """Extract Bearer token from Authorization header"""
        auth_header = self.header("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None
    
    def basic_auth(self) -> Optional[tuple]:
        """Extract username/password from Basic auth header"""
        auth_header = self.header("authorization", "")
        if auth_header.startswith("Basic "):
            try:
                import base64
                encoded = auth_header[6:]  # Remove "Basic " prefix
                decoded = base64.b64decode(encoded).decode("utf-8")
                if ":" in decoded:
                    username, password = decoded.split(":", 1)
                    return (username, password)
            except Exception:
                pass
        return None
    
    def is_authenticated(self) -> bool:
        """Check if request has any form of authentication"""
        return self.bearer_token() is not None or self.basic_auth() is not None
    
    async def body(self, as_binary: bool = False) -> str:
        """Get request body as string or bytes
        
        Args:
            as_binary: If True, returns bytes for binary data handling
        """
        if as_binary:
            # For binary data, use arrayBuffer to avoid text corruption
            return await self.bytes()
        
        if self._body_cache is None:
            if hasattr(self.raw_request, 'text'):
                self._body_cache = await self.raw_request.text()
            else:
                self._body_cache = ""
        return self._body_cache
    
    async def bytes(self) -> bytes:
        """Get request body as bytes (for binary data like images)"""
        if self._bytes_cache is None:
            if hasattr(self.raw_request, 'arrayBuffer'):
                # Use arrayBuffer for binary data in Workers/Pyodide environment
                array_buffer = await self.raw_request.arrayBuffer()
                # Convert ArrayBuffer to bytes in Python
                import js
                from js import Uint8Array
                uint8_array = Uint8Array.new(array_buffer)
                self._bytes_cache = bytes(uint8_array.to_py())
            else:
                # Fallback for test environments
                body_str = await self.body()
                self._bytes_cache = body_str.encode('utf-8') if isinstance(body_str, str) else body_str
        return self._bytes_cache
    
    async def json(self) -> Any:
        """Get request body as JSON"""
        if self._json_cache is None:
            body = await self.body()
            if body:
                try:
                    self._json_cache = json.loads(body)
                except json.JSONDecodeError:
                    self._json_cache = None
            else:
                self._json_cache = None
        return self._json_cache


class Response:
    """Response wrapper for Workers with convenient methods"""
    
    def __init__(
        self,
        content: Any = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ):
        self.content = content
        self.status = status
        self.headers = headers or {}
        
        # Auto-detect content type
        if content_type:
            self.headers['Content-Type'] = content_type
        elif 'Content-Type' not in self.headers:
            if isinstance(content, (dict, list)):
                self.headers['Content-Type'] = 'application/json'
            elif isinstance(content, str):
                self.headers['Content-Type'] = 'text/plain; charset=utf-8'
        
        # Add default CORS headers for API endpoints
        if 'Access-Control-Allow-Origin' not in self.headers:
            self.headers['Access-Control-Allow-Origin'] = '*'
    
    def header(self, key: str, value: str) -> 'Response':
        """Set a header (chainable)"""
        self.headers[key] = value
        return self
    
    def cors(
        self,
        origin: str = '*',
        methods: str = 'GET, POST, PUT, DELETE, HEAD, OPTIONS',
        headers: str = 'Content-Type, Authorization'
    ) -> 'Response':
        """Set CORS headers (chainable)"""
        self.headers['Access-Control-Allow-Origin'] = origin
        self.headers['Access-Control-Allow-Methods'] = methods
        self.headers['Access-Control-Allow-Headers'] = headers
        return self
    
    @staticmethod
    def json(data: Any, status: int = 200, request_id: str = None) -> 'Response':
        """Create a JSON response with request ID"""
        if isinstance(data, dict) and request_id:
            data = {**data, 'request_id': request_id}
        return Response(data, status)
    
    @staticmethod
    def error(message: str, status: int = 400, detail: str = None, request_id: str = None) -> 'Response':
        """Create a standardized error response"""
        error_data = {
            'error': message,
            'status_code': status
        }
        if detail:
            error_data['detail'] = detail
        if request_id:
            error_data['request_id'] = request_id
        return Response(error_data, status)
    
    def to_workers_response(self):
        """Convert to Workers Response object"""
        import json as json_module
        from workers import Response as WorkersResponse
        
        # Handle different content types
        if isinstance(self.content, (dict, list)):
            # Use Response.json for JSON content
            return WorkersResponse.json(self.content, status=self.status, headers=self.headers)
        else:
            # Serialize other content
            if isinstance(self.content, str):
                body = self.content
            elif self.content is None:
                body = ""
            else:
                body = str(self.content)
            
            # Use regular Response for text/other content
            return WorkersResponse(body, status=self.status, headers=self.headers)


def error_response(message: str, status: int = 400) -> Response:
    """Create an error response"""
    return Response({'error': message, 'status_code': status}, status=status)


def wrap_exceptions(step: str = None, expose_details: bool = None):
    """
    Decorator to automatically wrap exceptions in standardized error responses.
    
    Args:
        step: Optional step identifier for debugging (e.g., "homepage", "database_query")
        expose_details: Whether to expose exception details. None = auto-detect from debug mode
    
    Usage:
        @app.get("/api/data")
        @wrap_exceptions(step="get_data", expose_details=True)
        async def get_data(request):
            # Any exception here will be caught and wrapped
            dal = DataLayer(request.env.DB)
            return await dal.get_data()
    """
    def decorator(handler):
        @functools.wraps(handler)
        async def wrapper(request):
            try:
                return await handler(request)
            except HTTPError:
                # Re-raise HTTP errors as-is (already properly formatted)
                raise
            except Exception as e:
                # Determine if we should expose details
                should_expose = expose_details
                if should_expose is None:
                    # Auto-detect based on environment or debug flag
                    env_name = getattr(request.env, 'ENVIRONMENT', 'production').lower()
                    should_expose = env_name in ('development', 'dev', 'test')
                
                # Build error response
                error_data = {
                    'error': 'Internal server error',
                    'status_code': 500,
                    'request_id': getattr(request, 'request_id', None)
                }
                
                if should_expose:
                    error_data['detail'] = str(e)
                    if step:
                        error_data['step'] = step
                
                return Response(error_data, status=500)
        return wrapper
    return decorator


def require_dev():
    """
    Decorator to restrict endpoint to development environments only.
    
    Usage:
        @app.get("/admin/debug")
        @require_dev()
        async def debug_endpoint(request):
            return {"debug_info": "sensitive data"}
    """
    def decorator(handler):
        @functools.wraps(handler)
        async def wrapper(request):
            # Check environment
            env_name = getattr(request.env, 'ENVIRONMENT', 'production').lower()
            if env_name not in ('development', 'dev', 'test'):
                raise DevOnlyError()
            
            return await handler(request)
        return wrapper
    return decorator


def geo_restrict(allowed: List[str] = None, blocked: List[str] = None):
    """
    Decorator to restrict endpoint access by country.
    Uses Cloudflare's CF-IPCountry header.
    
    Args:
        allowed: List of allowed country codes (e.g., ["US", "CA", "EU"])
        blocked: List of blocked country codes (takes precedence over allowed)
    
    Usage:
        @app.get("/api/games")
        @geo_restrict(allowed=["US", "CA", "EU"])
        async def games(request):
            return await get_games()
    """
    def decorator(handler):
        @functools.wraps(handler)
        async def wrapper(request):
            # Get country from Cloudflare header
            country = request.header('cf-ipcountry', 'XX').upper()
            
            # Check blocked countries first
            if blocked and country in blocked:
                raise GeoRestrictedError(country, allowed or [])
            
            # Check allowed countries
            if allowed and country not in allowed:
                raise GeoRestrictedError(country, allowed)
            
            return await handler(request)
        return wrapper
    return decorator


class Route:
    """Represents a single route"""
    
    def __init__(self, path: str, handler: Callable, methods: List[str]):
        self.path = path
        self.handler = handler
        self.methods = [m.upper() for m in methods]
        
        # Convert path to regex with parameter extraction
        self.regex, self.param_names = self._compile_path(path)
    
    def _compile_path(self, path: str) -> Tuple[re.Pattern, List[str]]:
        """Convert path pattern to regex with parameter names"""
        param_names = []
        regex_pattern = path
        
        # Find path parameters like {id}, {slug}, etc.
        param_pattern = re.compile(r'\{([^}]+)\}')
        
        for match in param_pattern.finditer(path):
            param_name = match.group(1)
            param_names.append(param_name)
            
            # Support type hints like {id:int} or {slug:str}
            if ':' in param_name:
                param_name, param_type = param_name.split(':', 1)
                param_names[-1] = param_name  # Store clean name
                
                if param_type == 'int':
                    replacement = r'(\d+)'
                else:  # default to string
                    replacement = r'([^/]+)'
            else:
                replacement = r'([^/]+)'
            
            regex_pattern = regex_pattern.replace(match.group(0), replacement)
        
        # Ensure exact match
        if not regex_pattern.endswith('$'):
            regex_pattern += '$'
        if not regex_pattern.startswith('^'):
            regex_pattern = '^' + regex_pattern
        
        return re.compile(regex_pattern), param_names
    
    def matches(self, method: str, path: str) -> Tuple[bool, Dict[str, str]]:
        """Check if route matches method and path, return path params if match"""
        if method.upper() not in self.methods:
            return False, {}
        
        match = self.regex.match(path)
        if not match:
            return False, {}
        
        # Extract path parameters
        path_params = {}
        for i, param_name in enumerate(self.param_names):
            path_params[param_name] = match.group(i + 1)
        
        return True, path_params


class Router:
    """URL router with support for path parameters and sub-routers"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self.sub_routers: List[Tuple[str, Router]] = []
    
    def route(self, path: str, methods: List[str] = None):
        """Decorator for adding routes"""
        if methods is None:
            methods = ["GET"]
        
        def decorator(handler):
            route = Route(path, handler, methods)
            self.routes.append(route)
            return handler
        
        return decorator
    
    def get(self, path: str):
        """Decorator for GET routes"""
        return self.route(path, ["GET"])
    
    def post(self, path: str):
        """Decorator for POST routes"""
        return self.route(path, ["POST"])
    
    def put(self, path: str):
        """Decorator for PUT routes"""
        return self.route(path, ["PUT"])
    
    def delete(self, path: str):
        """Decorator for DELETE routes"""
        return self.route(path, ["DELETE"])
    
    def head(self, path: str):
        """Decorator for HEAD routes"""
        return self.route(path, ["HEAD"])
    
    def get_routes(self) -> List[Tuple[str, List[str], Callable]]:
        """Get list of all routes as (path, methods, handler) tuples"""
        routes = []
        for route in self.routes:
            routes.append((route.path, route.methods, route.handler))
        return routes
    
    def include_router(self, prefix: str, router: 'Router'):
        """Include a sub-router with path prefix"""
        # Normalize prefix (remove trailing slash, ensure leading slash)
        prefix = ('/' + prefix.strip('/')).rstrip('/')
        if prefix == '':
            prefix = '/'
        
        self.sub_routers.append((prefix, router))
    
    def resolve(self, method: str, path: str) -> Tuple[Optional[Callable], Dict[str, str]]:
        """Resolve a method and path to a handler and path parameters"""
        
        # Try direct routes first
        for route in self.routes:
            matches, path_params = route.matches(method, path)
            if matches:
                return route.handler, path_params
        
        # Try sub-routers
        for prefix, sub_router in self.sub_routers:
            if path.startswith(prefix):
                # Strip prefix and try sub-router
                sub_path = path[len(prefix):] or '/'
                handler, path_params = sub_router.resolve(method, sub_path)
                if handler:
                    return handler, path_params
        
        return None, {}


class Middleware(ABC):
    """Base middleware class"""
    
    @abstractmethod
    async def process_request(self, request: Request) -> Request:
        """Process incoming request (before routing)"""
        return request
    
    @abstractmethod
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process outgoing response (after handler)"""
        return response


class CorsMiddleware(Middleware):
    """CORS middleware for handling cross-origin requests"""
    
    def __init__(
        self,
        allow_origins: str = "*",
        allow_methods: str = "GET, POST, PUT, DELETE, HEAD, OPTIONS",
        allow_headers: str = "Content-Type, Authorization"
    ):
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
    
    async def process_request(self, request: Request) -> Request:
        """Handle preflight OPTIONS requests"""
        return request
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add CORS headers to all responses"""
        response.cors(
            origin=self.allow_origins,
            methods=self.allow_methods,
            headers=self.allow_headers
        )
        
        if request.method == "OPTIONS":
            response.status = 200
            response.content = ""
        
        return response


class TimingMiddleware(Middleware):
    """Middleware to add response time headers"""
    
    async def process_request(self, request: Request) -> Request:
        """Record start time"""
        request._start_time = time.time()
        return request
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add timing header"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            response.header("X-Response-Time", f"{duration:.3f}s")
        return response


class Kinglet:
    """Lightweight ASGI-style application for Python Workers"""
    
    def __init__(self, test_mode=False, root_path="", debug=False, auto_wrap_exceptions=True):
        self.router = Router()
        self.middleware_stack: List[Middleware] = []
        self.error_handlers: Dict[int, Callable] = {}
        self.test_mode = test_mode
        self.root_path = root_path.rstrip('/')  # Remove trailing slash
        self.debug = debug
        self.auto_wrap_exceptions = auto_wrap_exceptions
        
    def route(self, path: str, methods: List[str] = None):
        """Decorator for adding routes"""
        if methods is None:
            methods = ["GET"]
        # Apply root_path to the route
        full_path = self.root_path + path
        
        def decorator(handler):
            # Auto-wrap with exception handling if enabled
            if self.auto_wrap_exceptions:
                handler = wrap_exceptions(expose_details=self.debug)(handler)
            
            return self.router.route(full_path, methods)(handler)
        
        return decorator
    
    def get(self, path: str):
        """Decorator for GET routes"""
        return self.route(path, ["GET"])
    
    def post(self, path: str):
        """Decorator for POST routes"""
        return self.route(path, ["POST"])
    
    def put(self, path: str):
        """Decorator for PUT routes"""
        return self.route(path, ["PUT"])
    
    def delete(self, path: str):
        """Decorator for DELETE routes"""
        return self.route(path, ["DELETE"])
    
    def head(self, path: str):
        """Decorator for HEAD routes"""
        return self.route(path, ["HEAD"])
    
    def include_router(self, prefix: str, router: Router):
        """Include a sub-router with path prefix"""
        self.router.include_router(prefix, router)
    
    def exception_handler(self, status_code: int):
        """Decorator for custom error handlers"""
        def decorator(handler):
            self.error_handlers[status_code] = handler
            return handler
        return decorator
    
    def middleware(self, middleware_class):
        """Decorator for adding middleware classes"""
        middleware_instance = middleware_class()
        self.middleware_stack.append(middleware_instance)
        return middleware_class
    
    async def __call__(self, request, env):
        """ASGI-compatible entry point for Workers"""
        try:
            # Wrap the raw request
            kinglet_request = Request(request, env)
            
            # Apply middleware (pre-processing)
            for middleware in self.middleware_stack:
                kinglet_request = await middleware.process_request(kinglet_request)
            
            # Route the request
            handler, path_params = self.router.resolve(
                kinglet_request.method, 
                kinglet_request.path
            )
            
            if handler is None:
                response = Response({"error": "Not found"}, status=404)
            else:
                # Inject path parameters into request
                kinglet_request.path_params = path_params
                
                # Call the handler
                response = await handler(kinglet_request)
                
                # Check if handler returned a workers.Response directly
                if not self.test_mode:
                    try:
                        from workers import Response as WorkersResponse
                        if isinstance(response, WorkersResponse):
                            # Skip middleware processing for direct Workers responses
                            return response
                    except ImportError:
                        pass  # Continue with normal processing
                
                # Ensure response is a Kinglet Response object
                if not isinstance(response, Response):
                    if isinstance(response, dict):
                        response = Response(response)
                    elif isinstance(response, str):
                        response = Response({"message": response})
                    else:
                        response = Response(response)
            
            # Apply middleware (post-processing) - only for Kinglet Response objects
            if self.test_mode:
                # In test mode, skip Workers conversion and return Kinglet Response
                for middleware in reversed(self.middleware_stack):
                    response = await middleware.process_response(kinglet_request, response)
                # Add request ID header
                if hasattr(response, 'headers'):
                    response.headers['X-Request-ID'] = kinglet_request.request_id
                return response
            else:
                # Production mode - convert to Workers Response
                try:
                    from workers import Response as WorkersResponse
                    if not isinstance(response, WorkersResponse):
                        for middleware in reversed(self.middleware_stack):
                            response = await middleware.process_response(kinglet_request, response)
                        
                        # Add request ID header
                        if hasattr(response, 'headers'):
                            response.headers['X-Request-ID'] = kinglet_request.request_id
                        
                        # Convert Kinglet Response to Workers Response
                        return response.to_workers_response()
                    else:
                        # Already a Workers Response, return as-is
                        return response
                except ImportError:
                    # If workers module not available, return Kinglet response
                    for middleware in reversed(self.middleware_stack):
                        response = await middleware.process_response(kinglet_request, response)
                    return response
            
        except Exception as e:
            # Handle exceptions
            status_code = getattr(e, 'status_code', 500)
            
            if status_code in self.error_handlers:
                try:
                    response = await self.error_handlers[status_code](kinglet_request, e)
                    if not isinstance(response, Response):
                        response = Response(response)
                    
                    # Return based on mode
                    if self.test_mode:
                        return response
                    else:
                        try:
                            return response.to_workers_response()
                        except ImportError:
                            return response
                except:
                    pass  # Fall through to default error handler
            
            # Default error response with request ID and debug info
            if isinstance(e, HTTPError):
                error_message = e.message
            else:
                error_message = str(e) if self.debug else "Internal Server Error"
            
            error_resp = Response.error(
                message=error_message,
                status=status_code,
                request_id=kinglet_request.request_id
            )
            
            # Return based on mode
            if self.test_mode:
                return error_resp
            else:
                try:
                    return error_resp.to_workers_response()
                except ImportError:
                    return error_resp


# === NEW FEATURES ===

# === D1 DATABASE HELPERS ===

def d1_unwrap(obj):
    """
    Unwrap Cloudflare D1 JavaScript proxy objects to Python dictionaries.
    
    D1 query results are JavaScript proxy objects that need conversion to 
    Python dicts for safe access. This handles the standard D1 patterns.
    
    Args:
        obj: D1 result object (typically has .to_py() method)
        
    Returns:
        dict: Python dictionary with the data
        
    Raises:
        ValueError: If the object type cannot be unwrapped
        
    Usage:
        result = await db.prepare("SELECT * FROM games").first()
        game_data = d1_unwrap(result)  # Safe Python dict
    """
    if obj is None:
        return {}
    
    # Already a Python dict - return as-is
    if isinstance(obj, dict):
        return obj
    
    # Standard D1 proxy object with .to_py() method
    if hasattr(obj, "to_py"):
        try:
            return obj.to_py()
        except Exception as e:
            raise ValueError(f"Failed to unwrap D1 object via .to_py(): {e}")
    
    # Object with dict-like interface
    if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
        try:
            return {key: obj[key] for key in obj.keys()}
        except Exception as e:
            raise ValueError(f"Failed to unwrap dict-like object: {e}")
    
    # Unknown object type - raise instead of guessing
    raise ValueError(f"Cannot unwrap D1 object of type {type(obj).__name__}. Expected dict or object with .to_py() method.")

def d1_unwrap_results(results):
    """
    Lazily unwrap D1 query results.
    
    Returns:
        generator: Unwrapped dictionaries
    """
    if not results:
        return
    
    if hasattr(results, 'results') and results.results:
        for row in results.results:
            yield d1_unwrap(row)
    elif isinstance(results, list):
        for row in results:
            yield d1_unwrap(row)
    else:
        yield d1_unwrap(results)


# === R2 STORAGE HELPERS ===

def r2_get_metadata(obj, path, default=None):
    """
    Extract metadata from R2 objects using dot notation.
    
    Returns:
        Value at path or default
    """
    if obj is None:
        return default
    
    current = obj
    for part in path.split('.'):
        if current is None:
            return default
        
        # Try attribute access first (most common)
        if hasattr(current, part):
            current = getattr(current, part)
            # Check for JavaScript undefined immediately after getattr
            try:
                import js
                if current is js.undefined:
                    return default
            except:
                if str(current) == "undefined":
                    return default
        # Then dict access
        elif isinstance(current, dict):
            current = current.get(part)
        # Then JS object bracket access
        else:
            try:
                current = current[part]
            except (KeyError, TypeError, AttributeError):
                return default
    
    result = current if current is not None else default
    
    # Check for JavaScript undefined before stringifying
    try:
        import js
        if result is js.undefined:
            return default
    except:
        # Fallback: check string representation
        if str(result) == "undefined":
            return default
        
    return result

def r2_get_content_info(obj):
    """Extract common R2 object metadata."""
    result = {
        'content_type': r2_get_metadata(obj, "httpMetadata.contentType", "application/octet-stream"),
        'size': r2_get_metadata(obj, "size", None),
        'etag': r2_get_metadata(obj, "httpEtag", None), 
        'last_modified': r2_get_metadata(obj, "uploaded", None),
        'custom_metadata': r2_get_metadata(obj, "customMetadata", {})
    }
    
    # Ensure no undefined values leak through
    for key, value in result.items():
        if str(value) == "undefined":
            if key == 'content_type':
                result[key] = "application/octet-stream"
            elif key == 'custom_metadata':
                result[key] = {}
            else:
                result[key] = None
                
    return result

def r2_put(bucket, key: str, data: bytes, content_type: str = "application/octet-stream", metadata: dict = None):
    """Upload data to R2 with JS interop handling."""
    import js
    
    size = len(data)
    ab = js.ArrayBuffer.new(size)
    u8 = js.Uint8Array.new(ab)
    u8.set(bytearray(data))
    
    options = {"httpMetadata": {"contentType": content_type}}
    if metadata:
        options["customMetadata"] = metadata
    
    return bucket.put(key, ab, options)

def r2_delete(bucket, key: str):
    """Delete object from R2."""
    return bucket.delete(key)

def r2_list(bucket, prefix: str = "", limit: int = 1000):
    """List R2 objects with optional prefix filter."""
    options = {"limit": limit}
    if prefix:
        options["prefix"] = prefix
    return bucket.list(options)

# === ENHANCED ASSET URL GENERATION ===

def asset_url(request, identifier: str, asset_type: str = "media") -> str:
    """
    Generate environment-aware URLs for different asset types.
    
    Args:
        request: Request object
        identifier: Asset identifier (UID, filename, etc.)
        asset_type: Type of asset ("media", "static", "assets")
        
    Returns:
        str: Full URL to the asset
        
    Usage:
        media_url = asset_url(request, uid, "media")      # /api/media/{uid}
        static_url = asset_url(request, "style.css", "static")  # /assets/{file}
        asset_url = asset_url(request, "logo.png", "assets")    # /assets/{file}
    """
    cdn_base = getattr(request.env, 'CDN_BASE_URL', None)
    
    if asset_type == "media":
        path = f"/api/media/{identifier}"
    elif asset_type in ("static", "assets"):
        path = f"/assets/{identifier}"
    else:
        # Custom asset type
        path = f"/{asset_type}/{identifier}"
    
    if cdn_base:
        # Production: Use CDN domain
        return f"{cdn_base.rstrip('/')}{path}"
    else:
        # Development: Auto-detect host from request
        try:
            host = request.header('host', 'localhost:8787')
            forwarded_proto = request.header('x-forwarded-proto', 'http')
            protocol = 'https' if forwarded_proto == 'https' or host.startswith('https') else 'http'
            return f"{protocol}://{host}{path}"
        except Exception:
            return path

# 1 & 3: Cache-Aside Decorator with CacheService
class CacheService:
    """R2-backed cache service for Experience APIs"""
    
    def __init__(self, storage, ttl: int = 3600):
        self.storage = storage
        self.ttl = ttl
    
    async def get_or_generate(self, cache_key: str, generator_func: Callable, **kwargs):
        """Get from cache or generate fresh data"""
        try:
            # Try cache first
            obj = await self.storage.get(f"cache/{cache_key}")
            if obj:
                try:
                    if hasattr(obj, 'text'):
                        cached_data = json.loads((await obj.text()))
                    else:
                        # Mock storage returns string directly
                        cached_data = json.loads(obj)
                    # Check if still valid
                    if time.time() - cached_data.get('_cached_at', 0) < self.ttl:
                        cached_data['_cache_hit'] = True
                        return cached_data
                except (json.JSONDecodeError, AttributeError):
                    pass  # Invalid cache, generate fresh
            
            # Generate fresh data
            fresh_data = await generator_func(**kwargs)
            fresh_data['_cached_at'] = time.time()
            fresh_data['_cache_hit'] = False
            
            # Store in cache
            await self.storage.put(
                f"cache/{cache_key}",
                json.dumps(fresh_data),
                {"httpMetadata": {"contentType": "application/json"}}
            )
            
            return fresh_data
            
        except Exception:
            # If cache fails, just return fresh data
            return await generator_func(**kwargs)

def cache_aside(storage_binding: str = "STORAGE", cache_type: str = "default", ttl: int = 3600):
    """Decorator for cache-aside pattern with R2"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get storage from request environment
            storage = getattr(request.env, storage_binding, None)
            if not storage:
                # No storage available, call function directly
                return await func(request, *args, **kwargs)
            
            # Create cache service
            cache = CacheService(storage, ttl)
            
            # Generate cache key from function name, path params, and query string
            import hashlib
            cache_key_parts = [cache_type, func.__name__]
            
            # Include path parameters in cache key (e.g., /game/{slug} -> /game/wild-west)
            if hasattr(request, 'path_params') and request.path_params:
                path_param_str = "_".join(f"{k}={v}" for k, v in request.path_params.items())
                cache_key_parts.append(path_param_str)
            
            # Include query string if present
            if hasattr(request, 'query_string') and request.query_string:
                cache_key_parts.append(request.query_string)
                
            cache_key = hashlib.sha256("_".join(cache_key_parts).encode()).hexdigest()[:16]
            
            # Use cache service
            async def generator():
                return await func(request, *args, **kwargs)
            
            return await cache.get_or_generate(cache_key, generator)
        
        return wrapper
    return decorator

# 2: Environment-Aware URL Generation
def media_url(request, uid: str) -> str:
    """Generate environment-aware media URL"""
    cdn_base = getattr(request.env, 'CDN_BASE_URL', None)
    
    if cdn_base:
        return f"{cdn_base.rstrip('/')}/api/media/{uid}"
    else:
        try:
            host = request.header('host', 'localhost:8787')
            forwarded_proto = request.header('x-forwarded-proto', 'http')
            protocol = 'https' if forwarded_proto == 'https' or host.startswith('https') else 'http'
            return f"{protocol}://{host}/api/media/{uid}"
        except Exception:
            return f"/api/media/{uid}"

# 4: Request Validation Decorators  
def validate_json_body(func):
    """Decorator to validate JSON body exists and is valid"""
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        try:
            body = await request.json()
            if not body:
                return Response.error("Request body cannot be empty", 400, request.request_id)
        except Exception as e:
            return Response.error(f"Invalid JSON: {str(e)}", 400, request.request_id)
        
        return await func(request, *args, **kwargs)
    return wrapper

def require_field(field_name: str, field_type=str):
    """Decorator to require specific field in JSON body"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            try:
                body = await request.json()
                if field_name not in body:
                    return Response.error(f"Field '{field_name}' is required", 400, request.request_id)
                
                # Type validation
                if not isinstance(body[field_name], field_type):
                    return Response.error(f"Field '{field_name}' must be {field_type.__name__}", 400, request.request_id)
                
            except Exception as e:
                return Response.error(f"Invalid request: {str(e)}", 400, request.request_id)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Export main classes for convenience
__all__ = [
    "Kinglet", "Router", "Route", "Response", "Request", "Middleware", 
    "CorsMiddleware", "TimingMiddleware", "TestClient", "HTTPError", "GeoRestrictedError", "DevOnlyError",
    "generate_request_id", "error_response", "wrap_exceptions", "require_dev", "geo_restrict",
    "CacheService", "cache_aside", "media_url", "validate_json_body", "require_field",
    "d1_unwrap", "d1_unwrap_results",
    "r2_get_metadata", "r2_get_content_info", "r2_put", "r2_delete", "r2_list",
    "asset_url"
]

# Alias for backward compatibility and easier import
TestClient = _KingletTestClient
KingletTestClient = _KingletTestClient