"""
ProDegeit Project - AI Assistant
Uses Gemini 2.0 Flash for intelligent content generation
"""

import os
import sys
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in .env file")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration - Try Gemini 3 Pro first, fallback to 2.5 Pro
MODEL_PRIORITY = [
    "gemini-3-pro-preview",      # Best: Gemini 3 Pro Preview
    "gemini-2.5-pro",            # Fallback: Gemini 2.5 Pro
    "gemini-2.0-flash-exp"       # Final fallback: Gemini 2.0 Flash
]

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]


class AIAssistant:
    """AI Assistant using Gemini for content generation"""
    
    def __init__(self):
        """Initialize the AI assistant with model fallback"""
        self.available = False
        self.model_name = None
        
        # Try models in priority order
        for model_name in MODEL_PRIORITY:
            try:
                print(f"Attempting to initialize {model_name}...")
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=GENERATION_CONFIG,
                    safety_settings=SAFETY_SETTINGS
                )
                # Test the model with a simple request
                test_response = self.model.generate_content("Test")
                
                # If successful, use this model
                self.available = True
                self.model_name = model_name
                print(f"✓ Successfully initialized {model_name}")
                break
                
            except Exception as e:
                print(f"✗ {model_name} not available: {e}")
                continue
        
        if not self.available:
            print(f"WARNING: Could not initialize any Gemini model")
            self.model = None
    
    def generate_executive_summary(self, project_data: Dict, allocation_results: Dict, 
                                   risk_analysis: Dict) -> str:
        """Generate executive summary for the project report"""
        if not self.available:
            return self._fallback_executive_summary(project_data, allocation_results, risk_analysis)
        
        prompt = f"""
You are a project management expert writing an executive summary for a project plan.

Project: ProDegeit - Equipment Acquisition and Installation
Start Date: {project_data['start_date']}
Deadline: {project_data['deadline']}
Budget: €{project_data['budget_max']:,} (€{project_data['budget_with_reserve']:,} with 10% reserve)

Project Status:
- Total Activities: {allocation_results['total_activities']}
- Resources Allocated: {allocation_results['total_resources']}
- Estimated Total Cost: €{allocation_results['estimated_cost']:,.2f}
- Projected Completion: {allocation_results['completion_date']}
- Budget Status: {allocation_results['budget_status']}
- Timeline Status: {allocation_results['timeline_status']}

Risk Analysis:
- Identified Risks: {risk_analysis['total_risks']}
- Total Expected Risk Cost (before mitigation): €{risk_analysis['total_expected_cost']:,.2f}
- Mitigation Cost: €{risk_analysis['mitigation_cost']:,.2f}
- Expected Risk Cost (after mitigation): €{risk_analysis['expected_cost_after']:,.2f}

Write a professional, concise executive summary (250-300 words) that:
1. States the project objective clearly
2. Highlights key achievements in planning
3. Summarizes resource allocation approach
4. Mentions risk mitigation strategy
5. Confirms feasibility within budget and timeline constraints
6. Provides confidence level for successful delivery

Use professional project management terminology. Be specific with numbers.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating executive summary: {e}")
            return self._fallback_executive_summary(project_data, allocation_results, risk_analysis)
    
    def generate_resource_justification(self, activity: Dict, assigned_resources: List[Dict],
                                       skill_requirements: Dict[str, int]) -> str:
        """Generate justification for resource allocation to an activity"""
        if not self.available:
            return self._fallback_resource_justification(activity, assigned_resources, skill_requirements)
        
        resources_info = "\n".join([
            f"- {r['name']}: Cost €{r['cost']}/h, Skills: {r['skills']}"
            for r in assigned_resources
        ])
        
        prompt = f"""
You are a project manager explaining resource allocation decisions.

Activity: #{activity['id']} - {activity['name']}
Duration: {activity['duration']} days
Required People: {activity['num_people']}
Skill Requirements: {skill_requirements}

