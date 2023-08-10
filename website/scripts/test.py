import rospy

def main():
    rospy.init_node('param_monitor_node')

    num_runs = int(input("Enter the number of disinfection runs: "))
    runs_completed = 0
    rospy.set_param('/coverage/state', "NONE")
    rospy.set_param('/disinfect_status', 'NONE')
    
    while runs_completed < num_runs:
        rospy.logwarn(runs_completed)
        mode = rospy.get_param('/haystack/mode', default='IDLE')
        
        if mode == 'IDLE':
            rospy.set_param('/haystack/mode', 'DISINFECT')
            print("Setting mode to 'DISINFECT'")
            
            
            coverage_run_status = rospy.get_param('/coverage/state', "")
            if coverage_run_status == "STOPPED":
                disinfect_status = rospy.get_param('/disinfect_status', '')
                print("Coverage run status is STOPPED")
                print("Disinfect status:", disinfect_status)
                runs_completed += 1
                
                # coverage_run_status = rospy.delete_param('/coverage/state')
                # disinfect_status = rospy.delete_param('/disinfect_status')


        rospy.sleep(10)  # Adjust the sleep duration as needed

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
