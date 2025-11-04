"""
WellNavigator Mock Tools
These are mock implementations that can be replaced with real API calls in the future.
"""

from typing import Dict, List, Any


class MockTool:
    """Base class for mock tools - provides interface for future real implementations"""
    
    @staticmethod
    def execute(**kwargs) -> Dict[str, Any]:
        """Execute the tool and return results"""
        raise NotImplementedError


class AppointmentTool(MockTool):
    """Mock tool for appointment preparation and scheduling"""
    
    @staticmethod
    def prepare_appointment_guide(appointment_type: str = "general", user_context: str = "") -> Dict[str, Any]:
        """Generate a personalized appointment preparation guide"""
        guides = {
            "general": {
                "title": "General Appointment Preparation",
                "checklist": [
                    "Write down your symptoms and when they started",
                    "List any medications you're currently taking",
                    "Prepare questions you want to ask your doctor",
                    "Bring your insurance card and ID",
                    "Bring a list of any previous test results",
                    "Consider bringing a trusted friend or family member for support"
                ],
                "tips": "It can be helpful to write down your questions beforehand so you don't forget anything during the appointment."
            },
            "specialist": {
                "title": "Specialist Appointment Preparation",
                "checklist": [
                    "Bring referrals and previous medical records",
                    "Prepare a timeline of your condition or symptoms",
                    "List all current medications and dosages",
                    "Write down specific questions about your condition",
                    "Bring any relevant test results or imaging",
                    "Prepare to discuss your treatment goals"
                ],
                "tips": "Specialist appointments can be brief, so prioritize your most important questions first."
            },
            "follow-up": {
                "title": "Follow-up Appointment Preparation",
                "checklist": [
                    "Review what was discussed in your last appointment",
                    "Note any changes in your condition since then",
                    "Track how well treatments or medications are working",
                    "Prepare questions about next steps",
                    "Bring any new test results or concerns"
                ],
                "tips": "Follow-up appointments are great for tracking progress and adjusting your care plan."
            }
        }
        
        guide = guides.get(appointment_type, guides["general"])
        
        return {
            "tool": "appointment_preparation",
            "status": "success",
            "data": guide,
            "message": f"Here's a personalized guide to help you prepare for your appointment."
        }


class ResultsTool(MockTool):
    """Mock tool for explaining test results and medical information"""
    
    @staticmethod
    def explain_results(test_type: str = "general", results_summary: str = "") -> Dict[str, Any]:
        """Provide explanation and context for test results"""
        explanations = {
            "blood_test": {
                "title": "Understanding Your Blood Test Results",
                "common_components": [
                    "Complete Blood Count (CBC) - measures red and white blood cells",
                    "Basic Metabolic Panel - checks kidney function, electrolytes, and blood sugar",
                    "Lipid Panel - measures cholesterol levels",
                    "Liver Function Tests - assesses liver health"
                ],
                "general_advice": "Blood test results are interpreted in context with your symptoms and medical history. Your doctor will review these with you.",
                "when_to_ask": "Ask your doctor about any values marked as high or low, and what they mean for your specific situation."
            },
            "imaging": {
                "title": "Understanding Your Imaging Results",
                "general_advice": "Imaging results (X-rays, MRIs, CT scans) require interpretation by a radiologist and your doctor. They'll explain what the images show in the context of your symptoms.",
                "when_to_ask": "Important questions: What does this finding mean? Does it explain my symptoms? What are the next steps?"
            },
            "general": {
                "title": "Understanding Your Test Results",
                "general_advice": "Test results are just one piece of the puzzle. Your doctor considers them along with your symptoms, medical history, and physical examination.",
                "when_to_ask": "Always ask your doctor to explain results in plain language and what they mean for your care plan."
            }
        }
        
        explanation = explanations.get(test_type, explanations["general"])
        
        return {
            "tool": "results_explanation",
            "status": "success",
            "data": explanation,
            "message": f"Here's some helpful context about {test_type} results."
        }


