# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/src/rest.ipynb.

# %% auto 0
__all__ = ['async_get', 'async_put', 'async_post', 'async_delete', 'get', 'post', 'put', 'delete', 'AsyncAPIHandler']

# %% ../nbs/src/rest.ipynb 4
try:
    import requests
    from urllib.parse import urljoin
    import diskcache
    import aiohttp
    import tempfile
    from asynciolimiter import Limiter
except ImportError:
    print("Install adulib[rest] to use this API.")

# %% ../nbs/src/rest.ipynb 7
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

# %% ../nbs/src/rest.ipynb 13
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


# %% ../nbs/src/rest.ipynb 16
class AsyncAPIHandler:
    def __init__(self,
                 base_url=None,
                 default_params=None,
                 default_headers=None,
                 rate_limit=None,
                 use_cache=True,
                 cache_dir=None):
        """
        :param base_url: The base URL of the API.
        :param default_params: A dictionary of default query parameters.
        :param default_headers: A dictionary of default headers.
        :param rate_limit: The rate (calls per second) limit for the API.
        :param use_cache: Whether to use caching for the API.
        :param cache_dir: The directory to store the cache.
        """
        self.base_url = base_url
        self.default_params = default_params or {}
        self.default_headers = default_headers or {}
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        if use_cache:
            if self.cache_dir is None: self.cache_dir = tempfile.mkdtemp()
            self._cache = diskcache.Cache(self.cache_dir)
        else: self._cache = None
        
        self.rate_limit = rate_limit
        if rate_limit:
            self._rate_limiter = Limiter(rate_limit)
        else:
            self._rate_limiter = None
        
    def __get_defaults(self, method, endpoint, params, headers):
        endpoint = urljoin(self.base_url, endpoint) if endpoint else self.base_url
        params = params or {}
        headers = headers or {}
        params = {**params, **self.default_params}
        headers = {**headers, **self.default_headers}
        cache_key = f"{method}:{endpoint}:{params}:{headers}"
        return endpoint, params, headers, cache_key
    
    async def __load_cache_or_make_call(self, func, args, cache_key):
        if self.use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        else:
            if self._rate_limiter: await self._rate_limiter.wait()
            result = await func(*args)
            if self.use_cache: self._cache[cache_key] = result
        return result
    
    async def get(self, endpoint=None, params=None, headers=None, **param_kwargs):
        params = params or {}
        params = {**params, **param_kwargs}
        endpoint, params, headers, cache_key = self.__get_defaults("get", endpoint, params, headers)
        return await self.__load_cache_or_make_call(async_get, (endpoint, params, headers), cache_key)
    
    async def put(self, endpoint=None, data=None, headers=None):
        endpoint, _, headers, cache_key = self.__get_defaults("put", endpoint, None, headers)
        return await self.__load_cache_or_make_call(async_put, (endpoint, data, headers), cache_key)
    
    async def post(self, endpoint=None, data=None, headers=None):
        endpoint, _, headers, cache_key = self.__get_defaults("post", endpoint, None, headers)
        return await self.__load_cache_or_make_call(async_post, (endpoint, data, headers), cache_key)
    
    async def delete(self, endpoint=None, headers=None):
        endpoint, _, headers, cache_key = self.__get_defaults("delete", endpoint, None, headers)
        return await self.__load_cache_or_make_call(async_delete, (endpoint, headers), cache_key)