Assigned Resources:
{resources_info}

Write a brief justification (2-3 sentences) explaining why these specific resources were assigned to this activity. Focus on:
1. How their skills match the requirements
2. Cost-effectiveness
3. Availability considerations

Be concise and professional.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating resource justification: {e}")
            return self._fallback_resource_justification(activity, assigned_resources, skill_requirements)
    
    def generate_risk_narrative(self, risk: Dict, selected_mitigation: Dict, 
                               scenario_analysis: Dict) -> str:
        """Generate narrative description of risk and mitigation strategy"""
        if not self.available:
            return self._fallback_risk_narrative(risk, selected_mitigation, scenario_analysis)
        
        prompt = f"""
You are a risk management expert documenting a project risk.

Risk: {risk['name']}
Activity: #{risk['activity_id']}
Probability: {risk['probability']*100}%
Impact: €{risk['cost_impact']:,} / {risk['time_impact']} days

Selected Mitigation: {selected_mitigation['name']}
Mitigation Cost: €{selected_mitigation['cost']:,}
Expected Reduction: €{selected_mitigation['cost_reduction']:,} / {selected_mitigation['time_reduction']} days

Scenario Analysis:
- Without mitigation: Expected cost = €{scenario_analysis['without_mitigation']:,.2f}
- With mitigation: Expected cost = €{scenario_analysis['with_mitigation']:,.2f}
- Net benefit: €{scenario_analysis['net_benefit']:,.2f}

Write a professional risk narrative (3-4 sentences) that:
1. Describes the risk and its potential impact
2. Explains the chosen mitigation strategy
3. Justifies the decision with cost-benefit analysis

Be specific and use project management terminology.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating risk narrative: {e}")
            return self._fallback_risk_narrative(risk, selected_mitigation, scenario_analysis)
    
    def generate_conclusions(self, budget_status: Dict, timeline_status: Dict,
                           recommendations: List[str]) -> str:
        """Generate conclusions section for the report"""
        if not self.available:
            return self._fallback_conclusions(budget_status, timeline_status, recommendations)
        
        prompt = f"""
You are a senior project manager writing the conclusions section of a project plan.

Budget Analysis:
- Allocated: €{budget_status['allocated']:,.2f}
- Limit: €{budget_status['limit']:,.2f}
- Remaining: €{budget_status['remaining']:,.2f}
- Status: {budget_status['status']}

Timeline Analysis:
- Projected Completion: {timeline_status['projected_completion']}
- Deadline: {timeline_status['deadline']}
- Buffer: {timeline_status['buffer_days']} days
- Status: {timeline_status['status']}

Key Recommendations:
{chr(10).join([f'- {rec}' for rec in recommendations])}

Write a professional conclusions section (200-250 words) that:
1. Assesses overall project viability
2. Highlights critical success factors
3. Identifies key risks to monitor
4. Provides specific recommendations for execution phase
5. Expresses confidence level in successful delivery

