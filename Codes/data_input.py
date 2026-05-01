# data_input.py
import sys
import csv
import json

state = None

# Add events to the eventlist and timeline
def add_event(time, gid, event_type):
    timeline = state['timeline']
    eventlist = state['eventlist']
    
    if (time not in timeline):
        # Binary search to find the correct place in timeline
        left = 0
        right = len(timeline)
        while left < right:
            mid = (left + right) // 2
            if timeline[mid] < time:
                left = mid + 1
            else:
                right = mid
        timeline.insert(left, time)
        eventlist[time] = [(gid, event_type)]
    else:
        eventlist[time].append((gid, event_type))

# Read restaurant and customer information from files
def file_input(rest_stat, cust_stat):
    global state
    
    tables = state['tables']
    customers = state['customers']
    queues = state['queues']
    tab_num = state['tab_num']
    queues_min_size = state['queues_min_size']
    max_queue_length = state['max_queue_length']
    waiting_time = state['waiting_time']
    res_list = state['res_list']
    
    try:
        with open(rest_stat, 'r', encoding = 'utf-8') as file:
            data = json.load(file)
            sorted_queues = sorted(data["queue_definitions"], key = lambda x: x["min_size"])
            for data_queue in sorted_queues:
                tab_num.append(0)
                queues.append(list())
                res_list.append(list())
                queues_min_size.append(data_queue["min_size"])
                max_queue_length.append(0)
            
            sorted_tables = sorted(data["tables"], key = lambda x: x["capacity"])
            for data_table in sorted_tables:
                capacity = data_table["capacity"]
                tables.append({"capacity": capacity, "availability": True, "occupied_time": 0})
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
            
            for i in tab_num:
                if (i == 0):
                    print("Invalid queue definition. No table corresponds to the customer group size range for one of the queues.")
                    sys.exit()
    except FileNotFoundError:
        print("Input file not found.")
        sys.exit()
    except KeyError as e:
        print(f"JSON file missing expected key: {e}")
        print("Expected keys: 'queue_definitions' and 'tables'")
        sys.exit()
    except ValueError as e:
        print(f"Invalid data in JSON file: {e}")
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
                    if (arrival_time < 0 or arrival_time >= 2400 or int(time_shown[1]) >= 60):
                        print("Invalid arrival time for customer group: " + row['arrival_time'])
                        sys.exit()
                    if (group_size <= 0):
                        print("Invalid group size for customer group: " + row['group_size'])
                        sys.exit()
                    if (dining_duration <= 0):
                        print("Invalid dining duration for customer group: " + row['dining_duration'])
                        sys.exit()

                    # Process reservation time and abandon tolerance if applicable
                    if (row['group_type'] == "reservation"):
                        reservation_time_shown = (row['reservation_time'].strip()).split(':')
                        reservation_time = int(reservation_time_shown[0]) * 100 + int(reservation_time_shown[1])
                        if (reservation_time < 0 or reservation_time >= 2400 or int(reservation_time_shown[1]) >= 60):
                            print("Invalid reservation time for customer group: " + row['reservation_time'])
                            sys.exit()
                        
                        this_queue = -1

                        for i in range(len(queues_min_size)):
                            if (group_size >= queues_min_size[i]):
                                if (i == len(queues_min_size) - 1 or group_size < queues_min_size[i + 1]):
                                    this_queue = i
                                    break
                        if (this_queue == -1):
                            print("Invalid group size. No corresponding queue for customer group with size " + str(group_size) + ".")
                            sys.exit()
                        res_list[this_queue].append(len(customers))
                    else:
                        reservation_time = -1

                    if (row['abandon_tolerance'] != ""):
                        abandon_time = int(row['abandon_tolerance'].strip())
                        if (abandon_time < 0):
                            print("Invalid abandon tolerance for customer group: " + row['abandon_tolerance'])
                            sys.exit()
                        minutes = arrival_time % 100 + abandon_time
                        hours = arrival_time // 100 + minutes // 60
                        minutes = minutes % 60
                        abandon_time = hours * 100 + minutes
                    else:
                        abandon_time = -1
                    customers.append({"arrival_time": arrival_time, "group_size": group_size, "dining_duration": dining_duration, "table_id": -1, "reservation": reservation_time, "abandon_time": abandon_time})
                    add_event(arrival_time, len(customers) - 1, "arrival")
                    
                    waiting_time.append(-1)
                except ValueError as e:
                    print(f"Invalid customer information: {e}")
                    sys.exit()
            
            # To control the order of events in eventlist without sorting, we need to add the abandon events after all arrival events are added for the same time point
            for i in range(len(customers)):
                if (customers[i]["abandon_time"] != -1):
                    add_event(customers[i]["abandon_time"], i, "abandon")
    except FileNotFoundError:
        print("Input file not found.")
        sys.exit()
    except KeyError as e:
        print(f"CSV file missing expected column: {e}")
        print("Expected columns: 'arrival_time', 'group_size', 'dining_duration'")
        sys.exit()
    except ValueError as e:
        print(f"Invalid data in CSV file: {e}")
        sys.exit()