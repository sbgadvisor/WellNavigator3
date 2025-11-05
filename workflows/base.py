"""
Base WorkflowAgent class for WellNavigator workflows
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import streamlit as st


class WorkflowAgent(ABC):
    """
    Base class for all workflow agents.
    Workflows are invoked when user intent is conclusive and require structured interaction.
    They run to completion and then return control to the conversation.
    """
    
    def __init__(self, workflow_id: str, name: str, description: str, triggers: List[str]):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.triggers = triggers  # Keywords/intents that might trigger this workflow
    
    @abstractmethod
    def should_trigger(self, user_message: str, conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Determine if this workflow should be triggered.
        Returns dict with:
        - should_trigger: bool
        - confidence: str ("high", "medium", "low")
        - reasoning: str
        - context: dict (any relevant context extracted)
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow.
        This method should handle all UI rendering for the workflow.
        
        Args:
            context: Context from should_trigger() and conversation
            
        Returns:
            Dict with:
            - status: "completed" | "cancelled" | "error"
            - result: Any result data
            - message: str message to return to chat
        """
        pass
    
    def get_result_summary(self, result: Dict[str, Any]) -> str:
        """
        Generate a natural language summary of workflow results for chat.
        Override if you want custom formatting.
        """
        return result.get("message", "Workflow completed successfully.")
    
    def render_workflow_ui(self, context: Dict[str, Any]):
        """
        Render the workflow-specific UI.
        This is called from the main app when workflow_mode is active.
        """
        st.info(f"🔄 Running: {self.name}")
        result = self.execute(context)
        return result
