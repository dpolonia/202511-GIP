"""
ProDegeit Project - Resource Allocator
Implements intelligent resource allocation algorithm with skill-based matching
""" 

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import copy

from data_models import (
    Activity, Resource, ACTIVITIES, RESOURCES, PROJECT_START,
    HOURS_PER_DAY, calculate_project_weeks, get_activity_by_id
)


class ResourceAllocator:
    """Manages resource allocation to project activities"""
    
    def __init__(self, activities: List[Activity], resources: List[Resource]):
        """
        Initialize the resource allocator
        
        Args:
            activities: List of project activities
            resources: List of available resources
        """
        self.activities = copy.deepcopy(activities)
        self.resources = copy.deepcopy(resources)
        self.allocation_map = {}  # {activity_id: [resource_names]}
        self.schedule = {}  # {activity_id: {'start': date, 'end': date}}
        
    def calculate_activity_schedule(self) -> Dict:
        """
        Calculate start and end dates for all activities based on predecessors
        Uses forward pass of CPM (Critical Path Method)
        
        Returns:
            Dictionary of activity schedules
        """
        schedule = {}
        
        # Initialize all activities
        for activity in self.activities:
            schedule[activity.id] = {
                'start': None,
                'end': None,
                'duration_days': activity.duration_days
            }
        
        # Forward pass: calculate earliest start/end
        max_iterations = len(self.activities) * 2  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            for activity in self.activities:
                if schedule[activity.id]['start'] is not None:
                    continue  # Already scheduled
                
                # Check if all predecessors are scheduled
                predecessors_complete = True
                latest_predecessor_end = PROJECT_START
                
                for pred_id in activity.predecessors:
                    if schedule[pred_id]['end'] is None:
                        predecessors_complete = False
                        break
                    latest_predecessor_end = max(latest_predecessor_end, schedule[pred_id]['end'])
                
                if predecessors_complete:
                    # Schedule this activity
                    start_date = latest_predecessor_end if activity.predecessors else PROJECT_START
                    
                    # Ensure start is a working day (Monday)
                    while start_date.weekday() > 4:  # 5=Saturday, 6=Sunday
                        start_date += timedelta(days=1)
                    
                    # Calculate end date (working days only)
                    end_date = self._add_working_days(start_date, activity.duration_days)
                    
                    schedule[activity.id]['start'] = start_date
                    schedule[activity.id]['end'] = end_date
                    progress_made = True
            
            if not progress_made:
                break  # All schedulable activities have been scheduled
        
        self.schedule = schedule
        return schedule
    
    def _add_working_days(self, start_date: datetime, working_days: int) -> datetime:
        """
        Add working days to a date (Monday-Friday only)
        
        Args:
            start_date: Starting date
            working_days: Number of working days to add
            
        Returns:
            End date after adding working days
        """
        current_date = start_date
        days_added = 0
        
        while days_added < working_days:
            current_date += timedelta(days=1)
            # Only count weekdays
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                days_added += 1
        
        return current_date
    
    def allocate_resources(self, max_tasks_per_resource: int = 6,
                          duration_adjustment_factor: int = 2) -> Dict:
        """
        Main resource allocation algorithm
        
        Args:
            max_tasks_per_resource: Maximum tasks a resource can be assigned to
            duration_adjustment_factor: Hours per skill point for duration adjustment
            
        Returns:
            Allocation results dictionary
        """
        print("Starting resource allocation...")
        
        # Step 1: Calculate activity schedule
        self.calculate_activity_schedule()
        
        # Step 2: Allocate resources to each activity
        for activity in sorted(self.activities, key=lambda a: a.id):
            print(f"\nAllocating resources for Activity {activity.id}: {activity.name}")
            
            # Find best matching resources
            allocated = self._allocate_to_activity(activity, max_tasks_per_resource)
            
            if allocated:
                self.allocation_map[activity.id] = allocated
                print(f"  ✓ Allocated: {', '.join([r.name for r in allocated])}")
                
                # Adjust duration based on skill surplus
                adjusted_duration = self._adjust_duration(
                    activity, allocated, duration_adjustment_factor
                )
                if adjusted_duration != activity.duration_days:
                    print(f"  Duration adjusted: {activity.duration_days}d → {adjusted_duration}d")
                    activity.duration_days = adjusted_duration
                    # Recalculate schedule with new duration
                    self.calculate_activity_schedule()
            else:
                print(f"  ✗ WARNING: Could not allocate enough resources!")
                # Assign whoever is available as fallback
                self._allocate_fallback(activity, max_tasks_per_resource)
        
        # Step 3: Calculate costs
        results = self._calculate_results()
        
        return results
    
    def _allocate_to_activity(self, activity: Activity, max_tasks: int) -> List[Resource]:
        """
        Allocate best matching resources to an activity
        
        Args:
            activity: Activity to allocate resources to
            max_tasks: Maximum tasks per resource
            
        Returns:
            List of allocated resources
        """
        # Get activity week(s)
        schedule = self.schedule.get(activity.id)
        if not schedule or not schedule['start']:
            activity_week = 1
        else:
            delta = schedule['start'] - PROJECT_START
            activity_week = (delta.days // 7) + 1
        
        # Find candidate resources
        candidates = []
        for resource in self.resources:
            # Check availability
            if not resource.is_available(activity_week):
                continue
            
            # Check task limit
            if not resource.can_take_task(max_tasks):
                continue
            
            # Check skill match
            matches, surplus = resource.matches_skills(activity.skill_requirements)
            if matches:
                candidates.append({
                    'resource': resource,
                    'surplus': surplus,
                    'cost': resource.cost_per_hour
                })
        
        if not candidates:
            return []
        
        # Sort by: 1) skill surplus (descending), 2) cost (ascending)
        candidates.sort(key=lambda x: (-x['surplus'], x['cost']))
        
        # Allocate top N resources
        allocated = []
        for i in range(min(activity.num_people, len(candidates))):
            resource = candidates[i]['resource']
            allocated.append(resource)
            resource.assigned_tasks.append(activity.id)
        
        return allocated
    
    def _allocate_fallback(self, activity: Activity, max_tasks: int):
        """Fallback allocation when normal allocation fails"""
        schedule = self.schedule.get(activity.id)
        activity_week = 1 if not schedule or not schedule['start'] else \
                       ((schedule['start'] - PROJECT_START).days // 7) + 1
        
        allocated = []
        for resource in self.resources:
            if len(allocated) >= activity.num_people:
                break
            if resource.is_available(activity_week) and resource.can_take_task(max_tasks):
                allocated.append(resource)
                resource.assigned_tasks.append(activity.id)
        
        if allocated:
            self.allocation_map[activity.id] = allocated
            print(f"  ! Fallback allocated: {', '.join([r.name for r in allocated])}")
    
    def _adjust_duration(self, activity: Activity, allocated_resources: List[Resource],
                        factor: int) -> int:
        """
        Adjust activity duration based on resource skill surplus
        
        Args:
            activity: The activity
            allocated_resources: Allocated resources
            factor: Hours per skill point difference
            
        Returns:
            Adjusted duration in days
        """
        # Calculate total skill surplus
        total_surplus = 0
        for resource in allocated_resources:
            for skill, required_level in activity.skill_requirements.items():
                if required_level > 0:
                    resource_level = resource.skills.get(skill, 0)
                    total_surplus += max(0, resource_level - required_level)
        
        # Calculate adjustment
        base_hours = activity. num_people * activity.duration_days * HOURS_PER_DAY
        adjustment_hours = factor * total_surplus
        
        # Apply adjustment (can't go below 50% of original duration)
        adjusted_hours = max(base_hours * 0.5, base_hours - adjustment_hours)
        
        # Convert back to days
        adjusted_days = int((adjusted_hours / (activity.num_people * HOURS_PER_DAY)) + 0.5)
        
        # Ensure at least 1 day
        return max(1, adjusted_days)
    
    def _calculate_results(self) -> Dict:
        """Calculate final results including costs and timelines"""
        # Calculate costs for each activity
        total_cost = 0
        activity_costs = {}
        
        for activity in self.activities:
            allocated = self.allocation_map.get(activity.id, [])
            
            if not allocated:
                activity_costs[activity.id] = 0
                continue
            
            # Calculate hours per resource
            hours_per_resource = (activity.duration_days * HOURS_PER_DAY) / len(allocated) if allocated else 0
            
            # Calculate cost
            activity_cost = sum(r.cost_per_hour * hours_per_resource for r in allocated)
            activity_costs[activity.id] = activity_cost
            total_cost += activity_cost
            
            # Update resource totals
            for resource in allocated:
                resource.total_hours += hours_per_resource
                resource.total_cost += resource.cost_per_hour * hours_per_resource
        
        # Add core team fixed costs
        # Core team works 8h/day for entire project duration
        project_days = (max(s['end'] for s in self.schedule.values() if s['end']) - PROJECT_START).days
        project_working_days = project_days * (5/7)  # Approximate working days
        
        core_team_cost = 0
        for resource in self.resources:
            if resource.is_core_team:
                hours = project_working_days * HOURS_PER_DAY * resource.availability_pct
                cost = hours * resource.cost_per_hour
                core_team_cost += cost
                resource.total_hours += hours
                resource.total_cost += cost
        
        total_cost += core_team_cost
        
        # Get completion date
        completion_date = max(s['end'] for s in self.schedule.values() if s['end'])
        
        results = {
            'total_activities': len(self.activities),
            'total_resources': len([r for r in self.resources if r.assigned_tasks or r.is_core_team]),
            'estimated_cost': total_cost,
            'core_team_cost': core_team_cost,
            'activity_costs': activity_costs,
            'completion_date': completion_date,
            'schedule': self.schedule,
            'allocation_map': {aid: [r.name for r in resources] 
                             for aid, resources in self.allocation_map.items()},
            'resource_utilization': {r.name: {
                'hours': r.total_hours,
                'cost': r.total_cost,
                'tasks': len(r.assigned_tasks)
            } for r in self.resources if r.total_hours > 0}
        }
        
        return results
    
    def get_critical_path(self) -> List[int]:
        """
        Identify critical path (longest path through the network)
        
        Returns:
            List of activity IDs on critical path
        """
        # Calculate latest start/finish times (backward pass)
        latest_finish = {}
        project_end = max(s['end'] for s in self.schedule.values() if s['end'])
        
        # Initialize
        for activity in self.activities:
            latest_finish[activity.id] = project_end
        
        # Backward pass
        for activity in sorted(self.activities, key=lambda a: -a.id):
            # Find minimum latest start of successors
            successors = [a for a in self.activities if activity.id in a.predecessors]
            
            if successors:
                min_successor_start = min(
                    latest_finish[s.id] - timedelta(days=self.schedule[s.id]['duration_days'])
                    for s in successors
                )
                activity_duration = timedelta(days=self.schedule[activity.id]['duration_days'])
                latest_finish[activity.id] = min_successor_start
            else:
                latest_finish[activity.id] = project_end
        
        # Identify critical activities (earliest start = latest start)
        critical_path = []
        for activity in self.activities:
            earliest_start = self.schedule[activity.id]['start']
            latest_start = latest_finish[activity.id] - timedelta(
                days=self.schedule[activity.id]['duration_days']
            )
            
            # If dates match (or very close), it's on critical path
            if earliest_start and abs((earliest_start - latest_start).days) <= 1:
                critical_path.append(activity.id)
        
        return sorted(critical_path)


def run_allocation() -> Tuple[ResourceAllocator, Dict]:
    """
    Run the complete resource allocation process
    
    Returns:
        Tuple of (allocator instance, results dictionary)
    """
    allocator = ResourceAllocator(ACTIVITIES, RESOURCES)
    results = allocator.allocate_resources()
    
    # Print summary
    print("\n" + "="*70)
    print("RESOURCE ALLOCATION SUMMARY")
    print("="*70)
    print(f"Total Activities: {results['total_activities']}")
    print(f"Resources Used: {results['total_resources']}")
    print(f"Estimated Cost: €{results['estimated_cost']:,.2f}")
    print(f"  - Core Team Cost: €{results['core_team_cost']:,.2f}")
    print(f"  - Activity Costs: €{results['estimated_cost'] - results['core_team_cost']:,.2f}")
    print(f"Completion Date: {results['completion_date'].strftime('%Y-%m-%d')}")
    
    critical_path = allocator.get_critical_path()
    print(f"\nCritical Path: Activities {critical_path}")
    
    return allocator, results


if __name__ == "__main__":
    print("ProDegeit Resource Allocator")
    print("="*70)
    
    allocator, results = run_allocation()
    
    print("\n" + "="*70)
    print("RESOURCE UTILIZATION")
    print("="*70)
    
    for resource_name, util in sorted(
        results['resource_utilization'].items(),
        key=lambda x: x[1]['cost'],
        reverse=True
    ):
        print(f"\n{resource_name}:")
        print(f"  Hours: {util['hours']:.1f}")
        print(f"  Cost: €{util['cost']:,.2f}")
        print(f"  Tasks: {util['tasks']}")
