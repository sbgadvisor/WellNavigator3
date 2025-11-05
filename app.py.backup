import streamlit as st
import openai
from dotenv import load_dotenv
import os
import json

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, DISCLAIMER
from tools import TOOLS, AppointmentTool, ResultsTool, ResourcesTool, CaregiverTool

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

# Header with disclaimer
st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; color: white;">💚 WellNavigator</h1>
        <p style="margin:0.5rem 0 0 0; color: white; font-size: 1.1rem;">Your empathetic healthcare navigation companion</p>
    </div>
    <div class="disclaimer-box">
        <strong>⚠️ Important:</strong> I'm here to help guide and support you, but I'm not a doctor. 
        Always consult with healthcare professionals for medical advice.
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
                    
                    # If track is detected with high confidence and user seems to want action,
                    # we can enhance the prompt
                    enhanced_prompt = prompt
                    if track_info and track_info.get("confidence") == "high":
                        track = track_info.get("track")
                        if track in ["appointment", "results", "resources", "caregiver"]:
                            # Add context about available tools
                            enhanced_prompt = f"{prompt}\n\n[Context: The user seems to need help with {track}. If appropriate, suggest using relevant tools or guidance.]"
                    
                    # Update the last message with enhanced prompt
                    messages_for_api[-1]["content"] = enhanced_prompt
                    
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
                    
                    response_placeholder.markdown(full_response)
                    response = full_response
                    
                    # Check if user wants to use a tool (simple keyword detection + LLM reasoning)
                    # This is a simplified version - in production, you'd use function calling
                    use_tool = False
                    tool_result = None
                    
                    # Check if response suggests using a tool or if track detection suggests it
                    if track_info and track_info.get("confidence") in ["high", "medium"]:
                        track = track_info.get("track")
                        lower_response = response.lower()
                        
                        # Simple heuristics - in production, use OpenAI function calling
                        if track == "appointment" and any(word in lower_response for word in ["prepar", "checklist", "guide", "appointment"]):
                            tool_result = AppointmentTool.prepare_appointment_guide()
                            use_tool = True
                        elif track == "results" and any(word in lower_response for word in ["result", "test", "explain", "understand"]):
                            tool_result = ResultsTool.explain_results()
                            use_tool = True
                        elif track == "resources" and any(word in lower_response for word in ["resource", "support", "help", "find"]):
                            tool_result = ResourcesTool.find_resources()
                            use_tool = True
                        elif track == "caregiver" and any(word in lower_response for word in ["caregiv", "support", "help"]):
                            tool_result = CaregiverTool.provide_caregiver_guidance()
                            use_tool = True
                    
                    # Append tool result if available
                    if use_tool and tool_result:
                        response += "\n\n" + format_tool_result(tool_result)
                    
                    # Always add re-engagement at the end
                    response += f"\n\n{DISCLAIMER}\n\n"
                    response += "Would you like to talk about anything else—maybe your test results, appointment preparation, or finding additional resources? I'm here to help."
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_message = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again, or rephrase your question."
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
    else:
        with st.chat_message("assistant"):
            st.error("OpenAI API client not available. Please configure your API key in the .env file.")

# Footer
st.markdown("---")
st.caption("💚 WellNavigator - Making healthcare less overwhelming, one conversation at a time.")
