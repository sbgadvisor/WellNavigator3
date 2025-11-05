"""
WellNavigator Workflow Agents Registry
Workflows are invoked when user intent is conclusive and require structured interaction.
"""

from typing import Dict, Optional
from workflows.base import WorkflowAgent
from workflows.appointment_booking import AppointmentBookingWorkflow
from workflows.clinical_trial_search import ClinicalTrialSearchWorkflow

# Registry of all available workflows
WORKFLOW_REGISTRY: Dict[str, WorkflowAgent] = {
    "appointment_booking": AppointmentBookingWorkflow(),
    "clinical_trial_search": ClinicalTrialSearchWorkflow(),
}

def get_workflow(workflow_id: str) -> Optional[WorkflowAgent]:
    """Get a workflow by ID"""
    return WORKFLOW_REGISTRY.get(workflow_id)

def list_workflows() -> Dict[str, WorkflowAgent]:
    """List all available workflows"""
    return WORKFLOW_REGISTRY.copy()

__all__ = ['WORKFLOW_REGISTRY', 'get_workflow', 'list_workflows', 'WorkflowAgent']
