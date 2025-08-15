"""Main module."""
from gradio_client import Client
import time
import re
import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Union, Optional, Any
# https://working-tuna-massive.ngrok-free.app
# https://upright-mantis-intensely.ngrok-free.app/
# https://working-tuna-massive.ngrok-free.app/

# Load environment variables from .env file
load_dotenv()

OS_URL = "https://fintor-cute-test-1.ngrok.app"
HF_FINTOR_GUI_ENDPOINT = "https://jtpozbeohnafofam.us-east-1.aws.endpoints.huggingface.cloud/v1/"
HF_TOKEN = os.environ.get("HF_TOKEN")

HITL_URL = "https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
SHARED_STATE_URL = "https://c16bgaz0i2.execute-api.us-west-1.amazonaws.com/prod"

HITL_TOKEN = os.environ.get("HITL_TOKEN")

class WindowsAgent:
    def __init__(self, variable_name="friend", os_url=OS_URL, cache_token=None):
        """
        Initializes the WindowsAgent with a configurable variable name.

        Args:
            variable_name (str): The name to be used by hello_old_friend.
                                 Defaults to "friend".
            os_url (str): The URL for OS operations.
                         Defaults to OS_URL.
            cache_token (str): The API token for element search operations.
                              Defaults to None.
        """
        self.config_variable_name = variable_name
        self.os_url = os_url
        self.cache_token = cache_token

    def hello_world(self):
        """Prints a hello world message."""
        print("Hello World from WindowsAgent!")

    def hello_old_friend(self):
        """Prints a greeting to the configured variable name."""
        print(f"Hello, my old {self.config_variable_name}!")

    def add(self, a, b):
        """Adds two numbers and returns the result."""
        return a + b

    def act(self, input_data):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                user_input=str(input_data),
                api_name="/process_input1"
            )
            print(result)
        except Exception as e:
            print(f"Error in act operation: {e}")
            return None

    def click_element(self, x: int, y: int):
        """Click at the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        try:
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError("Coordinates must be numbers")
                
            input_data = {
                "action": "CLICK",
                "coordinate": [int(x), int(y)],
                "value": "value",
                "model_selected": "claude"
            }
            
            client = Client(self.os_url)
            result = client.predict(
                user_input=str(input_data),
                api_name="/process_input1"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in click operation: {e}")
            return None

    def screenshot(self):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                api_name="/get_screenshot_url"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in act operation: {e}")
            return result
        

    def screenshot_cropped(self, arr_input):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                array_input=arr_input,
                api_name="/get_cropped_screenshot"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in act operation: {e}")
            return result

    # def pause(self, seconds: float):
    #     """Pauses execution for the specified number of seconds.
        
    #     Args:
    #         seconds (float): Number of seconds to pause
    #     """
    #     try:
    #         if not isinstance(seconds, (int, float)) or seconds < 0:
    #             raise ValueError("Seconds must be a non-negative number")
                
    #         time.sleep(seconds)
    #         return True
    #     except Exception as e:
    #         print(f"Error in pause operation: {e}")
    #         return False

    def click_cached_element(self, task_type: str, element_name: str):
        """Click on an element using cached coordinates from the API.
        
        This method fetches cached element coordinates from the API based on the 
        element name and task type, then performs a click action at those coordinates.
        Instead of requiring direct coordinates, it uses the element name and task_type
        to retrieve cached coordinate data from the element search API.
        
        Args:
            task_type (str): The task type ID (e.g., 'approveITP')
            element_name (str): The name of the element to click
            
        Returns:
            Result from the click operation or None if failed
            
        Raises:
            ValueError: If cache_token is not provided during WindowsAgent initialization
        """
        try:
            # Check if cache_token is defined
            if self.cache_token is None:
                raise ValueError("cache_token is required for click_cached_element operation but was not provided during WindowsAgent initialization")
            
            # API configuration
            api_url = "https://cega6bexzc.execute-api.us-west-1.amazonaws.com/prod/elements/search"
            
            # Prepare API request parameters
            params = {
                "name": element_name,
                "taskTypeID": task_type
            }
            
            headers = {
                "x-api-key": self.cache_token
            }
            
            # Make API call to get coordinates
            response = requests.get(api_url, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"API request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            api_data = response.json()
            
            # Extract coordinates from API response
            if 'x' in api_data and 'y' in api_data:
                x = int(api_data['x'])
                y = int(api_data['y'])
            else:
                print(f"Could not find x/y coordinates in API response: {api_data}")
                return None
            
            print(f"Retrieved coordinates for '{element_name}': ({x}, {y})")
            
            # Validate coordinates
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError("Retrieved coordinates must be numbers")
            
            # Prepare input data for the click action
            input_data = {
                "action": "CLICK",
                "coordinate": [x, y],
                "value": "value",
                "model_selected": "claude"
            }
            
            # Execute the click using the existing client
            client = Client(self.os_url)
            result = client.predict(
                user_input=str(input_data),
                api_name="/process_input1"
            )
            
            print(f"Click result: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except KeyError as e:
            print(f"Missing key in API response: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"Error in click_cached_element operation: {e}")
            return None

class VisionAgent:
    def __init__(self,screen_size=(1366, 768), model_selected="FINTOR_GUI", hf_fintor_gui_endpoint=HF_FINTOR_GUI_ENDPOINT, hf_token=HF_TOKEN):
        """
        Initializes the Vision class with a configurable variable name and OS URL.

        Args:
            variable_name (str): The name to use for configuration.
                                Defaults to "friend".
            os_url (str): The URL for OS operations.
                        Defaults to OS_URL.
        """
        self.hf_fintor_gui_endpoint = hf_fintor_gui_endpoint
        self.hf_token = hf_token
        self.model_selected = model_selected
        self.screen_size = screen_size
        
    def find_element(self, screenshot_url, element_name):
        try:
            if self.model_selected != "FINTOR_GUI":
                raise ValueError("We only support FINTOR_GUI for now!")
            
            print("Element name in find_element", element_name)
            
            print("Screenshot url in find_element", screenshot_url)
            client = OpenAI(
                base_url = self.hf_fintor_gui_endpoint,   
                api_key = self.hf_token
            )
            _NAV_SYSTEM_GROUNDING = """
            You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

            ## Output Format
            ```Action: ...```

            ## Action Space
            click(start_box='<|box_start|>(x1,y1)<|box_end|>')
            hotkey(key='')
            type(content='') #If you want to submit your input, use \"\" at the end of `content`.
            scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
            wait() #Sleep for 5s and take a screenshot to check for any changes.
            finished()
            call_user() # Submit the task and call the user when the task is unsolvable, or when you need the user's help.

            ## Note
            - Do not generate any other text.
            """

            chat_completion = client.chat.completions.create(
                model="tgi",
                messages=[
                {"role": "system", "content": _NAV_SYSTEM_GROUNDING},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": screenshot_url}},
                        {
                            "type": "text",
                            "text": element_name
                        }
                    ]
                }
            ],
                top_p=None,
                temperature=0,
                max_tokens=150,
                stream=True,
                seed=None,
                stop=None,
                frequency_penalty=None,
                presence_penalty=None
            )
            word_buffer = ""
            full_text = []

            for message in chat_completion:
                chunk = message.choices[0].delta.content
                if chunk:
                    word_buffer += chunk
                    words = word_buffer.split()
                    full_text.extend(words[:-1])
                    word_buffer = words[-1] if words else ""

            if word_buffer:
                full_text.append(word_buffer)

            final_text = " ".join(full_text)
            print("final_text", final_text)
            pattern = r"\(\d+,\d+\)"

            matches = re.findall(pattern, final_text)
            print("matches", matches)

            if matches:
                if len(matches) == 1:
                    extracted_coordinates = matches[0]
                elif len(matches) == 2:
                    # Parse the two coordinate pairs
                    coord1 = matches[0].strip('()')
                    coord2 = matches[1].strip('()')
                    x1, y1 = map(int, coord1.split(','))
                    x2, y2 = map(int, coord2.split(','))
                    
                    # Average the coordinates
                    avg_x = (x1 + x2) // 2
                    avg_y = (y1 + y2) // 2
                    extracted_coordinates = f"({avg_x},{avg_y})"
                else:
                    # If more than 2 matches, use the first one
                    extracted_coordinates = matches[0]
                

                extracted_coordinates = self.convert_coordinates(extracted_coordinates)
                if extracted_coordinates:
                    return extracted_coordinates
            else:
                return "NOT FOUND"
        except Exception as e:
            print(f"Error in ui_tars_coordinates: {e}")
            return None

    def convert_coordinates(self, coordinates_str):
        """
        Convert coordinates based on screen size ratio (screen_size/1000).
        
        Args:
            coordinates_str (str): String in format "(x,y)"
            
        Returns:
            str: Converted coordinates in same format
        """
        try:
            # Strip parentheses and split by comma
            coords = coordinates_str.strip('()')
            x, y = map(int, coords.split(','))
            
            # Convert coordinates based on screen ratio
            x_ratio = self.screen_size[0] / 1000
            y_ratio = self.screen_size[1] / 1000
            
            new_x = int(x * x_ratio)
            new_y = int(y * y_ratio)
            
            return f"({new_x},{new_y})"
        except Exception as e:
            print(f"Error converting coordinates: {e}")
            return coordinates_str

class HumanAgent:
    def __init__(self, HITL_token=HITL_TOKEN, HITL_url=HITL_URL):
        """
        Initializes the HumanAgent with token and URL.

        Args:
            HITL_token (str): Authentication token
            HITL_url (str): API endpoint URL
        """
        self.HITL_token = HITL_token
        self.HITL_url = HITL_url

    def task(self,  image_urls, thread_id="1234567890", questions=None, task_type="NotSpecified", thread_state=None):
        """
        Creates a human task with images, instructions, and questions.

        Args:
            image_urls (list): List of image URLs to display
            instruction_markdown (str, optional): Markdown formatted instructions
            instruction_url (str, optional): URL to instructions
            questions (list, optional): List of question dictionaries with format:
                {
                    "Question": "Is this green?",
                    "Choices": ["Yes", "No", "Maybe"],  # Optional
                    "TypeIn": True  # Optional, defaults to True
                }

        Returns:
            Response from the human task API
        """
        try:
            if not image_urls:
                raise ValueError("At least one image URL is required")

            # Default empty list if questions parameter is None
            if questions is None:
                questions = []


            # Prepare task data
            task_data = {
                "type": "task",
                "image_urls": image_urls,
                "questions": questions,
                "thread_id": thread_id,
                "task_type": task_type,
                "thread_state": thread_state,
            }

            # Set up headers for the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.HITL_token}"
            }

            # Make the API call
            response = requests.post(
                self.HITL_url,
                headers=headers,
                data=json.dumps(task_data)
            )

            # Check if the request was successful
            response.raise_for_status()
            
            # Return the response from the API
            print(f"Task sent to {self.HITL_url} successfully")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except Exception as e:
            print(f"Error creating human task: {e}")
            return None

    def reporting(self, thread_id="1234567890", report_type="NotSpecified", thread_state=None):
            """
            Creates a human task with images, instructions, and questions.

            Args:
                thread_id (str): ID for the thread. Defaults to "1234567890"
                thread_state (dict, optional): Dictionary containing thread state information

            Returns:
                Response from the reporting API containing thread status and any updates
            """
            try:
                task_data = {
                    "type": "reporting",
                    "thread_id": thread_id,
                    "thread_state": thread_state,
                    "report_type": report_type
                }

                # Set up headers for the API request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.HITL_token}"
                }

                # Make the API call
                response = requests.post(
                    self.HITL_url,
                    headers=headers,
                    data=json.dumps(task_data)
                )

                # Check if the request was successful
                response.raise_for_status()
                
                # Return the response from the API
                print(f"Reporting sent to {self.HITL_url} successfully")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"API request error: {e}")
                return None
            except Exception as e:
                print(f"Error creating human reporting: {e}")
                return None