class ResourcesTool(MockTool):
    """Mock tool for finding health resources and support services"""
    
    @staticmethod
    def find_resources(resource_type: str = "general", condition: str = "") -> Dict[str, Any]:
        """Find relevant health resources and support services"""
        resources = {
            "support_groups": {
                "title": "Support Groups and Community Resources",
                "resources": [
                    "Local patient support groups (check with your healthcare provider or hospital)",
                    "Online communities for your specific condition",
                    "Caregiver support networks",
                    "Mental health and wellness resources"
                ],
                "tips": "Support groups can provide emotional support and practical advice from others who understand what you're going through."
            },
            "financial": {
                "title": "Financial and Insurance Resources",
                "resources": [
                    "Patient assistance programs for medications",
                    "Hospital financial aid programs",
                    "Insurance navigation services",
                    "Government healthcare programs (if eligible)"
                ],
                "tips": "Many hospitals and clinics have financial counselors who can help you understand costs and find assistance programs."
            },
            "educational": {
                "title": "Educational Resources",
                "resources": [
                    "Reliable health information websites (Mayo Clinic, WebMD, CDC)",
                    "Condition-specific educational materials from medical organizations",
                    "Your healthcare provider's patient education library",
                    "Trusted medical journals (for more detailed information)"
                ],
                "tips": "Always verify information from reliable, evidence-based sources and discuss what you learn with your healthcare team."
            },
            "general": {
                "title": "General Health Resources",
                "resources": [
                    "Your primary care provider's office for referrals",
                    "Local health department services",
                    "Mental health support services",
                    "Transportation assistance for medical appointments"
                ],
                "tips": "Don't hesitate to ask your healthcare team about available resources—they often know about local services that can help."
            }
        }
        
        resource = resources.get(resource_type, resources["general"])
        
        return {
            "tool": "resource_finder",
            "status": "success",
            "data": resource,
            "message": f"I've found some helpful {resource_type} resources for you."
        }


class CaregiverTool(MockTool):
    """Mock tool for caregiver support and advice"""
    
    @staticmethod
    def provide_caregiver_guidance(situation: str = "general") -> Dict[str, Any]:
        """Provide guidance and support for caregivers"""
        guidance = {
            "burnout": {
                "title": "Caregiver Self-Care and Burnout Prevention",
                "advice": [
                    "It's okay to ask for help—you don't have to do everything alone",
                    "Take breaks when you can, even if they're short",
                    "Connect with other caregivers who understand your experience",
                    "Prioritize your own health—you can't help others if you're not well",
                    "Consider respite care options to give yourself regular breaks"
                ],
                "resources": "Look into local caregiver support groups and respite care services in your area."
            },
            "communication": {
                "title": "Communicating with Healthcare Providers",
                "advice": [
                    "Come prepared to appointments with questions and concerns written down",
                    "Take notes during appointments or bring someone to help remember details",
                    "Ask for clarification if you don't understand medical terms",
                    "Keep a care journal to track symptoms, medications, and appointments",
                    "Don't be afraid to advocate for your loved one's needs"
                ],
                "resources": "Many hospitals offer caregiver education programs to help you navigate the healthcare system."
            },
            "general": {
                "title": "General Caregiver Support",
                "advice": [
                    "Remember that caregiving is a journey—be patient with yourself and your loved one",
                    "Seek support from family, friends, and community resources",
                    "Stay organized with calendars, medication schedules, and important documents",
                    "Take care of your own physical and mental health",
                    "Celebrate small victories and progress"
                ],
                "resources": "There are many resources available to support caregivers. Don't hesitate to reach out for help."
            }
        }
        
        guide = guidance.get(situation, guidance["general"])
        
        return {
            "tool": "caregiver_support",
            "status": "success",
            "data": guide,
            "message": "Here's some guidance to support you in your caregiving role."
        }


# Tool registry for easy access
TOOLS = {
    "appointment": AppointmentTool,
    "results": ResultsTool,
    "resources": ResourcesTool,
    "caregiver": CaregiverTool
}
