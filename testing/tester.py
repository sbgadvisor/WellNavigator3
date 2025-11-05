"""
Main Test Runner - Orchestrates the automated testing process

NOTE: Testing framework components (test_scenarios, user_simulator, chatbot_runner, evaluator)
are currently not available. This file is kept for future implementation.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
import sys

# Import testing modules - handle missing modules gracefully
try:
    from test_scenarios import TEST_SCENARIOS
    from user_simulator import UserSimulator
    from chatbot_runner import ChatbotRunner
    from evaluator import ConversationEvaluator
    TESTING_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Testing framework modules not available: {e}")
    print("   The testing framework requires the following modules:")
    print("   - test_scenarios.py")
    print("   - user_simulator.py")
    print("   - chatbot_runner.py")
    print("   - evaluator.py")
    TESTING_MODULES_AVAILABLE = False
    # Stub classes to prevent crashes
    TEST_SCENARIOS = []
    class UserSimulator:
        def __init__(self): pass
        def generate_user_message(self, *args, **kwargs): return "Test message"
        def should_continue_conversation(self, *args, **kwargs): return False
    class ChatbotRunner:
        def __init__(self): pass
        def chat(self, *args, **kwargs): return "Test response"
        def reset(self): pass
    class ConversationEvaluator:
        def __init__(self): pass
        def evaluate_conversation(self, *args, **kwargs): return {"overall_score": 0, "issues": []}
        def generate_cursor_agent_instructions(self, *args, **kwargs): return "No recommendations available"


class ChatTester:
    """Main test runner for WellNavigator chatbot"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.conversations_dir = os.path.join(output_dir, "conversations")
        self.recommendations_dir = os.path.join(output_dir, "recommendations")
        self.modules_available = TESTING_MODULES_AVAILABLE
        
        if not self.modules_available:
            print("⚠️  Testing framework modules not available. Testing will be limited.")
            return
        
        # Initialize components
        self.user_simulator = UserSimulator()
        self.chatbot_runner = ChatbotRunner()
        self.evaluator = ConversationEvaluator()
        
        # Ensure output directories exist
        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(self.recommendations_dir, exist_ok=True)
    
    def run_scenario(self, scenario: Dict[str, Any], max_turns: int = 10) -> Dict[str, Any]:
        """
        Run a single test scenario.
        
        Args:
            scenario: Test scenario definition
            max_turns: Maximum conversation turns
        
        Returns:
            Dict with conversation and results
        """
        if not self.modules_available:
            print(f"\n⚠️  Cannot run scenario '{scenario.get('name', 'Unknown')}': Testing framework modules not available.")
            return {
                "scenario": scenario,
                "conversation": [],
                "evaluation": {"overall_score": 0, "error": "Testing modules not available"},
                "status": "error"
            }
        
        print(f"\n{'='*60}")
        print(f"Running Scenario: {scenario['name']}")
        print(f"{'='*60}")
        
        # Reset chatbot for new conversation
        self.chatbot_runner.reset()
        
        conversation = []
        turn = 0
        
        # Run conversation
        while turn < max_turns:
            # Generate user message
            user_message = self.user_simulator.generate_user_message(
                scenario=scenario,
                conversation_history=conversation,
                turn_number=turn
            )
            
            print(f"\n[User Turn {turn + 1}]")
            print(f"User: {user_message}")
            
            # Get chatbot response
            bot_response = self.chatbot_runner.chat(user_message)
            
            print(f"\n[Bot Response]")
            print(f"Bot: {bot_response}")
            
            # Add to conversation
            conversation.append({"role": "user", "content": user_message})
            conversation.append({"role": "assistant", "content": bot_response})
            
            # Check if conversation should continue
            if not self.user_simulator.should_continue_conversation(
                scenario, conversation, max_turns
            ):
                print("\n[Conversation ended naturally]")
                break
            
            turn += 1
        
        # Evaluate conversation
        print(f"\n[Evaluating conversation...]")
        evaluation = self.evaluator.evaluate_conversation(scenario, conversation)
        
        print(f"Overall Score: {evaluation.get('overall_score', 'N/A')}/100")
        print(f"Issues Found: {len(evaluation.get('issues', []))}")
        
        # Save conversation transcript
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation_file = os.path.join(
            self.conversations_dir,
            f"{scenario['scenario_id']}_{timestamp}.json"
        )
        
        result = {
            "scenario": scenario,
            "conversation": conversation,
            "evaluation": evaluation,
            "timestamp": timestamp
        }
        
        with open(conversation_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Conversation saved to: {conversation_file}")
        
        return result
    
    def run_all_scenarios(self, scenario_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Run all or specified test scenarios.
        
        Args:
            scenario_ids: List of scenario IDs to run. If None, runs all.
        
        Returns:
            List of test results
        """
        if scenario_ids is None:
            scenarios_to_run = TEST_SCENARIOS
        else:
            scenarios_to_run = [
                s for s in TEST_SCENARIOS 
                if s["scenario_id"] in scenario_ids
            ]
        
        results = []
        
        for scenario in scenarios_to_run:
            try:
                result = self.run_scenario(scenario)
                results.append({
                    "scenario_name": scenario["name"],
                    "scenario_id": scenario["scenario_id"],
                    "evaluation": result["evaluation"]
                })
            except Exception as e:
                print(f"\n[ERROR] Failed to run scenario {scenario['scenario_id']}: {str(e)}")
                results.append({
                    "scenario_name": scenario["name"],
                    "scenario_id": scenario["scenario_id"],
                    "error": str(e)
                })
        
        return results
    
    def generate_recommendations(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate Cursor agent instructions from test results.
        
        Args:
            results: List of test results
        
        Returns:
            Path to recommendations file
        """
        print(f"\n{'='*60}")
        print("Generating Cursor Agent Instructions...")
        print(f"{'='*60}")
        
        # Get full evaluations (need to load conversation files for detailed issues)
        evaluations = []
        for result in results:
            if "evaluation" in result:
                evaluations.append(result["evaluation"])
        
        # Generate instructions
        instructions = self.evaluator.generate_cursor_agent_instructions(
            evaluations=evaluations,
            scenario_results=results
        )
        
        # Save recommendations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recommendations_file = os.path.join(
            self.recommendations_dir,
            f"recommendations_{timestamp}.md"
        )
        
        with open(recommendations_file, 'w') as f:
            f.write(instructions)
        
        print(f"\nRecommendations saved to: {recommendations_file}")
        print("\nYou can now review this file and provide it to Cursor agent for code improvements.")
        
        return recommendations_file


def main():
    """Main entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WellNavigator chatbot")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        help="Specific scenario IDs to run (default: all)",
        default=None
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=10,
        help="Maximum conversation turns per scenario"
    )
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = ChatTester()
    
    # Run tests
    results = tester.run_all_scenarios(scenario_ids=args.scenarios)
    
    # Generate recommendations
    recommendations_file = tester.generate_recommendations(results)
    
    print(f"\n{'='*60}")
    print("Testing Complete!")
    print(f"{'='*60}")
    print(f"\nReview recommendations in: {recommendations_file}")
    print("\nNext steps:")
    print("1. Review the recommendations file")
    print("2. Provide it to Cursor agent for code improvements")
    print("3. Test again after improvements")


if __name__ == "__main__":
    main()
