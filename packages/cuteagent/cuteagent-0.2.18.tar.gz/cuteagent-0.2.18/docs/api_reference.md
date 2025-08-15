# CuteAgent API Reference

## Overview

CuteAgent provides three main agent classes for comprehensive automation:

- **StationAgent**: Shared state management and server coordination for LangGraph workflows
- **WindowsAgent**: Computer automation and GUI interaction 
- **HumanAgent**: Human-in-the-loop task management

---

# WindowsAgent API Reference

## Overview

WindowsAgent provides computer automation capabilities including screen capture, element clicking, and GUI interaction. It supports both direct coordinate-based actions and cached element-based actions for improved reliability.

## Constructor

### `WindowsAgent(variable_name="friend", os_url=OS_URL, cache_token=None)`

Initialize a new WindowsAgent instance.

**Parameters:**
- `variable_name` (str, optional): Name used by hello_old_friend method. Defaults to "friend"
- `os_url` (str, optional): URL for OS operations. Defaults to OS_URL 
- `cache_token` (str, optional): API token for cached element search operations. Required for click_cached_element

**Example:**
```python
# Basic initialization
agent = WindowsAgent()

# With cache token for element-based clicking
agent = WindowsAgent(cache_token="your-api-key-here")

# With custom OS URL
agent = WindowsAgent(os_url="https://custom-server.ngrok.app")
```

---

## Screen Interaction Methods

### `agent.click_element(x, y)`

Click at specific screen coordinates.

**Parameters:**
- `x` (int): X coordinate on screen
- `y` (int): Y coordinate on screen

**Returns:**
- Result from click operation or None if failed

**Raises:**
- `ValueError`: If coordinates are not numbers

**Example:**
```python
# Click at specific coordinates
result = agent.click_element(100, 200)
if result:
    print("Click successful")
```

### `agent.click_cached_element(task_type, element_name)`

Click on an element using cached coordinates from the API.

This method fetches cached element coordinates from the API based on the element name and task type, then performs a click action at those coordinates. Instead of requiring direct coordinates, it uses the element name and task_type to retrieve cached coordinate data from the element search API.

**Parameters:**
- `task_type` (str): The task type ID (e.g., 'approveITP')
- `element_name` (str): The name of the element to click

**Returns:**
- Result from the click operation or None if failed

**Raises:**
- `ValueError`: If cache_token is not provided during WindowsAgent initialization
- `requests.exceptions.RequestException`: If API request fails
- `KeyError`: If required coordinates are missing from API response

**Example:**
```python
# Initialize with cache token (required)
agent = WindowsAgent(cache_token="your-api-key-here")

# Click on cached element
result = agent.click_cached_element("approveITP", "submit_button")
if result:
    print("Successfully clicked submit button")
else:
    print("Failed to click element")

# Error handling
try:
    agent.click_cached_element("workflowTask", "save_document")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### `agent.pause(seconds)`

Pause execution for the specified duration.

**Parameters:**
- `seconds` (float): Number of seconds to pause

**Returns:**
- `True` on success, `False` on failure

**Raises:**
- `ValueError`: If seconds is negative

**Example:**
```python
# Pause for 2 seconds
agent.pause(2.0)

