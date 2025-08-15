# LangGraph Integration Guide - Complete Multi-Agent Workflows

This guide demonstrates how to integrate all three CuteAgent agents (StationAgent, WindowsAgent, HumanAgent) with LangGraph workflows for comprehensive automation with human oversight and shared state coordination.

## Table of Contents

1. [State Class Setup](#state-class-setup)
2. [Complete Multi-Agent Workflow](#complete-multi-agent-workflow)
3. [Real-World Example: Document Processing](#real-world-example-document-processing)
4. [Advanced Patterns](#advanced-patterns)
5. [Configuration and Error Handling](#configuration-and-error-handling)

---

## State Class Setup

### Required State Structure for All Agents

Your LangGraph state class must include fields for all three agents:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class WorkflowState:
    # Core workflow fields
    current_node: float = 0
    user_input: str = ""
    status: str = "Ongoing"
    
    # StationAgent integration (required)
    stationThreadId: str = ""
    sharedState: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    # WindowsAgent fields
    screenshot_url: str | None = None
    
    # HumanAgent fields
    borrower_names: List[str] = field(default_factory=list)
    human_review_decision: str | None = None
    pending_review_info: Optional[Dict[str, Any]] = None
    
    # Workflow-specific fields
    table_csv: str | None = None
    webhook_status: str | None = None
    final_api_status: str | None = None
    reason_code: str | None = None
```

### LangGraph Configuration

```python
from langchain_core.runnables import RunnableConfig

config = RunnableConfig({
    "configurable": {
        # Thread management
        "thread_id": "workflow-thread-123",
        
        # StationAgent (uses default SharedState API URL)
        "shared_state_token": "your-api-token",
        
        # HumanAgent
        "hitl_token": "your-hitl-token",
        
        # WindowsAgent
        "os_url": "https://your-windows-server.ngrok.app",
        
        # Additional workflow config
        "openai_api_key": "your-openai-key",  # For data processing
        "aws_access_key_id": "your-aws-key",  # For textract
        "aws_secret_access_key": "your-aws-secret"
    }
})
```

---

## Complete Multi-Agent Workflow

### 1. Workflow Start Node with StationAgent Coordination

```python
from cuteagent import StationAgent, WindowsAgent, HumanAgent
import asyncio
import uuid

async def workflow_start_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Initialize workflow with StationAgent coordination."""
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent for shared state management
    # Initialize with workflow state (server variables added automatically)
    initial_workflow_state = {
        "workflowType": "document_processing",
        "startTime": "2024-01-01T12:00:00Z",
        "workflowStatus": "initializing"
    }
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or "document-workflow",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token"),
        initial_state=initial_workflow_state
    )
    # Agent now has station_agent.initial_state with server variables and workflow state
    
    # 2. Extract stationThreadId from user input if provided
    if state.user_input:
        try:
            if isinstance(state.user_input, dict):
                if "stationThreadId" in state.user_input:
                    state.stationThreadId = state.user_input["stationThreadId"]
            elif isinstance(state.user_input, str) and state.user_input.strip():
                user_data = json.loads(state.user_input.strip())
                if isinstance(user_data, dict) and "stationThreadId" in user_data:
                    state.stationThreadId = user_data["stationThreadId"]
        except (json.JSONDecodeError, KeyError):
            print("Could not extract stationThreadId from user_input")
    
    # 3. Initialize workflow state
    print("🆕 Starting document workflow")
    station_agent.state.set("document_workflow_thread_id", configuration.get("thread_id"))
    station_agent.state.set("workflowStartTime", "2024-01-01T12:00:00Z")
    
    # 4. Check server availability before starting
    server_status = station_agent.server.avail()
    if server_status.get("server") == "busy":
        print("⏳ Server is busy, workflow will wait...")
        return state
    
    # 5. Update shared state with workflow initialization
    station_agent.state.push({
        "workflowStatus": "initialized",
        "workflowType": "document_processing",
        "startTime": "2024-01-01T12:00:00Z"
    })
    
    state.current_node = 1
    return state
```

### 2. Computer Use Node with WindowsAgent

```python
async def computer_automation_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Perform computer use tasks with WindowsAgent."""
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent for coordination (without initial state since we're continuing workflow)
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
    # 2. Check and load server for computer use
    load_result = station_agent.server.load("computer_automation")
    if load_result["status"] == "busy":
        print("Server busy, waiting for availability...")
        return state
    
    # 3. Initialize WindowsAgent for computer tasks
    os_url = configuration.get("os_url")
    windows_agent = WindowsAgent(os_url=os_url)
    
    try:
        # 4. Perform sequence of computer use tasks
        print("Starting computer automation sequence...")
        
        # Click on application
        await asyncio.to_thread(windows_agent.click_element, 85, 60)
        await asyncio.to_thread(windows_agent.pause, 2)
        
        # Navigate to data area
        await asyncio.to_thread(windows_agent.click_element, 294, 98)
        await asyncio.to_thread(windows_agent.pause, 2)
        
        # Click on data table
        await asyncio.to_thread(windows_agent.click_element, 324, 531)
        await asyncio.to_thread(windows_agent.pause, 2)
        
        # Take screenshot of the result
        screenshot_result = await asyncio.to_thread(
            windows_agent.screenshot_cropped, 
            [10, 200, 1000, 450]  # [x, y, width, height]
        )
        
        # 5. Store screenshot URL
        if isinstance(screenshot_result, dict) and "url" in screenshot_result:
            state.screenshot_url = screenshot_result["url"]
        else:
            state.screenshot_url = screenshot_result
            
        print(f"Screenshot captured: {state.screenshot_url}")
        
        # 6. Update shared state with progress
        station_agent.state.push({
            "computerTasksCompleted": True,
            "screenshotUrl": state.screenshot_url,
            "lastCompletedNode": state.current_node
        })
        
    except Exception as e:
        print(f"Computer automation error: {e}")
        # Continue workflow even on errors
        
    finally:
        # 7. Always unload server when done
        station_agent.server.unload()
        print("Computer automation server unloaded")
    
    state.current_node = 5
    return state
```

### 3. Data Processing Node

```python
async def data_processing_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Process screenshot data and extract information."""
    configuration = config["configurable"]
    
    if not state.screenshot_url:
        print("No screenshot available for processing")
        state.current_node = 8
        return state
    
    # 1. Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
    try:
        # 2. Process image with AWS Textract (simplified example)
        print(f"Processing screenshot: {state.screenshot_url}")
        
        # Extract table data (implement your textract logic here)
        # This would typically involve downloading the image and processing with AWS
        extracted_data = await extract_table_data(state.screenshot_url, configuration)
        state.table_csv = extracted_data
        
        # 3. Process CSV data to extract borrower names
        borrower_names = await process_csv_data(state.table_csv, configuration)
        state.borrower_names = borrower_names
        
        print(f"Extracted {len(borrower_names)} borrower names: {borrower_names}")
        
        # 4. Update shared state with extracted data
        station_agent.state.push({
            "dataProcessingCompleted": True,
            "borrowersFound": len(borrower_names),
            "borrowerNames": borrower_names,
            "lastCompletedNode": state.current_node
        })
        
    except Exception as e:
        print(f"Data processing error: {e}")
        state.borrower_names = []
    
    state.current_node = 8
    return state

async def extract_table_data(screenshot_url: str, config: dict) -> str:
    """Extract table data from screenshot using AWS Textract."""
    # Implement your textract logic here
    # This is a simplified placeholder
    return "borrower_name,document_date\nSmith John,2024-01-01\nJohnson Mary,2024-01-02"

async def process_csv_data(csv_data: str, config: dict) -> List[str]:
    """Process CSV data to extract borrower names."""
    # Implement your CSV processing logic here
    # This is a simplified placeholder
    return ["Smith, John", "Johnson, Mary"]
```

### 4. Human Review Node with HumanAgent

```python
async def send_human_review_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Send task to humans for review using HumanAgent."""
    configuration = config["configurable"]
    
    # 1. Initialize HumanAgent
    hitl_token = configuration.get("hitl_token")
    human_agent = HumanAgent(
        HITL_token=hitl_token,
        HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    # 2. Prepare human review task
    image_urls = [state.screenshot_url] if state.screenshot_url else []
    
    question_text = f"Agent found {len(state.borrower_names)} borrowers with Document Date that should be checked for potential ITP approval:\n\n"
    if state.borrower_names:
        for borrower_name in state.borrower_names:
            question_text += f"- **{borrower_name}**\n"
    else:
        question_text += "- No borrower names extracted.\n"
    
    question_text += "\nDo you approve this decision?"
    
    questions = [{
        "Question": question_text,
        "Choices": ["TRUE", "FALSE"]
    }]
    
    thread_id = configuration.get("thread_id")
    
    # 3. Create state data for HITL system
    state_dict = {
        "user_input": state.user_input,
        "current_node": state.current_node,
        "borrower_names": state.borrower_names,
        "stationThreadId": state.stationThreadId,
        "screenshot_url": state.screenshot_url
    }
    
    try:
        # 4. Send task to human agent
        result = await asyncio.to_thread(
            human_agent.task,
            image_urls=image_urls,
            thread_id=thread_id,
            questions=questions,
            task_type="S1-T1",
            thread_state=state_dict
        )
        
        print(f"Human review task sent successfully for thread: {thread_id}")
        
        # 5. Store pending review info for interrupt
        state.pending_review_info = {
            "screenshot_url": state.screenshot_url,
            "borrower_names": state.borrower_names,
            "instructions": "Please review the extracted names and respond with 'TRUE' to approve or 'FALSE' to decline via the external HITL system.",
            "thread_id_of_task": thread_id
        }
        
    except Exception as e:
        print(f"Error sending human review task: {e}")
        # Set default state for error handling
        state.pending_review_info = None
    
    state.current_node = 10.5
    return state
```

### 5. Wait for Human Response Node

```python
async def wait_for_human_response_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Wait for human response via LangGraph interrupt."""
    from langgraph.types import interrupt
    
    if state.pending_review_info is None:
        print("No pending review info available")
        state.human_review_decision = "ERROR_NO_REVIEW_INFO"
        state.current_node = 11
        return state
    
    # Interrupt and wait for human decision
    print(f"Interrupting graph for human input: {state.pending_review_info}")
    human_decision = interrupt(state.pending_review_info)
    
    # Process human decision
    if isinstance(human_decision, str) and human_decision in ["TRUE", "FALSE"]:
        state.human_review_decision = human_decision
        print(f"Human decision received: {human_decision}")
    else:
        print(f"Unexpected human decision: {human_decision}, defaulting to FALSE")
        state.human_review_decision = "FALSE"
    
    # Clear pending review info
    state.pending_review_info = None
    state.current_node = 11
    return state
```

### 6. Final Reporting Node

```python
async def final_reporting_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Report final results to human operators and update shared state."""
    configuration = config["configurable"]
    
    # 1. Initialize agents
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
    hitl_token = configuration.get("hitl_token")
    human_agent = HumanAgent(
        HITL_token=hitl_token,
        HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    # 2. Determine final status
    if state.human_review_decision == "TRUE":
        state.status = "HumanApproved"
        state.reason_code = "HumanReviewApproved"
        status_message = "Workflow completed successfully - human approved"
    else:
        state.status = "HumanRejected"
        state.reason_code = "HumanReviewRejected"
        status_message = "Workflow completed but passed - human did not approve"
    
    print(f"Final status: {state.status}")
    
    # 3. Update shared state with final results
    final_state_data = {
        "workflowCompleted": True,
        "finalStatus": state.status,
        "reasonCode": state.reason_code,
        "humanDecision": state.human_review_decision,
        "borrowersProcessed": len(state.borrower_names),
        "completionTime": "2024-01-01T12:00:00Z"
    }
    
    station_agent.state.push(final_state_data)
    
    # 4. Prepare final report for human operators
    thread_id = configuration.get("thread_id")
    
    state_dict = {
        "user_input": state.user_input,
        "current_node": state.current_node,
        "screenshot_url": state.screenshot_url,
        "borrower_names": state.borrower_names,
        "human_review_decision": state.human_review_decision,
        "status": state.status,
        "reason_code": state.reason_code,
        "stationThreadId": state.stationThreadId
    }
    
    try:
        # 5. Send final report to human operators
        result = await asyncio.to_thread(
            human_agent.reporting,
            thread_id=thread_id,
            report_type="S1-R1",
            thread_state=state_dict
        )
        
        print(f"Final report sent to human operators: {result}")
        
    except Exception as e:
        print(f"Error sending final report: {e}")
    
    state.current_node = 12
    return state
```

---

## Real-World Example: Document Processing

Here's a complete LangGraph workflow definition using all three agents:

```python
from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt

def create_document_processing_workflow() -> StateGraph:
    """Create a complete document processing workflow with all three agents."""
    
    workflow = StateGraph(WorkflowState)
    
    # Add all nodes
    workflow.add_node("start", workflow_start_node)
    workflow.add_node("computer_automation", computer_automation_node)
    workflow.add_node("data_processing", data_processing_node)
    workflow.add_node("send_human_review", send_human_review_node)
    workflow.add_node("wait_human_response", wait_for_human_response_node)
    workflow.add_node("final_reporting", final_reporting_node)
    
    # Define workflow edges
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "computer_automation")
    workflow.add_edge("computer_automation", "data_processing")
    workflow.add_edge("data_processing", "send_human_review")
    workflow.add_edge("send_human_review", "wait_human_response")
    workflow.add_edge("wait_human_response", "final_reporting")
    workflow.add_edge("final_reporting", END)
    
    return workflow.compile()

# Usage
workflow = create_document_processing_workflow()

# Run the workflow
initial_state = WorkflowState(
    user_input={"stationThreadId": "doc-workflow-123"},
    current_node=0
)

config = RunnableConfig({
    "configurable": {
        "thread_id": "main-thread-456",
        "shared_state_token": "your-token",
        "hitl_token": "your-hitl-token",
        "os_url": "https://your-server.ngrok.app"
    }
})

final_state = await workflow.ainvoke(initial_state, config)
```

---

## Advanced Patterns

### 1. Multi-Instance Coordination

```python
async def coordinated_processing_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Coordinate multiple workflow instances using StationAgent."""
    configuration = config["configurable"]
    
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
    # Register this workflow instance
    instance_id = state.stationThreadId
    station_agent.state.set(f"workflow_instance_{instance_id}", {
        "status": "active",
        "current_node": state.current_node,
        "thread_id": configuration.get("thread_id"),
        "last_heartbeat": "2024-01-01T12:00:00Z"
    })
    
    # Check for other active instances
    state = station_agent.state.sync_all(state)
    active_instances = []
    
    for key, value in state.sharedState.items():
        if key.startswith("workflow_instance_") and isinstance(value, dict):
            if value.get("status") == "active":
                active_instances.append(value)
    
    print(f"Found {len(active_instances)} active workflow instances")
    
    # Coordinate based on instance count
    if len(active_instances) > 3:
        print("Too many active instances, implementing queue...")
        station_agent.state.set("coordinationMode", "queued")
        state.current_node = 0  # Wait
    else:
        station_agent.state.set("coordinationMode", "active")
        state.current_node = 5  # Proceed
    
    return state
```

### 2. Error Recovery with All Agents

```python
async def error_recovery_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Comprehensive error recovery using all three agents."""
    configuration = config["configurable"]
    
    try:
        # 1. Test StationAgent connection
        station_agent = StationAgent(
            station_thread_id=state.stationThreadId,
            graph_thread_id=configuration.get("thread_id"),
            token=configuration.get("shared_state_token")
        )
        
        connection = station_agent.validate_connection()
        if not connection["connected"]:
            raise Exception(f"StationAgent connection failed: {connection.get('error')}")
        
        # 2. Test WindowsAgent server
        windows_agent = WindowsAgent(os_url=configuration.get("os_url"))
        # Test with a simple pause
        await asyncio.to_thread(windows_agent.pause, 1)
        
        # 3. Test HumanAgent service
        human_agent = HumanAgent(
            HITL_token=configuration.get("hitl_token"),
            HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
        )
        
        # All agents working - continue normal operation
        state.status = "AllAgentsOperational"
        print("✅ All agents operational, continuing workflow")
        
    except Exception as e:
        print(f"⚠️ Agent error detected: {e}")
        
        # Implement graceful degradation
        if "StationAgent" in str(e):
            print("StationAgent unavailable - continuing with local state only")
            state.status = "LocalStateOnly"
        elif "WindowsAgent" in str(e):
            print("WindowsAgent unavailable - skipping computer use tasks")
            state.status = "NoComputerUse"
        elif "HumanAgent" in str(e):
            print("HumanAgent unavailable - using default decisions")
            state.status = "AutoApproval"
            state.human_review_decision = "TRUE"  # Default approval
        
        # Log error to shared state if StationAgent is available
        try:
            station_agent.state.set("lastError", {
                "error": str(e),
                "node": state.current_node,
                "timestamp": "2024-01-01T12:00:00Z",
                "recovery_action": state.status
            })
        except:
            pass  # Fail silently if we can't log
    
    state.current_node += 1
    return state
```

---

## Configuration and Error Handling

### Environment Variables Setup

```bash
# StationAgent
export SHARED_STATE_URL="https://your-api.amazonaws.com/prod"
export SHARED_STATE_TOKEN="your-station-token"

# HumanAgent
export HITL_TOKEN="your-hitl-token"

# WindowsAgent
# os_url configured per workflow in LangGraph config

# Additional services
export OPENAI_API_KEY="your-openai-key"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_REGION="us-east-1"
```

### Comprehensive Error Handling Pattern

```python
async def robust_multi_agent_node(state: WorkflowState, config: RunnableConfig) -> WorkflowState:
    """Robust node with comprehensive error handling for all agents."""
    configuration = config["configurable"]
    
    # Initialize all agents with error handling
    agents = {}
    
    try:
        agents["station"] = StationAgent(
            station_thread_id=state.stationThreadId,
            graph_thread_id=configuration.get("thread_id"),
            token=configuration.get("shared_state_token")
        )
    except Exception as e:
        print(f"StationAgent initialization failed: {e}")
        agents["station"] = None
    
    try:
        agents["windows"] = WindowsAgent(os_url=configuration.get("os_url"))
    except Exception as e:
        print(f"WindowsAgent initialization failed: {e}")
        agents["windows"] = None
    
    try:
        agents["human"] = HumanAgent(
            HITL_token=configuration.get("hitl_token"),
            HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
        )
    except Exception as e:
        print(f"HumanAgent initialization failed: {e}")
        agents["human"] = None
    
    # Execute workflow with available agents
    if agents["station"]:
        try:
            state = agents["station"].state.sync_all(state)
        except Exception as e:
            print(f"StationAgent sync failed: {e}")
    
    if agents["windows"]:
        try:
            # Server coordination
            if agents["station"]:
                load_result = agents["station"].server.load("task")
                if load_result["status"] == "loaded":
                    # Perform computer tasks
                    await asyncio.to_thread(agents["windows"].pause, 1)
                    agents["station"].server.unload()
        except Exception as e:
            print(f"WindowsAgent task failed: {e}")
    
    if agents["human"]:
        try:
            # Send human task if needed
            if state.borrower_names:
                questions = [{"Question": "Approve?", "Choices": ["YES", "NO"]}]
                await asyncio.to_thread(
                    agents["human"].task,
                    image_urls=[],
                    thread_id=configuration.get("thread_id"),
                    questions=questions,
                    task_type="S1-T1",
                    thread_state={"status": "review_needed"}
                )
        except Exception as e:
            print(f"HumanAgent task failed: {e}")
    
    # Always continue workflow
    state.current_node += 1
    return state
```

This comprehensive guide provides everything needed to integrate all three CuteAgent agents in production LangGraph workflows with proper error handling, coordination, and human oversight. 