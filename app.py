import streamlit as st
import openai
from dotenv import load_dotenv
import os
import json
from typing import List, Dict

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, DISCLAIMER
from tools import TOOLS, AppointmentTool, ResultsTool, ResourcesTool, CaregiverTool
from workflows import WORKFLOW_REGISTRY, get_workflow

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="WellNavigator - Patient Advocacy Chatbot",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    client = None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.welcome_shown = False
    st.session_state.conversation_context = {}
    st.session_state.appointment_offered = False
    st.session_state.offered_workflow_id = None

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #10B981 0%, #059669 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
    }
    .disclaimer-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; color: white;">💚 WellNavigator</h1>
        <p style="margin:0.5rem 0 0 0; color: white; font-size: 1.1rem;">Your empathetic healthcare navigation companion</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    if not client:
        st.error("⚠️ OpenAI API key not configured.\n\nPlease set OPENAI_API_KEY in your .env file.")
    else:
        st.success("✅ OpenAI API configured")
    
    st.markdown("---")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="Choose the OpenAI model to use"
    )
    
    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make responses more creative, lower values more focused"
    )
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.welcome_shown = False
        st.session_state.conversation_context = {}
        st.session_state.appointment_offered = False
        st.session_state.offered_workflow_id = None
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Tip:** Share your situation freely. I'll ask questions if I need more context to help you best.")

def prepare_messages_for_llm():
    """Prepare messages with system prompt for OpenAI API"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    for msg in st.session_state.messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return messages

def detect_track_and_tool(user_message: str, conversation_history: list) -> dict:
    """
    Use LLM to detect which track/tool would be most helpful.
    Returns a dictionary with track info and suggested tool.
    """
    if not client:
        return None
    
    detection_prompt = f"""Based on this conversation, determine what kind of help the user needs most:

User's latest message: "{user_message}"

Conversation context: {json.dumps([m["content"][:200] for m in conversation_history[-3:]])}

Determine which track fits best:
1. "appointment" - User needs help preparing for or booking appointments
2. "results" - User needs help understanding test results or medical information
3. "resources" - User needs to find resources, support groups, or services
4. "caregiver" - User needs caregiver support or advice
5. "general" - General health navigation or unclear

