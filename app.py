import streamlit as st
import openai
from dotenv import load_dotenv
import os
import json
from typing import List, Dict

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, DISCLAIMER
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
    Surgically detect if user is confirming APPOINTMENT BOOKING (not just general guidance).
    Must check full context to see what was actually offered.
    """
    if not client:
        return False
    
    # Simple keyword check first (fast)
    message_lower = user_message.lower()
    confirmation_keywords = ["yes", "yeah", "yep", "sure", "okay", "ok", "sounds good", 
                            "that works", "let's do it", "let's do that", "i'd like that",
                            "please", "that would be great", "sounds great"]
    
    if not any(keyword in message_lower for keyword in confirmation_keywords):
        return False
    
    # Use LLM to verify it's actually a BOOKING confirmation, not general guidance confirmation
    context_text = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')[:200]}"
        for msg in conversation_context[-4:]  # Last 4 messages for context
    ])
    
    check_prompt = f"""You are detecting if a user is confirming they want to BOOK/SCHEDULE an appointment (not just get guidance).

Recent conversation:
{context_text}

User's latest message: "{user_message}"

CRITICAL: Only return "yes" if the assistant explicitly offered to HELP BOOK/SCHEDULE an appointment AND the user is confirming that booking request.

Return "no" if:
- The assistant only offered guidance/preparation help (even if it mentioned appointments)
- The assistant only suggested seeing a doctor (without offering to book)
- The user is just confirming they want more information/guidance
- The user is confirming something else entirely

Respond with only "yes" or "no"."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a confirmation detector for appointment booking. You must be strict - only return 'yes' for explicit booking confirmations. Respond with only 'yes' or 'no'."},
                {"role": "user", "content": check_prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        result = response.choices[0].message.content.strip().lower()
        return result == "yes"
    except:
        # Fallback: be conservative - don't trigger if we can't verify
        return False

def detect_appointment_offer_in_response(response: str) -> bool:
    """
    Detect if chatbot's response offered to help with appointment BOOKING (not just appointment-related guidance).
    This should only trigger on explicit booking offers, not general appointment discussion.
    """
    response_lower = response.lower()
    
    # Only trigger on explicit booking/scheduling offers
    # Must have both "book"/"schedule" AND "appointment" in close context
    explicit_booking_phrases = [
        "help you book",
        "help with booking",
        "help booking",
        "book an appointment",
        "schedule an appointment",
        "make an appointment",
        "book your appointment",
        "schedule your appointment",
        "can book",
        "can schedule"
    ]
    
    # Check if any explicit booking phrase exists
    has_booking_offer = any(phrase in response_lower for phrase in explicit_booking_phrases)
    
    # Exclude if it's just about preparation/guidance for appointments (not booking)
    is_preparation_only = any(phrase in response_lower for phrase in [
        "prepare for",
        "preparation",
        "guidance on",
        "what to do",
        "how to prepare"
    ]) and not has_booking_offer
    
    return has_booking_offer and not is_preparation_only

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
                    
                    # Get natural acknowledgment for confirmation
                    with st.chat_message("assistant"):
                        # Prepare messages for acknowledgment - explicitly state that we WILL book the appointment
                        acknowledgment_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nIMPORTANT: The user has confirmed they want to book an appointment, and you (WellNavigator) WILL be booking it for them through the appointment booking system. Acknowledge their confirmation warmly and confirm that you're helping them book it (1-2 sentences max). Do NOT say you cannot book - you ARE booking it. Be conversational and brief."}]
                        for msg in st.session_state.messages:
                            acknowledgment_messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                        
                        try:
                            ack_response = client.chat.completions.create(
                                model=model,
                                messages=acknowledgment_messages,
                                temperature=temperature,
                                max_tokens=150
                            )
                            acknowledgment = ack_response.choices[0].message.content.strip()
                            st.markdown(acknowledgment)
                            
                            # Execute the workflow
                            workflow_result = workflow.execute({"intent": "confirmed"})
                            
                            # Combine acknowledgment + workflow result
                            if workflow_result.get("status") == "completed":
                                workflow_message = workflow_result.get("message", "Workflow completed.")
                                full_response = f"{acknowledgment}\n\n{workflow_message}"
                                
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": full_response
                                })
                        except Exception as e:
                            # Fallback: just execute workflow
                            workflow_result = workflow.execute({"intent": "confirmed"})
                            if workflow_result.get("status") == "completed":
                                workflow_message = workflow_result.get("message", "Workflow completed.")
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": workflow_message
                                })
                    
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
                    
                    # First, get a natural conversational acknowledgment from the LLM
                    with st.chat_message("assistant"):
                        # Prepare messages for acknowledgment - explicitly state that we WILL book the appointment
                        acknowledgment_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nIMPORTANT: The user has requested to book an appointment, and you (WellNavigator) WILL be booking it for them through the appointment booking system. Acknowledge their request warmly and confirm that you're helping them book it (1-2 sentences max). Do NOT say you cannot book - you ARE booking it. Be conversational and brief."}]
                        for msg in st.session_state.messages:
                            acknowledgment_messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                        
                        # Get brief acknowledgment
                        try:
                            ack_response = client.chat.completions.create(
                                model=model,
                                messages=acknowledgment_messages,
                                temperature=temperature,
                                max_tokens=150  # Keep it brief but natural
                            )
                            acknowledgment = ack_response.choices[0].message.content.strip()
                            
                            # Display acknowledgment
                            st.markdown(acknowledgment)
                            
                            # Now execute the workflow seamlessly
                            workflow_result = workflow.execute(trigger_info.get("context", {}))
                            
                            # Combine acknowledgment + workflow result for chat history
                            if workflow_result.get("status") == "completed":
                                workflow_message = workflow_result.get("message", "Workflow completed.")
                                full_response = f"{acknowledgment}\n\n{workflow_message}"
                                
                                # Add to chat history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": full_response
                                })
                        except Exception as e:
                            # Fallback: just execute workflow if acknowledgment fails
                            workflow_result = workflow.execute(trigger_info.get("context", {}))
                            if workflow_result.get("status") == "completed":
                                workflow_message = workflow_result.get("message", "Workflow completed.")
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": workflow_message
                                })
                    
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
