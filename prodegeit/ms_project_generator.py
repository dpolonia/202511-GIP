"""
ProDegeit Project - MS Project XML Generator
Generates MS Project-compatible XML file
"""

from datetime import datetime, timedelta
from typing import Dict, List
from lxml import etree
from data_models import PROJECT_START, ACTIVITIES, RESOURCES


class MSProjectXMLGenerator:
    """Generates MS Project XML format"""
    
    def __init__(self, schedule: Dict, allocation_map: Dict, resource_list: List):
        """
        Initialize XML generator
        
        Args:
            schedule: Activity schedule from allocator
            allocation_map: Resource allocation mapping
            resource_list: List of resources
        """
        self.schedule = schedule
        self.allocation_map = allocation_map
        self.resources = resource_list
        
    def generate_xml(self, output_path: str):
        """
        Generate complete MS Project XML file
        
        Args:
            output_path: Path to save XML file
        """
        print(f"\nGenerating MS Project XML: {output_path}")
        
        # Create root element
        root = etree.Element("Project", xmlns="http://schemas.microsoft.com/project")
        
        # Add project properties
        self._add_project_properties(root)
        
        # Add calendars
        self._add_calendars(root)
        
        # Add tasks
        self._add_tasks(root)
        
        # Add resources
        self._add_resources(root)
        
        # Add assignments
        self._add_assignments(root)
        
        # Write to file
        tree = etree.ElementTree(root)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        
        print(f"✓ MS Project XML generated successfully")
    
    def _add_project_properties(self, root):
        """Add project-level properties"""
        etree.SubElement(root, "SaveVersion").text = "14"
        etree.SubElement(root, "Name").text = "ProDegeit Equipment Installation"
        etree.SubElement(root, "Title").text = "ProDegeit Project Plan"
        etree.SubElement(root, "Author").text = "ProDegeit Team"
        etree.SubElement(root, "Company").text = "ProDegeit International"
        etree.SubElement(root, "StartDate").text = PROJECT_START.strftime("%Y-%m-%dT08:00:00")
        etree.SubElement(root, "ScheduleFromStart").text = "1"
        etree.SubElement(root, "CurrentDate").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        etree.SubElement(root, "CalendarUID").text = "1"
        etree.SubElement(root, "DefaultStartTime").text = "08:00:00"
        etree.SubElement(root, "DefaultFinishTime").text = "17:00:00"
        etree.SubElement(root, "HoursPerDay").text = "8.0"
        etree.SubElement(root, "HoursPerWeek").text = "40.0"
        etree.SubElement(root, "DaysPerMonth").text= "20"
        etree.SubElement(root, "CurrencySymbol").text = "€"
    
    def _add_calendars(self, root):
        """Add project calendars"""
        calendars = etree.SubElement(root, "Calendars")
        
        # Standard calendar (Mon-Fri, 8h/day)
        calendar = etree.SubElement(calendars, "Calendar")
        etree.SubElement(calendar, "UID").text = "1"
        etree.SubElement(calendar, "Name").text = "Standard"
        etree.SubElement(calendar, "IsBaseCalendar").text = "1"
        
        # Define weekdays
        weekdays = etree.SubElement(calendar, "WeekDays")
        
        # Sunday (non-working)
        sunday = etree.SubElement(weekdays, "WeekDay")
        etree.SubElement(sunday, "DayType").text = "1"
        etree.SubElement(sunday, "DayWorking").text = "0"
        
        # Monday-Friday (working days)
        for day in range(2, 7):  # 2=Monday, 6=Friday
            weekday = etree.SubElement(weekdays, "WeekDay")
            etree.SubElement(weekday, "DayType").text = str(day)
            etree.SubElement(weekday, "DayWorking").text = "1"
            
            working_times = etree.SubElement(weekday, "WorkingTimes")
            working_time = etree.SubElement(working_times, "WorkingTime")
            etree.SubElement(working_time, "FromTime").text = "08:00:00"
            etree.SubElement(working_time, "ToTime").text = "17:00:00"
        
        # Saturday (non-working)
        saturday = etree.SubElement(weekdays, "WeekDay")
        etree.SubElement(saturday, "DayType").text = "7"
        etree.SubElement(saturday, "DayWorking").text = "0"
    
    def _add_tasks(self, root):
        """Add all project tasks"""
        tasks = etree.SubElement(root, "Tasks")
        
        for activity in ACTIVITIES:
            task = etree.SubElement(tasks, "Task")
            
            schedule_info = self.schedule.get(activity.id, {})
            start_date = schedule_info.get('start')
            end_date = schedule_info.get('end')
            
            etree.SubElement(task, "UID").text = str(activity.id)
            etree.SubElement(task, "ID").text = str(activity.id)
            etree.SubElement(task, "Name").text = activity.name
            etree.SubElement(task, "Type").text = "1"  # Fixed duration
            etree.SubElement(task, "IsNull").text = "0"
            
             # Convert days to hours (8 hours per day)
            duration_hours = activity.duration_days * 8
            etree.SubElement(task, "Duration").text = f"PT{duration_hours}H0M0S"
            
            if start_date:
                etree.SubElement(task, "Start").text = start_date.strftime("%Y-%m-%dT08:00:00")
            if end_date:
                etree.SubElement(task, "Finish").text = end_date.strftime("%Y-%m-%dT17:00:00")
            
            # Add predecessors
            if activity.predecessors:
                predecessor_links = etree.SubElement(task, "PredecessorLink")
                for pred_id in activity.predecessors:
                    pred_link = etree.SubElement(predecessor_links, "PredecessorLink")
                    etree.SubElement(pred_link, "PredecessorUID").text = str(pred_id)
                    etree.SubElement(pred_link, "Type").text = "1"  # Finish-to-Start
            
            etree.SubElement(task, "PercentComplete").text = "0"
            etree.SubElement(task, "ConstraintType").text = "0"  # As Soon As Possible
    
    def _add_resources(self, root):
        """Add all project resources"""
        resources_elem = etree.SubElement(root, "Resources")
        
        for i, resource in enumerate(self.resources, start=1):
            resource_elem = etree.SubElement(resources_elem, "Resource")
            
            etree.SubElement(resource_elem, "UID").text = str(i)
            etree.SubElement(resource_elem, "ID").text = str(i)
            etree.SubElement(resource_elem, "Name").text = resource.name
            etree.SubElement(resource_elem, "Type").text = "1"  # Work resource
            etree.SubElement(resource_elem, "IsNull").text = "0"
            
            # Standard rate (cost per hour)
            etree.SubElement(resource_elem, "StandardRate").text = str(resource.cost_per_hour * 8)  # Daily rate
            etree.SubElement(resource_elem, "OvertimeRate").text = str(resource.cost_per_hour * 1.5 * 8)
            
            # Max units (availability percentage)
            max_units = int(resource.availability_pct * 100)
            etree.SubElement(resource_elem, "MaxUnits").text = f"{max_units}%"
    
    def _add_assignments(self, root):
        """Add resource assignments to tasks"""
        assignments = etree.SubElement(root, "Assignments")
        
        assignment_uid = 1
        
        for activity_id, resource_names in self.allocation_map.items():
            if not resource_names:
                continue
            
            # Calculate units per resource (split evenly if multiple resources)
            units_per_resource = 100 // len(resource_names) if resource_names else 0
            
            for resource_name in resource_names:
                # Find resource UID
                resource_uid = None
                for i, res in enumerate(self.resources, start=1):
                    if res.name == resource_name:
                        resource_uid = i
                        break
                
                if not resource_uid:
                    continue
                
                assignment = etree.SubElement(assignments, "Assignment")
                
                etree.SubElement(assignment, "UID").text = str(assignment_uid)
                etree.SubElement(assignment, "TaskUID").text = str(activity_id)
                etree.SubElement(assignment, "ResourceUID").text = str(resource_uid)
                etree.SubElement(assignment, "Units").text = f"{units_per_resource}%"
                
                assignment_uid += 1


def generate_ms_project_xml(schedule: Dict, allocation_map: Dict, 
                           resource_list: List, output_path: str):
    """
    Generate MS Project XML file
    
    Args:
        schedule: Activity schedule
        allocation_map: Resource allocations
        resource_list: List of resources
        output_path: Output file path
    """
    generator = MSProjectXMLGenerator(schedule, allocation_map, resource_list)
    generator.generate_xml(output_path)


if __name__ == "__main__":
    # Test with sample data
    print("Testing MS Project XML Generator...")
    
    # Simple test schedule
    test_schedule = {
        1: {'start': PROJECT_START, 'end': PROJECT_START + timedelta(days=5), 'duration_days': 5}
    }
    
    test_allocation = {
        1: ['Francisco', 'Susana', 'Tim']
    }
    
    output_file = "output/test_project.xml"
    generate_ms_project_xml(test_schedule, test_allocation, RESOURCES, output_file)
    print(f"Test XML generated: {output_file}")
