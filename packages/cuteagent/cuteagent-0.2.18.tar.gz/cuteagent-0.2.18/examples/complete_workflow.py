#!/usr/bin/env python3
"""
Complete Multi-Agent Workflow Example

This example demonstrates how to use all three CuteAgent agents:
- StationAgent: Shared state management and coordination
- WindowsAgent: Computer use automation  
- HumanAgent: Human-in-the-loop task management

This creates a complete document processing workflow where:
1. AI takes screenshots and extracts data
2. Humans review and approve decisions
3. Shared state coordinates everything across multiple workflow instances
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt

from cuteagent import StationAgent, WindowsAgent, HumanAgent


@dataclass
class DocumentWorkflowState:
    """Complete state class supporting all three CuteAgent agents."""
    
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


async def workflow_start_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Initialize workflow with StationAgent coordination."""
    print("🚀 Starting document processing workflow...")
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent for shared state management
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId or f"doc-workflow-{uuid.uuid4().hex[:8]}",
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
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
    print("🆕 Starting new document workflow")
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


async def computer_automation_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Perform computer use tasks with WindowsAgent."""
    print("🖥️ Starting computer automation...")
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent for coordination
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
    if not os_url:
        print("❌ No os_url configured for WindowsAgent")
        state.current_node = 5
        return state
    
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


async def data_processing_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Process screenshot data and extract information."""
    print("📊 Processing extracted data...")
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
        # 2. Process image with data extraction (simplified example)
        print(f"Processing screenshot: {state.screenshot_url}")
        
        # In a real implementation, you would:
        # - Download the image from the URL
        # - Use AWS Textract, OCR, or other image processing
        # - Extract structured data like tables or text
        
        # For this example, we'll simulate extracted data
        extracted_data = await simulate_table_extraction(state.screenshot_url, configuration)
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


async def send_human_review_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Send task to humans for review using HumanAgent."""
    print("👥 Sending task for human review...")
    configuration = config["configurable"]
    
    # 1. Initialize HumanAgent
    hitl_token = configuration.get("hitl_token")
    if not hitl_token:
        print("❌ No HITL token configured, skipping human review")
        state.human_review_decision = "AUTO_APPROVED"
        state.current_node = 11
        return state
    
    human_agent = HumanAgent(
        HITL_token=hitl_token,
        HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    # 2. Prepare human review task
    image_urls = [state.screenshot_url] if state.screenshot_url else []
    
    question_text = f"🤖 Document Processing Agent found {len(state.borrower_names)} borrowers that should be checked:\n\n"
    if state.borrower_names:
        for borrower_name in state.borrower_names:
            question_text += f"• **{borrower_name}**\n"
    else:
        question_text += "• No borrower names extracted.\n"
    
    question_text += "\n**Do you approve this decision?**"
    
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
        
        print(f"✅ Human review task sent successfully for thread: {thread_id}")
        
        # 5. Store pending review info for interrupt
        state.pending_review_info = {
            "screenshot_url": state.screenshot_url,
            "borrower_names": state.borrower_names,
            "instructions": "Please review the extracted names and respond with 'TRUE' to approve or 'FALSE' to decline via the external HITL system.",
            "thread_id_of_task": thread_id
        }
        
    except Exception as e:
        print(f"❌ Error sending human review task: {e}")
        # Set default state for error handling
        state.pending_review_info = None
        state.human_review_decision = "ERROR_SENDING_TASK"
    
    state.current_node = 10.5
    return state


async def wait_for_human_response_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Wait for human response via LangGraph interrupt."""
    print("⏳ Waiting for human decision...")
    
    if state.pending_review_info is None:
        print("No pending review info available")
        state.human_review_decision = "ERROR_NO_REVIEW_INFO"
        state.current_node = 11
        return state
    
    # Interrupt and wait for human decision
    print(f"🛑 Interrupting graph for human input: {state.pending_review_info}")
    human_decision = interrupt(state.pending_review_info)
    
    # Process human decision
    if isinstance(human_decision, str) and human_decision in ["TRUE", "FALSE"]:
        state.human_review_decision = human_decision
        print(f"✅ Human decision received: {human_decision}")
    else:
        print(f"⚠️ Unexpected human decision: {human_decision}, defaulting to FALSE")
        state.human_review_decision = "FALSE"
    
    # Clear pending review info
    state.pending_review_info = None
    state.current_node = 11
    return state


