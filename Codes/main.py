# main.py
import sys
from data_input import file_input
from simulation import run_simulation
from statistics import file_output

# Use a dictionary to store all variables and pass the other files
state = {
    # Define variables for storing restaurant and customers information
    'tables': [], # Each element represents a table: {"capacity": int, "availability": bool}
    'customers': [], # Each element represents a customer group: {"arrival_time": int, "group_size": int, "dining_duration": int, "table_id": int, "reservation": int, "abandon_time": int}
    'queues': [], # Each element represents a queue for a capacity range: list of group ids
    'queues_min_size': [], # Each element represents the minimun number of customers in each queue
    'tab_num': [], # Each element represents the number of tables corresponding to the customer group size range for each queue
    'res_list': [], # Each element represents the list of group_id for reservation in the corresponding queue, sorted by reservation time
    
    #Define variables for storing events
    'timeline': [], # Each element represents a time point when an event occurs
    'eventlist': {}, # Key: time point, Value: list of events at that time point

    #Define variables for computing statistics
    'waiting_time': [], # Each element represents the waiting time of a customer group
    'avg_waiting_time': 0, # Average waiting time for all groups served
    'max_waiting_time': 0, # Maximum waiting time for all groups served
    'groups_served': 0, # Number of groups served
    'max_queue_length': [] # Each element represents the maximum queue length during simulation
}

#Pass state to other files
import data_input
import simulation
import statistics
import process_events

data_input.state = state
simulation.state = state
statistics.state = state
process_events.state = state

# Main function
def main():
    rest_stat = str(input("Input the file for restaurant statistics (.json): "))
    cust_stat = str(input("Input the file for customer statistics (.csv): "))
    
    # Load data
    file_input(rest_stat, cust_stat)
    
    # Run simulation
    run_simulation()
    
    # Output statistics
    file_output()

if __name__ == "__main__":
    main()