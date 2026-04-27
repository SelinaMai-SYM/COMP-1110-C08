# process_events.py
import sys

state = None

# Calculate the time after adding minutes to a given time
def add_time(time, minutes):
    new_minutes = time % 100 + minutes
    new_hours = time // 100 + new_minutes // 60
    new_minutes = new_minutes % 60
    return new_hours * 100 + new_minutes

# Add events to the eventlist and timeline
def add_event(time, gid, event_type):
    timeline = state['timeline']
    eventlist = state['eventlist']
    
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
                    break
        eventlist[time] = [(gid, event_type)]
    else:
        eventlist[time].append((gid, event_type))

# Handle the start of dining for a customer group
def dining_start(time, tid, qid, group_reserve = -1):
    queues = state['queues']
    customers = state['customers']
    tables = state['tables']
    waiting_time = state['waiting_time']
    
    groups_served = state['groups_served']
    max_waiting_time = state['max_waiting_time']
    
    groups_served += 1
    if (group_reserve == -1):
        temp = queues[qid][0]
        queues[qid].pop(0)
    else:
        temp = group_reserve
    customers[temp]["table_id"] = tid
    tables[tid]["availability"] = False

    # Calculate waiting time
    sstart = (customers[temp]["arrival_time"] // 100) * 60 + (customers[temp]["arrival_time"] % 100)
    send = (time // 100) * 60 + (time % 100)
    waiting_time[temp] = send - sstart
    if (waiting_time[temp] > max_waiting_time):
        max_waiting_time = waiting_time[temp]

    # Update state
    state['groups_served'] = groups_served
    state['max_waiting_time'] = max_waiting_time
    state['waiting_time'] = waiting_time

    # Calculate the departure time and add the departure event
    departure_time = add_time(time, customers[temp]["dining_duration"])
    add_event(departure_time, temp, "departure")

# Handle the end of dining for a customer group
def dining_end(time, tid, gid):
    customers = state['customers']
    tables = state['tables']
    
    customers[gid]["table_id"] = -1
    tables[tid]["availability"] = True
    tables[tid]["occupied_time"] += customers[gid]["dining_duration"]

# Add a customer group to a queue
def add_to_queue(gid, time):
    customers = state['customers']
    queues = state['queues']
    queues_min_size = state['queues_min_size']
    max_queue_length = state['max_queue_length']
    tab_num = state['tab_num']
    
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
    
    if_reserve = False
    # Check if the group has a reservation and can be seated immediately
    if (customers[gid]["reservation"] != -1):
        if (customers[gid]["reservation"] < time and time < add_time(customers[gid]["reservation"], 15)):
            table_end = sum(tab_num[:this_queue + 1])
            table_start = table_end - tab_num[this_queue]
            for i in range(table_start, table_end):
                if (customers[gid]["group_size"] <= state['tables'][i]["capacity"] and state['tables'][i]["availability"] == True):
                    dining_start(time, i, this_queue, gid)
                    return
            # If the group has a reservation but cannot be seated immediately, they will become the first in the queue
            if_reserve = True

    if (if_reserve):
        queues[this_queue].insert(0, gid)
    else:
        queues[this_queue].append(gid)
    if (len(queues[this_queue]) > max_queue_length[this_queue]):
        max_queue_length[this_queue] = len(queues[this_queue])

def check_reservation(end_time, qid, tid, tab_start, tab_end):
    this_res_list = state['res_list'][qid]
    customers = state['customers']
    tables = state['tables']
    this_size = tables[tid]["capacity"]
    
    # Find the number of reservations that are scheduled before the end of dining time for this group
    cust_count = 0
    this_cust_count = 0
    for i in range(len(this_res_list)):
        if (customers[this_res_list[i]]["reservation"] <= end_time):
            cust_count += 1
            if (customers[this_res_list[i]]["group_size"] == this_size):
                this_cust_count += 1
    # Find the number of tables that will be available before the end of dining time for this group
    tab_count = 0
    this_tab_count = 0
    for i in tables[tab_start:tab_end]:
        if (i["availability"] == True):
            tab_count += 1
            if (i["capacity"] == this_size):
                this_tab_count += 1
    if (cust_count <= tab_count and this_cust_count <= this_tab_count):
        return True
    else:
        return False

# Check if there are available tables for the queue and start dining if possible
def check_queue(qid, time):
    tab_num = state['tab_num']
    queues = state['queues']
    tables = state['tables']
    customers = state['customers']
    
    table_end = sum(tab_num[:qid + 1])
    table_start = table_end - tab_num[qid]
    max_group = len(queues[qid])
    for i in range(table_start, table_end):
        if (max_group == 0):
            break
        if (tables[i]["availability"] == True and customers[queues[qid][0]]["group_size"] <= tables[i]["capacity"]):
            if (check_reservation(add_time(time, customers[queues[qid][0]]["dining_duration"]), qid, i, table_start, table_end)):
                dining_start(time, i, qid)
                max_group -= 1

def abandon_queue(gid):
    customers = state['customers']
    if (customers[gid]["table_id"] != -1):
        return
    else:
        queues = state['queues']
        for queue in queues:
            if (gid in queue):
                queue.remove(gid)
                break
