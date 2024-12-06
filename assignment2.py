#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: Ivan Vassiljenko
Semester: Fall 2024

The python code in this file is original work written by
"Ivan Vassiljenko". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Assignment 2.

'''

import argparse
import os, sys

def parse_command_args() -> argparse.Namespace:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    # Adding command line arguments
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Show memory sizes in human-readable format.")
    parser.add_argument("program", type=str, nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    # Parsing the arguments
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int = 20) -> str:
    "Convert percentage to a visual bar of specified length."
    bar_length = int(length * (percent / 100))
    bar = '#' * bar_length + ' ' * (length - bar_length)
    return '[' + bar[:length-2] + ']'

def get_sys_mem() -> int:
    "Returns total system memory in KiB (kibibytes)."
    mem_total = 0
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
                break
    return mem_total

def get_avail_mem() -> int:
    "Returns total available memory in KiB (kibibytes)."
    mem_avail = 0
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemAvailable:'):
                mem_avail = int(line.split()[1])
                break
    return mem_avail  

def pids_of_prog(app_name: str) -> list:
   "Given an app name, return all PIDs associated with the app."
   # Call the pidof command using os.popen
   pid_output = os.popen(f'pidof {app_name}').read().strip()
   
   # If pidof returns an empty string, no processes were found, return an empty list
   if not pid_output:
       return []
   
   # Split the output into a list of PIDs
   pids = pid_output.split()
   return pids

def rss_mem_of_pid(proc_id: str) -> int:
    "Returns RSS memory usage of a process in KiB (kibibytes) given its PID."
    rss_mem = 0
    path = f'/proc/{proc_id}/smaps'
    
    try:
        with open(path, 'r') as f:
            for line in f:
                if line.startswith('Rss:'):
                    # Extract the Rss value (in KiB)
                    rss_mem += int(line.split()[1])
    except FileNotFoundError:
        print(f"Error: The file '/proc/{proc_id}/smaps' does not exist.")
    
    return rss_mem

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "Converts memory size from KiB to human-readable format."
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    count = 0
    result = kibibytes
    # Convert to higher units (KiB to MiB, GiB, etc.) until less than 1024
    while result > 1024 and count < len(suffixes) - 1: 
        result /= 1024
        count += 1  
    # Format the result to the specified decimal places
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[count]
    return str_result



if __name__ == "__main__":
    args = parse_command_args()
   
    if not args.program:
        # No program specified
        total_memory = get_sys_mem()  # Get total system memory
        available_memory = get_avail_mem()  # Get available system memory
        used_memory = total_memory - available_memory  # Calculate used memory

        # Convert values to human-readable format
        if args.human_readable:
            total_memory_h = bytes_to_human_r(total_memory)
            used_memory_h = bytes_to_human_r(used_memory)
            print(f"Total Memory: {total_memory_h}")
            print(f"Used Memory: {used_memory_h}")
        else:
            print(f"Total Memory: {total_memory} KiB")
            print(f"Used Memory: {used_memory} KiB")

        # Display bar graph for used memory percentage
        used_percent = (used_memory / total_memory) * 100
        print("Memory Usage:")
        print(percent_to_graph(used_percent, args.length))
    else:
        # Program specified
        pids = pids_of_prog(args.program)
       
        if not pids:
            print(f"No processes found for the program '{args.program}'.")
        else:
            total_rss = 0
            for pid in pids:
                total_rss += rss_mem_of_pid(pid)

            # Convert values to human-readable format
            if args.human_readable:
                total_rss_h = bytes_to_human_r(total_rss)
                print(f"Total RSS Memory Used by {args.program}: {total_rss_h}")
            else:
                print(f"Total RSS Memory Used by {args.program}: {total_rss} KiB")

            # Display bar graph for RSS memory percentage relative to system memory
            rss_percent = (total_rss / get_sys_mem()) * 100
            print("RSS Memory Usage:")
            print(percent_to_graph(rss_percent, args.length))