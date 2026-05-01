# simulation.py
from process_events import add_to_queue, check_queue, dining_end, abandon_queue

state = None

def run_simulation():
    global state
    
    timeline = state['timeline']
    eventlist = state['eventlist']
    queues = state['queues']
    customers = state['customers']
    
    temp = 0
    time = 0

    # Process events in chronological order
    while (temp < len(timeline)):
        eventlist = state['eventlist']
        time = timeline[temp]
        event_id = 0
        
        # Handle Customer Arrivals
        while (eventlist[time][event_id][1] == "arrival"):
            add_to_queue(eventlist[time][event_id][0], time)
            event_id += 1
            if (event_id >= len(eventlist[time])):
                break
        
        if (event_id >= len(eventlist[time])):
            temp += 1
            for i in range(len(queues)):
                check_queue(i, time)
            continue
        # Handle Customer Abandonments
        while (eventlist[time][event_id][1] == "abandon"):
            abandon_queue(eventlist[time][event_id][0])
            event_id += 1
            if (event_id >= len(eventlist[time])):
                break

        # Handle Customer Departures
        while (event_id < len(eventlist[time])):
            dining_end(customers[eventlist[time][event_id][0]]["table_id"], eventlist[time][event_id][0])
            event_id += 1

        # Handle Table Assignments
        for i in range(len(queues)):
            check_queue(i, time)

        temp += 1