# Pause for half a second
agent.pause(0.5)
```

---

## Screen Capture Methods

### `agent.screenshot()`

Take a full screenshot of the current screen.

**Returns:**
- Screenshot URL or error information

**Example:**
```python
screenshot_url = agent.screenshot()
print(f"Screenshot saved: {screenshot_url}")
```

### `agent.screenshot_cropped(arr_input)`

Take a cropped screenshot of a specific screen area.

**Parameters:**
- `arr_input` (list): Crop coordinates [x, y, width, height]

**Returns:**
- Cropped screenshot URL or error information

**Example:**
```python
# Crop area from (10, 50) with 800x600 size
cropped = agent.screenshot_cropped([10, 50, 800, 600])
print(f"Cropped screenshot: {cropped}")
```

---

## General Methods

### `agent.act(input_data)`

Send raw action data to the OS interface.

**Parameters:**
- `input_data`: Action data to send

**Returns:**
- Result from the action or None if failed

**Example:**
```python
action_data = {
    "action": "TYPE",
    "value": "Hello World",
    "model_selected": "claude"
}
result = agent.act(action_data)
```

### `agent.hello_world()`

Print a hello world message.

**Example:**
```python
agent.hello_world()  # Prints: "Hello World from WindowsAgent!"
```

### `agent.hello_old_friend()`

Print a greeting using the configured variable name.

**Example:**
```python
agent = WindowsAgent(variable_name="colleague")
agent.hello_old_friend()  # Prints: "Hello, my old colleague!"
```

### `agent.add(a, b)`

Add two numbers (utility method).

**Parameters:**
- `a` (number): First number
- `b` (number): Second number

**Returns:**
- Sum of a and b

**Example:**
```python
result = agent.add(5, 3)  # Returns 8
```

---

## Usage Patterns

### Basic Screen Automation

```python
# Initialize agent
agent = WindowsAgent()

# Take screenshot to see current state
screenshot = agent.screenshot()
print(f"Current screen: {screenshot}")

# Click on specific coordinates
agent.click_element(100, 200)
agent.pause(1)

# Take another screenshot to verify
final_screenshot = agent.screenshot()
```

### Element-Based Automation (Recommended)

```python
# Initialize with cache token
agent = WindowsAgent(cache_token="your-api-key-here")

try:
    # Click on named elements instead of coordinates
    agent.click_cached_element("loginForm", "username_field")
    agent.pause(0.5)
    
    agent.click_cached_element("loginForm", "password_field") 
    agent.pause(0.5)
    
    agent.click_cached_element("loginForm", "login_button")
    agent.pause(2)
    
    # Verify result
    screenshot = agent.screenshot()
    print(f"Login completed: {screenshot}")
    
except ValueError as e:
    print(f"Element clicking failed: {e}")
```

### Error Handling

```python
agent = WindowsAgent(cache_token="your-token")

def safe_click_element(task_type, element_name, max_retries=3):
    """Safely click element with retries."""
    for attempt in range(max_retries):
        try:
            result = agent.click_cached_element(task_type, element_name)
            if result:
                return True
            print(f"Attempt {attempt + 1} failed, retrying...")
            agent.pause(1)
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            agent.pause(2)
    return False

# Usage
if safe_click_element("myTask", "submit_button"):
    print("Element clicked successfully")
else:
    print("Failed to click element after all retries")
```

## Error Handling

### Common Exceptions

#### `ValueError`
- Raised when cache_token is required but not provided
- Raised when coordinates are invalid
- Raised when pause duration is negative

#### `requests.exceptions.RequestException`
- Network connectivity issues with element search API
- API server errors
- Authentication failures

#### `KeyError`
- Missing required fields in API response
- Invalid coordinate data from API

### API Configuration

The element search API uses:
- **URL**: `https://cega6bexzc.execute-api.us-west-1.amazonaws.com/prod/elements/search`
- **Authentication**: x-api-key header with cache_token
- **Parameters**: 
  - `name`: Element name to search for
  - `taskTypeID`: Task type identifier

---

# StationAgent API Reference

## Overview

StationAgent provides shared state management and server coordination for LangGraph workflows through three main components:

- **State Management** (`agent.state.*`)
- **Server Management** (`agent.server.*`) 
- **Pause/Unpause Management** (`agent.pause()`, `agent.unpause()`)

---

## Constructor

### `StationAgent(station_thread_id, graph_thread_id, token, initial_state=None)`

Initialize a new StationAgent instance with optional initial state.

**Parameters:**
- `station_thread_id` (str): Unique identifier for the station/workflow instance
- `graph_thread_id` (str): LangGraph thread identifier from config
- `token` (str): Bearer token for SharedState API authentication
- `initial_state` (dict, optional): Initial state to push to SharedState API. Automatically includes `server` and `serverThread` variables (both set to "idle")

**Attributes:**
- `agent.initial_state` (dict): Enhanced initial state with server variables automatically added

