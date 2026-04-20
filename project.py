import sys
import csv
import json

#Define lists for tables, customers, and queues
tables = list() #Each element represents a table: {"capacity": int, "availability": bool}
customers = list() #Each element represents a customer group: {"arrival_time": int, "group_size": int, "dining_duration": int, "table_id": int}
queues = list() #Each element represents a queue for a capacity range: list of group ids
queues_min_size = list()
tab_num = list()

#Define timeline and eventlist to store events
timeline = list() #Each element represents a time point when an event occurs
eventlist = dict() #Key: time point, Value: list of events at that time point

#Define variables for computing statistics
waiting_time = list() #Each element represents the waiting time of a customer group
avg_waiting_time = 0
max_waiting_time = 0
groups_served = 0
max_queue_length = list()

#Define function add_event to add events to the eventlist and timeline
def add_event(time, gid, event_type):
    if (time not in timeline):
        if (len(timeline) == 0):
            timeline.append(time)
        elif (len(timeline) == 1):
            if (timeline[0] < time):
                timeline.append(time)
            else:
                timeline.insert(0, time)
        elif (timeline[-1] < time):
            timeline.append(time)
        else:
            for i in range(len(timeline) - 1):
                if (timeline[i] < time) and (timeline[i + 1] > time):
                    timeline.insert(i + 1, time)
                    temp = i + 1
                    break
        eventlist[time] = [(gid, event_type)]
    else:
        eventlist[time].append((gid, event_type))
    #print("This event is added at time " + str(time) + ": " + ("Customer group " + str(gid) + " arrives." if event_type == True else "Customer group " + str(gid) + " departs."))

