"""
ProDegeit Project - Risk Analyzer
Analyzes project risks and optimizes mitigation strategies
"""

from typing import List, Dict, Tuple, Optional
import itertools
from data_models import Risk, RISKS, get_activity_by_id


class RiskAnalyzer:
    """Analyzes and manages project risks"""
    
    def __init__(self, risks: List[Risk]):
        """
        Initialize risk analyzer
        
        Args:
            risks: List of identified risks
        """
        self.risks = risks
        self.mitigation_selections = {}
    
    def calculate_worst_case(self) -> Dict:
        """
        Calculate worst-case scenario (all risks occur)
        
        Returns:
            Dictionary with worst-case impact
        """
        total_cost_impact = sum(r.cost_impact for r in self.risks)
        total_time_impact = sum(r.time_impact_days for r in self.risks)
        
        return {
            'total_cost': total_cost_impact,
            'total_time_days': total_time_impact,
            'risks': [(r.id, r.name, r.cost_impact, r.time_impact_days) for r in self.risks]
        }
    
    def calculate_expected_value_scenario(self) -> Dict:
        """
        Calculate expected value scenario (probability-weighted)
        
        Returns:
            Dictionary with expected values
        """
        total_expected_cost = sum(r.expected_value() for r in self.risks)
        total_expected_time = sum(r.probability * r.time_impact_days for r in self.risks)
        
        return {
            'total_expected_cost': total_expected_cost,
            'total_expected_time': total_expected_time,
            'risks': [(r.id, r.name, r.expected_value(), r.probability * r.time_impact_days) 
                     for r in self.risks]
        }
    
    def optimize_mitigation_strategy(self, budget_constraint: Optional[float] = None) -> Dict:
        """
        Optimize mitigation strategy selection to minimize total expected cost
        
        Args:
            budget_constraint: Maximum mitigation budget (optional)
            
        Returns:
            Dictionary with optimal mitigation strategy
        """
        print("\nOptimizing risk mitigation strategy...")
        
        best_strategy = None
        best_net_benefit = float('-inf')
        
        # Try all combinations of mitigation options
        mitigation_combinations = []
        for risk in self.risks:
            mitigation_combinations.append(risk.mitigation_options)
        
        # Generate all possible combinations
        total_combinations = 1
        for options in mitigation_combinations:
            total_combinations *= len(options)
        
        print(f"Evaluating {total_combinations} possible mitigation combinations...")
        
        for combination in itertools.product(*mitigation_combinations):
            # Calculate total cost and benefit
            total_cost = sum(opt['cost'] for opt in combination)
            
            # Check budget constraint
            if budget_constraint and total_cost > budget_constraint:
                continue
            
            # Calculate expected cost reduction
            total_cost_reduction = 0
            total_time_reduction = 0
            
            for i, (risk, mitigation) in enumerate(zip(self.risks, combination)):
                # Expected benefit = probability × (cost_reduction + time_reduction_value)
                # For simplicity, we'll value time reduction at €1000/day
                time_value = 1000
                
                expected_benefit = risk.probability * (
                    mitigation['cost_reduction'] + 
                    mitigation['time_reduction'] * time_value
                )
                total_cost_reduction += expected_benefit
                total_time_reduction += risk.probability * mitigation['time_reduction']
            
            # Net benefit = benefit - cost
            net_benefit = total_cost_reduction - total_cost
            
            if net_benefit > best_net_benefit:
                best_net_benefit = net_benefit
                best_strategy = {
                    'mitigations': list(combination),
                    'total_cost': total_cost,
                    'expected_reduction': total_cost_reduction,
                    'expected_time_reduction': total_time_reduction,
                    'net_benefit': net_benefit
                }
        
        if best_strategy:
            # Store selections
            for i, (risk, mitigation) in enumerate(zip(self.risks, best_strategy['mitigations'])):
                risk.selected_mitigation = mitigation
                self.mitigation_selections[risk.id] = mitigation
            
            print(f"\nOptimal strategy found:")
            print(f"  Total mitigation cost: €{best_strategy['total_cost']:,.2f}")
            print(f"  Expected reduction: €{best_strategy['expected_reduction']:,.2f}")
            print(f"  Net benefit: €{best_strategy['net_benefit']:,.2f}")
            
            for risk, mitigation in zip(self.risks, best_strategy['mitigations']):
                print(f"\n  Risk {risk.id} ({risk.name}):")
                print(f"    Selected: {mitigation['id']} - {mitigation['name']}")
                print(f"    Cost: €{mitigation['cost']:,.2f}")
                print(f"    Reduces: €{mitigation['cost_reduction']:,.2f}, {mitigation['time_reduction']}d")
        
        return best_strategy
    
    def calculate_residual_risk(self) -> Dict:
        """
        Calculate residual risk after mitigation
        
        Returns:
            Dictionary with residual risk values
        """
        total_residual_cost = 0
        total_residual_time = 0
        
        for risk in self.risks:
            if risk.selected_mitigation:
                # Residual impact = original impact - mitigation reduction
                residual_cost = max(0, risk.cost_impact - risk.selected_mitigation['cost_reduction'])
                residual_time = max(0, risk.time_impact_days - risk.selected_mitigation['time_reduction'])
                
                # Expected residual value
                expected_residual_cost = risk.probability * residual_cost
                expected_residual_time = risk.probability * residual_time
            else:
                # No mitigation - full risk remains
                expected_residual_cost = risk.expected_value()
                expected_residual_time = risk.probability * risk.time_impact_days
            
            total_residual_cost += expected_residual_cost
            total_residual_time += expected_residual_time
        
        return {
            'expected_cost': total_residual_cost,
            'expected_time_days': total_residual_time
        }
    
    def generate_risk_register(self) -> List[Dict]:
        """
        Generate complete risk register
        
        Returns:
            List of risk register entries
        """
        register = []
        
        for risk in self.risks:
            activity = get_activity_by_id(risk.activity_id)
            activity_name = activity.name if activity else f"Activity {risk.activity_id}"
            
            entry = {
                'risk_id': risk.id,
                'risk_name': risk.name,
                'activity_id': risk.activity_id,
                'activity_name': activity_name,
                'probability': risk.probability,
                'cost_impact': risk.cost_impact,
                'time_impact_days': risk.time_impact_days,
                'expected_value': risk.expected_value(),
                'selected_mitigation': risk.selected_mitigation,
                'mitigation_options': risk.mitigation_options
            }
            
            if risk.selected_mitigation:
                residual_cost = max(0, risk.cost_impact - risk.selected_mitigation['cost_reduction'])
                residual_time = max(0, risk.time_impact_days - risk.selected_mitigation['time_reduction'])
                
                entry['residual_cost_impact'] = residual_cost
                entry['residual_time_impact'] = residual_time
                entry['residual_expected_value'] = risk.probability * residual_cost
            else:
                entry['residual_cost_impact'] = risk.cost_impact
                entry['residual_time_impact'] = risk.time_impact_days
                entry['residual_expected_value'] = risk.expected_value()
            
            register.append(entry)
        
        return register
    
    def generate_mitigation_summary(self) -> str:
        """
        Generate text summary of mitigation strategy
        
        Returns:
            Formatted summary text
        """
        summary = "RISK MITIGATION SUMMARY\n"
        summary += "="*70 + "\n\n"
        
        for risk in self.risks:
            summary += f"Risk {risk.id}: {risk.name}\n"
            summary += f"  Activity: {risk.activity_id}\n"
            summary += f"  Probability: {risk.probability*100}%\n"
            summary += f"  Impact: €{risk.cost_impact:,} / {risk.time_impact_days} days\n"
            summary += f"  Expected Value: €{risk.expected_value():,.2f}\n"
            
            if risk.selected_mitigation:
                mit = risk.selected_mitigation
                summary += f"\n  Selected Mitigation: {mit['id']} - {mit['name']}\n"
                summary += f"    Cost: €{mit['cost']:,}\n"
                summary += f"    Reduces Impact: €{mit['cost_reduction']:,} / {mit['time_reduction']} days\n"
                
                residual_cost = max(0, risk.cost_impact - mit['cost_reduction'])
                summary += f"    Residual Risk: €{risk.probability * residual_cost:,.2f} expected\n"
            else:
                summary += f"\n  No mitigation selected (accepting risk)\n"
            
            summary += "\n"
        
        return summary


