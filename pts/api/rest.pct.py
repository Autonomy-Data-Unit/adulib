# %% [markdown]
# # rest

# %%
#|default_exp rest

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()

# %%
#|export
import requests
from urllib.parse import urljoin
import diskcache
import aiohttp
import tempfile
from asynciolimiter import Limiter

# %%
import adulib.rest


# %% [markdown]
# # Async REST functions

# %%
#|export
async def async_get(endpoint, params=None, headers=None):
    """Fetch data from a given RESTful API endpoint using an HTTP GET request.

    :param endpoint: The API endpoint URL (string).
    :param params: A dictionary of query parameters (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Request failed with status {response.status}", "details": await response.text()}
  
async def async_put(endpoint, data=None, headers=None):
    """Update data at a given RESTful API endpoint using an HTTP PUT request.

    :param endpoint: The API endpoint URL (string).
    :param data: A dictionary of data to send in the body of the request (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    async with aiohttp.ClientSession() as session:
        async with session.put(endpoint, json=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Request failed with status {response.status}", "details": await response.text()}

async def async_post(endpoint, data=None, headers=None):
    """Send data to a given RESTful API endpoint using an HTTP POST request.

    :param endpoint: The API endpoint URL (string).
    :param data: A dictionary of data to send in the body of the request (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Request failed with status {response.status}", "details": await response.text()}
    
async def async_delete(endpoint, headers=None):
    """Delete a resource at a given RESTful API endpoint using an HTTP DELETE request.

    :param endpoint: The API endpoint URL (string).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    async with aiohttp.ClientSession() as session:
        async with session.delete(endpoint, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Request failed with status {response.status}", "details": await response.text()}


# %%
await async_get("https://httpbin.org/get",
    params={
        "query": "test",
        "page": 2
    },
    headers={
        "User-Agent": "MyTestClient/1.0",
        "Authorization": "Bearer testtoken123"
    }
)

# %%
await async_put("https://httpbin.org/put",
    data={
        "key1": "value1",
        "key2": "value2"
    },
    headers={"Content-Type": "application/json"}
)

# %%
await async_post("https://httpbin.org/post",
    data={
        "key1": "value1",
        "key2": "value2"
    },
    headers={"Content-Type": "application/json"}
)

# %%
await async_delete("https://httpbin.org/delete",
    headers={"Content-Type": "application/json"}
)


# %% [markdown]
# # Sync REST functions

# %%
#|export
def get(endpoint, params=None, headers=None):
    """Fetch data from a given RESTful API endpoint using an HTTP GET request.

    :param endpoint: The API endpoint URL (string).
    :param params: A dictionary of query parameters (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    response = requests.get(endpoint, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}
    
def post(endpoint, data=None, headers=None):
    """Send data to a given RESTful API endpoint using an HTTP POST request.

    :param endpoint: The API endpoint URL (string).
    :param data: A dictionary of data to send in the body of the request (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    response = requests.post(endpoint, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}

def put(endpoint, data=None, headers=None):
    """Update data at a given RESTful API endpoint using an HTTP PUT request.

    :param endpoint: The API endpoint URL (string).
    :param data: A dictionary of data to send in the body of the request (default is None).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    response = requests.put(endpoint, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}

def delete(endpoint, headers=None):
    """Delete a resource at a given RESTful API endpoint using an HTTP DELETE request.

    :param endpoint: The API endpoint URL (string).
    :param headers: A dictionary of HTTP headers (default is None).
    :return: The JSON response as a dictionary, or an error message.
    """
    response = requests.delete(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}



# %%
get("https://httpbin.org/get",
    params={
        "query": "test",
        "page": 2
    },
    headers={
        "User-Agent": "MyTestClient/1.0",
        "Authorization": "Bearer testtoken123"
    }
)


# %% [markdown]
# # `AsyncAPIHandler`

# %%
#|export
class AsyncAPIHandler:
    GET="get"
    PUT="put"
    POST="post"
    DELETE="delete"
    
    def __init__(self,
                 base_url=None,
                 default_params=None,
                 default_headers=None,
                 rate_limit=None,
                 use_cache=True,
                 cache_dir=None,
                 call_quota=None):
        """
        A handler for making asynchronous API calls with support for caching, rate limiting, and default parameters.

        :param base_url: The base URL of the API. This will be prepended to all endpoint calls.
        :param default_params: A dictionary of default query parameters to be included in every request.
        :param default_headers: A dictionary of default headers to be included in every request.
        :param rate_limit: The rate limit for API calls, specified as the number of calls per second.
        :param use_cache: A boolean indicating whether to enable caching of API responses.
        :param cache_dir: The directory where cached responses will be stored. If None, a temporary directory will be created.
        :param call_quota: An optional limit on the number of API calls that can be made. If None, there is no limit.

        This class provides methods for making GET, POST, PUT, and DELETE requests asynchronously, while managing
        caching and rate limiting. It also allows checking and clearing the cache for specific API calls.
        """
        self.base_url = base_url
        self.default_params = default_params or {}
        self.default_headers = default_headers or {}
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.call_quota = call_quota
        self.call_counter = 0
        
        if use_cache:
            if self.cache_dir is None: self.cache_dir = tempfile.mkdtemp()
            self._cache = diskcache.Cache(self.cache_dir, eviction_policy="none", size_limit=2**40)
        else: self._cache = None
        
        self.rate_limit = rate_limit
        if rate_limit:
            self._rate_limiter = Limiter(rate_limit)
        else:
            self._rate_limiter = None
        
    @property
    def remaining_call_quota(self):
        if self.call_quota is None:
            return None
        return self.call_quota - self.call_counter
        
    def reset_quota(self):
        self.call_counter = 0
        
    def __get_defaults(self, method, endpoint, params, headers):
        endpoint = urljoin(self.base_url, endpoint) if endpoint else self.base_url
        params = params or {}
        headers = headers or {}
        params = {**params, **self.default_params}
        headers = {**headers, **self.default_headers}
        cache_key = f"{method}:{endpoint}:{params}:{headers}"
        return endpoint, params, headers, cache_key
    
    async def __load_cache_or_make_call(self, func, args, only_use_cache, cache_key):
        if only_use_cache or (self.use_cache and cache_key in self._cache):
            return self._cache[cache_key]
        else:
            if self.call_quota is not None and self.remaining_call_quota <= 0:
                raise RuntimeError("API call quota has been exceeded.")
            self.call_counter += 1
            if self._rate_limiter: await self._rate_limiter.wait()
            result = await func(*args)
            if self.use_cache: self._cache[cache_key] = result
        return result
    
    async def call(self, method, endpoint=None, params=None, data=None, headers=None, only_use_cache=False, **param_kwargs):
        """
        Make a request to the API.

        :param method: The HTTP method to use (e.g., "get", "put", "post", "delete").
        :param endpoint: The API endpoint to request.
        :param params: A dictionary of query parameters for the request.
        """
        params = params or {}
        params = {**params, **param_kwargs}
        endpoint, params, headers, cache_key = self.__get_defaults(method, endpoint, params, headers)
        if method == AsyncAPIHandler.GET: func = async_get
        elif method == AsyncAPIHandler.PUT: func = async_put
        elif method == AsyncAPIHandler.POST: func = async_post
        elif method == AsyncAPIHandler.DELETE: func = async_delete
        else: raise ValueError(f"Invalid method: {method}")
        return await self.__load_cache_or_make_call(func, (endpoint, params, headers), only_use_cache, cache_key)
    
    async def get(self, endpoint=None, params=None, headers=None, only_use_cache=False, **param_kwargs):
        return await self.call(self.GET, endpoint, params, headers, only_use_cache, **param_kwargs)
    
    async def put(self, endpoint=None, data=None, only_use_cache=False, headers=None):
        return await self.call(self.PUT, endpoint, data, headers, only_use_cache)
    
    async def post(self, endpoint=None, data=None, only_use_cache=False, headers=None):
        return await self.call(self.POST, endpoint, data, headers, only_use_cache)
    
    async def delete(self, endpoint=None, only_use_cache=False, headers=None):
        return await self.call(self.DELETE, endpoint, headers, only_use_cache)
    
    def check_cache(self, method, endpoint=None, params=None, headers=None, **param_kwargs):
        params = params or {}
        params = {**params, **param_kwargs}
        _, _, _, cache_key = self.__get_defaults(method, endpoint, params, headers)
        return cache_key in self._cache
    
    def clear_cache_key(self, method, endpoint=None, params=None, headers=None, **param_kwargs):
        params = params or {}
        params = {**params, **param_kwargs}
        _, _, _, cache_key = self.__get_defaults(method, endpoint, params, headers)
        del self._cache[cache_key]


# %%
api_handler = AsyncAPIHandler(
    base_url="https://httpbin.org/",
    default_params={"api_key": "your_api_key"},
    default_headers={"User-Agent": "MyTestClient/1.0"},
    rate_limit=10
)

await api_handler.get("get")

# %%
api_handler.check_cache("get", "get")

# %%
api_handler.clear_cache_key("get", "get")
api_handler.check_cache("get", "get")