Respond ONLY with valid JSON in this exact format:
{{
    "track": "appointment|results|resources|caregiver|general",
    "confidence": "high|medium|low",
    "reasoning": "brief explanation"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a healthcare intent classifier. Respond only with valid JSON."},
                {"role": "user", "content": detection_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return None

def detect_confirmation(user_message: str, conversation_context: List[Dict[str, str]]) -> bool:
    """
    Surgically detect if user is confirming a previously offered workflow.
    Returns True if user's message indicates confirmation/agreement.
    """
    if not client:
        return False
    
    # Simple keyword check first (fast)
    message_lower = user_message.lower()
    confirmation_keywords = ["yes", "yeah", "yep", "sure", "okay", "ok", "sounds good", 
                            "that works", "let's do it", "let's do that", "i'd like that",
                            "please", "that would be great", "sounds great"]
    
    if any(keyword in message_lower for keyword in confirmation_keywords):
        # Use LLM to verify it's actually a confirmation in context (surgical check)
        check_prompt = f"""User message: "{user_message}"

Previous conversation context suggests the assistant just offered to help with something (like booking an appointment).

Does the user's message indicate they are confirming/agreeing to proceed? 
Respond with only "yes" or "no"."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a confirmation detector. Respond with only 'yes' or 'no'."},
                    {"role": "user", "content": check_prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip().lower()
            return result == "yes"
        except:
            # Fallback to keyword match if LLM fails
            return True
    
    return False

def detect_appointment_offer_in_response(response: str) -> bool:
    """
    Detect if chatbot's response offered to help with appointment booking.
    This is a simple check to track when we should listen for confirmations.
    """
    response_lower = response.lower()
    # Look for patterns like "help booking", "book an appointment", "schedule", etc.
    offer_patterns = [
        "book" in response_lower and "appointment" in response_lower,
        "schedule" in response_lower and "appointment" in response_lower,
        "help you book" in response_lower,
        "help with booking" in response_lower,
        ("appointment" in response_lower and ("help" in response_lower or "can" in response_lower))
    ]
    return any(offer_patterns)

def format_tool_result(tool_result: dict) -> str:
    """Format tool result into a readable response"""
    data = tool_result.get("data", {})
    tool_type = tool_result.get("tool", "")
    
    if tool_type == "appointment_preparation":
        result_text = f"## {data.get('title', 'Appointment Preparation Guide')}\n\n"
        result_text += "**Checklist:**\n"
        for item in data.get("checklist", []):
            result_text += f"- {item}\n"
        result_text += f"\n💡 **Tip:** {data.get('tips', '')}\n"
        return result_text
    
    elif tool_type == "results_explanation":
        result_text = f"## {data.get('title', 'Understanding Your Results')}\n\n"
        if "common_components" in data:
            result_text += "**Common components:**\n"
            for item in data["common_components"]:
                result_text += f"- {item}\n"
            result_text += "\n"
        result_text += f"{data.get('general_advice', '')}\n\n"
        result_text += f"**Questions to ask:** {data.get('when_to_ask', '')}\n"
        return result_text
    
    elif tool_type == "resource_finder":
        result_text = f"## {data.get('title', 'Resources')}\n\n"
        for resource in data.get("resources", []):
            result_text += f"- {resource}\n"
        result_text += f"\n💡 **Tip:** {data.get('tips', '')}\n"
        return result_text
    
    elif tool_type == "caregiver_support":
        result_text = f"## {data.get('title', 'Caregiver Support')}\n\n"
        for advice in data.get("advice", []):
            result_text += f"- {advice}\n"
        result_text += f"\n**Resources:** {data.get('resources', '')}\n"
        return result_text
    
    else:
        return tool_result.get("message", "I've gathered some information for you.")

# Show welcome message if not shown yet
if not st.session_state.welcome_shown and len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": WELCOME_MESSAGE
    })
    st.session_state.welcome_shown = True

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Tell me what's going on—how can I support you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check for workflow triggers first
    workflow_triggered = False
    workflow_result = None
    
    if client:
        # FIRST: Check if a workflow was previously offered and user is confirming
        if st.session_state.get("appointment_offered") and st.session_state.get("offered_workflow_id"):
            if detect_confirmation(prompt, st.session_state.messages[-3:]):
                # User confirmed - trigger the offered workflow
                workflow_id = st.session_state.offered_workflow_id
                workflow = get_workflow(workflow_id)
                
                if workflow:
                    workflow_triggered = True
                    
                    # Execute the workflow
                    with st.chat_message("assistant"):
                        workflow_result = workflow.execute({"intent": "confirmed"})
                        
                        # Add workflow result message to chat
                        if workflow_result.get("status") == "completed":
                            workflow_message = workflow_result.get("message", "Workflow completed.")
                            
                            # Display workflow result in chat
                            st.markdown(workflow_message)
                            
                            # Add to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": workflow_message
                            })
                            
                            # Note: Re-engagement is now handled naturally by the LLM when appropriate
                    
                    # Clear the offered state
                    st.session_state.appointment_offered = False
                    st.session_state.offered_workflow_id = None
        
        # SECOND: Check for direct workflow triggers (explicit user requests)
        if not workflow_triggered:
            for workflow_id, workflow in WORKFLOW_REGISTRY.items():
                trigger_info = workflow.should_trigger(
                    user_message=prompt,
                    conversation_context=st.session_state.messages[-5:]  # Last 5 messages for context
                )
                
                # Only trigger if confidence is high and workflow says it should trigger
                if trigger_info.get("should_trigger") and trigger_info.get("confidence") == "high":
                    workflow_triggered = True
                    
                    # Execute the workflow
                    with st.chat_message("assistant"):
                        workflow_result = workflow.execute(trigger_info.get("context", {}))
                        
                        # Add workflow result message to chat
                        if workflow_result.get("status") == "completed":
                            workflow_message = workflow_result.get("message", "Workflow completed.")
                            
                            # Display workflow result in chat
                            st.markdown(workflow_message)
                            
                            # Add to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": workflow_message
                            })
                            
                            # Note: Re-engagement is now handled naturally by the LLM when appropriate
                    
                    break  # Only one workflow at a time
    
    # If no workflow was triggered, proceed with normal chat
    if not workflow_triggered:
        # Generate assistant response
        if client:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Detect track/tool if we have enough context
                        track_info = None
                        if len(st.session_state.messages) >= 2:
                            track_info = detect_track_and_tool(
                                prompt,
                                st.session_state.messages
                            )
                        
                        # Prepare messages for API (includes system prompt)
                        messages_for_api = prepare_messages_for_llm()
                        
                        # Stream response
                        stream = client.chat.completions.create(
                            model=model,
                            messages=messages_for_api,
                            temperature=temperature,
                            stream=True
                        )
                        
                        # Collect streamed response
                        response_parts = []
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                response_parts.append(content)
                                full_response = "".join(response_parts)
                                response_placeholder.markdown(full_response + "▌")
                        
                        # Finalize the response
                        response = full_response
                        
                        # Track if chatbot offered appointment booking (for conversational workflow triggering)
                        if detect_appointment_offer_in_response(response):
                            st.session_state.appointment_offered = True
                            st.session_state.offered_workflow_id = "appointment_booking"
                        
                        # Note: Automatic tool invocation removed - tools should only be invoked via workflows
                        # or when explicitly requested by the user. The LLM handles conversational support naturally.
                        # Re-engagement is now handled naturally by the LLM when appropriate.
                        
                        # Update placeholder with final response (without cursor)
                        response_placeholder.markdown(response)
                        
                        # Add assistant response to chat history AFTER finalizing
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    except Exception as e:
                        error_message = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again, or rephrase your question."
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
        else:
            with st.chat_message("assistant"):
                st.error("OpenAI API client not available. Please configure your API key in the .env file.")

# Footer with disclaimer
st.markdown("---")
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.caption("💚 WellNavigator - Making healthcare less overwhelming, one conversation at a time.")
with footer_col2:
    st.caption(f"<span style='font-size: 0.85em; color: #666;'>{DISCLAIMER}</span>", unsafe_allow_html=True)