def run_risk_analysis(budget_constraint: Optional[float] = None) -> Tuple[RiskAnalyzer, Dict]:
    """
    Run complete risk analysis
    
    Args:
        budget_constraint: Optional budget limit for mitigations
        
    Returns:
        Tuple of (analyzer instance, analysis results)
    """
    analyzer = RiskAnalyzer(RISKS)
    
    print("ProDegeit Risk Analysis")
    print("="*70)
    
    # Calculate scenarios
    worst_case = analyzer.calculate_worst_case()
    expected_case = analyzer.calculate_expected_value_scenario()
    
    print(f"\nWorst Case (all risks occur):")
    print(f"  Total Cost Impact: €{worst_case['total_cost']:,}")
    print(f"  Total Time Impact: {worst_case['total_time_days']} days")
    
    print(f"\nExpected Case (probability-weighted):")
    print(f"  Expected Cost: €{expected_case['total_expected_cost']:,.2f}")
    print(f"  Expected Time: {expected_case['total_expected_time']:.1f} days")
    
    # Optimize mitigation
    strategy = analyzer.optimize_mitigation_strategy(budget_constraint)
    
    # Calculate residual risk
    residual = analyzer.calculate_residual_risk()
    
    print(f"\nResidual Risk (after mitigation):")
    print(f"  Expected Cost: €{residual['expected_cost']:,.2f}")
    print(f"  Expected Time: {residual['expected_time_days']:.1f} days")
    
    results = {
        'worst_case': worst_case,
        'expected_case': expected_case,
        'optimal_strategy': strategy,
        'residual_risk': residual,
        'risk_register': analyzer.generate_risk_register(),
        'summary': analyzer.generate_mitigation_summary()
    }
    
    return analyzer, results


if __name__ == "__main__":
    analyzer, results = run_risk_analysis()
    
    print("\n" + "="*70)
    print(results['summary'])
    
    print("=" *70)
    print("RISK REGISTER")
    print("="*70)
    
    for entry in results['risk_register']:
        print(f"\nRisk #{entry['risk_id']}: {entry['risk_name']}")
        print(f"  Activity: #{entry['activity_id']} - {entry['activity_name']}")
        print(f"  Original EV: €{entry['expected_value']:,.2f}")
        print(f"  Residual EV: €{entry['residual_expected_value']:,.2f}")
        if entry['selected_mitigation']:
            print(f"  Mitigation: {entry['selected_mitigation']['name']} (€{entry['selected_mitigation']['cost']:,})")