class StationAgent:
    """
    A class for managing shared state and server coordination between LangGraph workflows.
    
    This class integrates with a SharedState API to coordinate state and server management
    across different workflow instances in LangGraph.
    
    Server Status Constraint:
        The "server" variable can only have two values: "busy" or "idle"
        - "idle": Server is available for new tasks
        - "busy": Server is currently processing a task
        
    Reserved Variables:
        - "server": Server status (managed by server.load/unload methods only)
        - "serverThread": Current task type (managed by server.load/unload methods only)
    """
    
    # Reserved variable names that cannot be set by users
    RESERVED_VARIABLES = {"server", "serverThread", "serverCheckpoint", "serverTaskType"}
    
    # Valid server status values
    VALID_SERVER_STATUS = {"busy", "idle"}
    
    def __init__(self, station_thread_id: str, graph_thread_id: str, token: str, initial_state: Optional[Dict[str, Any]] = None, langgraph_token: Optional[str] = None, current_graph_url: Optional[str] = None, current_graph_assistant_id: Optional[str] = None):
        """
        Initialize the StationAgent with thread IDs and authentication tokens.
        
        Args:
            station_thread_id (str): Identifier for the station/workflow instance
            graph_thread_id (str): LangGraph thread identifier
            token (str): Authentication token for SharedState API access
            initial_state (dict, optional): Initial state object to push to SharedState API. Defaults to None.
            langgraph_token (str, optional): Authentication token for LangGraph API access. Required for pause/unpause functionality.
            current_graph_url (str, optional): Current graph URL for pause/unpause functionality
            current_graph_assistant_id (str, optional): Current graph assistant ID for pause/unpause functionality
        """
        self.station_thread_id = station_thread_id
        self.graph_thread_id = graph_thread_id
        self.token = token
        self.langgraph_token = langgraph_token
        self.current_graph_url = current_graph_url
        self.current_graph_assistant_id = current_graph_assistant_id
        self.base_url = SHARED_STATE_URL
        
        # Set up HTTP session with authentication
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        })
        
        # Initialize nested classes
        self.state = self.State(self)
        self.server = self.Server(self)
        
        # Handle initial state and server variable initialization
        if initial_state is not None:
            # Ensure initial_state includes server variables
            self.initial_state = initial_state.copy()
            num_servers = 4  # Default number of servers
            if "server" not in self.initial_state:
                self.initial_state["server"] = ["idle"] * num_servers
            if "serverThread" not in self.initial_state:
                self.initial_state["serverThread"] = ["idle"] * num_servers
            if "serverCheckpoint" not in self.initial_state:
                self.initial_state["serverCheckpoint"] = ["setup"] * num_servers
            if "serverTaskType" not in self.initial_state:
                self.initial_state["serverTaskType"] = ["taskPlaceholder"] * num_servers
                
            # Use direct API call during initialization to bypass reserved variable protection
            data = {
                "stationThread": self.station_thread_id,
                "variables": self.initial_state
            }
            
            response = self._make_request("POST", "/shared-state/bulk-upsert", data=data)
            push_result = response is not None and response.get("success", False)
            
            if push_result:
                print(f"🚀 StationAgent initialized and pushed {len(self.initial_state)} variables to SharedState API")
            else:
                print(f"⚠️ StationAgent initialized but failed to push {len(self.initial_state)} variables to SharedState API")
        else:
            # No initial state provided - check if server variables exist, if not initialize them
            self.initial_state = None
            print("🆕 StationAgent initialized with no initial state to push")
            
            # Check if server variables exist as arrays, if not initialize them
            server_vars = self.state.get("server")
            if server_vars is None or not isinstance(server_vars, list):
                print("⚠️ Server variables not found or not arrays, initializing...")
                num_servers = 4  # Default number of servers
                server_initialization = {
                    "server": ["idle"] * num_servers,
                    "serverThread": ["idle"] * num_servers,
                    "serverCheckpoint": ["setup"] * num_servers,
                    "serverTaskType": ["taskPlaceholder"] * num_servers
                }
                
                # Use direct API call to initialize server variables
                data = {
                    "stationThread": self.station_thread_id,
                    "variables": server_initialization
                }
                
                response = self._make_request("POST", "/shared-state/bulk-upsert", data=data)
                if response and response.get("success", False):
                    print("✅ Server variables initialized successfully")
                else:
                    print("❌ Failed to initialize server variables")
            else:
                print("✅ Server variables already exist as arrays")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, max_retries: int = 3) -> Optional[Dict]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            dict: Response JSON or None on failure
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 401:
                    raise ValueError("Authentication failed: Invalid token")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    print(f"Request timeout, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Request timeout after maximum retries")
                    return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1
                    print(f"Request error: {e}, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Request failed after maximum retries: {e}")
                    return None
                    
            except json.JSONDecodeError:
                print("Invalid JSON response received")
                return None
                
        return None
    
    def validate_server_status(self, status: str) -> bool:
        """
        Validate that a server status value is allowed.
        
        Args:
            status (str): Server status to validate
            
        Returns:
            bool: True if status is "busy" or "idle", False otherwise
        """
        return status in self.VALID_SERVER_STATUS
    
    def validate_connection(self) -> Dict:
        """
        Validate the connection to the SharedState API.
        
        Returns:
            dict: Connection status and information
        """
        try:
            # Try to list variables to test connection
            response = self._make_request("GET", f"/shared-state/list?stationThread={self.station_thread_id}")
            
            if response is not None:
                return {
                    "connected": True,
                    "api_url": self.base_url,
                    "station_thread": self.station_thread_id,
                    "variable_count": len(response.get("attributes", {}))
                }
            else:
                return {
                    "connected": False,
                    "error": "Failed to connect to API",
                    "api_url": self.base_url
                }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "api_url": self.base_url
            }
    
    class State:
        """Nested class for state management operations."""
        
        def __init__(self, agent: 'StationAgent'):
            self.agent = agent
        
        def get(self, variable_name: str) -> Union[Dict, str, None]:
            """
            Get single variable from SharedState API.
            
            Args:
                variable_name (str): Name of the variable to retrieve
                
            Returns:
                Union[Dict, str, None]: The attributeValue from response or None if not found
            """
            params = {
                "stationThread": self.agent.station_thread_id,
                "attributeName": variable_name
            }
            
            response = self.agent._make_request("GET", "/shared-state", params=params)
            
            if response and response.get("success"):
                return response.get("data", {}).get("attributeValue")
            
            return None
        
        def set(self, variable_name: str, variable_value: Any) -> bool:
            """
            Create/update single variable using PUT endpoint.
            
            Args:
                variable_name (str): Name of the variable to set
                variable_value (Any): Value to assign to the variable
                
            Returns:
                bool: True on success, False on failure
                
            Raises:
                ValueError: If variable_name is a reserved variable
            """
            if variable_name in self.agent.RESERVED_VARIABLES:
                raise ValueError(f"Cannot set reserved variable '{variable_name}'. Reserved variables: {self.agent.RESERVED_VARIABLES}")
            
            return self._set_internal(variable_name, variable_value)
        
        def _set_internal(self, variable_name: str, variable_value: Any) -> bool:
            """
            Internal method to set variables without reserved variable protection.
            Used by server management methods to update server variables.
            
            Args:
                variable_name (str): Name of the variable to set
                variable_value (Any): Value to assign to the variable
                
            Returns:
                bool: True on success, False on failure
            """
            data = {
                "stationThread": self.agent.station_thread_id,
                "attributeName": variable_name,
                "attributeValue": variable_value
            }
            
            response = self.agent._make_request("PUT", "/shared-state", data=data)
            
            return response is not None and response.get("success", False)
        
        def pull(self) -> Dict:
            """
            Get ALL variables from SharedState API using list endpoint.
            
            Returns:
                dict: The attributes dict from response
            """
            params = {
                "stationThread": self.agent.station_thread_id
            }
            
            response = self.agent._make_request("GET", "/shared-state/list", params=params)
            
            if response and response.get("success"):
                return response.get("attributes", {})
            
            return {}
        
        def push(self, json_object: Dict) -> bool:
            """
            Bulk create/update variables using bulk-upsert endpoint.
            
            Args:
                json_object (Dict): Dictionary of variables to create/update
                
            Returns:
                bool: True on success, False on failure
                
            Raises:
                ValueError: If any variable name is reserved
            """
            # Check for reserved variables in the input
            reserved_found = set(json_object.keys()) & self.agent.RESERVED_VARIABLES
            if reserved_found:
                raise ValueError(f"Cannot set reserved variables: {reserved_found}. Reserved variables: {self.agent.RESERVED_VARIABLES}")
            
            # Don't automatically add server variables - they should be explicitly managed
            variables = json_object.copy()
                
            data = {
                "stationThread": self.agent.station_thread_id,
                "variables": variables
            }
            
            response = self.agent._make_request("POST", "/shared-state/bulk-upsert", data=data)
            
            return response is not None and response.get("success", False)
        
        def sync(self, variable_name: str, langgraph_state: Any = None) -> Any:
            """
            Sync variable from SharedState API to LangGraph state.
            
            If langgraph_state is provided, this method will:
            1. Get the variable from SharedState API
            2. Create state.sharedState if it doesn't exist
            3. Set state.sharedState[variable_name] = retrieved_value
            4. Return the updated state object
            
            Args:
                variable_name (str): Name of the variable to sync
                langgraph_state (Any, optional): LangGraph state object to update
                
            Returns:
                Any: If langgraph_state provided, returns the updated state object.
                     If no langgraph_state provided, returns just the variable value.
            """
            # Get the variable from SharedState API
            variable_value = self.get(variable_name)
            
            # If LangGraph state is provided, update it and return the state
            if langgraph_state is not None:
                # Check if sharedState exists, if not create it
                if not hasattr(langgraph_state, 'sharedState'):
                    langgraph_state.sharedState = {}
                elif langgraph_state.sharedState is None:
                    langgraph_state.sharedState = {}
                
                # Set the variable in sharedState
                langgraph_state.sharedState[variable_name] = variable_value
                
                print(f"✅ Synced '{variable_name}' to LangGraph state.sharedState['{variable_name}'] = {variable_value}")
                
                # Return the updated state object
                return langgraph_state
            
            # Backward compatibility: return just the variable value if no state provided
            return variable_value
        
        def sync_all(self, langgraph_state: Any) -> Any:
            """
            Sync ALL variables from SharedState API to LangGraph state.
            
            This method will:
            1. Pull all variables from SharedState API
            2. Create state.sharedState if it doesn't exist
            3. Replace state.sharedState with all variables from API
            4. Return the updated state object
            
            Args:
                langgraph_state (Any): LangGraph state object to update
                
            Returns:
                Any: The updated LangGraph state object
            """
            # Get all variables from SharedState API
            all_variables = self.pull()
            
            # Update LangGraph state
            if not hasattr(langgraph_state, 'sharedState'):
                langgraph_state.sharedState = {}
            
            # Replace sharedState with all variables from API
            langgraph_state.sharedState = all_variables.copy()
            
            print(f"✅ Synced ALL variables to LangGraph state.sharedState: {len(all_variables)} variables")
            return langgraph_state
        
        def sync_multiple(self, variable_names: list, langgraph_state: Any = None) -> Any:
            """
            Sync multiple variables from SharedState API to LangGraph state.
            
            Args:
                variable_names (list): List of variable names to sync
                langgraph_state (Any, optional): LangGraph state object to update
                
            Returns:
                Any: If langgraph_state provided, returns the updated state object.
                     If no langgraph_state provided, returns dict with variable_name -> value mappings.
            """
            results = {}
            
            # Create sharedState if needed
            if langgraph_state is not None:
                if not hasattr(langgraph_state, 'sharedState'):
                    langgraph_state.sharedState = {}
                elif langgraph_state.sharedState is None:
                    langgraph_state.sharedState = {}
            
            # Sync each variable
            for variable_name in variable_names:
                variable_value = self.get(variable_name)
                results[variable_name] = variable_value
                
                # Update LangGraph state if provided
                if langgraph_state is not None:
                    langgraph_state.sharedState[variable_name] = variable_value
            
            if langgraph_state is not None:
                print(f"✅ Synced {len(variable_names)} variables to LangGraph state.sharedState")
                # Return the updated state object
                return langgraph_state
            
            # Backward compatibility: return just the results dict if no state provided
            return results
        
        def delete(self, variable_name: str) -> bool:
            """
            Delete a variable from SharedState API.
            
            Args:
                variable_name (str): Name of the variable to delete
                
            Returns:
                bool: True on success, False on failure
                
            Raises:
                ValueError: If variable_name is a reserved variable
            """
            if variable_name in self.agent.RESERVED_VARIABLES:
                raise ValueError(f"Cannot delete reserved variable '{variable_name}'. Reserved variables: {self.agent.RESERVED_VARIABLES}")
            
            params = {
                "stationThread": self.agent.station_thread_id,
                "attributeName": variable_name
            }
            
            response = self.agent._make_request("DELETE", "/shared-state", params=params)
            
            return response is not None and response.get("success", False)
        
        def exists(self, variable_name: str) -> bool:
            """
            Check if a variable exists in SharedState API.
            
            Args:
                variable_name (str): Name of the variable to check
                
            Returns:
                bool: True if variable exists, False otherwise
            """
            return self.get(variable_name) is not None
        
        def list_variables(self) -> list:
            """
            Get list of all variable names for the station thread.
            
            Returns:
                list: List of variable names
            """
            all_vars = self.pull()
            return list(all_vars.keys())
    
    class Server:
        """
        Nested class for server management operations.
        
        Note: Server management methods use direct API calls to manage reserved variables
        (server, serverThread, serverCheckpoint, serverTaskType) which are arrays to manage multiple servers.
        Server status can only be "busy" or "idle".
        """
        
        def __init__(self, agent: 'StationAgent'):
            self.agent = agent
        
        def load(self, serverThreadId: str, serverCheckpoint: str = "setup", serverIndex: int = 0, serverTaskType: str = "taskPlaceholder") -> Dict:
            """
            Load server for a specific task type.

            Args:
                serverThreadId (str): The thread ID to assign to the server.
                serverCheckpoint (str, optional): The checkpoint to check against. Defaults to "setup".
                serverIndex (int, optional): The index of the server to load. Defaults to 0.
                serverTaskType (str, optional): The task type to assign. Defaults to "taskPlaceholder".

            Returns:
                dict: Status information about the load operation
            """
            # Get current server states
            servers = self.agent.state.get("server")
            checkpoints = self.agent.state.get("serverCheckpoint")

            if servers is None or checkpoints is None or not isinstance(servers, list) or not isinstance(checkpoints, list):
                 return {"status": "error", "error": "Server state variables are not initialized as arrays."}

            if not (0 <= serverIndex < len(servers)):
                return {"status": "error", "error": f"serverIndex {serverIndex} is out of bounds."}

            if servers[serverIndex] == "busy":
                return {"status": "busy", "error": "Server is busy"}

            if checkpoints[serverIndex] != serverCheckpoint:
                return {"status": "wrongCheckpoint", "error": f"Incorrect checkpoint. Expected {checkpoints[serverIndex]}, got {serverCheckpoint}"}

            # Update server state arrays
            servers[serverIndex] = "busy"
            
            threads = self.agent.state.get("serverThread") or ["idle"] * len(servers)
            task_types = self.agent.state.get("serverTaskType") or ["taskPlaceholder"] * len(servers)

            threads[serverIndex] = serverThreadId
            task_types[serverIndex] = serverTaskType
            
            # Persist changes using internal method to bypass reserved variable protection
            self.agent.state._set_internal("server", servers)
            self.agent.state._set_internal("serverCheckpoint", checkpoints)
            self.agent.state._set_internal("serverThread", threads)
            self.agent.state._set_internal("serverTaskType", task_types)

            return {"status": "loaded", "serverThread": serverThreadId}

        def unload(self, checkpoint: str = "setup", index: int = 0) -> Dict:
            """
            Unload the server and set it to idle.

            Args:
                checkpoint (str): The checkpoint to set after unloading.
                index (int, optional): The index of the server to unload. Defaults to 0.

            Returns:
                dict: Status information about the unload operation
            """
            servers = self.agent.state.get("server")
            if servers is None or not isinstance(servers, list):
                 return {"status": "error", "error": "Server state is not initialized correctly."}

            if not (0 <= index < len(servers)):
                return {"status": "error", "error": f"serverIndex {index} is out of bounds."}

            if servers[index] == "idle":
                return {"status": "idle", "error": "Server is already idle"}

            servers[index] = "idle"
            checkpoints = self.agent.state.get("serverCheckpoint") or ["setup"] * len(servers)
            checkpoints[index] = checkpoint

            self.agent.state._set_internal("server", servers)
            self.agent.state._set_internal("serverCheckpoint", checkpoints)

            return {"status": "unloaded"}

        def avail(self, index: int = 0) -> Dict:
            """
            Get current server availability status for a specific server.

            Args:
                index (int, optional): The index of the server to check. Defaults to 0.

            Returns:
                dict: Current server and serverThread values for the specified index.
                      Server status will be "busy" or "idle" only
            """
            servers = self.agent.state.get("server")
            threads = self.agent.state.get("serverThread")
            checkpoints = self.agent.state.get("serverCheckpoint")
            task_types = self.agent.state.get("serverTaskType")

            if any(v is None or not isinstance(v, list) for v in [servers, threads, checkpoints, task_types]):
                return {"status": "error", "error": "Server state is not initialized correctly as arrays."}

            if not (0 <= index < len(servers)):
                return {"status": "error", "error": f"serverIndex {index} is out of bounds."}

            server_status = servers[index]
            if server_status not in self.agent.VALID_SERVER_STATUS:
                return {
                    "server": "idle",  # Default to safe state
                    "serverThread": threads[index],
                    "serverCheckpoint": checkpoints[index],
                    "serverTaskType": task_types[index],
                    "warning": f"Invalid server status '{server_status}' detected, defaulting to 'idle'"
                }

            return {
                "server": server_status,
                "serverThread": threads[index],
                "serverCheckpoint": checkpoints[index],
                "serverTaskType": task_types[index]
            }
    


    def pause(self, pause_tag: str) -> Dict:
        """
        Pause an already initiated StationAgent by interrupting the graph with a pause tag.
        
        This method uses LangGraph's built-in interrupt() function and is designed to be 
        called from within a LangGraph node execution.
        
        Args:
            pause_tag (str): The pause tag identifier
            
        Returns:
            Dict: Status information about the pause operation
        """
        print(f"Attempting to pause with tag: '{pause_tag}'")
        
        # Step 1: Check if pause_tag-waitpoint exists and is "paused"
        waitpoint_var = f"{pause_tag}-waitpoint"
        waitpoint_status = self.state.get(waitpoint_var)
        
        if waitpoint_status == "paused":
            return {"success": False, "status": "tagInUse", "error": f"Pause tag '{pause_tag}' is already in use"}
        
        # Step 2: Store waitpoint variables for unpause functionality
        graph_url = self.current_graph_url or self.state.get("current-graph-url")
        graph_assistant_id = self.current_graph_assistant_id or self.state.get("current-graph-assistant-id")
        
        waitpoint_url_var = f"{pause_tag}-waitpoint-url"
        waitpoint_assistant_var = f"{pause_tag}-waitpoint-assistant"
        waitpoint_thread_var = f"{pause_tag}-waitpoint-threadId"
        waitpoint_apikey_var = f"{pause_tag}-waitpoint-apikey"
        
        try:
            # Store pause information in shared state for unpause functionality
            self.state.set(waitpoint_url_var, graph_url)
            self.state.set(waitpoint_assistant_var, graph_assistant_id)
            self.state.set(waitpoint_thread_var, self.graph_thread_id)
            self.state.set(waitpoint_apikey_var, self.langgraph_token)
            
            # Step 3: Use LangGraph's built-in interrupt function
            try:
                import inspect
                
                # Find the interrupt function in the caller's context
                frame = inspect.currentframe().f_back
                interrupt_func = None
                
                # Check caller's globals for interrupt function
                if frame and 'interrupt' in frame.f_globals and callable(frame.f_globals['interrupt']):
                    interrupt_func = frame.f_globals['interrupt']
                
                if not interrupt_func:
                    # Fallback: check current frame's globals
                    frame = inspect.currentframe()
                    while frame:
                        if 'interrupt' in frame.f_globals and callable(frame.f_globals['interrupt']):
                            interrupt_func = frame.f_globals['interrupt']
                            break
                        frame = frame.f_back
                
                if not interrupt_func:
                    return {"success": False, "error": "interrupt function not found - ensure this is called from within a LangGraph node"}
                
                # Prepare interrupt info
                interrupt_info = {
                    "pause_tag": pause_tag,
                    "question_text": f"Graph paused with tag: {pause_tag}",
                    "expected_format": "Resume command or nextstep: Proceed"
                }
                
                # Use built-in interrupt (NO AWAIT!)
                human_response = interrupt_func(interrupt_info)
                
                # Step 4: Mark as paused in shared state
                self.state.set(waitpoint_var, "paused")
                
                print(f"Successfully paused graph with tag: {pause_tag}")
                return {
                    "success": True,
                    "status": "paused",
                    "pause_tag": pause_tag,
                    "thread_id": self.graph_thread_id,
                    "response": human_response,
                    "message": f"Graph successfully paused with tag '{pause_tag}'"
                }
                
            except Exception as e:
                # Clean up waitpoint variables if interrupt failed
                self.state.delete(waitpoint_url_var)
                self.state.delete(waitpoint_assistant_var)
                self.state.delete(waitpoint_thread_var)
                self.state.delete(waitpoint_apikey_var)
                
                error_message = f"Error with LangGraph interrupt: {str(e)}"
                print(f"ERROR: {error_message}")
                return {"success": False, "error": error_message}
                
        except Exception as e:
            error_message = f"Error setting waitpoint variables: {str(e)}"
            print(f"ERROR: {error_message}")
            return {"success": False, "error": error_message}

    def unpause(self, pause_tag: str, resume_payload: str = "nextstep: Proceed") -> Dict:
        """
        Unpause a previously paused StationAgent by calling the LangGraph Thread Unpause API.
        
        Args:
            pause_tag (str): The pause tag identifier
            resume_payload (str, optional): Payload to send to resume thread. Defaults to "nextstep: Proceed"
            
        Returns:
            Dict: Status information about the unpause operation
        """
        print(f"Attempting to unpause with tag: '{pause_tag}'")
        
        # Step 1: Check if pause_tag-waitpoint exists and is "paused"
        waitpoint_var = f"{pause_tag}-waitpoint"
        waitpoint_status = self.state.get(waitpoint_var)
        
        if waitpoint_status != "paused":
            return {"success": False, "status": "tagNotPaused", "error": f"Pause tag '{pause_tag}' is not in paused state"}
        
        # Step 2: Get waitpoint variables
        waitpoint_url_var = f"{pause_tag}-waitpoint-url"
        waitpoint_assistant_var = f"{pause_tag}-waitpoint-assistant"
        waitpoint_thread_var = f"{pause_tag}-waitpoint-threadId"
        waitpoint_apikey_var = f"{pause_tag}-waitpoint-apikey"
        
        graph_url = self.state.get(waitpoint_url_var)
        graph_assistant_id = self.state.get(waitpoint_assistant_var)
        thread_id = self.state.get(waitpoint_thread_var)
        api_key = self.state.get(waitpoint_apikey_var)
        
        if not all([graph_url, graph_assistant_id, thread_id, api_key]):
            missing = []
            if not graph_url: missing.append("url")
            if not graph_assistant_id: missing.append("assistant_id")
            if not thread_id: missing.append("thread_id")
            if not api_key: missing.append("api_key")
            
            return {"success": False, "error": f"Missing waitpoint variables: {', '.join(missing)}"}
        
        # Step 3: Call the LangGraph Thread Unpause API
        try:
            # Prepare API request payload
            unpause_payload = {
                "thread_id": thread_id,
                "assistant_id": graph_assistant_id,
                "langgraph_url": graph_url,
                "api_key": api_key,
                "resume_payload": resume_payload
            }
            
            # Make API call to unpause endpoint
            unpause_url = f"{self.base_url}/shared-state/unpause"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.post(unpause_url, headers=headers, json=unpause_payload, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False, 
                    "error": f"Unpause API request failed with status {response.status_code}: {response.text}"
                }
            
            api_result = response.json()
            
            if not api_result.get("success", False):
                return {
                    "success": False,
                    "error": f"Unpause API returned error: {api_result.get('error', 'Unknown error')}"
                }
            
            # Step 4: If successful, mark as unpaused and clean up waitpoint variables
            self.state.set(waitpoint_var, "unPaused")
            
            # Optional: Clean up waitpoint variables after successful unpause
            try:
                self.state.delete(waitpoint_url_var)
                self.state.delete(waitpoint_assistant_var)
                self.state.delete(waitpoint_thread_var)
                self.state.delete(waitpoint_apikey_var)
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up waitpoint variables: {cleanup_error}")
            
            print(f"Successfully unpaused graph with tag: {pause_tag}")
            return {
                "success": True,
                "status": "unPaused",
                "pause_tag": pause_tag,
                "thread_id": thread_id,
                "assistant_id": graph_assistant_id,
                "message": f"Graph successfully unpaused from tag '{pause_tag}' using API",
                "response_preview": api_result.get("response_preview", ""),
                "unpause_method": "shared_state_api"
            }
            
        except requests.exceptions.RequestException as e:
            error_message = f"Network error calling unpause API: {str(e)}"
            print(f"ERROR: {error_message}")
            return {"success": False, "error": error_message}
        
        except json.JSONDecodeError as e:
            error_message = f"Invalid JSON response from unpause API: {str(e)}"
            print(f"ERROR: {error_message}")
            return {"success": False, "error": error_message}
        
        except Exception as e:
            error_message = f"Unexpected error during unpause operation: {str(e)}"
            print(f"ERROR: {error_message}")
            return {"success": False, "error": error_message}