**Example:**
```python
# Initialize without initial state
agent = StationAgent(
    station_thread_id="workflow-instance-1",
    graph_thread_id=config["thread_id"],
    token="dev-token-123"
)

# Initialize with initial state (server variables added automatically)
initial_workflow_state = {
    "workflowId": "wf-123",
    "currentStep": "start",
    "userInput": "process this data"
}
agent = StationAgent(
    station_thread_id="workflow-instance-1",
    graph_thread_id=config["thread_id"],
    token="dev-token-123",
    initial_state=initial_workflow_state
)

# Check what was automatically enhanced
print(f"Initial variables: {list(agent.initial_state.keys())}")
# Output: ['workflowId', 'currentStep', 'userInput', 'server', 'serverThread']
```

---

## State Management API

### Sync Methods

#### `agent.state.sync(variable_name, langgraph_state=None)`

Sync a single variable from SharedState API to LangGraph state.

**Parameters:**
- `variable_name` (str): Name of the variable to sync
- `langgraph_state` (object, optional): LangGraph state object to update

**Returns:**
- If `langgraph_state` provided: Updated state object with `sharedState` populated
- If `langgraph_state` is None: Variable value or None if not found

**Example:**
```python
# Update LangGraph state
state = agent.state.sync("currentStep", state)

# Get just the value
current_step = agent.state.sync("currentStep")
```

#### `agent.state.sync_multiple(variable_names, langgraph_state=None)`

Sync multiple variables from SharedState API to LangGraph state.

**Parameters:**
- `variable_names` (List[str]): List of variable names to sync
- `langgraph_state` (object, optional): LangGraph state object to update

**Returns:**
- If `langgraph_state` provided: Updated state object
- If `langgraph_state` is None: Dict of {variable_name: value}

**Example:**
```python
state = agent.state.sync_multiple(["step", "status", "data"], state)
```

#### `agent.state.sync_all(langgraph_state)`

Sync all variables from SharedState API to LangGraph state.

**Parameters:**
- `langgraph_state` (object): LangGraph state object to update (required)

**Returns:**
- Updated state object with all variables in `sharedState`

**Example:**
```python
state = agent.state.sync_all(state)
print(state.sharedState)  # All shared variables
```

### CRUD Methods

#### `agent.state.get(variable_name)`

Get a single variable value from SharedState API.

**Parameters:**
- `variable_name` (str): Name of the variable to retrieve

**Returns:**
- Variable value (any type) or None if not found

**Raises:**
- `Exception`: Network or API errors

**Example:**
```python
user_prefs = agent.state.get("userPreferences")
if user_prefs:
    theme = user_prefs.get("theme", "light")
```

#### `agent.state.set(variable_name, value)`

Create or update a single variable in SharedState API.

**Parameters:**
- `variable_name` (str): Name of the variable to set
- `value` (any): Value to store (must be JSON serializable)

**Returns:**
- Dict with creation/update status

**Raises:**
- `ValueError`: If variable_name is a reserved variable ("server", "serverThread")
- `Exception`: Network or API errors

**Example:**
```python
agent.state.set("currentStep", "processing")
agent.state.set("workflowData", {"progress": 50, "status": "active"})

# ❌ This will raise ValueError
agent.state.set("server", "custom_status")
```

#### `agent.state.push(variables_dict)`

Bulk create/update multiple variables in SharedState API.

**Parameters:**
- `variables_dict` (Dict[str, any]): Dictionary of variable names and values

**Returns:**
- Dict with bulk operation status

**Raises:**
- `ValueError`: If any key is a reserved variable
- `Exception`: Network or API errors

**Example:**
```python
agent.state.push({
    "workflowId": "wf-123",
    "status": "running",
    "startTime": "2024-01-01T12:00:00Z",
    "metadata": {"version": "1.0"}
})
```

#### `agent.state.pull()`

Get all variables from SharedState API.

**Parameters:**
- None

**Returns:**
- Dict containing all variables and their values

**Example:**
```python
all_variables = agent.state.pull()
for name, value in all_variables.items():
    print(f"{name}: {value}")
```

