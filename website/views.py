from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from openpyxl import Workbook
from django.core.paginator import Paginator
from django.utils import timezone
import subprocess, os, rospy, threading
from .models import DisinfectionRun
from django.db.models import Q
from datetime import datetime, timedelta
from .utils import check_device_availability
from threading import Lock, Event

from .param_monitor import monitor_param_changes


def check_sensor_status(request):
    if request.method == 'POST':
        remote_ip = request.POST.get('ros_master_ip', '')
        username = 'haystack'  # Replace with your actual username
        password = 'haystack'  # Replace with your actual password

        lidar_available = check_device_availability(remote_ip, username, password, 'lidar')
        battery_available = check_device_availability(remote_ip, username, password, 'battery')
        arduino_available = check_device_availability(remote_ip, username, password, 'arduino')
        ubiquity_available = check_device_availability(remote_ip, username, password, 'ubiquity') 
        camera_available = check_device_availability(remote_ip, username, password, 'video') 

        return JsonResponse({'lidar_available': lidar_available, 'battery_available': battery_available, 'arduino_available': arduino_available, 'ubiquity_available': ubiquity_available, 'camera_available': camera_available})




def change_mode_to_disinfect():
    # rospy.set_param('/disinfect_room_number', int(12))
    rospy.set_param('/haystack/mode', 'DISINFECT')

def change_mode_to_idle():
    rospy.set_param('/haystack/mode', 'IDLE')

def run_ros_node():
    rospy.init_node('disinfection_node', anonymous=True)
    rospy.spin()

# Create a global variable to store the current disinfect status
current_disinfect_status = ""
# status_lock = Lock() 
# status_event = Event()

# def update_disinfect_status(value):
#     global current_disinfect_status
#     with status_lock:
#         current_disinfect_status = value
#         status_event.set()
# Define a callback function to update the global variable
def update_disinfect_status(value):
    global current_disinfect_status
    current_disinfect_status = value

def run_dis(request):

    # Get the ROS_MASTER_URI from the form submission
    ros_master_uri = request.POST.get('ros_master_uri', 'http://default-ros-master-uri:11311')
    os.environ['ROS_MASTER_URI'] = ros_master_uri
    os.environ['ROS_IP'] = '172.16.2.66'

    ros_thread = threading.Thread(target=run_ros_node)
    ros_thread.start()
    input_number = int(request.POST.get('number', 0))
    

    if request.method == 'POST':
        try:
            num_runs = int(request.POST.get('num_runs'))
            room_setup_number = int(request.POST.get('room_setup'))
            

            if num_runs <= 0:
                return HttpResponse("Error: Invalid number of runs.")
            
            run = 0
            while run < num_runs:
                mode = rospy.get_param('/haystack/mode', default='IDLE')
                if mode == 'IDLE':
                    rospy.loginfo("Mode is IDLE. Waiting for 10 seconds...")
                    rospy.sleep(duration=10.0)
                    rospy.set_param('/disinfect_room_number', input_number)
                    change_mode_to_disinfect()
                    rospy.loginfo("Mode changed to DISINFECT.")

                    # run_status = rospy.get_param('/coverage/state', "")
                    # disinfect_status = rospy.get_param('/disinfect_status', "")

                    # rospy.sleep(duration=2.0)
                    # with status_lock:
                    #     status_event.wait()  # Wait for the event to be set
                    #     disinfect_status = current_disinfect_status
                    #     status_event.clear()


                    # Save the data to the database for each run
                    disinfection_run = DisinfectionRun(
                        room_number=input_number ,
                        room_setup=room_setup_number,
                        run_count=run+1 ,
                        master_ip=request.POST.get('ros_master_uri', ''),
                        disinfect_status=current_disinfect_status,
                    )
                    disinfection_run.save()

                    run += 1
                    input_number += 1  
                
                else:
                    rospy.loginfo("Mode is not IDLE. Waiting for 5 seconds...")
                    rospy.sleep(duration=3.0)
            

            # change_mode_to_idle()
            rospy.loginfo("All runs completed. Mode changed back to IDLE.")

            return HttpResponse("Runs started successfully.")

        except Exception as e:
            return HttpResponse(f"Error: {e}")
    else:
        # Fetch all previous disinfection runs from the database
        previous_runs = DisinfectionRun.objects.all()
        return render(request, 'home.html', {'runs': previous_runs})




def reports(request):
    # Fetch all previous disinfection runs from the database
    runs = DisinfectionRun.objects.all()
    
    # Filter reports based on IP address if provided
    ip_filter = request.GET.get('ip_filter')
    if ip_filter:
        # Check if the user-provided IP filter contains 'http://' or ':11311'
        if 'http://' not in ip_filter:
            ip_filter = 'http://' + ip_filter
        if ':11311' not in ip_filter:
            ip_filter += ':11311'
        
        runs = runs.filter(master_ip__icontains=ip_filter)

    # Filter reports based on date if provided
    date_filter = request.GET.get('date_filter')
    if date_filter:
        runs = runs.filter(created_at__date=date_filter)

    # Paginate the queryset to show 10 rows per page
    paginator = Paginator(runs, 10)
    page_number = request.GET.get('page')  # Get the page number from the request
    page_runs = paginator.get_page(page_number)
    
    return render(request, 'reports.html', {'runs': page_runs})



def export_reports(request):
    # Fetch all previous disinfection runs from the database
    runs = DisinfectionRun.objects.all()
    
    # Filter reports based on IP address if provided
    ip_filter = request.GET.get('ip_filter')
    if ip_filter:
        if 'http://' not in ip_filter:
            ip_filter = 'http://' + ip_filter
        if ':11311' not in ip_filter:
            ip_filter += ':11311'
        runs = runs.filter(master_ip__icontains=ip_filter)

    # Filter reports based on date if provided
    date_filter = request.GET.get('date_filter')
    if date_filter:
        runs = runs.filter(created_at__date=date_filter)
    
    # Create a new Excel workbook and add the data
    wb = Workbook()
    ws = wb.active
    ws.append(['Room Number', 'Room Setup Number', 'Run Count', 'Master IP', 'Created At'])
    for run in runs:
        # Convert datetime to naive datetime
        created_at_naive = run.created_at.astimezone(timezone.utc).replace(tzinfo=None)
        ws.append([run.room_number, run.room_setup, run.run_count, run.master_ip, created_at_naive])

    # Create a response with Excel content type and attach the workbook
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reports.xlsx'
    wb.save(response)

    return response


def home(request):
    #check if logging in or not
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #auth
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "welcome to haystack!")
            # Get the ROS_MASTER_URI from the form submission
            return redirect('home')
        else: 
            messages.success(request, "there was an error logging in, please try again latter...!")
            return redirect('home')
    else:


        today = timezone.now().date()
        runs = DisinfectionRun.objects.filter(created_at__date=today)

        # Calculate the remaining reports count
        total_reports = runs.count()
        reports_per_page = 10
        current_page = request.GET.get('page')
        if current_page:
            current_page = int(current_page)
        else:
            current_page = 1
        displayed_reports = (current_page - 1) * reports_per_page
        remaining_reports = total_reports - displayed_reports

        # Paginate the queryset to show 10 rows per page
        paginator = Paginator(runs, reports_per_page)
        page_number = request.GET.get('page')
        page_runs = paginator.get_page(page_number)

        return render(request, 'home.html', {'runs': page_runs, 'remaining_reports': remaining_reports})

        # return render(request, 'home.html', {})
    


def logout_user(request):
    logout(request)
    messages.success(request, "Sucessfully loged out...")
    return redirect('home')
