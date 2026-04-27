# statistics.py
state = None

def file_output():
    global state
    
    groups_served = state['groups_served']
    waiting_time = state['waiting_time']
    max_queue_length = state['max_queue_length']
    queues_min_size = state['queues_min_size']
    tables = state['tables']
    customers = state['customers']
    max_waiting_time = state['max_waiting_time']
    timeline = state['timeline']
    avg_waiting_time = state['avg_waiting_time']
    
    if (groups_served > 0):
        waiting_time_sum = 0
        for i in range(len(waiting_time)):
            if (waiting_time[i] >= 0):
                waiting_time_sum += waiting_time[i]
        avg_waiting_time = waiting_time_sum / groups_served
    
    # Calculate the simulation time
    sstart = (timeline[0] // 100) * 60 + (timeline[0] % 100)
    send = (timeline[-1] // 100) * 60 + (timeline[-1] % 100)
    total_time = send - sstart
    soutput = str(total_time // 60) + " hours and " + str(total_time % 60) + " minutes"

    # Calculate the distribution of waiting times
    seated_immediately = 0
    seated_between_0_15 = 0
    seated_between_15_30 = 0
    seated_greater_than_30 = 0

    # Calculate table utilization
    utilization = list()
    unused_tables = 0
    total_percentage = 0
    occupied_greater_than_50 = 0
    occupied_greater_than_75 = 0
    for table in tables:
        if (total_time > 0):
            utilization.append(table["occupied_time"] / total_time * 100)
            total_percentage += utilization[-1]
            if (utilization[-1] > 50.0):
                occupied_greater_than_50 += 1
            if (utilization[-1] > 75.0):
                occupied_greater_than_75 += 1
            if (table["occupied_time"] == 0):
                unused_tables += 1
        else:
            utilization.append(0)
    
    for i in range(len(waiting_time)):
        if (waiting_time[i] < 0):
            continue
        if (waiting_time[i] == 0):
            seated_immediately += 1
        elif (waiting_time[i] <= 15):
            seated_between_0_15 += 1
        elif (waiting_time[i] <= 30):
            seated_between_15_30 += 1
        else:
            seated_greater_than_30 += 1
    
    with open("operation_statistics.txt", "w") as file:
        file.write("Restaurant Seating Simulation Results\n\n")

        file.write("Simulation start at " + str(timeline[0] // 100) + ' : ' + str(timeline[0] % 100) + "\n")
        file.write("Simulation end at " + str(timeline[-1] // 100) + ' : ' + str(timeline[-1] % 100) + "\n")
        file.write("Total simulation time: " + soutput + "\n")

        file.write("\nTotal number of tables: " + str(len(tables)) + "\n")
        file.write("Average table utilization percentage: " + f"{total_percentage / len(tables):.2f}%" + "\n")
        file.write("Number of tables with utilization > 75%: " + str(occupied_greater_than_75) + "\n")
        file.write("Number of tables with utilization > 50%: " + str(occupied_greater_than_50) + "\n")
        file.write("Number of unused tables: " + str(unused_tables) + "\n")

        file.write("\nTotal number of queues: " + str(len(queues_min_size)) + "\n")
        file.write("Maximum queue length for each queue:\n")
        for i in range(len(queues_min_size)):
            file.write("    Queue " + str(i + 1) + ": " + str(max_queue_length[i]) + "\n")
        
        file.write("\nTotal number of customer groups: " + str(len(customers)) + "\n")
        file.write("Total number of customer groups served: " + str(groups_served) + "\n")
        file.write("Average waiting time: " + f"{avg_waiting_time:.2f}" + " minutes\n")
        file.write("Maximum waiting time: " + str(max_waiting_time) + " minutes\n")
        file.write("Distribution of waiting times:\n")
        if groups_served > 0:
            file.write("    Seated immediately: " + f"{seated_immediately / groups_served * 100:.2f}%" + "\n")
            file.write("    Seated between 0-15 minutes: " + f"{seated_between_0_15 / groups_served * 100:.2f}%" + "\n")
            file.write("    Seated between 15-30 minutes: " + f"{seated_between_15_30 / groups_served * 100:.2f}%" + "\n")
            file.write("    Seated greater than 30 minutes: " + f"{seated_greater_than_30 / groups_served * 100:.2f}%" + "\n")