#### `agent.state.delete(variable_name)`

Delete a variable from SharedState API.

**Parameters:**
- `variable_name` (str): Name of the variable to delete

**Returns:**
- Dict with deletion status

**Raises:**
- `ValueError`: If variable_name is a reserved variable
- `Exception`: Network or API errors

**Example:**
```python
agent.state.delete("temporary_data")
```

### Utility Methods

#### `agent.state.exists(variable_name)`

Check if a variable exists in SharedState API.

**Parameters:**
- `variable_name` (str): Name of the variable to check

**Returns:**
- `True` if variable exists, `False` otherwise

**Example:**
```python
if agent.state.exists("userSettings"):
    settings = agent.state.get("userSettings")
else:
    # Initialize default settings
    agent.state.set("userSettings", {"theme": "dark"})
```

#### `agent.state.list_variables()`

Get a list of all variable names in SharedState API.

**Parameters:**
- None

**Returns:**
- List[str] of all variable names

**Example:**
```python
variable_names = agent.state.list_variables()
print(f"Found {len(variable_names)} variables: {variable_names}")
```

---

## Server Management API

### `agent.server.load(task_type)`

Load the server for a specific task type, setting it to "busy".

**Parameters:**
- `task_type` (str): Type of task the server will be used for

**Returns:**
- Dict with load status:
  - Success: `{"status": "loaded", "serverThread": task_type}`
  - Busy: `{"status": "busy", "error": "Server is busy"}`

**Example:**
```python
load_result = agent.server.load("screenshot_processing")
if load_result["status"] == "loaded":
    # Server is now reserved for your task
    take_screenshot()
    agent.server.unload()  # Don't forget to unload!
elif load_result["status"] == "busy":
    # Handle busy server - retry later or queue
    print("Server busy, will retry in 5 seconds")
```

### `agent.server.unload()`

Unload the server, setting it to "idle".

**Parameters:**
- None

**Returns:**
- Dict with unload status:
  - Success: `{"status": "unloaded"}`
  - Already idle: `{"status": "idle", "error": "Server is already idle"}`

**Example:**
```python
unload_result = agent.server.unload()
print(f"Server unloaded: {unload_result['status']}")
```

### `agent.server.avail()`

Get current server availability status.

**Parameters:**
- None

**Returns:**
- Dict with server status:
  - `{"server": "idle", "serverThread": "idle"}` - Available
  - `{"server": "busy", "serverThread": "task_type"}` - In use

**Example:**
```python
status = agent.server.avail()
if status["server"] == "idle":
    print("Server is available")
else:
    print(f"Server busy with: {status['serverThread']}")
```

---

## Pause/Unpause Management API

### `agent.pause(reason=None)`

Pause the agent's execution and update the shared state with pause information.

**Parameters:**
- `reason` (str, optional): Descriptive reason for pausing. Defaults to "Agent paused for manual intervention."

**Returns:**
- Dict with pause status:
  - Success: `{"status": "paused", "reason": reason, "pausedAt": timestamp}`
  - Error: `{"status": "error", "error": "error_message"}`

**Example:**
```python
# Basic pause
result = agent.pause()
print(f"Paused: {result['status']}")

# Pause with custom reason
result = agent.pause("Waiting for user input on complex decision")
if result["status"] == "paused":
    print(f"Paused: {result['reason']}")
```

### `agent.unpause()`

Unpause the agent's execution by removing pause information from shared state.

**Parameters:**
- None

**Returns:**
- Dict with unpause status:
  - Success: `{"status": "unpaused", "unpausedAt": timestamp}`
  - Already active: `{"status": "already_active", "message": "Agent is not paused"}`
  - Error: `{"status": "error", "error": "error_message"}`

**Example:**
```python
result = agent.unpause()
if result["status"] == "unpaused":
    print("Agent resumed execution")
elif result["status"] == "already_active":
    print("Agent was not paused")
```

### `agent.is_paused()`

Check if the agent is currently paused.

**Parameters:**
- None

