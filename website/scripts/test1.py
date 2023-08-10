import rospy, time

def main():
    rospy.init_node('param_monitor_node')

    num_runs = int(input("Enter the number of disinfection runs: "))
    runs_completed = 0
    
    while runs_completed < num_runs:
        rospy.logwarn(runs_completed)
        mode = rospy.get_param('/haystack/mode', '')

        if mode == 'DISINFECT':
            coverage_run_status = rospy.get_param('/coverage/state', "")
            rospy.loginfo(coverage_run_status)
        
        if mode == 'IDLE':

            if runs_completed != 0 :
                disinfect_status = rospy.get_param('/disinfect_status', '')
                print(disinfect_status)
                time.sleep(5)

            rospy.set_param('/haystack/mode', 'DISINFECT')
            print("Setting mode to 'DISINFECT'")
            runs_completed += 1
        rospy.sleep(5)  # Adjust the sleep duration as needed
    # if mode == 'IDLE':
    #     disinfect_status = rospy.get_param('/disinfect_status', '')
    #     print(disinfect_status)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
