"""
Appointment Booking Workflow
For now, this is a stub that shows a prebooked appointment.
Future implementation will include actual booking steps.
"""

from workflows.base import WorkflowAgent
from typing import Dict, Any, List
import streamlit as st
from datetime import datetime, timedelta
import openai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AppointmentBookingWorkflow(WorkflowAgent):
    """Workflow for booking appointments"""
    
    def __init__(self):
        super().__init__(
            workflow_id="appointment_booking",
            name="Appointment Booking",
            description="Help users book medical appointments",
            triggers=["book appointment", "schedule appointment", "make appointment", 
                     "appointment booking", "need appointment", "want to see doctor"]
        )
        # Initialize OpenAI client for intent detection
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
    
    def should_trigger(self, user_message: str, conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Use LLM to detect if user wants to BOOK an appointment.
        Distinguishes between:
        - Booking/scheduling an appointment (should trigger)
        - Preparing for an appointment (should NOT trigger)
        - Asking about an appointment (should NOT trigger)
        - General appointment discussion (should NOT trigger)
        """
        if not self.client:
            # Fallback to basic keyword check if no API key
            message_lower = user_message.lower()
            if any(phrase in message_lower for phrase in [
                "book an appointment", "book appointment", "schedule an appointment",
                "make an appointment", "i need to book", "want to book",
                "can i book", "how do i book"
            ]):
                return {
                    "should_trigger": True,
                    "confidence": "medium",
                    "reasoning": "Keyword match found (API key not available)",
                    "context": {"intent": "booking"}
                }
            return {
                "should_trigger": False,
                "confidence": "low",
                "reasoning": "No booking intent detected (API key not available)",
                "context": {}
            }
        
        # Use LLM for intelligent intent detection
        conversation_summary = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')[:150]}"
            for msg in conversation_context[-3:]
        ])
        
        detection_prompt = f"""You are an intent classifier for a healthcare chatbot. Determine if the user wants to BOOK/SCHEDULE a new appointment.

User's latest message: "{user_message}"

Recent conversation context:
{conversation_summary}

IMPORTANT: Only return TRUE if the user explicitly wants to BOOK or SCHEDULE a new appointment. 

Pay special attention to phrases like "help me make/book/schedule" - these ARE booking requests and should return TRUE.

Return FALSE if:
- User is asking how to PREPARE for an appointment (already scheduled)
- User is asking ABOUT an appointment (questions, concerns, what to expect)
- User is asking to UNDERSTAND something about an appointment
- User mentions appointments in general without wanting to book
- User is discussing a past or existing appointment

Examples that should return TRUE:
- "I need to book an appointment"
- "Can you schedule me an appointment?"
- "I want to see a doctor"
- "How do I make an appointment?"
- "I'd like to schedule something"
- "Can you help me in making this appointment?"
- "Can you help me make an appointment?"
- "Can you help me book an appointment?"
- "Help me schedule an appointment"
- "I need help making an appointment"
- "Will you help me book this appointment?"
- "Can you help with booking?"
- Any request where user asks for help WITH booking/making/scheduling an appointment

Examples that should return FALSE:
- "I'm not sure how to prepare for that appointment"
- "What should I bring to my appointment?"
- "I have questions about my appointment"
- "What will happen at the appointment?"
- "I'm nervous about my appointment"
- "Can you help me understand my appointment?" (understanding vs booking)
- "Help me prepare for my appointment" (preparation vs booking)

Respond ONLY with valid JSON in this exact format:
{{
    "should_trigger": true or false,
    "confidence": "high" or "medium" or "low",
    "reasoning": "brief explanation of why this is/isn't a booking request"
}}"""

        try:
            # Use gpt-5 for better intent detection
            detection_model = "gpt-5"
            
            # Helper functions for GPT-5 parameter handling
            def get_token_param(model: str, max_tokens: int):
                """Get the correct token parameter based on model"""
                if model and model.startswith("gpt-5"):
                    return {"max_completion_tokens": max_tokens}
                else:
                    return {"max_tokens": max_tokens}
            
            def get_model_params(model: str, temperature: float = 0.7, reasoning_effort: str = "medium"):
                """Get the correct model parameters based on model type"""
                if model and model.startswith("gpt-5"):
                    return {"reasoning_effort": reasoning_effort}
                else:
                    return {"temperature": temperature}
            
            response = self.client.chat.completions.create(
                model=detection_model,
                messages=[
                    {"role": "system", "content": "You are an intent classifier. Respond only with valid JSON. Be strict - only return true for explicit booking requests."},
                    {"role": "user", "content": detection_prompt}
                ],
                **get_model_params(detection_model, temperature=0.2, reasoning_effort="low"),
                **get_token_param(detection_model, 200)
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure we have the required fields
            should_trigger = result.get("should_trigger", False)
            confidence = result.get("confidence", "low")
            reasoning = result.get("reasoning", "LLM classification")
            
            # Only trigger if should_trigger is True AND confidence is high
            if should_trigger and confidence == "high":
                return {
                    "should_trigger": True,
                    "confidence": "high",
                    "reasoning": reasoning,
                    "context": {"intent": "booking"}
                }
            
            return {
                "should_trigger": False,
                "confidence": confidence,
                "reasoning": reasoning,
                "context": {}
            }
            
        except Exception as e:
            # Fallback on error
            return {
                "should_trigger": False,
                "confidence": "low",
                "reasoning": f"Error in LLM detection: {str(e)}",
                "context": {}
            }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute appointment booking workflow.
        For now, this is a stub showing a prebooked appointment.
        """
        # Mock prebooked appointment
        appointment_date = datetime.now() + timedelta(days=7)
        appointment_time = "10:00 AM"
        provider = "Dr. Sarah Johnson"
        location = "Wellness Medical Center, 123 Health Street, Suite 200"
        appointment_type = "General Consultation"
        
        # Display the appointment details in a clean, integrated way
        st.markdown("")
        with st.container():
            st.markdown("**✅ Your appointment is confirmed!**")
            st.markdown("")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Date:** {appointment_date.strftime('%A, %B %d, %Y')}")
                st.markdown(f"**Time:** {appointment_time}")
                st.markdown(f"**Provider:** {provider}")
            
            with col2:
                st.markdown(f"**Type:** {appointment_type}")
                st.markdown(f"**Location:** {location}")
                st.markdown(f"**Appointment ID:** APT-{appointment_date.strftime('%Y%m%d')}-001")
        
        st.markdown("")
        st.caption("💡 *Note: This is a demonstration. In the future, you'll be able to select your preferred date, time, and provider.*")
        
        # Small delay to show the workflow UI
        import time
        time.sleep(0.5)
        
        return {
            "status": "completed",
            "result": {
                "appointment_id": f"APT-{appointment_date.strftime('%Y%m%d')}-001",
                "date": appointment_date.strftime('%Y-%m-%d'),
                "time": appointment_time,
                "provider": provider,
                "location": location,
                "type": appointment_type
            },
            "message": f"I've booked your appointment with {provider} on {appointment_date.strftime('%A, %B %d')} at {appointment_time}. Your appointment ID is APT-{appointment_date.strftime('%Y%m%d')}-001. You'll receive a confirmation email shortly."
        }
