# ProDegeit AI-Enhanced Project Management Solution

**Automated project planning system using Gemini 2.0 Flash AI and Scopus academic research**

## 📋 Overview

This solution provides a complete, automated approach to solving the ProDegeit case study for project management. It generates:

- ✅ MS Project XML file (importable directly into Microsoft Project)
- ✅ Professional Excel workbooks with resource data and allocation matrices
- ✅ AI-enhanced executive summaries and recommendations
- ✅ Academic references from Scopus database
- ✅ Comprehensive project summary with cost and schedule analysis

## 🎯 Project Results

### Budget Performance
- **Total Cost**: €292,407.33
- **Budget Limit**: €440,000
- **Status**: ✅ **WITHIN BUDGET** (€147,593 remaining)
- **Breakdown**:
  - Core Team Fixed Costs: €119,160
  - Activity Costs: €173,247
  - Risk Mitigation: €0 (selected zero-cost strategies)

### Timeline Performance
- **Start Date**: January 5, 2026
- **Completion Date**: March 16, 2026
- **Deadline**: March 21, 2026
- **Status**: ✅ **ON TRACK** (5 days buffer)

### Resource Allocation
- **Total Activities**: 17
- **Resources Used**: 8 out of 16 available
- **Allocation Efficiency**: Optimized with skill-based matching
- **Constraint**: Max 6 tasks per resource ✅ (all compliant)

### Risk Management
- **Identified Risks**: 3
- **Expected Impact (before)**: €3,700
- **Expected Impact (after)**: €2,875
- **Risk Reduction**: 22.3%
- **Mitigation Cost**: €0 (optimized for zero-cost strategies)

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+ required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file in the parent directory with:
```
GOOGLE_API_KEY=your_gemini_api_key_here
SCOPUS_API_KEY=your_scopus_api_key_here
```

### Run the Solution
```bash
# Run complete analysis
python main.py

# Generate only MS Project XML
python main.py --xml-only

# Verbose output
python main.py --verbose
```

## 📂 Generated Files

All outputs are saved in the `output/` directory:

| File | Description |
|------|-------------|
| `ProDegeit_Project.xml` | MS Project file - import via File > Open in MS Project |
| `ProDegeit_Resources.xlsx` | Resource data, skills matrix, availability calendar |
| `ProDegeit_Allocation.xlsx` | Activity list, allocation matrix, utilization, costs |
| `ProDegeit_Summary.txt` | AI-generated executive summary and conclusions |

## 🧠 AI Integration

### Gemini 2.0 Flash API
- **Executive Summaries**: Professional project overviews
- **Resource Justifications**: Explains why resources were assigned
- **Risk Narratives**: Detailed risk analysis with mitigation rationale
- **Conclusions**: Comprehensive recommendations for project success

### Scopus API
- **Academic References**: Searches for relevant project management literature
- **Topics Covered**:
  - Resource allocation optimization
  - Critical path method
  - Risk management (ISO 31000)
  - Project cash flow
  - Skills-based task assignment
- **Output**: APA 7th edition formatted citations

## 🔧 Technical Architecture

### Module Structure

```
prodegeit/
├── data_models.py           # Core data structures (activities, resources, risks)
├── resource_allocator.py    # CPM scheduling + skill-based allocation
├── risk_analyzer.py         # Risk optimization using expected value
├── ms_project_generator.py  # XML generation for MS Project
├── excel_generator.py       # Professional Excel reports
├── ai_assistant.py          # Gemini API integration
├── academic_references.py   # Scopus API integration
├── main.py                  # Orchestrator
└── requirements.txt         # Dependencies
```

### Key Algorithms

#### 1. Resource Allocation
```python
# Skill-based matching with duration adjustment
adjusted_hours = base_hours - (factor × skill_surplus)

# Where:
# - base_hours = num_people × days × 8
# - factor = 2-3 hours per skill point
# - skill_surplus = (resource_skills - required_skills)
```

