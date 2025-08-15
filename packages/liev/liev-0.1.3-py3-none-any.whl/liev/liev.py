import requests
import json
import io
from openai import OpenAI
import os

class Liev:
    """
    A Python client for interacting with the Liev AI API.
    
    The Liev class provides methods to communicate with language models through the Liev AI platform,
    including support for chat completions, streaming responses, and OpenAI-compatible endpoints.
    
    Attributes:
        __api_key (str): The API key for authentication
        __base_url (str): The base URL for the Liev API
        __last_call_consumption_info (dict): Information about the last API call's resource consumption
        __last_call_is_failover_response (bool): Whether the last response was from a failover model
        __last_call_model (str): The model that was used for the last API call
        __last_call_response_failed_models (list): List of models that failed before getting a response
    """
    
    def __init__(self, api_key=None, base_url=os.getenv('LIEV_BASE_URL','https://api.liev.ai/')):
        """
        Initialize the Liev client.
        
        Args:
            api_key (str, optional): The API key required for authentication. If None, will look for LIEV_API_KEY environment variable.
            base_url (str, optional): The base URL for the Liev API.
                                    Defaults to 'https://api.liev.ai/'.
        
        Raises:
            ValueError: If api_key is None and LIEV_API_KEY environment variable is not set.
        """
        if api_key is None:
            api_key = os.getenv('LIEV_API_KEY')
            if api_key is None:
                raise ValueError("API key is required. Pass api_key=<key> in constructor or set LIEV_API_KEY environment variable.")
        self.__api_key = api_key
        self.__base_url = base_url
        self.__last_call_consumption_info = None
        self.__last_call_is_failover_response = False
        self.__last_call_model = None
        self.__last_call_response_failed_models = []
    
    def get_last_call_info(self):
        """
        Get information about the last API call made.
        
        Returns:
            dict: A dictionary containing:
                - model (str): The model used for the last call
                - consumption_info (dict): Resource consumption information
                - is_failover_response (bool): Whether the response came from a failover model
                - response_failed_models (list): List of models that failed before success
        """
        return {
            'model': self.__last_call_model,
            'consumption_info': self.__last_call_consumption_info,
            'is_failover_response': self.__last_call_is_failover_response,
            'response_failed_models': self.__last_call_response_failed_models
        }
    
    def __clear_last_call_stats(self):
        """
        Clear the statistics from the last API call.
        
        This is a private method that resets all tracking variables to their initial state.
        """
        self.__last_call_consumption_info = None
        self.__last_call_is_failover_response = False
        self.__last_call_model = None
        self.__last_call_response_failed_models = []

    def __set_last_call_stats(self, headers):
        """
        Set the statistics from the last API call based on response headers.
        
        This is a private method that extracts and stores call statistics from API response headers.
        
        Args:
            headers (dict): HTTP response headers containing Liev-specific metadata.
        """
        self.__last_call_consumption_info = json.loads(headers['Liev-Consumption']) if 'Liev-Consumption' in headers and headers['Liev-Consumption'] != 'None' else {}
        self.__last_call_is_failover_response = headers['Liev-Response-Is-Failover']
        self.__last_call_model = headers['Liev-Response-Model']
        self.__last_call_response_failed_models = headers['Liev-Response-Failed-Models']

    def get_llms(self):
        """
        Retrieve a list of available language models.
        
        Returns:
            dict: JSON response containing available language models.
        
        Raises:
            Exception: For various error conditions including:
                - Authentication errors (401)
                - Access denied (403)
                - Endpoint not found (404)
                - Connection errors
                - Timeout errors
                - JSON decode errors
                - Other HTTP and request errors
        """
        try:
            response = requests.get(
                self.__base_url + "/v1/llm",
                headers={'Authorization': f"Bearer {self.__api_key}"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err: 
            status_code = http_err.response.status_code
            if status_code == 401:
                raise Exception(f"Authentication error: Invalid or expired API token. Code: {status_code}")
            elif status_code == 403:
                raise Exception(f"Access denied: Insufficient permissions. Code: {status_code}")
            elif status_code == 404:
                raise Exception(f"Endpoint not found. Code: {status_code}")
            else:
                raise Exception(f"HTTP Error: {http_err}. Code: {status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: Check your internet connection or if the server is available")
        except requests.exceptions.Timeout:
            raise Exception("Timeout: The server took too long to respond")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error: {e}")
        except json.JSONDecodeError:
            raise Exception("JSON decode error: The server response is not valid JSON")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    def get_llms_and_types(self, type: str = None):
        """
        Retrieve available language models and their types, optionally filtered by type.
        
        Args:
            type (str, optional): Filter models by specific type. Defaults to None.
        
        Returns:
            dict: JSON response containing language models and their types.
        
        Raises:
            Exception: For various error conditions including:
                - Authentication errors (401)
                - Access denied (403)
                - Endpoint not found (404)
                - Invalid type parameter (400)
                - Connection errors
                - Timeout errors
                - JSON decode errors
                - Other HTTP and request errors
        """
        try:
            params = {"type": type} if type else {}
            response = requests.get(
                self.__base_url + "/v1/llms_and_types", 
                headers={'Authorization': f"Bearer {self.__api_key}"},
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            status_code = http_err.response.status_code
            if status_code == 401:
                raise Exception(f"Authentication error: Invalid or expired API token. Code: {status_code}")
            elif status_code == 403:
                raise Exception(f"Access denied: Insufficient permissions. Code: {status_code}")
            elif status_code == 404:
                raise Exception(f"Endpoint not found. Code: {status_code}")
            elif status_code == 400 and type:
                raise Exception(f"Invalid 'type' parameter: '{type}'. Code: {status_code}")
            else:
                raise Exception(f"HTTP Error: {http_err}. Code: {status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: Check your internet connection or if the server is available")
        except requests.exceptions.Timeout:
            raise Exception("Timeout: The server took too long to respond")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error: {e}")
        except json.JSONDecodeError:
            raise Exception("JSON decode error: The server response is not valid JSON")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    def ask(self, instruction="", input=None, messages=None, function=None, system_msg="",
            max_new_tokens=1000, temperature=0.1, timeout=120, llm_name=None,
            try_next_on_failure=True, client_username=None, **kwargs) -> str | dict | bytes:
        """
        Send a request to the language model and get a response.
        
        Args:
            instruction (str, optional): The instruction or prompt for the model. Defaults to "".
            input (str, optional): Additional input data. Defaults to None.
            messages (list, optional): List of messages for chat-based interactions. Defaults to None.
            function (str, optional): Specific function to call. Defaults to None.
            system_msg (str, optional): System message to set context. Defaults to "".
            max_new_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
            temperature (float, optional): Sampling temperature for randomness. Defaults to 0.1.
            timeout (int, optional): Request timeout in seconds. Defaults to 120.
            llm_name (str, optional): Specific language model to use. Defaults to None.
            try_next_on_failure (bool, optional): Whether to try alternative models on failure. Defaults to True.
            client_username (str, optional): Username to identify the client making the request. Defaults to None.
            **kwargs: Additional parameters to be included in the request payload.
        
        Returns:
            str | dict | bytes: The model's response. Can be:
                - str: Text response
                - dict: JSON response
                - bytes: Binary data (e.g., images) wrapped in BytesIO
        
        Raises:
            Exception: If the API call fails with details about the error code and message.
        
        Note:
            If messages or input are provided, the instruction parameter is ignored.
        """
        data = {
            "function": function,
            "instruction": instruction,
            "input": input,
            "messages": messages,
            "system_msg": system_msg,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "timeout": timeout,
            "llm_name": llm_name,
            "try_next_on_failure": try_next_on_failure,
            **kwargs
        }

        if messages or input:
            data.pop('instruction')
            data.pop('system_msg')
        
        headers = {'Authorization': f"Bearer {self.__api_key}"}

        if client_username:
           headers.update({'Liev-Client-Username': client_username})

        self.__clear_last_call_stats()
        load = requests.get(self.__base_url+"/response", data=json.dumps(data), 
                           headers=headers)
        if load.status_code == 200:
            if "image" in load.headers['content-type']:
                self.__clear_last_call_stats()
                return(io.BytesIO(load.content))
            else:
                self.__set_last_call_stats(load.headers)
                return json.loads(load.text)
        else:
            raise Exception(f"Error calling liev: {load.status_code} - {load.text}")

    def ask_stream(self, instruction="", messages=None, function=None, system_msg="",
                   max_new_tokens=1000, temperature=0.1, timeout=120, llm_name=None,
                   try_next_on_failure=True, client_username=None, **kwargs):
        """
        Send a request to the language model and get a streaming response.
        
        This method yields response chunks as they become available, allowing for real-time
        processing of the model's output.
        
        Args:
            instruction (str, optional): The instruction or prompt for the model. Defaults to "".
            messages (list, optional): List of messages for chat-based interactions. Defaults to None.
            function (str, optional): Specific function to call. Defaults to None.
            system_msg (str, optional): System message to set context. Defaults to "".
            max_new_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
            temperature (float, optional): Sampling temperature for randomness. Defaults to 0.1.
            timeout (int, optional): Request timeout in seconds. Defaults to 120.
            llm_name (str, optional): Specific language model to use. Defaults to None.
            try_next_on_failure (bool, optional): Whether to try alternative models on failure. Defaults to True.
            client_username (str, optional): Username to identify the client making the request. Defaults to None.
            **kwargs: Additional parameters to be included in the request payload.
        
        Yields:
            str: Chunks of the response as they become available.
        
        Returns:
            str: Error message if the request fails, including status code and response text.
        
        Note:
            If messages are provided, the instruction parameter is ignored.
        """
        data = {
            "function": function,
            "instruction": instruction,
            "messages": messages,
            "system_msg": system_msg,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "timeout": timeout,
            "llm_name": llm_name,
            "try_next_on_failure": try_next_on_failure,
            **kwargs
        }
       
        if messages:
            data.pop('instruction')
            data.pop('system_msg')


        headers = {'Authorization': f"Bearer {self.__api_key}"}

        if client_username:
           headers.update({'Liev-Client-Username': client_username})
            
        
        try:
            load = requests.post(self.__base_url+"/stream", 
                               headers=headers, 
                               data=json.dumps(data), stream=True)
            for chunk in load.iter_content(chunk_size=1000):
                if chunk:
                    yield chunk.decode()
        except Exception as e:
            return "Error calling the SERVER. Error code: " + str(load.status_code) + str(load.text)
    
    def get_openai_client(self, client_username=None):
        """
        Get an OpenAI-compatible client for the Liev API.
        
        This method returns an OpenAI client instance configured to work with Liev's
        OpenAI-compatible endpoint, allowing you to use familiar OpenAI SDK patterns.
        
        Args:
            client_username (str, optional): Username to identify the client making the request. Defaults to None.
        
        Returns:
            OpenAI: An OpenAI client instance configured for the Liev API.
        """
        default_headers = {}

        if client_username:
            default_headers.update({'Liev-Client-Username': client_username })
        return OpenAI(api_key=self.__api_key, base_url=self.__base_url+'/api/v2alpha1/openai',default_headers=default_headers)
