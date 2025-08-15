# 🐾 CuteAgent

**Computer Use Task Execution Agent**  
*A Python library for building, orchestrating, and integrating computer-use AI agents in agentic workflows.*

---
[![PyPI](https://img.shields.io/pypi/v/cuteagent?color=blue)](https://pypi.org/project/cuteagent/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

# CuteAgent - Complete Agent Suite for LangGraph Workflows

**CuteAgent** provides three powerful agents for building comprehensive LangGraph workflows:

- **🤖 StationAgent**: Shared state management and workflow coordination
- **🖥️ WindowsAgent**: Computer use automation on Windows servers  
- **🧭 VisionAgent**: Vision model integration for GUI element grounding and coordinate extraction
- **👥 HumanAgent**: Human-in-the-loop (HITL) task management

Together, these agents enable complete automation workflows where AI performs computer tasks, humans provide oversight and decisions, and shared state coordinates everything seamlessly.

## 🧭 VisionAgent - Vision Grounding and GUI Coordinate Extraction

**VisionAgent** integrates with vision models to locate UI elements in screenshots and return click coordinates.

### 🚀 Key Features

- Claude Integration: Send a screenshot and element description to Claude and get grounded coordinates
- Hugging Face GUI Model: Use OpenAI-compatible endpoint to parse GUI and extract coordinates via `find_element`
- Screen Scaling: Converts model coordinates to your actual screen resolution

### 🔧 Quick Start

```python
from cuteagent import VisionAgent

# Initialize with screen size and optional Anthropic API key via env
# export ANTHROPIC_API_KEY=... in your environment or .env
vision = VisionAgent(screen_size=(1366, 768))

# Claude grounding: description + image URL → (x,y)
image_url = "https://datacollectionfintor.s3.amazonaws.com/screenshot_20250517_180131.png"
description = {
    "name": "Reports",
    "description": "Reports tab on the top navigation bar",
    "element_type": "tab"
}
coords = vision.claude(image_url, description)
print("Claude coordinates:", coords)  # e.g. "(339,66)" or "NOT FOUND" or "ERROR: ..."

# Hugging Face GUI model: element name + screenshot URL
vision_hf = VisionAgent(model_selected="FINTOR_GUI")
coords_hf = vision_hf.find_element(
    screenshot_url=image_url,
    element_name="click on Reports tab on navigation bar"
)
print("HF model coordinates:", coords_hf)
```

### ⚙️ Configuration

```bash
# Anthropic (Claude) - required for VisionAgent.claude
export ANTHROPIC_API_KEY="your-anthropic-key"

# Hugging Face GUI endpoint (optional; defaults are provided)
export HF_TOKEN="your-hf-token"
```

### 📝 Notes

- `VisionAgent.claude(...)` returns:
  - "(x,y)" coordinate string on success
  - "NOT FOUND" if element cannot be grounded
  - "ERROR: ..." for explicit error messaging (e.g., missing key, invalid media type)
- Coordinates are clamped to your `screen_size` and converted if the model returns a different reference size.

## 📦 Installation

```bash
pip install cuteagent
```

---

# 🤖 StationAgent - Shared State Management

**StationAgent** provides shared state management and server coordination for LangGraph workflows. It integrates with a SharedState API to enable multiple workflow instances to coordinate, share data, and manage server resources efficiently.

## 🚀 Key Features

- **Shared State Management**: Sync variables between multiple LangGraph workflow instances
- **Server Coordination**: Prevent conflicts with "busy"/"idle" server status management  
- **Workflow Resumption**: Handle interrupted workflows with thread ID tracking
- **Reserved Variable Protection**: Secure server management variables from user modification (`server`, `serverThread`, `serverCheckpoint`, `serverTaskType`)
- **Multi-Server Management**: Manages state for multiple servers using array-based variables.
- **LangGraph Integration**: Seamless integration with LangGraph state objects
- **Error Handling**: Robust retry logic and comprehensive error handling

## 🔧 Quick Start

### 1. Add Shared State to Your LangGraph State Class

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class State:
    # Your existing fields...
    current_node: float = 0
    user_input: str = ""
    stationThreadId: str = ""
    
    # Add this field for SharedState integration
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)
```

### 2. Initialize StationAgent in Your LangGraph Nodes

⚠️ **IMPORTANT**: All StationAgent operations use synchronous HTTP calls internally and must be wrapped in `asyncio.to_thread()` to prevent blocking the ASGI event loop.

```python
from cuteagent import StationAgent
import asyncio

async def your_langgraph_node(state: State, config: RunnableConfig) -> State:
    # Initialize StationAgent - MUST use asyncio.to_thread()
    agent = await asyncio.to_thread(
        StationAgent,
        station_thread_id=state.stationThreadId,
        graph_thread_id=config.get("thread_id"),
        token=config.get("shared_state_token", "your-api-token"),
        langgraph_token=config.get("langgraph_token")  # Required for pause/unpause functionality
    )
    # 🔄 Agent now has agent.initial_state with any existing variables
    
    # Sync shared state variables to LangGraph state - MUST use asyncio.to_thread()
    state = await asyncio.to_thread(agent.state.sync_all, state)
    
    # Check what initial state was loaded (optional)
    if agent.initial_state:
        print(f"Loaded {len(agent.initial_state)} existing variables")
        # initial_state now contains arrays for server management
        print(f"Server states: {agent.initial_state['server']}")
    
    # Your node logic here...
    
    # Update shared state - MUST use asyncio.to_thread()
    await asyncio.to_thread(agent.state.set, "currentNode", "processing")
    await asyncio.to_thread(agent.state.set, "timestamp", "2024-01-01T12:00:00Z")
    
    return state
```

## 📊 Sync Patterns

StationAgent provides three sync patterns that update your LangGraph state and return the updated state object. **All sync operations must use `asyncio.to_thread()`**:

### Pattern 1: Sync Single Variable
```python
state = await asyncio.to_thread(agent.state.sync, "variableName", state)
```

### Pattern 2: Sync Multiple Variables  
```python
state = await asyncio.to_thread(agent.state.sync_multiple, ["var1", "var2", "var3"], state)
```

### Pattern 3: Sync All Variables
```python
state = await asyncio.to_thread(agent.state.sync_all, state)
```

---

# 🖥️ WindowsAgent - Computer Use Automation

**WindowsAgent** enables computer use automation on Windows servers maintained by Fintor. It provides methods for clicking, taking screenshots, and performing other computer tasks remotely.

## 🚀 Key Features

- **Remote Computer Control**: Click, pause, and interact with Windows servers
- **Screenshot Capabilities**: Full and cropped screenshots with URL responses
- **Async Integration**: Thread-safe operations for LangGraph workflows
- **Error Resilience**: Graceful handling of server issues
- **Coordinate-based Actions**: Precise control with x,y coordinates

## 🔧 Quick Start

### 1. Initialize WindowsAgent

⚠️ **IMPORTANT**: All WindowsAgent operations use synchronous HTTP calls internally and must be wrapped in `asyncio.to_thread()` to prevent blocking the ASGI event loop.

```python
from cuteagent import WindowsAgent
import asyncio

async def windows_automation_node(state: State, config: RunnableConfig) -> State:
    configuration = config["configurable"]
    
    # Initialize WindowsAgent with server URL
    os_url = configuration.get("os_url", "https://your-windows-server.ngrok.app")
    agent = WindowsAgent(os_url=os_url)
    
    try:
        # Click at specific coordinates - MUST use asyncio.to_thread()
        await asyncio.to_thread(agent.click_element, 100, 200)
        
        # Wait/pause - MUST use asyncio.to_thread()
        await asyncio.to_thread(agent.pause, 3)
        
        # Take a full screenshot - MUST use asyncio.to_thread()
        screenshot_result = await asyncio.to_thread(agent.screenshot)
        if isinstance(screenshot_result, dict) and "url" in screenshot_result:
            state.screenshot_url = screenshot_result["url"]
        else:
            state.screenshot_url = screenshot_result
        
        # Take a cropped screenshot [x, y, width, height] - MUST use asyncio.to_thread()
        cropped_result = await asyncio.to_thread(
            agent.screenshot_cropped, 
            [10, 200, 1000, 450]
        )
        
        print(f"Screenshot URL: {state.screenshot_url}")
        
    except Exception as e:
        print(f"Windows automation error: {e}")
        # Continue workflow even on errors
        
    state.current_node = 8
    return state
```

## 📖 WindowsAgent API Reference

### Constructor

```python
WindowsAgent(os_url: str)
```

**Parameters:**
- `os_url` (str): URL of the Windows server (e.g., "https://server.ngrok.app")

### Methods

⚠️ **All methods must be wrapped in `asyncio.to_thread()` when called from async LangGraph nodes.**

#### `agent.click_element(x: int, y: int)`
Click at specific screen coordinates.

```python
await asyncio.to_thread(agent.click_element, 150, 300)
```

#### `agent.pause(seconds: int)`
Pause execution for specified seconds.

```python
await asyncio.to_thread(agent.pause, 5)
```

#### `agent.screenshot()`
Take a full screenshot of the desktop.

```python
result = await asyncio.to_thread(agent.screenshot)
# Returns: {"url": "https://..."} or URL string
```

#### `agent.screenshot_cropped(coordinates: List[int])`
Take a cropped screenshot with [x, y, width, height] coordinates.

```python
result = await asyncio.to_thread(agent.screenshot_cropped, [10, 50, 800, 600])
# Returns: {"url": "https://..."} or URL string
```

---

# 👥 HumanAgent - Human-in-the-Loop Task Management

**HumanAgent** integrates with Fintor's HITL service to bring humans into LangGraph workflows for approvals, decisions, and oversight. Responses are processed manually outside of CuteAgent and update shared state via StationAgent.

## 🚀 Key Features

- **Task Submission**: Send tasks with questions and images to humans
- **Choice-based Responses**: Multiple choice questions with predefined options
- **Image Support**: Include screenshots and visual content for human review
- **External State Updates**: Human responses processed outside the system
- **Task Type Management**: Categorize tasks with custom task types
- **Reporting**: Report workflow results back to human operators

## 🔧 Quick Start

### 1. Send Task for Human Review

⚠️ **IMPORTANT**: All HumanAgent operations use synchronous HTTP calls internally and must be wrapped in `asyncio.to_thread()` to prevent blocking the ASGI event loop.

```python
from cuteagent import HumanAgent
import asyncio

async def send_human_task_node(state: State, config: RunnableConfig) -> State:
    """Send a task to humans for review with image and questions."""
    configuration = config["configurable"]
    
    hitl_token = configuration.get("hitl_token", os.getenv("HITL_TOKEN"))
    agent = HumanAgent(
        HITL_token=hitl_token, 
        HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    # Prepare the human review task
    image_urls = [state.screenshot_url] if state.screenshot_url else []
    
    question_text = f"Agent found {len(state.borrower_names)} borrowers with Document Date.\n"
    question_text += "Please review and approve:\n"
    for borrower in state.borrower_names:
        question_text += f"- {borrower}\n"
    question_text += "\nDo you approve this decision?"
    
    questions = [{
        "Question": question_text, 
        "Choices": ["TRUE", "FALSE"]
    }]
    
    thread_id = configuration.get("thread_id", str(uuid.uuid4()))
    
    # Create state data for HITL system
    state_dict = {
        "user_input": state.user_input,
        "current_node": state.current_node,
        "borrower_names": state.borrower_names,
        "stationThreadId": state.stationThreadId
    }
    
    try:
        # Send task to human agent - MUST use asyncio.to_thread()
        result = await asyncio.to_thread(
            agent.task,
            image_urls=image_urls,
            thread_id=thread_id,
            questions=questions,
            task_type="S1-T1",  # Your task type
            thread_state=state_dict
        )
        
        print(f"Human task sent successfully for thread: {thread_id}")
        
        # Store pending review info for interrupt
        state.pending_review_info = {
            "screenshot_url": state.screenshot_url,
            "borrower_names": state.borrower_names,
            "instructions": "Review extracted borrower names and respond via HITL system",
            "thread_id_of_task": thread_id
        }
        
    except Exception as e:
        print(f"Error sending human task: {e}")
        # Continue workflow or handle error appropriately
        
    state.current_node = 10.5
    return state
```

### 2. Report Results to Humans

```python
async def report_to_human_node(state: State, config: RunnableConfig) -> State:
    """Report final workflow results to human operators."""
    configuration = config["configurable"]
    
    hitl_token = configuration.get("hitl_token", os.getenv("HITL_TOKEN"))
    agent = HumanAgent(
        HITL_token=hitl_token, 
        HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    thread_id = configuration.get("thread_id")
    
    # Prepare final state report
    state_dict = {
        "user_input": state.user_input,
        "current_node": state.current_node,
        "screenshot_url": state.screenshot_url,
        "borrower_names": state.borrower_names,
        "human_review_decision": state.human_review_decision,
        "status": state.status,
        "stationThreadId": state.stationThreadId
    }
    
    try:
        # Report final results - MUST use asyncio.to_thread()
        result = await asyncio.to_thread(
            agent.reporting,
            thread_id=thread_id,
            report_type="S1-R1",  # Your report type
            thread_state=state_dict
        )
        
        print(f"Results reported to human agent: {result}")
        
    except Exception as e:
        print(f"Error reporting to human agent: {e}")
    
    state.current_node = 12
    return state
```

## 📖 HumanAgent API Reference

### Constructor

```python
HumanAgent(HITL_token: str, HITL_url: str)
```

**Parameters:**
- `HITL_token` (str): Authentication token for HITL service
- `HITL_url` (str): URL of the HITL service API

### Methods

⚠️ **All methods must be wrapped in `asyncio.to_thread()` when called from async LangGraph nodes.**

#### `agent.task(image_urls, thread_id, questions, task_type, thread_state)`
Send a task to humans for review and decision.

**Usage:**
```python
result = await asyncio.to_thread(
    agent.task,
    image_urls=image_urls,
    thread_id=thread_id,
    questions=questions,
    task_type=task_type,
    thread_state=thread_state
)
```

**Parameters:**
- `image_urls` (List[str]): URLs of images (e.g., screenshots) for human review
- `thread_id` (str): Unique thread identifier for the task
- `questions` (List[Dict]): Questions with choices for humans to answer
- `task_type` (str): Category/type of the task (e.g., "S1-T1", "S2-T3")
- `thread_state` (Dict): Current workflow state data

**Questions Format:**
```python
questions = [{
    "Question": "Do you approve these borrower names?",
    "Choices": ["TRUE", "FALSE"]
}]
```

#### `agent.reporting(thread_id, report_type, thread_state)`
Report workflow results and final state to human operators.

**Usage:**
```python
result = await asyncio.to_thread(
    agent.reporting,
    thread_id=thread_id,
    report_type=report_type,
    thread_state=thread_state
)
```

**Parameters:**
- `thread_id` (str): Thread identifier for the report
- `report_type` (str): Type of report (e.g., "S1-R1", "FINAL")
- `thread_state` (Dict): Final workflow state and results

---

# 🔄 Complete Multi-Agent Workflow Example

Here's a complete example showing all three agents working together with proper async handling:

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
import asyncio
import uuid
from cuteagent import StationAgent, WindowsAgent, HumanAgent

@dataclass
class WorkflowState:
    current_node: float = 0
    user_input: str = ""
    stationThreadId: str = ""
    borrower_names: List[str] = field(default_factory=list)
    screenshot_url: str | None = None
    status: str = "Ongoing"
    human_review_decision: str | None = None
    pending_review_info: Optional[Dict[str, Any]] = None
    
    # Required for StationAgent integration
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)

async def complete_workflow_node(state: WorkflowState, config) -> WorkflowState:
    """Complete workflow using all three agents with proper async handling."""
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent for coordination with initial workflow state
    initial_workflow_state = {
        "workflowType": "complete_multi_agent",
        "startTime": "2024-01-01T12:00:00Z",
        "workflowStatus": "active"
    }
    station_agent = await asyncio.to_thread(
        StationAgent,
        station_thread_id=state.stationThreadId or "main-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token"),
        initial_state=initial_workflow_state,
        langgraph_token=configuration.get("langgraph_token")
    )
    
    # 2. Sync shared state to get latest workflow data
    state = await asyncio.to_thread(station_agent.state.sync_all, state)
    
    # 3. Check server availability and load for computer use
    server_status = await asyncio.to_thread(station_agent.server.avail)
    if server_status.get("server") == "idle":
        load_result = await asyncio.to_thread(station_agent.server.load, "screenshot_task")
        if load_result["status"] == "loaded":
            
            # 4. Use WindowsAgent for computer automation
            os_url = configuration.get("os_url")
            windows_agent = WindowsAgent(os_url=os_url)
            
            try:
                # Perform computer tasks
                await asyncio.to_thread(windows_agent.click_element, 294, 98)
                await asyncio.to_thread(windows_agent.pause, 2)
                
                # Take screenshot for human review
                screenshot_result = await asyncio.to_thread(
                    windows_agent.screenshot_cropped, 
                    [10, 200, 1000, 450]
                )
                
                if isinstance(screenshot_result, dict):
                    state.screenshot_url = screenshot_result["url"]
                else:
                    state.screenshot_url = screenshot_result
                    
            except Exception as e:
                print(f"Windows automation error: {e}")
            
            # 5. Send task to HumanAgent for review
            hitl_token = configuration.get("hitl_token")
            human_agent = HumanAgent(
                HITL_token=hitl_token,
                HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
            )
            
            questions = [{
                "Question": f"Screenshot taken successfully. Proceed with processing?",
                "Choices": ["APPROVE", "REJECT"]
            }]
            
            thread_id = configuration.get("thread_id")
            state_dict = {
                "screenshot_url": state.screenshot_url,
                "current_node": state.current_node,
                "stationThreadId": state.stationThreadId
            }
            
            try:
                await asyncio.to_thread(
                    human_agent.task,
                    image_urls=[state.screenshot_url] if state.screenshot_url else [],
                    thread_id=thread_id,
                    questions=questions,
                    task_type="S1-T1",
                    thread_state=state_dict
                )
                
                print("Human review task sent successfully")
                
            except Exception as e:
                print(f"Human task error: {e}")
            
            # 6. Update shared state with workflow progress
            await asyncio.to_thread(station_agent.state.push, {
                "lastCompletedNode": state.current_node,
                "screenshotTaken": True,
                "humanTaskSent": True,
                "workflowStatus": "awaiting_human_review"
            })
            
            # 7. Unload server when done
            await asyncio.to_thread(station_agent.server.unload)
            
    else:
        print("Server is busy, waiting...")
        
    # 8. Sync final state back to LangGraph
    state = await asyncio.to_thread(station_agent.state.sync_all, state)
    
    state.current_node += 1
    return state
```

This example demonstrates how all three agents work together with proper async handling:
- **StationAgent** coordinates shared state and server access for multiple servers
- **WindowsAgent** performs computer automation tasks
- **HumanAgent** provides human oversight and decision-making

---

# 📋 StationAgent Detailed API Reference

## Constructor and Initialization

### `StationAgent(station_thread_id, graph_thread_id, token, initial_state=None, langgraph_token=None)`

Create a new StationAgent instance with initial state push capability.

⚠️ **IMPORTANT**: Constructor must be wrapped in `asyncio.to_thread()` in async contexts.

```python
# Correct async usage
agent = await asyncio.to_thread(
    StationAgent,
    station_thread_id="workflow-123",
    graph_thread_id="thread-456", 
    token="your-shared-state-token",
    initial_state=initial_state,  # optional
    langgraph_token="your-langgraph-token"  # required for pause/unpause functionality
)
```

**Parameters:**
- `station_thread_id` (str): Identifier for the station/workflow instance
- `graph_thread_id` (str): LangGraph thread identifier  
- `token` (str): Authentication token for SharedState API
- `initial_state` (dict, optional): Initial state object to push to SharedState API
- `langgraph_token` (str, optional): Authentication token for LangGraph API. Required for `pause()` and `unpause()` functionality.

**Automatic Initialization:**
- Automatically pushes initial_state to SharedState API during initialization (if provided)
- Automatically adds `server`, `serverThread`, `serverCheckpoint`, and `serverTaskType` as arrays to `initial_state` to manage 4 servers by default.
- Stores enhanced initial_state in `agent.initial_state` attribute for easy access
- Provides console feedback about pushed variables

**Attributes:**
- `agent.initial_state` (dict): Dictionary of initial state with server variables automatically added

**Example:**
```python
# Initialize agent with initial state
initial_workflow_state = {
    "workflowId": "wf-123",
    "currentStep": "start",
    "userInput": "process this data"
}
agent = await asyncio.to_thread(
    StationAgent, 
    "workflow-123", 
    "thread-456", 
    "token", 
    initial_state=initial_workflow_state
)

# Check what was automatically enhanced (server variables added)
print(f"Initial variables: {list(agent.initial_state.keys())}")
# Output: ['workflowId', 'currentStep', 'userInput', 'server', 'serverThread', 'serverCheckpoint', 'serverTaskType']
print(f"Workflow ID: {agent.initial_state['workflowId']}")
print(f"Server status: {agent.initial_state['server']}")  # ['idle', 'idle', 'idle', 'idle']
print(f"Server thread: {agent.initial_state['serverThread']}")  # ['idle', 'idle', 'idle', 'idle']

# Initialize without initial state
agent_empty = await asyncio.to_thread(StationAgent, "workflow-456", "thread-789", "token")
print(f"No initial state: {agent_empty.initial_state}")  # None
```

## State Management Methods

⚠️ **All state methods must be wrapped in `asyncio.to_thread()` when called from async LangGraph nodes.**

### `agent.state.sync(variable_name, langgraph_state=None)`
Sync single variable from SharedState API to LangGraph state.

```python
# Returns updated state object
state = await asyncio.to_thread(agent.state.sync, "currentStep", state)

# Returns just the variable value (backward compatibility)
value = await asyncio.to_thread(agent.state.sync, "currentStep")
```

### `agent.state.sync_multiple(variable_names, langgraph_state=None)`
Sync multiple variables from SharedState API to LangGraph state.

```python
state = await asyncio.to_thread(agent.state.sync_multiple, ["var1", "var2", "var3"], state)
```

### `agent.state.sync_all(langgraph_state)`
Sync all variables from SharedState API to LangGraph state.

```python
state = await asyncio.to_thread(agent.state.sync_all, state)
```

### `agent.state.set(variable_name, value)`
Create or update a single variable in SharedState API.

```python
await asyncio.to_thread(agent.state.set, "currentStep", "processing")
await asyncio.to_thread(agent.state.set, "userPrefs", {"theme": "dark"})
```

### `agent.state.get(variable_name)`
Get a single variable from SharedState API.

```python
current_step = await asyncio.to_thread(agent.state.get, "currentStep")  # Returns value or None
```

### `agent.state.push(variables_dict)`
Bulk create/update multiple variables in SharedState API.

```python
await asyncio.to_thread(agent.state.push, {
    "workflowId": "wf-123",
    "status": "processing", 
    "data": {"key": "value"}
})
```

### `agent.state.pull()`
Get all variables from SharedState API.

```python
all_vars = await asyncio.to_thread(agent.state.pull)  # Returns dict of all variables
```

### `agent.state.delete(variable_name)`
Delete a variable from SharedState API.

```python
await asyncio.to_thread(agent.state.delete, "temporary_data")
```

### `agent.state.exists(variable_name)`
Check if a variable exists in SharedState API.

```python
exists = await asyncio.to_thread(agent.state.exists, "userPreferences")
if exists:
    prefs = await asyncio.to_thread(agent.state.get, "userPreferences")
```

### `agent.state.list_variables()`
Get list of all variable names.

```python
var_names = await asyncio.to_thread(agent.state.list_variables)  # Returns list of strings
```

## Server Management Methods

⚠️ **All server methods must be wrapped in `asyncio.to_thread()` when called from async LangGraph nodes. They now operate on a specific server via an index.**

### `agent.server.load(serverThreadId, serverCheckpoint="setup", serverIndex=0, serverTaskType="taskPlaceholder")`
Load a specific server for a task. The server must be in "idle" status and have the expected checkpoint.

**Parameters:**
- `serverThreadId` (str): The thread ID to assign to the server when loaded
- `serverCheckpoint` (str, optional): The checkpoint to verify before loading. Defaults to "setup"
- `serverIndex` (int, optional): The index of the server to load (0-3). Defaults to 0
- `serverTaskType` (str, optional): The task type to assign. Defaults to "taskPlaceholder"

```python
result = await asyncio.to_thread(
    agent.server.load,
    serverThreadId="GetNames",
    serverCheckpoint="setup",
    serverIndex=0,
    serverTaskType="data_processing"
)
# Returns: {"status": "loaded", "serverThread": "GetNames"} 
# or {"status": "busy", "error": "Server is busy"}
# or {"status": "wrongCheckpoint", "error": "Incorrect checkpoint. Expected setup, got running"}
# or {"status": "error", "error": "serverIndex 0 is out of bounds."}
```

### `agent.server.unload(checkpoint="setup", index=0)`
Unload a server and set it to idle with a new checkpoint. The server must be in "busy" status.

**Parameters:**
- `checkpoint` (str, optional): The checkpoint to set after unloading. Defaults to "setup"
- `index` (int, optional): The index of the server to unload (0-3). Defaults to 0

```python
result = await asyncio.to_thread(agent.server.unload, checkpoint="completed", index=0)
# With default checkpoint:
result = await asyncio.to_thread(agent.server.unload, index=0)  # Uses "setup" as default

# Returns: {"status": "unloaded"}
#       or {"status": "idle", "error": "Server is already idle"}
#       or {"status": "error", "error": "serverIndex 0 is out of bounds."}
```

### `agent.server.avail(index=0)`
Get availability status for a specific server.

**Parameters:**
- `index` (int, optional): The index of the server to check (0-3). Defaults to 0

```python
status = await asyncio.to_thread(agent.server.avail, index=0)
# Returns: {
#     "server": "busy|idle", 
#     "serverThread": "GetNames|idle", 
#     "serverCheckpoint": "setup|running|completed", 
#     "serverTaskType": "data_processing|taskPlaceholder"
# }
# or {"status": "error", "error": "Server state is not initialized correctly as arrays."}
```



## 🔒 Reserved Variables

StationAgent protects these variables from user modification:

*   **`server`**: Array of server statuses ("busy" or "idle" only)
*   **`serverThread`**: Array of current task threads when server is busy
*   **`serverCheckpoint`**: Array of server checkpoints
*   **`serverTaskType`**: Array of server task types

These can only be modified through server management methods:
*   `agent.server.load(...)` - Sets a server to "busy"
*   `agent.server.unload(...)` - Sets a server to "idle"

```python
# ❌ This will raise ValueError
await asyncio.to_thread(agent.state.set, "server", "custom_status")  

# ✅ This is the correct way
await asyncio.to_thread(agent.server.load, serverThreadId="my_task_thread")  # Sets server 0 to "busy"
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# StationAgent
export SHARED_STATE_URL="https://your-api.amazonaws.com/prod"
export SHARED_STATE_TOKEN="your-shared-state-api-token"
export LANGGRAPH_TOKEN="your-langgraph-api-token"

# HumanAgent
export HITL_TOKEN="your-hitl-token"

# WindowsAgent (configured per workflow)
# os_url provided in LangGraph configuration
```

### LangGraph Configuration
```python
config = {
    "configurable": {
        "shared_state_token": "your-shared-state-api-token",
        "langgraph_token": "your-langgraph-api-token",  # Required for pause/unpause functionality
        "hitl_token": "your-hitl-token", 
        "os_url": "https://your-windows-server.ngrok.app",
        "thread_id": "your-langgraph-thread-id"
    }
}
```

## 🚨 Error Handling

### StationAgent
- **Network Retries**: 3 attempts with exponential backoff
- **Authentication Errors**: Clear messages for invalid tokens
- **Reserved Variable Protection**: ValueError for protected variables
- **Blocking Call Prevention**: All operations must use `asyncio.to_thread()` in async contexts

### WindowsAgent  
- **Connection Issues**: Graceful failure with workflow continuation
- **Server Errors**: Exception handling with logging
- **Timeout Handling**: Async operations with proper error propagation
- **Blocking Call Prevention**: All operations must use `asyncio.to_thread()` in async contexts

### HumanAgent
- **Service Issues**: Contact support_eng@fintor.com
- **Task Failures**: Manual processing required outside the system
- **Response Processing**: Done manually outside CuteAgent
- **Blocking Call Prevention**: All operations must use `asyncio.to_thread()` in async contexts

```python
try:
    state = await asyncio.to_thread(agent.state.sync_all, state)
except ValueError as e:
    # Handle reserved variable violations
    print(f"Configuration error: {e}")
except Exception as e:
    # Handle network/API errors
    print(f"Network error: {e}")
    # Continue with workflow using existing state
```

## 📚 Best Practices for Multi-Agent Workflows

1. **Always use `asyncio.to_thread()`** for all CuteAgent operations in async LangGraph nodes
2. **Initialize StationAgent first** in each node for state coordination
3. **Check server availability** before WindowsAgent operations
4. **Use HumanAgent for critical decisions** and quality assurance
5. **Include screenshots** in human tasks for better context
6. **Handle errors gracefully** - workflows should be resilient
7. **Update shared state regularly** for workflow coordination
8. **Use meaningful task types** for HumanAgent categorization
9. **Clean up resources** - unload servers when done
10. **Test blocking call prevention** - ensure no "Blocking call to socket.socket.connect" errors

## 🚨 Critical Async Requirements

**ALL CuteAgent operations use synchronous HTTP calls internally and MUST be wrapped in `asyncio.to_thread()` when used in async LangGraph nodes to prevent blocking the ASGI event loop.**

### ✅ Correct Usage:
```python
# StationAgent
agent = await asyncio.to_thread(StationAgent, station_id, graph_id, token)
state = await asyncio.to_thread(agent.state.sync_all, state)
await asyncio.to_thread(agent.state.set, "key", "value")

# HumanAgent  
await asyncio.to_thread(agent.task, images, thread_id, questions, task_type, state)

# WindowsAgent
await asyncio.to_thread(agent.click_element, x, y)
await asyncio.to_thread(agent.screenshot)
```

### ❌ Incorrect Usage (will cause blocking errors):
```python
# These will cause "Blocking call to socket.socket.connect" errors
agent = StationAgent(station_id, graph_id, token)  # ❌
state = agent.state.sync_all(state)  # ❌
agent.task(images, thread_id, questions, task_type, state)  # ❌
```

## 📖 Additional Documentation

- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[LangGraph Integration](docs/langgraph_integration.md)** - Detailed integration guide
- **[Deployment Guide](DEPLOYMENT.md)** - Automated deployment instructions

## 🤝 Contributing

CuteAgent is part of a comprehensive agent suite. For issues, feature requests, or contributions, please contact the development team.

## 📄 License

This project is licensed under the MIT License.

---

**Ready to build complete AI workflows with computer use, human oversight, and shared coordination? Start using CuteAgent today!** 🚀



