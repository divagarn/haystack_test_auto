# #!/usr/bin/env python

# import rospy

# def monitor_param_changes():
#     previous_value = rospy.get_param('/disinfect_status')

#     rate = rospy.Rate(1)  # Set the rate at which you want to check for changes (1 Hz in this case)

#     while not rospy.is_shutdown():
#         current_value = rospy.get_param('/disinfect_status')
#         if current_value != previous_value:
#             rospy.loginfo("Parameter '/disinfect_status' changed to: %s", current_value)
#             previous_value = current_value
#         rate.sleep()

# if __name__ == '__main__':
#     rospy.init_node('param_change_monitor')

#     try:
#         monitor_param_changes()
#     except rospy.ROSInterruptException:
#         pass


#!/usr/bin/env python

import rospy

def monitor_param_changes(callback):
    previous_value = rospy.get_param('/disinfect_status')

    rate = rospy.Rate(1)  # Set the rate at which you want to check for changes (1 Hz in this case)

    while not rospy.is_shutdown():
        current_value = rospy.get_param('/disinfect_status')
        if current_value != previous_value:
            rospy.loginfo("Parameter '/disinfect_status' changed to: %s", current_value)
            callback(current_value)  # Call the callback function with the updated value
            previous_value = current_value
        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('param_change_monitor')

    try:
        monitor_param_changes()
    except rospy.ROSInterruptException:
        pass
