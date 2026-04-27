# Group C08 Restaurant Queue Simulation
This project is about restaurant queue simulation. Simulation process is done on the first-come-first-served basis. However, it also supports reservation and abandon tolerance for customers. Codes can be found in folder `/Codes`. 

## Programming Language
All codes are done in Python.

## Compilation Instructions
To execute the code on your computer, you need to install python (version 3.13 or higher) and operate under macOS, Linux or Windows system.
- Download Python from [python.org](https://www.python.org)
No external package required. 

To execute the program, you need to create input files as required (details will be mentioned later) and put them in the folder `/Codes`.
Input the command to navigate to the directory and execute the program:
```bash
cd Codes
python3 main.py
```
The following instruction would be shown in terminal:
`Input the file for restaurant statistics (.json): `
Input the file name for restaurant statistics. For example, if you are using the sample input file, input `restaurant.json` and press Enter. 
After that, the following instruction would be shown in terminal:
`Input the file for customer statistics (.csv): `
Input the file name for customer statistics. For example, if you are using the sample input file, input `customers.csv` and press Enter.
If the program runs successfully, output statistics will be in the file `operation_statistics.txt`.
- If a run-time error occurs during execution, no output will be in the `operation_statistics.txt` (or it will remain the same as last success execution). There may be invalid data in the input files, invalid input format or no corresponding file. An error message will be shown in terminal.

## Description
There are a total of 8 files in the folder `/Codes`. 5 of them are the codes, and the others are for saving data. Below is a brief description of the functions of each file.

### main.py
This code is the program entry file for restaurant queue simulation. It will read the input files, execute the simulation process and output the statistics to `operation_statistics.txt`. You need to execute this file to run the program.

### data_input.py
This file contains the functions for reading input files. It will read the restaurant statistics from a JSON file and customer statistics from a CSV file. The functions will update the data in a structured format for further processing in the main program.

### simulation.py
This file contains the functions for simulation process. This program is an event-based simulation. Events will be processed in chronological order, and the program will do 4 types of events at a specific time:
- Customer arrival: A customer group arrives, and it is added to the corresponding queue.
- Customer abandonment: A customer group abandons the queue if their waiting time exceeds their abandon tolerance.
- Customer departure: A customer group departs after being served.
- Table assignment: Check each queue and assign tables to customers if there are available tables.

### process_events.py
This file contains the major functions for all the events in `simulation.py`. It can do all the events mentioned above, update customer / table status during simulation and record statistics.

### statistics.py
This file contains the functions for computing simulation statistics and results and write the statistics to the file `operation_statistics.txt`.

### restaurant.json
This is the data for restaurant information. This JSON file should include a dictionary with 2 elements:
- `queue_definitions`: The value to this key is a list that defines queues. Each element should be in the same format: 
    ```json
    {
        "min_size": 1,
        "max_size": 2
    }
    ```
    `min_size` implies the minimum size for this queue, while `max_size` implies the maximum size for this queue.
- `tables`: The value to this key is a list that defines tables. Each element should be in the same format:
    ```json
    {
        "capacity": 2
    }
    ```
    `capacity` implies the size of this table.

### customers.csv
This is the data for customers information. Each row represent a seperate customer group. This CSV file should include the following columns:
- `arrival_time`: This should be a time in `hh:mm` format which represent the time a customer group arrives. The time must be between `00:00` and `23:59`, and the minutes should be less than 60.
- `group_size`: This should be an positive integer, which represents the size of the group.
    - Note that the size must be in the size range of any 1 queue defined in `restaurant.json`. There will be an error if this group cannot be assigned to any queue.
- `dining_duration`: This should be an integer representing the dining duration (in minutes) of this group. (Note that if the time after dining is later than 23:59, this group will be viewed as not served.)
- `group_type` (if applicable): This should be a string, either "reservation" or "walkin". If reservation is not enabled, leave this blank, and the default value would be "walkin". If the string is neither of them, this group will be viewed as "walkin".
- `reservation_time` (if applicable): This should be a time in `hh:mm` format which represent the reservation time for a customer group. Grace period will always be 15 minutes (that is, reservation will be invalid 15 minutes after reservation time). This column will be read only when `group_type` is "reservation" and the time is in required format; otherwise, you can leave it blank.
- `abandon_tolerance` (if applicable): This should be an integer representing the abandon tolerance for this group. If there is no abandon tolerance for this group, you can leave it blank.
Reminder: All of the six headers is required. However, only the first 3 columns (arrival time, group size and dining duration) requires data in each row; for the others, input data if applicable. Missing any one header or data in first 3 columns of any row will cause an error.

### operation_statistics.txt
This is the statistics generated during simulation. Sample output corresponding to the sample input files is in this file. If there is no error, the following statistics will be generated:
- Simulation period: Simulation starts when the first group comes and ends when the last group departs.
- Table utilization: Include average utilization percentage (percent of time this table is occupied), number of tables with high utilization percentage and number of unused tables.
- Queues statistics: Include the maximum length for each queue during simulation.
- Customer statistics: Include the number of customer groups served, average waiting time, maximum waiting time, and the distribution of waiting time.