#Define function file_input to read input from file
def file_input(rest_stat, cust_stat):
    global tables, customers, queues, tab_num
    try:
        with open(rest_stat, 'r', encoding = 'utf-8') as file:
            data = json.load(file)
            sorted_queues = sorted(data["queue_definitions"], key=lambda x: x["min_size"])
            for data_queue in sorted_queues:
                tab_num.append(0)
                queues.append(list())
                queues_min_size.append(data_queue["min_size"])
                max_queue_length.append(0)
            
            sorted_tables = sorted(data["tables"], key=lambda x: x["capacity"])
            for data_table in sorted_tables:
                capacity = data_table["capacity"]
                tables.append({"capacity": capacity, "availability": True})
                if_set = False
                for i in range(len(queues_min_size)):
                    if (capacity >= queues_min_size[i]):
                        if (i == len(queues_min_size) - 1 or capacity < queues_min_size[i + 1]):
                            tab_num[i] += 1
                            if_set = True
                            break
                if (if_set == False):
                    print("Invalid table capacity. No corresponding queue for table with capacity " + str(capacity) + ".")
                    sys.exit()
    except FileNotFoundError:
        print("Input file not found.")
        sys.exit()
    
    try:
        with open(cust_stat, 'r', encoding = 'utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    time_shown = (row['arrival_time'].strip()).split(':')
                    arrival_time = int(time_shown[0]) * 100 + int(time_shown[1])
                    group_size = int(row['group_size'].strip())
                    dining_duration = int(row['dining_duration'].strip())
                    customers.append({"arrival_time": arrival_time, "group_size": group_size, "dining_duration": dining_duration, "table_id": -1})
                    add_event(arrival_time, len(customers) - 1, True)
                    
                    waiting_time.append(-1)
                except ValueError:
                    print("Invalid customer information.")
                    sys.exit()
    except FileNotFoundError:
        print("Input file not found.")
        sys.exit()

#Define function dining_start to handle the start of dining for a customer group
def dining_start(time, tid, qid):
    global groups_served, avg_waiting_time, max_waiting_time, waiting_time
    groups_served += 1

    temp = queues[qid][0]
    queues[qid].pop(0)
    customers[temp]["table_id"] = tid
    tables[tid]["availability"] = False

    #Calculate waiting time
    waiting_time[temp] = time - customers[temp]["arrival_time"]
    if (waiting_time[temp] > max_waiting_time):
        max_waiting_time = waiting_time[temp]

    #Calculate the departure time and add the departure event
    minutes = time % 100 + customers[temp]["dining_duration"]
    hours = time // 100 + minutes // 60
    minutes = minutes % 60
    departure_time = hours * 100 + minutes
    add_event(departure_time, temp, False)

#Define function dining_end to handle the end of dining for a customer group
def dining_end(time, tid, gid):
    customers[gid]["table_id"] = -1
    tables[tid]["availability"] = True

#Define function add_to_queue to add a customer group to a queue
def add_to_queue(gid):
    group_size = customers[gid]["group_size"]
    this_queue = -1
    for i in range(len(queues_min_size)):
        if (group_size >= queues_min_size[i]):
            if (i == len(queues_min_size) - 1 or group_size < queues_min_size[i + 1]):
                this_queue = i
                break
    if (this_queue == -1):
        print("Invalid group size. No corresponding queue for customer group with size " + str(group_size) + ".")
        sys.exit()
    queues[this_queue].append(gid)
    if (len(queues[this_queue]) > max_queue_length[this_queue]):
        max_queue_length[this_queue] = len(queues[this_queue])

#Check if there are available tables for the queue and start dining if possible
def check_queue(qid, time):
    table_end = sum(tab_num[:qid + 1])
    table_start = table_end - tab_num[qid]
    max_group = len(queues[qid])
    for i in range(table_start, table_end):
        if (max_group == 0):
            break
        if (tables[i]["availability"] == True and customers[queues[qid][0]]["group_size"] <= tables[i]["capacity"]):
            dining_start(time, i, qid)
            max_group -= 1

def file_output():
    global avg_waiting_time
    if (groups_served > 0):
        waiting_time_sum = 0
        for i in range(len(waiting_time)):
            if (waiting_time[i] >= 0):
                waiting_time_sum += waiting_time[i]
        avg_waiting_time = waiting_time_sum / groups_served
    seated_immediately = 0
    seated_between_0_15 = 0
    seated_between_15_30 = 0
    seated_greater_than_30 = 0
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
        file.write("Restaurant Seating Simulation Results\n")

        file.write("Total number of tables: " + str(len(tables)) + "\n")
        file.write("Total number of customer groups: " + str(len(customers)) + "\n")
        file.write("Total number of customer groups served: " + str(groups_served) + "\n")

        file.write("Average waiting time: " + f"{avg_waiting_time:.2f}" + " minutes\n")
        file.write("Maximum waiting time: " + str(max_waiting_time) + " minutes\n")

        file.write("Maximum queue length for each queue:\n")
        for i in range(len(queues_min_size)):
            file.write("   Queue " + str(i + 1) + ": " + str(max_queue_length[i]) + "\n")
        
        file.write("Distribution of waiting times:\n")
        file.write("   Seated immediately: " + f"{seated_immediately / groups_served * 100:.2f}%" + "\n")
        file.write("   Seated between 0-15 minutes: " + f"{seated_between_0_15 / groups_served * 100:.2f}%" + "\n")
        file.write("   Seated between 15-30 minutes: " + f"{seated_between_15_30 / groups_served * 100:.2f}%" + "\n")
        file.write("   Seated greater than 30 minutes: " + f"{seated_greater_than_30 / groups_served * 100:.2f}%" + "\n")

#Main function    
def main():
    rest_stat = str(input("Input the file for restaurant statistics (.json): "))
    cust_stat = str(input("Input the file for customer statistics (.csv): "))
    file_input(rest_stat, cust_stat)
    #print("There are " + str(len(tables)) + " tables and " + str(len(customers)) + " customer groups in total.")
    temp = 0
    time = 0

    #Process events in chronological order
    while (temp < len(timeline)):
        time = timeline[temp]
        #print("Processing events at time " + str(time) + ".")
        event_id = 0
        #Handle Customer Arrivals
        while (eventlist[time][event_id][1] == True):
            #print("Customer group " + str(eventlist[time][event_id][0]) + " arrives at time " + str(time) + ".")
            add_to_queue(eventlist[time][event_id][0])
            event_id += 1
            if (event_id >= len(eventlist[time])):
                break

        #Handle Customer Departures
        while (event_id < len(eventlist[time])):
            dining_end(time, customers[eventlist[time][event_id][0]]["table_id"], eventlist[time][event_id][0])
            event_id += 1

        #Handle Table Assignments
        for i in range(len(queues)):
            check_queue(i, time)

        temp += 1
    
    #Output statistics to file
    file_output()

main()