Use authoritative, professional language appropriate for senior management review.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating conclusions: {e}")
            return self._fallback_conclusions(budget_status, timeline_status, recommendations)
    
    def generate_best_practices(self, project_context: str) -> List[str]:
        """Generate project management best practices relevant to the context"""
        if not self.available:
            return self._fallback_best_practices()
        
        prompt = f"""
You are a PMBOK-certified project management consultant.

Project Context: {project_context}

List 5 specific project management best practices that are most relevant to this project.
Each practice should be:
- Specific and actionable
- Based on PMBOK or other recognized PM frameworks
- Relevant to resource allocation, risk management, or schedule management
- No more than one sentence each

Format as a numbered list.
"""
        
        try:
            response = self.model.generate_content(prompt)
            practices = response.text.strip().split('\n')
            # Clean up and filter
            practices = [p.strip() for p in practices if p.strip() and any(c.isalpha() for c in p)]
            return practices[:5]
        except Exception as e:
            print(f"Error generating best practices: {e}")
            return self._fallback_best_practices()
    
    # Fallback methods (when AI is not available)
    
    def _fallback_executive_summary(self, project_data, allocation_results, risk_analysis):
        return f"""This project plan outlines the acquisition and installation of equipment for ProDegeit, 
scheduled from {project_data['start_date']} to {project_data['deadline']}. The plan encompasses 
{allocation_results['total_activities']} activities with {allocation_results['total_resources']} 
allocated resources. Total estimated cost is €{allocation_results['estimated_cost']:,.2f}, which is 
{allocation_results['budget_status']} the budget limit of €{project_data['budget_with_reserve']:,}. 
The timeline is {allocation_results['timeline_status']}, with projected completion on 
{allocation_results['completion_date']}. Risk analysis identified {risk_analysis['total_risks']} 
major risks with total mitigation cost of €{risk_analysis['mitigation_cost']:,.2f}. The plan demonstrates 
feasibility within all constraints and provides a solid foundation for project execution."""
    
    def _fallback_resource_justification(self, activity, assigned_resources, skill_requirements):
        return f"""Resources assigned based on skill match to requirements: {skill_requirements}. 
Selected team members possess necessary expertise while maintaining cost-effectiveness. 
Availability verified for activity timeframe."""
    
    def _fallback_risk_narrative(self, risk, selected_mitigation, scenario_analysis):
        return f"""{risk['name']} poses a {risk['probability']*100}% probability risk with potential 
impact of €{risk['cost_impact']:,} and {risk['time_impact']} days delay. Selected mitigation 
strategy '{selected_mitigation['name']}' costs €{selected_mitigation['cost']:,} but reduces 
expected cost by €{selected_mitigation['cost_reduction']:,}, resulting in net benefit of 
€{scenario_analysis['net_benefit']:,.2f}."""
    
    def _fallback_conclusions(self, budget_status, timeline_status, recommendations):
        return f"""The project plan is viable within the established constraints. Budget allocation of 
€{budget_status['allocated']:,.2f} is {budget_status['status']}, leaving €{budget_status['remaining']:,.2f} 
buffer. Timeline shows {timeline_status['buffer_days']} days buffer to deadline. Key success factors 
include effective risk mitigation and resource availability management. Recommended actions: 
{', '.join(recommendations)}. Overall confidence in successful delivery is high given thorough planning 
and appropriate contingencies."""
    
    def _fallback_best_practices(self):
        return [
            "Apply critical path method to identify and monitor schedule-critical activities",
            "Use resource leveling to prevent over-allocation and optimize team utilization",
            "Implement risk response strategies for all identified high-probability/high-impact risks",
            "Maintain management reserve (10%) for unforeseen circumstances",
            "Conduct regular earned value analysis to track cost and schedule performance"
        ]


# Singleton instance
_ai_assistant = None

def get_ai_assistant() -> AIAssistant:
    """Get or create AI assistant instance"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant()
    return _ai_assistant


if __name__ == "__main__":
    # Test AI assistant
    print("Testing AI Assistant...")
    assistant = get_ai_assistant()
    
    if assistant.available:
        print("✓ Gemini API initialized successfully")
        
        # Test executive summary generation
        test_data = {
            'start_date': '2026-01-05',
            'deadline': '2026-03-21',
            'budget_max': 400000,
            'budget_with_reserve': 440000,
        }
        test_allocation = {
            'total_activities': 17,
            'total_resources': 16,
            'estimated_cost': 385000,
            'completion_date': '2026-03-18',
            'budget_status': 'within',
            'timeline_status': 'on track',
        }
        test_risk = {
            'total_risks': 3,
            'total_expected_cost': 4300,
            'mitigation_cost': 1300,
            'expected_cost_after': 2100,
        }
        
        print("\nGenerating test executive summary...")
        summary = assistant.generate_executive_summary(test_data, test_allocation, test_risk)
        print(summary)
    else:
        print("✗ Gemini API not available")
