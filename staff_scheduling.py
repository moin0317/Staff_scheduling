import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import calendar

class StaffScheduler:
    def __init__(self):
        # Staff categories
        self.staff_categories = ['Caregivers', 'Nurses', 'Support Staff']
        
        # Hourly wages
        self.hourly_wages = {
            'Caregivers': 300,
            'Nurses': 450,
            'Support Staff': 250
        }
        
        # Regular hours per week
        self.regular_hours = {
            'Caregivers': 40,
            'Nurses': 35,
            'Support Staff': 30
        }
        
        # Minimum staff required per shift on weekdays
        self.min_staff_weekday = {
            'Caregivers': {'Morning': 10, 'Evening': 12, 'Night': 8},
            'Nurses': {'Morning': 6, 'Evening': 5, 'Night': 4},
            'Support Staff': {'Morning': 5, 'Evening': 4, 'Night': 3}
        }
        
        # Historical demand data
        self.historical_demand = {
            'September': {
                'Morning': {'Caregivers': 12, 'Nurses': 7, 'Support Staff': 6},
                'Evening': {'Caregivers': 14, 'Nurses': 6, 'Support Staff': 5},
                'Night': {'Caregivers': 9, 'Nurses': 5, 'Support Staff': 4}
            },
            'October': {
                'Morning': {'Caregivers': 11, 'Nurses': 6, 'Support Staff': 5},
                'Evening': {'Caregivers': 13, 'Nurses': 5, 'Support Staff': 4},
                'Night': {'Caregivers': 8, 'Nurses': 4, 'Support Staff': 3}
            },
            'November': {
                'Morning': {'Caregivers': 10, 'Nurses': 6, 'Support Staff': 5},
                'Evening': {'Caregivers': 12, 'Nurses': 5, 'Support Staff': 4},
                'Night': {'Caregivers': 8, 'Nurses': 4, 'Support Staff': 3}
            },
            'December': {
                'Morning': {'Caregivers': 13, 'Nurses': 8, 'Support Staff': 7},
                'Evening': {'Caregivers': 15, 'Nurses': 7, 'Support Staff': 6},
                'Night': {'Caregivers': 10, 'Nurses': 6, 'Support Staff': 5}
            },
            'January': {
                'Morning': {'Caregivers': 14, 'Nurses': 9, 'Support Staff': 8},
                'Evening': {'Caregivers': 16, 'Nurses': 8, 'Support Staff': 7},
                'Night': {'Caregivers': 11, 'Nurses': 7, 'Support Staff': 6}
            },
            'February': {
                'Morning': {'Caregivers': 12, 'Nurses': 7, 'Support Staff': 6},
                'Evening': {'Caregivers': 14, 'Nurses': 6, 'Support Staff': 5},
                'Night': {'Caregivers': 9, 'Nurses': 5, 'Support Staff': 4}
            }
        }
        
        # Hiring and firing costs
        self.hiring_cost = {
            'Caregivers': 5000,
            'Nurses': 7500,
            'Support Staff': 4000
        }
        
        self.firing_cost = {
            'Caregivers': 3500,
            'Nurses': 5000,
            'Support Staff': 2500
        }
        
        # Shifts
        self.shifts = ['Morning', 'Evening', 'Night']
        
        # Days of the week
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Model variables
        self.problem = None
        self.staff_assigned = None
        self.overtime_assigned = None
        self.staff_hired = None
        self.staff_fired = None
        self.total_staff = None
        
    def forecast_demand(self, month, day_type='weekday'):
        """
        Forecast demand based on historical data and day type
        """
        demand = {}
        base_demand = self.historical_demand.get(month, self.historical_demand['February'])
        
        for shift in self.shifts:
            demand[shift] = {}
            for category in self.staff_categories:
                if day_type == 'weekend':
                    # Weekend shifts require 10% more staff
                    demand[shift][category] = int(base_demand[shift][category] * 1.1)
                else:
                    demand[shift][category] = base_demand[shift][category]
        
        return demand
    
    def build_model(self, month, num_days=28, initial_staff=None):
        """
        Build the staff scheduling optimization model
        """
        # Create the problem
        self.problem = pulp.LpProblem("Staff_Scheduling", pulp.LpMinimize)
        
        # Set initial staff if provided, otherwise assume default values
        if initial_staff is None:
            initial_staff = {
                'Caregivers': 40,  # Assuming enough staff to cover all shifts
                'Nurses': 30,
                'Support Staff': 20
            }
        
        # Create a calendar for the given month
        today = datetime.today()
        # Use the month number (1-12) from the provided month name
        month_number = list(calendar.month_name).index(month)
        if month_number == 0:  # Handle the case where month name is not recognized
            month_number = today.month
        
        year = today.year
        
        # Generate the days in the month
        first_day = datetime(year, month_number, 1)
        if num_days > calendar.monthrange(year, month_number)[1]:
            num_days = calendar.monthrange(year, month_number)[1]
        
        days = [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]
        day_types = ['weekday' if (first_day + timedelta(days=i)).weekday() < 5 else 'weekend' for i in range(num_days)]
        
        # Decision variables
        
        # Number of staff of each category assigned to each shift on each day
        self.staff_assigned = pulp.LpVariable.dicts("Staff_Assigned", 
                                                 [(d, s, c) for d in range(num_days) 
                                                             for s in self.shifts 
                                                             for c in self.staff_categories],
                                                 lowBound=0, cat='Integer')
        
        # Overtime hours for staff (not applicable for nurses)
        self.overtime_assigned = pulp.LpVariable.dicts("Overtime", 
                                                    [(d, s, c) for d in range(num_days) 
                                                                for s in self.shifts 
                                                                for c in self.staff_categories if c != 'Nurses'],
                                                    lowBound=0, cat='Integer')
        
        # Staff hired or fired at the beginning of the month
        self.staff_hired = pulp.LpVariable.dicts("Staff_Hired", 
                                              self.staff_categories, 
                                              lowBound=0, cat='Integer')
        
        self.staff_fired = pulp.LpVariable.dicts("Staff_Fired", 
                                              self.staff_categories, 
                                              lowBound=0, cat='Integer')
        
        # Total staff after hiring/firing
        self.total_staff = pulp.LpVariable.dicts("Total_Staff", 
                                              self.staff_categories, 
                                              lowBound=0, cat='Integer')
        
        # Constraint: Total staff equals initial staff plus hired minus fired
        for c in self.staff_categories:
            self.problem += self.total_staff[c] == initial_staff[c] + self.staff_hired[c] - self.staff_fired[c]
        
        # Objective function: Minimize total cost
        total_regular_cost = pulp.lpSum([
            self.staff_assigned[(d, s, c)] * self.hourly_wages[c] * 8  # 8-hour shifts
            for d in range(num_days) for s in self.shifts for c in self.staff_categories
        ])
        
        total_overtime_cost = pulp.lpSum([
            self.overtime_assigned[(d, s, c)] * self.hourly_wages[c] * 1.5 * 8  # Overtime at 1.5x regular wage
            for d in range(num_days) for s in self.shifts for c in self.staff_categories if c != 'Nurses'
        ])
        
        total_hiring_cost = pulp.lpSum([
            self.staff_hired[c] * self.hiring_cost[c]
            for c in self.staff_categories
        ])
        
        total_firing_cost = pulp.lpSum([
            self.staff_fired[c] * self.firing_cost[c]
            for c in self.staff_categories
        ])
        
        self.problem += total_regular_cost + total_overtime_cost + total_hiring_cost + total_firing_cost
        
        # Constraints
        
        # 1. Staffing requirements per shift
        for d in range(num_days):
            day_type = day_types[d]
            demand = self.forecast_demand(month, day_type)
            
            for s in self.shifts:
                for c in self.staff_categories:
                    # Regular staff plus overtime must meet or exceed demand
                    if c != 'Nurses':
                        self.problem += self.staff_assigned[(d, s, c)] + self.overtime_assigned[(d, s, c)] >= demand[s][c]
                    else:
                        self.problem += self.staff_assigned[(d, s, c)] >= demand[s][c]
        
        # 2. Maximum available staff constraint
        for c in self.staff_categories:
            # For each shift, the total staff assigned cannot exceed total available staff
            for s in self.shifts:
                for d in range(num_days):
                    self.problem += self.staff_assigned[(d, s, c)] <= self.total_staff[c]
        
        # 3. Work hour limitations
        # Each staff category has a maximum number of regular hours per week
        for c in self.staff_categories:
            for week in range(num_days // 7):  # For each complete week
                week_start = week * 7
                week_end = min((week + 1) * 7, num_days)
                
                # Total regular hours in the week
                total_weekly_hours = pulp.lpSum([
                    self.staff_assigned[(d, s, c)] * 8  # 8-hour shifts
                    for d in range(week_start, week_end) for s in self.shifts
                ])
                
                # Ensure regular hours don't exceed weekly limit for total staff
                self.problem += total_weekly_hours <= self.total_staff[c] * self.regular_hours[c]
        
        # 4. Shift distribution constraint
        # At least 50% of shifts must be evenly distributed between morning and evening
        for c in self.staff_categories:
            total_morning_evening = pulp.lpSum([
                self.staff_assigned[(d, s, c)]
                for d in range(num_days) for s in ['Morning', 'Evening']
            ])
            
            total_night = pulp.lpSum([
                self.staff_assigned[(d, 'Night', c)]
                for d in range(num_days)
            ])
            
            self.problem += total_morning_evening >= total_night
        
        return self.problem
    
    def solve_model(self):
        """
        Solve the optimization model
        """
        if self.problem is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        # Solve the problem
        self.problem.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Check status
        status = pulp.LpStatus[self.problem.status]
        if status != 'Optimal':
            print(f"Warning: Solution is {status}, not optimal.")
        
        return status
    
    def get_schedule(self, num_days):
        """
        Get the optimized schedule in a structured format
        """
        if self.problem is None or pulp.LpStatus[self.problem.status] != 'Optimal':
            raise ValueError("Model not solved optimally yet.")
        
        schedule = {
            'regular': {},
            'overtime': {},
            'staff_changes': {},
            'total_cost': pulp.value(self.problem.objective)
        }
        
        # Extract regular staff assignments
        for d in range(num_days):
            for s in self.shifts:
                for c in self.staff_categories:
                    key = (d, s, c)
                    if key not in schedule['regular']:
                        schedule['regular'][key] = pulp.value(self.staff_assigned[key])
        
        # Extract overtime assignments
        for d in range(num_days):
            for s in self.shifts:
                for c in self.staff_categories:
                    if c != 'Nurses':  # Nurses can't do overtime
                        key = (d, s, c)
                        if key not in schedule['overtime']:
                            schedule['overtime'][key] = pulp.value(self.overtime_assigned.get(key, 0))
        
        # Extract staff changes
        for c in self.staff_categories:
            schedule['staff_changes'][c] = {
                'hired': pulp.value(self.staff_hired[c]),
                'fired': pulp.value(self.staff_fired[c]),
                'total': pulp.value(self.total_staff[c])
            }
        
        return schedule
    
    def visualize_schedule(self, schedule, num_days, month, output_file=None):
        """
        Create visualizations for the schedule
        """
        # Prepare data for heatmap
        heatmap_data = []
        for d in range(num_days):
            for s in self.shifts:
                for c in self.staff_categories:
                    regular = schedule['regular'].get((d, s, c), 0)
                    overtime = schedule['overtime'].get((d, s, c), 0) if c != 'Nurses' else 0
                    
                    heatmap_data.append({
                        'Day': d + 1,
                        'Shift': s,
                        'Category': c,
                        'Regular Staff': regular,
                        'Overtime Staff': overtime,
                        'Total Staff': regular + overtime
                    })
        
        df = pd.DataFrame(heatmap_data)
        
        # Create figure and axes for multiple plots
        fig, axes = plt.subplots(len(self.staff_categories), 1, figsize=(15, 5 * len(self.staff_categories)))
        
        # Create heatmap for each staff category
        for i, category in enumerate(self.staff_categories):
            category_df = df[df['Category'] == category].pivot(
                index='Shift', columns='Day', values='Total Staff'
            )
            
            sns.heatmap(category_df, cmap='YlGnBu', annot=True, fmt='.0f', ax=axes[i])
            axes[i].set_title(f'{category} Staffing - {month}')
            axes[i].set_xlabel('Day of Month')
            axes[i].set_ylabel('Shift')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            plt.close()
        else:
            return fig

def main():
    # Initialize the scheduler
    scheduler = StaffScheduler()
    
    # Set the month and initial staff levels
    month = "March"  # Current month
    initial_staff = {
        'Caregivers': 40,
        'Nurses': 30,
        'Support Staff': 20
    }
    
    num_days = 28  # Four weeks
    
    # Build and solve the model
    scheduler.build_model(month, num_days, initial_staff)
    status = scheduler.solve_model()
    
    print(f"Optimization Status: {status}")
    
    if status == 'Optimal':
        # Get the optimized schedule
        schedule = scheduler.get_schedule(num_days)
        
        # Display the results
        print(f"\nTotal Cost: ₹{schedule['total_cost']:,.2f}")
        
        print("\nStaff Changes:")
        for category, changes in schedule['staff_changes'].items():
            print(f"{category}: Hired: {changes['hired']}, Fired: {changes['fired']}, Total: {changes['total']}")
        
        # Create visualization
        fig = scheduler.visualize_schedule(schedule, num_days, month)
        plt.show()
        
        # Save detailed schedule to CSV
        detailed_schedule = []
        for d in range(num_days):
            for s in scheduler.shifts:
                for c in scheduler.staff_categories:
                    regular = schedule['regular'].get((d, s, c), 0)
                    overtime = schedule['overtime'].get((d, s, c), 0) if c != 'Nurses' else 0
                    
                    detailed_schedule.append({
                        'Day': d + 1,
                        'Shift': s,
                        'Category': c,
                        'Regular Staff': regular,
                        'Overtime Staff': overtime,
                        'Total Staff': regular + overtime
                    })
        
        df_schedule = pd.DataFrame(detailed_schedule)
        df_schedule.to_csv('detailed_schedule.csv', index=False)
        print("\nDetailed schedule saved to 'detailed_schedule.csv'")

if __name__ == "__main__":
    main()
