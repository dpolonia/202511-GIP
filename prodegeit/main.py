"""
ProDegeit Project - Main Orchestrator
Coordinates all modules to generate complete project plan
"""

import os
import sys
from datetime import datetime
import argparse

from data_models import (
    ACTIVITIES, RESOURCES, RISKS, PROJECT_START, PROJECT_DEADLINE,
    BUDGET_MAX, BUDGET_WITH_RESERVE
)
from resource_allocator import run_allocation
from risk_analyzer import run_risk_analysis
from ms_project_generator import generate_ms_project_xml
from excel_generator import ExcelGenerator
from ai_assistant import get_ai_assistant
from academic_references import get_reference_manager


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='ProDegeit Project Management Solution')
    parser.add_argument('--xml-only', action='store_true', help='Generate only MS Project XML')
    parser.add_argument('--report-only', action='store_true', help='Generate only PDF report')
    parser.add_argument('--verbose', action='store_true', help='Show detailed progress')
    
    args = parser.parse_args()
    
    print("="*70)
    print("PRODEGEIT PROJECT MANAGEMENT SOLUTION")
    print("AI-Enhanced Project Planning System")
    print("="*70)
    print(f"\nProject: Equipment Acquisition and Installation")
    print(f"Period: {PROJECT_START.strftime('%Y-%m-%d')} to {PROJECT_DEADLINE.strftime('%Y-%m-%d')}")
    print(f"Budget: €{BUDGET_MAX:,} (€{BUDGET_WITH_RESERVE:,} with reserve)")
    print(f"\nActivities: {len(ACTIVITIES)}")
    print(f"Resources: {len(RESOURCES)}")
    print(f"Risks: {len(RISKS)}")
    
    # Initialize output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # STEP 1: Resource Allocation
    if not args.report_only:
        print("\n" + "="*70)
        print("STEP 1: RESOURCE ALLOCATION")
        print("="*70)
        
        allocator, allocation_results = run_allocation()
        
        # Check budget compliance
        if allocation_results['estimated_cost'] <= BUDGET_WITH_RESERVE:
            print(f"\n✓ Budget: COMPLIANT (€{allocation_results['estimated_cost']:,.2f} / €{BUDGET_WITH_RESERVE:,})")
            budget_status = "within budget"
        else:
            print(f"\n✗ Budget: EXCEEDED (€{allocation_results['estimated_cost']:,.2f} / €{BUDGET_WITH_RESERVE:,})")
            budget_status = "over budget"
        
        # Check timeline compliance
        if allocation_results['completion_date'] <= PROJECT_DEADLINE:
            buffer_days = (PROJECT_DEADLINE - allocation_results['completion_date']).days
            print(f"✓ Timeline: COMPLIANT ({buffer_days} days buffer)")
            timeline_status = "on track"
        else:
            delay_days = (allocation_results['completion_date'] - PROJECT_DEADLINE).days
            print(f"✗ Timeline: DELAYED ({delay_days} days late)")
            timeline_status = "delayed"
    
    # STEP 2: Risk Analysis
    if not args.report_only:
        print("\n" + "="*70)
        print("STEP 2: RISK ANALYSIS")
        print("="*70)
        
        risk_analyzer, risk_results = run_risk_analysis()
        
        # Update costs with risk mitigation
        if risk_results['optimal_strategy']:
            total_with_risk = (allocation_results['estimated_cost'] + 
                              risk_results['optimal_strategy']['total_cost'])
            print(f"\nTotal Cost with Risk Mitigation: €{total_with_risk:,.2f}")
            
            if total_with_risk <= BUDGET_WITH_RESERVE:
                print(f"✓ Still within budget (€{BUDGET_WITH_RESERVE - total_with_risk:,.2f} remaining)")
            else:
                print(f"✗ Exceeds budget by €{total_with_risk - BUDGET_WITH_RESERVE:,.2f}")
    
    # STEP 3: Generate MS Project XML
    if not args.report_only:
        print("\n" + "="*70)
        print("STEP 3: MS PROJECT XML GENERATION")
        print("="*70)
        
        xml_path = os.path.join(output_dir, "ProDegeit_Project.xml")
        generate_ms_project_xml(
            allocation_results['schedule'],
            {k: v for k, v in allocation_results['allocation_map'].items()},
            RESOURCES,
            xml_path
        )
    
    # STEP 4: Generate Excel Reports
    if not args.report_only:
        print("\n" + "="*70)
        print("STEP 4: EXCEL REPORTS GENERATION")
        print("="*70)
        
        excel_gen = ExcelGenerator()
        
        # Resource workbook
        resource_path = os.path.join(output_dir, "ProDegeit_Resources.xlsx")
        excel_gen.generate_resource_workbook(resource_path)
        
        # Allocation workbook
        allocation_path = os.path.join(output_dir, "ProDegeit_Allocation.xlsx")
        excel_gen.generate_allocation_workbook(allocation_results, allocation_path)
    
    # STEP 5: Gather Academic References
    print("\n" + "="*70)
    print("STEP 5: ACADEMIC REFERENCES")
    print("="*70)
    
    ref_manager = get_reference_manager()
    if ref_manager.available:
        print("Gathering academic references from Scopus...")
        try:
            references = ref_manager.gather_all_references(max_per_topic=3)
            print(f"✓ Found {len(references)} relevant articles")
        except Exception as e:
            print(f"! Using fallback references: {e}")
            references = []
    else:
        print("Using fallback academic references")
        references = []
    
    # STEP 6: Generate AI-Enhanced Content
    print("\n" + "="*70)
    print("STEP 6: AI CONTENT GENERATION")
    print("="*70)
    
    ai_assistant = get_ai_assistant()
    
    if ai_assistant.available:
        print("Generating AI-enhanced content...")
        
        # Executive summary
        exec_summary = ai_assistant.generate_executive_summary(
            {
                'start_date': PROJECT_START.strftime('%Y-%m-%d'),
                'deadline': PROJECT_DEADLINE.strftime('%Y-%m-%d'),
                'budget_max': BUDGET_MAX,
                'budget_with_reserve': BUDGET_WITH_RESERVE,
            },
            {
                'total_activities': len(ACTIVITIES),
                'total_resources': allocation_results['total_resources'],
                'estimated_cost': allocation_results['estimated_cost'],
                'completion_date': allocation_results['completion_date'].strftime('%Y-%m-%d'),
                'budget_status': budget_status,
                'timeline_status': timeline_status,
            },
            {
                'total_risks': len(RISKS),
                'total_expected_cost': risk_results['expected_case']['total_expected_cost'],
                'mitigation_cost': risk_results['optimal_strategy']['total_cost'] if risk_results['optimal_strategy'] else 0,
                'expected_cost_after': risk_results['residual_risk']['expected_cost'],
            }
        )
        
        print("✓ Executive summary generated")
        
        # Conclusions
        conclusions = ai_assistant.generate_conclusions(
            {
                'allocated': allocation_results['estimated_cost'] + (risk_results['optimal_strategy']['total_cost'] if risk_results.get('optimal_strategy') else 0),
                'limit': BUDGET_WITH_RESERVE,
                'remaining': BUDGET_WITH_RESERVE - allocation_results['estimated_cost'],
                'status': budget_status,
            },
            {
                'projected_completion': allocation_results['completion_date'].strftime('%Y-%m-%d'),
                'deadline': PROJECT_DEADLINE.strftime('%Y-%m-%d'),
                'buffer_days': (PROJECT_DEADLINE - allocation_results['completion_date']).days,
                'status': timeline_status,
            },
            [
                "Monitor critical path activities closely",
                "Implement selected risk mitigations immediately",
                "Conduct weekly resource utilization reviews",
                "Maintain communication with core team during vacation periods"
            ]
        )
        
        print("✓ Conclusions generated")
    else:
        print("! AI assistant not available - using fallback content")
        exec_summary = "AI content generation unavailable. Please review generated data files."
        conclusions = "Review the generated Excel and XML files for complete project information."
    
    # STEP 7: Generate PDF Report
    print("\n" + "="*70)
    print("STEP 7: PDF REPORT GENERATION")
    print("="*70)
    
    print("Note: Full PDF report generation requires additional implementation.")
    print("Current deliverables ready:")
    print(f"  - MS Project XML: {os.path.abspath(xml_path) if not args.report_only else 'Skipped'}")
    print(f"  - Resource Excel: {os.path.abspath(resource_path) if not args.report_only else 'Skipped'}")
    print(f"  - Allocation Excel: {os.path.abspath(allocation_path) if not args.report_only else 'Skipped'}")
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print("FINAL PROJECT SUMMARY")
    print("="*70)
    
    print(f"\n📊 Project Statistics:")
    print(f"  Total Activities: {len(ACTIVITIES)}")
    print(f"  Resources Used: {allocation_results['total_resources']}")
    print(f"  Critical Path: {len(allocator.get_critical_path())} activities")
    
    print(f"\n💰 Financial Summary:")
    print(f"  Activity Costs: €{allocation_results['estimated_cost'] - allocation_results['core_team_cost']:,.2f}")
    print(f"  Core Team Costs: €{allocation_results['core_team_cost']:,.2f}")
    print(f"  Risk Mitigation: €{risk_results['optimal_strategy']['total_cost'] if risk_results.get('optimal_strategy') else 0:,.2f}")
    total_project_cost = allocation_results['estimated_cost'] + (risk_results['optimal_strategy']['total_cost'] if risk_results.get('optimal_strategy') else 0)
    print(f"  TOTAL: €{total_project_cost:,.2f}")
    print(f"  Budget Status: {budget_status.upper()}")
    
    print(f"\n📅 Schedule Summary:")
    print(f"  Start Date: {PROJECT_START.strftime('%Y-%m-%d')}")
    print(f"  Projected End: {allocation_results['completion_date'].strftime('%Y-%m-%d')}")
    print(f"  Deadline: {PROJECT_DEADLINE.strftime('%Y-%m-%d')}")
    print(f"  Status: {timeline_status.upper()}")
    
    print(f"\n⚠️  Risk Summary:")
    print(f"  Identified Risks: {len(RISKS)}")
    print(f"  Expected Impact (before): €{risk_results['expected_case']['total_expected_cost']:,.2f}")
    print(f"  Expected Impact (after): €{risk_results['residual_risk']['expected_cost']:,.2f}")
    print(f"  Risk Reduction: {((1 - risk_results['residual_risk']['expected_cost'] / risk_results['expected_case']['total_expected_cost']) * 100):.1f}%")
    
    # API Usage Statistics
    if ai_assistant.available:
        usage_stats = ai_assistant.get_usage_stats()
        print(f"\n🤖 AI API Usage:")
        print(f"  Model: {usage_stats['model']}")
        print(f"  Total Tokens: {usage_stats['total_tokens']:,}")
        print(f"    - Input: {usage_stats['input_tokens']:,}")
        print(f"    - Output: {usage_stats['output_tokens']:,}")
        print(f"  Estimated Cost: ${usage_stats['estimated_cost_usd']:.4f}")
        print(f"  Pricing: ${usage_stats['pricing']['input']:.2f}/${usage_stats['pricing']['output']:.2f} per 1M tokens")
    
    print("\n" + "="*70)
    print("✓ PROJECT PLANNING COMPLETE")
    print("="*70)
    
    # Save summary to text file
    summary_path = os.path.join(output_dir, "ProDegeit_Summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("PRODEGEIT PROJECT SUMMARY\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Cost: €{total_project_cost:,.2f}\n")
        f.write(f"Budget: €{BUDGET_WITH_RESERVE:,}\n")
        f.write(f"Status: {budget_status}\n\n")
        f.write(f"Completion: {allocation_results['completion_date'].strftime('%Y-%m-%d')}\n")
        f.write(f"Deadline: {PROJECT_DEADLINE.strftime('%Y-%m-%d')}\n")
        f.write(f"Timeline: {timeline_status}\n\n")
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write(exec_summary + "\n\n")
        f.write("CONCLUSIONS\n")
        f.write("-"*70 + "\n")
        f.write(conclusions + "\n")
        
        # Add API usage stats
        if ai_assistant.available:
            usage_stats = ai_assistant.get_usage_stats()
            f.write("\n" + "="*70 + "\n")
            f.write("AI API USAGE STATISTICS\n")
            f.write("="*70 + "\n")
            f.write(f"Model: {usage_stats['model']}\n")
            f.write(f"Total Tokens: {usage_stats['total_tokens']:,}\n")
            f.write(f"  - Input Tokens: {usage_stats['input_tokens']:,}\n")
            f.write(f"  - Output Tokens: {usage_stats['output_tokens']:,}\n")
            f.write(f"Estimated Cost: ${usage_stats['estimated_cost_usd']:.4f} USD\n")
            f.write(f"Pricing: ${usage_stats['pricing']['input']:.2f}/${usage_stats['pricing']['output']:.2f} per 1M tokens\n")
    
    print(f"\nSummary saved to: {os.path.abspath(summary_path)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
