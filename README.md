# HealthyLife Home Care Staff Scheduling Optimization

This project implements a sophisticated staff scheduling optimization solution for HealthyLife Home Care facility using mixed-integer linear programming. The system optimizes staff assignments across different shifts while considering dynamic demand patterns, hiring/firing costs, and various operational constraints.

## Features

- **Optimal Scheduling**: Determines the optimal number of staff for each category (Caregivers, Nurses, Support Staff) across all shifts
- **Dynamic Demand Handling**: Accounts for seasonal fluctuations in staffing requirements
- **Cost Optimization**: Minimizes total costs including wages, overtime, and hiring/firing expenses
- **Constraint Satisfaction**: Ensures all regulatory and quality standards are met
- **Interactive Dashboard**: Visualize and analyze scheduling results through an intuitive interface

## Requirements

- Python 3.7+
- PuLP (Linear Programming toolkit)
- Pandas, NumPy, Matplotlib, Seaborn (for data manipulation and visualization)
- Streamlit (for the web interface)

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the staff scheduling model directly:

```bash
python staff_scheduling.py
```

### Web Interface

For a more interactive experience, run the Streamlit application:

```bash
streamlit run app.py
```

This will launch a web interface where you can:
- Select the month for scheduling
- Adjust the number of days to schedule
- Set initial staff counts
- Generate and visualize optimized schedules
- Export detailed schedules as CSV files

## Model Constraints

The model incorporates the following constraints:
- No employee works more than six days a week
- Each employee has at least 12 hours of rest between shifts
- Weekend shifts require 10% more staff than weekdays
- Night shifts are evenly distributed (at least 50% of shifts must be morning/evening)
- Nurses cannot work overtime due to licensing restrictions
- Overtime for caregivers and support staff is paid at 1.5x regular wages
- All staffing requirements must be met while minimizing total cost

## Mathematical Model

The implemented mathematical model formulates the scheduling problem as a mixed-integer linear program (MILP) with:
- Decision variables for staff assignments, overtime, hiring, and firing
- Objective function minimizing total staffing costs
- Constraints ensuring staffing requirements, work hours, rest periods, and shift distribution

## Output

The system provides:
- Optimized staff schedules for each day and shift
- Total cost breakdown (regular wages, overtime, hiring/firing)
- Visualization of staff distribution across the schedule
- Detailed data export for further analysis or implementation

## License

This project is proprietary and confidential to HealthyLife Home Care.
