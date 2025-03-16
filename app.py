import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from staff_scheduling import StaffScheduler
import calendar
from datetime import datetime
import numpy as np

st.set_page_config(page_title="HealthyLife Staff Scheduler", layout="wide")

def main():
    st.title("HealthyLife Home Care Staff Scheduling Optimization")
    
    st.sidebar.header("Configuration")
    
    # Month selection
    months = list(calendar.month_name)[1:]
    selected_month = st.sidebar.selectbox("Select Month", months, index=datetime.now().month - 1)
    
    # Days in month
    num_days = st.sidebar.slider("Number of Days to Schedule", 7, 31, 28)
    
    # Initial staff configuration
    st.sidebar.subheader("Initial Staff Count")
    initial_caregivers = st.sidebar.number_input("Initial Caregivers", min_value=0, max_value=100, value=40)
    initial_nurses = st.sidebar.number_input("Initial Nurses", min_value=0, max_value=100, value=30)
    initial_support = st.sidebar.number_input("Initial Support Staff", min_value=0, max_value=100, value=20)
    
    initial_staff = {
        'Caregivers': initial_caregivers,
        'Nurses': initial_nurses,
        'Support Staff': initial_support
    }
    
    # Solve button
    if st.sidebar.button("Generate Schedule"):
        with st.spinner("Optimizing staff schedule..."):
            # Initialize the scheduler
            scheduler = StaffScheduler()
            
            # Build and solve the model
            scheduler.build_model(selected_month, num_days, initial_staff)
            status = scheduler.solve_model()
            
            if status == 'Optimal':
                # Get the optimized schedule
                schedule = scheduler.get_schedule(num_days)
                
                # Display results
                st.header("Optimization Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Cost Summary")
                    st.metric("Total Cost", f"₹{schedule['total_cost']:,.2f}")
                    
                    st.subheader("Staff Changes")
                    staff_changes = pd.DataFrame({
                        'Category': list(schedule['staff_changes'].keys()),
                        'Hired': [changes['hired'] for changes in schedule['staff_changes'].values()],
                        'Fired': [changes['fired'] for changes in schedule['staff_changes'].values()],
                        'Total': [changes['total'] for changes in schedule['staff_changes'].values()]
                    })
                    st.table(staff_changes)
                
                with col2:
                    st.subheader("Cost Breakdown")
                    
                    # Regular wage cost
                    regular_cost = sum(
                        schedule['regular'].get((d, s, c), 0) * scheduler.hourly_wages[c] * 8
                        for d in range(num_days) for s in scheduler.shifts for c in scheduler.staff_categories
                    )
                    
                    # Overtime cost
                    overtime_cost = sum(
                        schedule['overtime'].get((d, s, c), 0) * scheduler.hourly_wages[c] * 1.5 * 8
                        for d in range(num_days) for s in scheduler.shifts 
                        for c in scheduler.staff_categories if c != 'Nurses'
                    )
                    
                    # Hiring and firing costs
                    hiring_cost = sum(
                        schedule['staff_changes'][c]['hired'] * scheduler.hiring_cost[c]
                        for c in scheduler.staff_categories
                    )
                    
                    firing_cost = sum(
                        schedule['staff_changes'][c]['fired'] * scheduler.firing_cost[c]
                        for c in scheduler.staff_categories
                    )
                    
                    cost_breakdown = pd.DataFrame({
                        'Cost Type': ['Regular Wages', 'Overtime Wages', 'Hiring Costs', 'Firing Costs', 'Total'],
                        'Amount (₹)': [regular_cost, overtime_cost, hiring_cost, firing_cost, schedule['total_cost']]
                    })
                    
                    st.table(cost_breakdown)
                    
                    # Create cost breakdown pie chart
                    fig, ax = plt.subplots(figsize=(8, 5))
                    labels = ['Regular Wages', 'Overtime Wages', 'Hiring Costs', 'Firing Costs']
                    sizes = [regular_cost, overtime_cost, hiring_cost, firing_cost]
                    
                    # Filter out zero values for better visualization
                    non_zero_labels = [label for label, size in zip(labels, sizes) if size > 0]
                    non_zero_sizes = [size for size in sizes if size > 0]
                    
                    if non_zero_sizes:
                        ax.pie(non_zero_sizes, labels=non_zero_labels, autopct='%1.1f%%', startangle=90)
                        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                        st.pyplot(fig)
                
                # Create detailed schedule visualization
                st.header("Staffing Schedule Visualization")
                
                # Create tabs for different visualizations
                tab1, tab2, tab3 = st.tabs(["Heatmap", "Daily Staffing", "Detailed Data"])
                
                with tab1:
                    # Generate the visualization
                    fig = scheduler.visualize_schedule(schedule, num_days, selected_month)
                    st.pyplot(fig)
                
                with tab2:
                    # Prepare data for daily staffing chart
                    daily_data = []
                    for d in range(num_days):
                        day_total = {'Day': d + 1}
                        for c in scheduler.staff_categories:
                            total_staff = sum(
                                schedule['regular'].get((d, s, c), 0) + 
                                (schedule['overtime'].get((d, s, c), 0) if c != 'Nurses' else 0)
                                for s in scheduler.shifts
                            )
                            day_total[c] = total_staff
                        daily_data.append(day_total)
                    
                    daily_df = pd.DataFrame(daily_data)
                    
                    # Plot the daily staffing
                    fig, ax = plt.subplots(figsize=(15, 6))
                    for c in scheduler.staff_categories:
                        ax.plot(daily_df['Day'], daily_df[c], marker='o', label=c)
                    
                    ax.set_xlabel('Day of Month')
                    ax.set_ylabel('Total Staff')
                    ax.set_title(f'Daily Total Staffing by Category - {selected_month}')
                    ax.grid(True)
                    ax.legend()
                    
                    st.pyplot(fig)
                
                with tab3:
                    # Prepare detailed schedule data
                    detailed_data = []
                    for d in range(num_days):
                        for s in scheduler.shifts:
                            for c in scheduler.staff_categories:
                                regular = schedule['regular'].get((d, s, c), 0)
                                overtime = schedule['overtime'].get((d, s, c), 0) if c != 'Nurses' else 0
                                
                                detailed_data.append({
                                    'Day': d + 1,
                                    'Shift': s,
                                    'Category': c,
                                    'Regular Staff': int(regular),
                                    'Overtime Staff': int(overtime),
                                    'Total Staff': int(regular + overtime),
                                    'Regular Cost (₹)': int(regular * scheduler.hourly_wages[c] * 8),
                                    'Overtime Cost (₹)': int(overtime * scheduler.hourly_wages[c] * 1.5 * 8)
                                })
                    
                    detailed_df = pd.DataFrame(detailed_data)
                    
                    # Allow the user to filter the data
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        category_filter = st.multiselect("Filter by Category", scheduler.staff_categories, default=scheduler.staff_categories)
                    with col2:
                        shift_filter = st.multiselect("Filter by Shift", scheduler.shifts, default=scheduler.shifts)
                    with col3:
                        day_filter = st.slider("Filter by Day Range", 1, num_days, (1, num_days))
                    
                    # Apply filters
                    filtered_df = detailed_df[
                        (detailed_df['Category'].isin(category_filter)) &
                        (detailed_df['Shift'].isin(shift_filter)) &
                        (detailed_df['Day'] >= day_filter[0]) &
                        (detailed_df['Day'] <= day_filter[1])
                    ]
                    
                    # Allow downloading the data
                    if not filtered_df.empty:
                        st.dataframe(filtered_df)
                        
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="Download Detailed Schedule as CSV",
                            data=csv,
                            file_name="healthylife_staff_schedule.csv",
                            mime="text/csv",
                        )
                    else:
                        st.warning("No data matches the selected filters.")
            else:
                st.error(f"Optimization failed with status: {status}")
                st.info("Try adjusting your initial staff levels or reducing the number of days to schedule.")

    # Show info about the model
    with st.expander("About the Staff Scheduling Model"):
        st.markdown("""
        ### HealthyLife Home Care Staff Scheduling Optimization
        
        This application uses mixed-integer linear programming to optimize staff scheduling for HealthyLife Home Care, a senior care facility that provides round-the-clock assistance to elderly residents.
        
        #### Model Constraints:
        - No employee is allowed to work more than six days a week
        - Each employee must have at least 12 hours of rest before taking up another shift
        - Weekend shifts require 10% more staff compared to weekdays
        - Night shifts must not exceed 50% of total shifts assigned
        - Nurses cannot take overtime shifts due to medical licensing restrictions
        - Caregivers and support staff can work overtime at 1.5 times regular pay
        
        #### Staff Categories and Hourly Wages:
        - Caregivers: ₹300/hour
        - Nurses: ₹450/hour
        - Support Staff: ₹250/hour
        
        #### Hiring and Firing Costs:
        - Caregivers: ₹5,000 to hire, ₹3,500 to fire
        - Nurses: ₹7,500 to hire, ₹5,000 to fire
        - Support Staff: ₹4,000 to hire, ₹2,500 to fire
        
        The model considers historical demand patterns and dynamically adjusts staffing levels to meet changing requirements while minimizing overall costs.
        """)

if __name__ == "__main__":
    main()
