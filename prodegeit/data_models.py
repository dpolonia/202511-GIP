"""
ProDegeit Project - Data Models
Defines all project data including activities, resources, risks, and constants
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Project Constants
PROJECT_START = datetime(2026, 1, 5)  # Monday, 5 January 2026
PROJECT_DEADLINE = datetime(2026, 3, 21)  # Saturday, 21 March 2026
BUDGET_MAX = 400000  # EUR
BUDGET_WITH_RESERVE = 440000  # EUR (10% management reserve)
PENALTY_DELAY = 50000  # EUR per delay
HOURS_PER_DAY = 8
WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Portuguese Public Holidays in 2026 (during project period)
HOLIDAYS_2026 = [
    datetime(2026, 1, 1),   # New Year's Day (before project)
    datetime(2026, 2, 17),  # Carnival Tuesday
    datetime(2026, 4, 3),   # Good Friday (after project end)
    datetime(2026, 4, 5),   # Easter Sunday (after project end)
    datetime(2026, 4, 25),  # Freedom Day (after project end)
]

# Skill Categories (0-6 scale)
SKILL_PETROLEUM = "Petroleum Technology"
SKILL_CONSTRUCTION = "Construction"
SKILL_FINANCE = "Finance"
SKILL_PROCUREMENT = "Procurement"
SKILL_HR = "Human Resources"

ALL_SKILLS = [SKILL_PETROLEUM, SKILL_CONSTRUCTION, SKILL_FINANCE, SKILL_PROCUREMENT, SKILL_HR]


class Activity:
    """Represents a project activity/task"""
    def __init__(self, id: int, name: str, duration_days: int, 
                 num_people: int, predecessors: List[int],
                 skill_requirements: Dict[str, int]):
        self.id = id
        self.name = name
        self.duration_days = duration_days
        self.num_people = num_people
        self.predecessors = predecessors
        self.skill_requirements = skill_requirements
        self.assigned_resources = []
        self.start_date = None
        self.end_date = None
        self.total_hours = num_people * duration_days * HOURS_PER_DAY
        
    def __repr__(self):
        return f"Activity({self.id}: {self.name}, {self.duration_days}d, {self.num_people}p)"


class Resource:
    """Represents a project resource/team member"""
    def __init__(self, name: str, cost_per_hour: float, availability_pct: float,
                 start_week: int, vacation_weeks: List[int], skills: Dict[str, int],
                 is_core_team: bool = False):
        self.name = name
        self.cost_per_hour = cost_per_hour
        self.availability_pct = availability_pct
        self.start_week = start_week
        self.vacation_weeks = vacation_weeks
        self.skills = skills
        self.is_core_team = is_core_team
        self.assigned_tasks = []
        self.total_hours = 0
        self.total_cost = 0
        
    def __repr__(self):
        return f"Resource({self.name}, €{self.cost_per_hour}/h, {self.availability_pct*100}%)"
    
    def is_available(self, week: int) -> bool:
        """Check if resource is available in given week"""
        if week < self.start_week:
            return False
        if week in self.vacation_weeks:
            return False
        return True
    
    def can_take_task(self, max_tasks: int = 6) -> bool:
        """Check if resource can take another task"""
        return len(self.assigned_tasks) < max_tasks
    
    def matches_skills(self, requirements: Dict[str, int]) -> tuple[bool, int]:
        """
        Check if resource matches skill requirements
        Returns: (matches: bool, skill_surplus: int)
        """
        matches = True
        surplus = 0
        
        for skill, required_level in requirements.items():
            if required_level > 0:  # Only check if skill is required
                resource_level = self.skills.get(skill, 0)
                if resource_level == 0:  # Resource doesn't have required skill
                    matches = False
                    return (False, 0)
                surplus += (resource_level - required_level)
        
        return (matches, surplus)


class Risk:
    """Represents a project risk"""
    def __init__(self, id: int, name: str, activity_id: int, 
                 probability: float, cost_impact: float, time_impact_days: int,
                 mitigation_options: List[Dict]):
        self.id = id
        self.name = name
        self.activity_id = activity_id
        self.probability = probability
        self.cost_impact = cost_impact
        self.time_impact_days = time_impact_days
        self.mitigation_options = mitigation_options
        self.selected_mitigation = None
        
    def __repr__(self):
        return f"Risk({self.name}, P={self.probability*100}%, Impact=€{self.cost_impact})"
    
    def expected_value(self) -> float:
        """Calculate expected monetary value of risk"""
        return self.probability * self.cost_impact


# Define all 17 activities
ACTIVITIES = [
    Activity(1, "Lista de especificações", 5, 3, [], 
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 1, SKILL_FINANCE: 2}),
    
    Activity(2, "Requisitos do local", 7, 1, [1],
             {SKILL_PETROLEUM: 3, SKILL_CONSTRUCTION: 4}),
    
    Activity(3, "Convite à apresentação de propostas", 10, 2, [1],
             {SKILL_PROCUREMENT: 5, SKILL_FINANCE: 3}),
    
    Activity(4, "Aprovação do orçamento", 12, 2, [1],
             {SKILL_FINANCE: 6, SKILL_PETROLEUM: 2}),
    
    Activity(5, "Negociações contratuais", 8, 2, [3, 4],
             {SKILL_PROCUREMENT: 4, SKILL_FINANCE: 4}),
    
    Activity(6, "Assinatura de contratos", 13, 2, [2, 5],
             {SKILL_PROCUREMENT: 3, SKILL_FINANCE: 5}),
    
    Activity(7, "Conhecimentos especializados do projeto", 15, 4, [5],
             {SKILL_PETROLEUM: 6, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 2}),
    
    Activity(8, "Plano de comunicação", 14, 3, [5],
             {SKILL_HR: 3, SKILL_FINANCE: 2}),
    
    Activity(9, "Equipamento adicional", 5, 3, [4],
             {SKILL_PETROLEUM: 4, SKILL_CONSTRUCTION: 3}),
    
    Activity(10, "Plano de instalação", 10, 1, [6, 9],
             {SKILL_CONSTRUCTION: 6, SKILL_PETROLEUM: 4}),
    
    Activity(11, "Planeamento do pessoal", 11, 2, [1],
             {SKILL_HR: 4, SKILL_FINANCE: 3}),
    
    Activity(12, "Documentação operacional", 6, 3, [5],
             {SKILL_PETROLEUM: 3, SKILL_CONSTRUCTION: 2}),
    
    Activity(13, "Contratação/formação do pessoal", 11, 4, [11],
             {SKILL_HR: 6, SKILL_FINANCE: 2}),
    
    Activity(14, "Plano de gestão de riscos", 5, 1, [7, 12, 13],
             {SKILL_FINANCE: 5, SKILL_PETROLEUM: 3}),
    
    Activity(15, "Plano de integração", 3, 3, [8, 10, 14],
             {SKILL_PETROLEUM: 4, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 3}),
    
    Activity(16, "Documentação", 22, 1, [2],
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 2}),
    
    Activity(17, "Aprovação do plano de produção", 2, 4, [15, 16],
             {SKILL_PETROLEUM: 5, SKILL_FINANCE: 4, SKILL_CONSTRUCTION: 2}),
]

# Define all resources
RESOURCES = [
    # Core Team (permanent)
    Resource("Francisco", 89, 0.90, 1, [11], 
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 4, SKILL_FINANCE: 2}, is_core_team=True),
    Resource("Susana", 151, 0.80, 1, [6],
             {SKILL_PETROLEUM: 5, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 4, 
              SKILL_PROCUREMENT: 5, SKILL_HR: 3}, is_core_team=True),
    Resource("Tim", 97, 1.00, 1, [7, 8],
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 4, SKILL_FINANCE: 3}, is_core_team=True),
    
    # Extended Team
    Resource("Alex", 86, 1.00, 4, [],
             {SKILL_PETROLEUM: 3, SKILL_CONSTRUCTION: 1, SKILL_FINANCE: 2, SKILL_PROCUREMENT: 2}),
    Resource("Ana", 160, 1.00, 2, [3],
             {SKILL_PETROLEUM: 6, SKILL_CONSTRUCTION: 5, SKILL_FINANCE: 6, SKILL_PROCUREMENT: 3}),
    Resource("Bernardo", 102, 1.00, 4, [9, 10],
             {SKILL_PETROLEUM: 3, SKILL_CONSTRUCTION: 2, SKILL_FINANCE: 4, SKILL_PROCUREMENT: 2}),
    Resource("Cátia", 87, 0.80, 3, [],
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 3}),
    Resource("Félix", 89, 1.00, 6, [],
             {SKILL_PETROLEUM: 1, SKILL_CONSTRUCTION: 4, SKILL_FINANCE: 1}),
    Resource("Horácio", 135, 0.80, 2, [],
             {SKILL_PETROLEUM: 6, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 5, SKILL_PROCUREMENT: 2}),
    Resource("João", 125, 1.00, 3, [],
             {SKILL_PETROLEUM: 4, SKILL_CONSTRUCTION: 6, SKILL_FINANCE: 5}),
    Resource("Leandro", 97, 1.00, 2, [4, 5],
             {SKILL_PETROLEUM: 1, SKILL_CONSTRUCTION: 1, SKILL_FINANCE: 4, SKILL_PROCUREMENT: 6}),
    Resource("Lucas", 70, 0.70, 3, [],
             {SKILL_PETROLEUM: 2, SKILL_CONSTRUCTION: 4}),
    Resource("Marco", 89, 1.00, 3, [],
             {SKILL_PETROLEUM: 1, SKILL_CONSTRUCTION: 5, SKILL_FINANCE: 5}),
    Resource("Paulo", 175, 1.00, 4, [],
             {SKILL_PETROLEUM: 5, SKILL_CONSTRUCTION: 5, SKILL_FINANCE: 6, 
              SKILL_PROCUREMENT: 3, SKILL_HR: 1}),
    Resource("Pedro", 128, 0.80, 2, [],
             {SKILL_PETROLEUM: 6, SKILL_CONSTRUCTION: 4, SKILL_FINANCE: 4, SKILL_PROCUREMENT: 1}),
    Resource("Teófilo", 58, 1.00, 3, [],
             {SKILL_PETROLEUM: 4, SKILL_CONSTRUCTION: 3, SKILL_FINANCE: 3}),
]

# Define risks with mitigation options
RISKS = [
    Risk(1, "Avaria do Servidor", 7, 0.05, 8000, 2, [
        {"id": "A", "name": "Comprar equipamento", "cost": 4000, "cost_reduction": 1500, "time_reduction": 2},
        {"id": "B", "name": "Lista fornecedores", "cost": 500, "cost_reduction": 500, "time_reduction": 0},
        {"id": "C", "name": "Treinar substituição", "cost": 800, "cost_reduction": 800, "time_reduction": 0},
        {"id": "D", "name": "Contrato backup", "cost": 2000, "cost_reduction": 900, "time_reduction": 0},
        {"id": "E", "name": "Aceitar risco", "cost": 0, "cost_reduction": 0, "time_reduction": 0},
    ]),
    
    Risk(2, "Qualidade não conforme", 10, 0.15, 12000, 3, [
        {"id": "A", "name": "Avaliações regulares", "cost": 0, "cost_reduction": 4000, "time_reduction": 1},
        {"id": "B", "name": "Pessoa testes adicionais", "cost": 2000, "cost_reduction": 500, "time_reduction": 0},
        {"id": "C", "name": "Representante cliente", "cost": 1200, "cost_reduction": 500, "time_reduction": 0},
        {"id": "D", "name": "Competências especializadas", "cost": 0, "cost_reduction": 1000, "time_reduction": 1},
        {"id": "E", "name": "Aceitar risco", "cost": 0, "cost_reduction": 0, "time_reduction": 0},
    ]),
    
    Risk(3, "Conflito de prioridades", 13, 0.25, 6000, 7, [
        {"id": "A", "name": "Divulgar projeto", "cost": 800, "cost_reduction": 2000, "time_reduction": 2},
        {"id": "B", "name": "Confirmação escrita", "cost": 0, "cost_reduction": 900, "time_reduction": 1},
        {"id": "C", "name": "Horas extras", "cost": 2000, "cost_reduction": 0, "time_reduction": 1},
        {"id": "D", "name": "Escalar à administração", "cost": 0, "cost_reduction": 0, "time_reduction": 1},
        {"id": "E", "name": "Aceitar risco", "cost": 0, "cost_reduction": 0, "time_reduction": 0},
    ]),
]


def get_activity_by_id(activity_id: int) -> Optional[Activity]:
    """Get activity by ID"""
    for activity in ACTIVITIES:
        if activity.id == activity_id:
            return activity
    return None


def get_resource_by_name(name: str) -> Optional[Resource]:
    """Get resource by name"""
    for resource in RESOURCES:
        if resource.name == name:
            return resource
    return None


def calculate_project_weeks() -> int:
    """Calculate number of weeks in project"""
    delta = PROJECT_DEADLINE - PROJECT_START
    return (delta.days // 7) + 1


if __name__ == "__main__":
    print("ProDegeit Project Data Models")
    print("=" * 50)
    print(f"\nProject Period: {PROJECT_START.strftime('%Y-%m-%d')} to {PROJECT_DEADLINE.strftime('%Y-%m-%d')}")
    print(f"Budget: €{BUDGET_MAX:,} (€{BUDGET_WITH_RESERVE:,} with reserve)")
    print(f"\nActivities: {len(ACTIVITIES)}")
    print(f"Resources: {len(RESOURCES)} ({sum(1 for r in RESOURCES if r.is_core_team)} core team)")
    print(f"Risks: {len(RISKS)}")
    print(f"\nProject Duration: {calculate_project_weeks()} weeks")
