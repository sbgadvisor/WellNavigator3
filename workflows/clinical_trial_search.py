"""
Clinical Trial Search Workflow
Performs a background search for relevant clinical trials and displays results.
"""

from workflows.base import WorkflowAgent
from typing import Dict, Any, List
import streamlit as st
import time


class ClinicalTrialSearchWorkflow(WorkflowAgent):
    """Workflow for searching clinical trials"""
    
    def __init__(self):
        super().__init__(
            workflow_id="clinical_trial_search",
            name="Clinical Trial Search",
            description="Search for relevant clinical trials based on user's condition",
            triggers=["clinical trial", "clinical trials", "research studies", "find trials",
                     "trials for", "participate in research", "experimental treatment",
                     "clinical study", "research study"]
        )
    
    def should_trigger(self, user_message: str, conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """Check if user wants to search for clinical trials"""
        message_lower = user_message.lower()
        
        # High confidence triggers
        high_confidence_keywords = [
            "clinical trial", "clinical trials", "find trials", "search for trials",
            "research study", "research studies", "experimental treatment",
            "participate in research", "clinical study"
        ]
        
        # Medium confidence triggers
        medium_confidence_keywords = [
            "trials", "research", "studies", "experimental"
        ]
        
        # Extract condition/context from message
        context_data = {}
        
        # Simple keyword extraction (in production, use NLP)
        condition_keywords = []
        if any(keyword in message_lower for keyword in ["diabetes", "diabetic"]):
            condition_keywords.append("diabetes")
        if any(keyword in message_lower for keyword in ["cancer", "oncology", "tumor"]):
            condition_keywords.append("cancer")
        if any(keyword in message_lower for keyword in ["heart", "cardiac", "cardiovascular"]):
            condition_keywords.append("cardiovascular")
        if any(keyword in message_lower for keyword in ["arthritis", "joint"]):
            condition_keywords.append("arthritis")
        
        context_data["conditions"] = condition_keywords if condition_keywords else ["general"]
        
        # Check for high confidence
        if any(keyword in message_lower for keyword in high_confidence_keywords):
            return {
                "should_trigger": True,
                "confidence": "high",
                "reasoning": "User explicitly wants to search for clinical trials",
                "context": context_data
            }
        
        # Check for medium confidence
        if any(keyword in message_lower for keyword in medium_confidence_keywords):
            # Check if user confirmed in conversation
            recent_messages = " ".join([msg.get("content", "") for msg in conversation_context[-3:]])
            if "yes" in message_lower or "okay" in message_lower or "sure" in message_lower:
                return {
                    "should_trigger": True,
                    "confidence": "high",
                    "reasoning": "User confirmed clinical trial search",
                    "context": context_data
                }
            
            return {
                "should_trigger": False,
                "confidence": "medium",
                "reasoning": "Mentioned trials/research but not conclusive",
                "context": context_data
            }
        
        return {
            "should_trigger": False,
            "confidence": "low",
            "reasoning": "No clinical trial search intent detected",
            "context": {}
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute clinical trial search workflow.
        Performs a background search and displays results.
        """
        st.markdown("### 🔬 Clinical Trial Search")
        
        conditions = context.get("conditions", ["general"])
        search_query = ", ".join(conditions) if conditions else "general health"
        
        st.markdown(f"Searching for clinical trials related to: **{search_query}**")
        
        # Show search progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate background search
        status_text.text("🔍 Searching databases...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        status_text.text("📊 Analyzing eligibility criteria...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("✅ Compiling results...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        progress_bar.progress(100)
        status_text.text("✅ Search complete!")
        time.sleep(0.3)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.markdown("---")
        
        # Mock search results
        mock_trials = self._generate_mock_trials(conditions)
        
        st.success(f"Found {len(mock_trials)} potentially relevant clinical trials")
        
        # Display results
        for i, trial in enumerate(mock_trials, 1):
            with st.expander(f"Trial {i}: {trial['title']}", expanded=(i == 1)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Study Focus:** {trial['focus']}")
                    st.markdown(f"**Location:** {trial['location']}")
                    st.markdown(f"**Status:** {trial['status']}")
                    if trial.get('eligibility'):
                        st.markdown(f"**Eligibility:** {trial['eligibility']}")
                
                with col2:
                    if trial.get('link'):
                        st.link_button("Learn More", trial['link'], use_container_width=True)
                    st.caption(f"Trial ID: {trial['id']}")
        
        st.markdown("---")
        st.info("💡 **Note:** These are example results. In the future, this will search real clinical trial databases. Always consult with your healthcare provider before considering participation in a clinical trial.")
        
        return {
            "status": "completed",
            "result": {
                "query": search_query,
                "trials_found": len(mock_trials),
                "trials": mock_trials
            },
            "message": f"I found {len(mock_trials)} potentially relevant clinical trials for {search_query}. I've displayed them above. Remember to discuss any trials you're interested in with your healthcare provider."
        }
    
    def _generate_mock_trials(self, conditions: List[str]) -> List[Dict[str, Any]]:
        """Generate mock clinical trial results"""
        base_trials = [
            {
                "id": "CT-2024-001",
                "title": "Novel Treatment Approaches for Chronic Conditions",
                "focus": "Investigating new therapeutic interventions",
                "location": "Multiple locations nationwide",
                "status": "Recruiting",
                "eligibility": "Adults 18-75 with relevant conditions",
                "link": "https://clinicaltrials.gov/example-1"
            },
            {
                "id": "CT-2024-002",
                "title": "Long-term Safety and Efficacy Study",
                "focus": "Safety monitoring and outcome assessment",
                "location": "Regional Medical Centers",
                "status": "Active, not recruiting",
                "eligibility": "Participants from previous studies",
                "link": "https://clinicaltrials.gov/example-2"
            },
            {
                "id": "CT-2024-003",
                "title": "Patient-Reported Outcomes Research",
                "focus": "Quality of life and patient experience",
                "location": "Online and local clinics",
                "status": "Recruiting",
                "eligibility": "All ages, various conditions welcome",
                "link": "https://clinicaltrials.gov/example-3"
            }
        ]
        
        # If specific conditions mentioned, adjust results slightly
        if "diabetes" in conditions:
            base_trials[0]["title"] = "Diabetes Management and Treatment Study"
            base_trials[0]["focus"] = "New approaches to diabetes care"
        
        if "cancer" in conditions:
            base_trials[1]["title"] = "Oncology Treatment Protocols"
            base_trials[1]["focus"] = "Cancer treatment effectiveness"
        
        return base_trials