**Returns:**
- Dict with pause status:
  - Paused: `{"paused": True, "reason": "pause_reason", "pausedAt": timestamp}`
  - Not paused: `{"paused": False}`
  - Error: `{"paused": False, "error": "error_message"}`

**Example:**
```python
status = agent.is_paused()
if status["paused"]:
    print(f"Agent is paused: {status['reason']}")
    print(f"Paused since: {status['pausedAt']}")
else:
    print("Agent is active")
```

**State Variables Used:**
- `is_paused` (bool): True when agent is paused, False otherwise
- `pause_reason` (str): Reason for pausing
- `paused_at` (str): ISO timestamp when agent was paused

---

## Utility Methods

### `agent.validate_connection()`

Test the connection to SharedState API.

**Parameters:**
- None

**Returns:**
- Dict with connection status:
  - Success: `{"connected": True, "variable_count": N}`
  - Failure: `{"connected": False, "error": "error_message"}`

**Example:**
```python
connection = agent.validate_connection()
if connection["connected"]:
    print(f"Connected! Found {connection['variable_count']} variables")
else:
    print(f"Connection failed: {connection['error']}")
```

### `agent.validate_server_status(status)`

Validate if a server status value is allowed.

**Parameters:**
- `status` (str): Status value to validate

**Returns:**
- `True` if status is valid ("busy" or "idle"), `False` otherwise

**Example:**
```python
assert agent.validate_server_status("busy") == True
assert agent.validate_server_status("idle") == True
assert agent.validate_server_status("custom") == False
```

---

## Constants

### `SHARED_STATE_URL`
Default API endpoint: `"https://c16bgaz0i2.execute-api.us-west-1.amazonaws.com/prod/"`

### `RESERVED_VARIABLES`
Protected variables: `{"server", "serverThread"}`

### `VALID_SERVER_STATUS`
Allowed server statuses: `{"busy", "idle"}`

---

## Error Handling

### Common Exceptions

#### `ValueError`
- Raised when attempting to modify reserved variables
- Raised when providing invalid server status values

#### `requests.exceptions.RequestException`
- Network connectivity issues
- API server errors
- Authentication failures

#### `json.JSONDecodeError`
- Invalid API response format

### Error Response Format

API errors return structured error information:

```python
{
    "error": "Detailed error message",
    "status_code": 404,
    "request_url": "https://api.example.com/endpoint"
}
```

### Retry Logic

StationAgent automatically retries failed requests:
- **Attempts**: 3 total attempts
- **Backoff**: Exponential (1s, 2s, 4s)
- **Retryable Errors**: Network timeouts, 5xx server errors
- **Non-retryable**: 401 authentication, 404 not found

---

## Thread Safety

StationAgent instances are not thread-safe. Create separate instances for concurrent workflows:

```python
# ✅ Good - separate instances
agent1 = StationAgent("workflow-1", thread_id_1, token)
agent2 = StationAgent("workflow-2", thread_id_2, token)

# ❌ Avoid - shared instance across threads
shared_agent = StationAgent("shared", "thread", token)
# Don't use shared_agent in multiple threads
```

---

## Performance Considerations

- **Sync Operations**: `sync_all()` fetches all variables - use `sync()` for single variables when possible
- **Bulk Operations**: Use `push()` for multiple variable updates instead of multiple `set()` calls
- **Connection Pooling**: StationAgent reuses HTTP connections within an instance
- **Caching**: No built-in caching - implement at application level if needed

---

## API Response Examples

### Successful Variable Get
```json
{
    "value": {"theme": "dark", "language": "en"},
    "type": "object",
    "lastModified": "2024-01-01T12:00:00Z"
}
```

### Variable Not Found
```json
{
    "error": "Variable 'nonexistent' not found",
    "status_code": 404
}
```

### Server Load Success
```json
{
    "server": "busy",
    "serverThread": "screenshot_processing",
    "loadedAt": "2024-01-01T12:00:00Z"
}
```

### Authentication Error
```json
{
    "error": "Invalid or missing authorization token",
    "status_code": 401
}
``` 