#### 2. Risk Mitigation Optimization
```python
# Expected value minimization
net_benefit = probability × (cost_reduction + time_reduction × value_per_day) - mitigation_cost

# Evaluates all 125 combinations (5^3 options)
# Selects strategy maximizing net benefit
```

#### 3. Critical Path Analysis
```python
# Forward pass: Earliest start/finish
# Backward pass: Latest start/finish
# Critical: earliest_start == latest_start
```

## 📊 Key Insights

### Resource Utilization
- **Most Utilized**: Susana (Core Team) - 80% availability, 5 tasks
- **Most Cost-Effective**: Teófilo - €58/hour, petroleum + construction skills
- **Most Valuable**: Ana - €160/hour, 6 skills at level 5-6

### Critical Activities
The system identifies activities with zero float (critical path) to prioritize monitoring.

### Risk Strategy
- **Risk 1** (Server Failure): Accept risk (5% probability, low impact)
- **Risk 2** (Quality Issues): Free regular evaluations (saves €4,000)
- **Risk 3** (Priority Conflicts): Written confirmation (saves €900)

## 🎓 Academic Foundation

The solution incorporates best practices from:
- **PMBOK Guide** (7th Edition) - Resource leveling, risk management
- **ISO 31000:2009** - Risk management framework
- **Critical Path Method** - Kelley & Walker (1959)
- **Resource-Constrained Scheduling** - Kolisch & Hartmann (2006)

## ⚙️ Configuration Options

### Adjust Allocation Parameters
In `resource_allocator.py`:
```python
allocator.allocate_resources(
    max_tasks_per_resource=6,       # Task limit per person
    duration_adjustment_factor=2   # Hours saved per skill point
)
```

### Risk Budget Constraint
In `risk_analyzer.py`:
```python
analyzer.optimize_mitigation_strategy(
    budget_constraint=5000  # Max €5,000 for mitigations
)
```

## 🐛 Troubleshooting

### API Keys Not Working
- Verify `.env` file is in parent directory (`202511-GIP/`)
- Check API key validity at:
  - Gemini: https://ai.google.dev/
  - Scopus: https://dev.elsevier.com/

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### MS Project Won't Import XML
- Ensure MS Project 2010+ (XML format version 14+)
- Try: File > Open > Select "All Files (*.*)" > Choose .xml

## 📝 Customization

### Add New Activities
Edit `data_models.py`:
```python
Activity(18, "New Activity Name", duration=5, num_people=2,
         predecessors=[17],
         skill_requirements={SKILL_FINANCE: 3})
```

### Add New Resources
```python
Resource("New Person", cost_per_hour=100, availability_pct=1.0,
         start_week=1, vacation_weeks=[],
         skills={SKILL_PETROLEUM: 4, SKILL_FINANCE: 3})
```

### Modify Risk Mitigations
Update `mitigation_options` in `RISKS` list.

## 📈 Performance Metrics

- **Execution Time**: ~30 seconds (with API calls)
- **Optimization Space**: 125 risk mitigation combinations evaluated
- **Resource Candidates**: 16 team members evaluated per activity
- **API Calls**: 
  - Gemini: 4 (summary, justifications, conclusions)
  - Scopus: 5 (one per research topic)

## 🤝 Contributing

This solution was developed for the ProDegeit case study. To adapt for other projects:

1. Update `data_models.py` with new project data
2. Adjust skill categories if needed
3. Modify calendar in `ms_project_generator.py` for different working days
4. Update risk models in `risk_analyzer.py`

## 📄 License

Educational use - ProDegeit Case Study 2025-26

## 🙏 Acknowledgments

- **Gemini 2.0 Flash**: Google DeepMind
- **Scopus API**: Elsevier
- **MS Project XML Schema**: Microsoft Corporation
- **Project Management Framework**: PMI (PMBOK)

---

**Generated by**: ProDegeit AI Solution  
**Version**: 1.0  
**Date**: November 2025