async def final_reporting_node(state: DocumentWorkflowState, config: RunnableConfig) -> DocumentWorkflowState:
    """Report final results to human operators and update shared state."""
    print("📋 Generating final report...")
    configuration = config["configurable"]
    
    # 1. Initialize StationAgent
    station_agent = StationAgent(
        station_thread_id=state.stationThreadId,
        graph_thread_id=configuration.get("thread_id"),
        token=configuration.get("shared_state_token")
    )
    
    # 2. Determine final status
    if state.human_review_decision == "TRUE":
        state.status = "HumanApproved"
        state.reason_code = "HumanReviewApproved"
        status_message = "✅ Workflow completed successfully - human approved"
    else:
        state.status = "HumanRejected"
        state.reason_code = "HumanReviewRejected"
        status_message = "❌ Workflow completed but rejected - human did not approve"
    
    print(status_message)
    
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
    
    # 4. Send final report to human operators if HumanAgent is available
    hitl_token = configuration.get("hitl_token")
    if hitl_token:
        try:
            human_agent = HumanAgent(
                HITL_token=hitl_token,
                HITL_url="https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
            )
            
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
            
            # Send final report to human operators
            result = await asyncio.to_thread(
                human_agent.reporting,
                thread_id=thread_id,
                report_type="S1-R1",
                thread_state=state_dict
            )
            
            print(f"📤 Final report sent to human operators: {result}")
            
        except Exception as e:
            print(f"⚠️ Error sending final report: {e}")
    
    state.current_node = 12
    return state


# Helper functions for data processing simulation
async def simulate_table_extraction(screenshot_url: str, config: dict) -> str:
    """Simulate table data extraction from screenshot."""
    # In a real implementation, this would:
    # 1. Download the image from screenshot_url
    # 2. Use AWS Textract or OCR to extract table data
    # 3. Convert to CSV format
    
    print("🔍 Simulating table extraction...")
    await asyncio.sleep(1)  # Simulate processing time
    
    # Return simulated CSV data
    return """borrower_name,document_date,status
Smith, John,2024-01-15,Active
Johnson, Mary,2024-01-20,Active
Williams, Robert,2024-01-18,Pending"""


async def process_csv_data(csv_data: str, config: dict) -> List[str]:
    """Process CSV data to extract borrower names."""
    if not csv_data:
        return []
    
    borrower_names = []
    lines = csv_data.strip().split('\n')[1:]  # Skip header
    
    for line in lines:
        parts = line.split(',')
        if len(parts) >= 1:
            borrower_name = parts[0].strip()
            if borrower_name:
                borrower_names.append(borrower_name)
    
    return borrower_names


def create_document_processing_workflow() -> StateGraph:
    """Create a complete document processing workflow with all three agents."""
    
    workflow = StateGraph(DocumentWorkflowState)
    
    # Add all workflow nodes
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


async def main():
    """Example usage of the complete workflow."""
    
    # Create the workflow
    workflow = create_document_processing_workflow()
    
    # Initial state
    initial_state = DocumentWorkflowState(
        user_input={"stationThreadId": "example-doc-workflow-123"},
        current_node=0
    )
    
    # Configuration
    config = RunnableConfig({
        "configurable": {
            "thread_id": f"main-thread-{uuid.uuid4().hex[:8]}",
            "shared_state_token": "dev-token-123",  # Your actual token
            "hitl_token": "your-hitl-token",        # Your HITL token
            "os_url": "https://your-server.ngrok.app"  # Your Windows server URL
        }
    })
    
    try:
        print("🚀 Starting complete multi-agent workflow...")
        final_state = await workflow.ainvoke(initial_state, config)
        
        print(f"\n✅ Workflow completed!")
        print(f"Final status: {final_state.status}")
        print(f"Borrowers found: {len(final_state.borrower_names)}")
        print(f"Human decision: {final_state.human_review_decision}")
        print(f"Station Thread ID: {final_state.stationThreadId}")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main()) 