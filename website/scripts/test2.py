# import threading, rospy

# # Global variable to track the state of the disinfection
# disinfection_state_count = {
#     'previous_mode': '',
#     'current_mode': '',
#     'runs_finished': False
#     # 'runs_finished': 0
# }

# # Function to monitor disinfection state
# def monitor_disinfection_state_count():
#     global disinfection_state_count
#     while True:
#         current_mode = rospy.get_param('/haystack/mode', default='IDLE')
        
#         if current_mode != disinfection_state_count['current_mode']:
#             # Mode has changed
#             disinfection_state_count['previous_mode'] = disinfection_state_count['current_mode']
#             disinfection_state_count['current_mode'] = current_mode
            
#             if disinfection_state_count['previous_mode'] == 'DISINFECT' and disinfection_state_count['current_mode'] == 'IDLE':
#                 # A disinfection run has started
#                 disinfection_state_count['runs_finished'] = True
#                 # disinfection_state_count['runs_finished'] += 1
#                 print(f"Disinfection run finished. Total runs finished: {disinfection_state_count['runs_finished']}")
        
#         rospy.sleep(1.0)  # Adjust the sleep interval as needed

# # Start the monitoring thread
# monitor_thread = threading.Thread(target=monitor_disinfection_state_count)
# monitor_thread.start()


import threading, rospy

# Global variable to track the state of the disinfection
disinfection_state = {
    'previous_mode': '',
    'current_mode': '',
    'run_finished': False
}

# Function to monitor disinfection state
def monitor_disinfection_state():
    global disinfection_state
    while True:
        current_mode = rospy.get_param('/haystack/mode', default='IDLE')
        
        if current_mode != disinfection_state['current_mode']:
            # Mode has changed
            disinfection_state['previous_mode'] = disinfection_state['current_mode']
            disinfection_state['current_mode'] = current_mode
            
            if disinfection_state['previous_mode'] == 'DISINFECT' and disinfection_state['current_mode'] == 'IDLE':
                # A disinfection run has finished
                disinfection_state['run_finished'] = True
                print("Disinfection run finished.")
                
        # Check if a new run has started and reset the flag
        if disinfection_state['run_finished'] and disinfection_state['current_mode'] == 'DISINFECT':
            disinfection_state['run_finished'] = False
            
        rospy.sleep(1.0)  # Adjust the sleep interval as needed

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_disinfection_state)
monitor_thread.start()
