from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from openpyxl import Workbook
from django.core.paginator import Paginator
from django.utils import timezone
import subprocess, os, threading, rospy, sqlite3
from .models import DisinfectionRun
from django.db.models import Q
from datetime import datetime, timedelta
from .utils import check_device_availability
from .models import FilteredData
import paramiko
import sqlite3
import datetime, re

DEFAULT_USERNAME = "haystack"
DEFAULT_PASSWORD = "haystack"
REMOTE_DB_PATH = "/haystack_disinfect_report/database/disinfect_status_report.db"
LOCAL_DB_PATH = "/tmp/disinfect_status_report.db"


def check_sensor_status(request):
    if request.method == 'POST':
        remote_ip = request.POST.get('ros_master_ip', '')
        username = 'haystack'  
        password = 'haystack'  

        lidar_available = check_device_availability(remote_ip, username, password, 'lidar')
        battery_available = check_device_availability(remote_ip, username, password, 'battery')
        arduino_available = check_device_availability(remote_ip, username, password, 'arduino')
        ubiquity_available = check_device_availability(remote_ip, username, password, 'ubiquity') 
        camera_available = check_device_availability(remote_ip, username, password, 'video') 

        return JsonResponse({'lidar_available': lidar_available, 'battery_available': battery_available, 'arduino_available': arduino_available, 'ubiquity_available': ubiquity_available, 'camera_available': camera_available})


def change_mode_to_disinfect():
    rospy.set_param('/haystack/mode', 'DISINFECT')
 

def change_mode_to_idle():
    rospy.set_param('/haystack/mode', 'IDLE')
  

def run_ros_node():
    rospy.init_node('disinfection_node', anonymous=True)
    rospy.spin()



def filter_and_save_data(ip, table_name):
    # Date filter
        today = datetime.date.today()
        today_date = today.strftime("%Y_%-m_%-d")
        columns, table_data = get_table_data(ip, table_name)

        # Retrieve the last data row from the table
        last_data_row = table_data[-1]

        # Check if the last data row already exists in the FilteredData table
        existing_row = FilteredData.objects.filter(id=last_data_row[0]).first()

        # If the last data row doesn't exist in the FilteredData table, add it
        if not existing_row:
            filtered_row = FilteredData(
                id=last_data_row[0],
                year=last_data_row[1],
                month=last_data_row[2],
                day=last_data_row[3],
                hour=last_data_row[4],
                min=last_data_row[5],
                room=last_data_row[6],
                percentage=last_data_row[7],
                duration=last_data_row[8],
                image=last_data_row[9],
                date=last_data_row[10],
                status=last_data_row[11],
                ip_address=ip  # Add the IP address to the database
            )
            filtered_row.save()

        # Store the filtered data and non-filtered data in separate lists
        filtered_data = [last_data_row] if last_data_row[10] == today_date else []
    # today = datetime.date.today()
    # today_date = today.strftime("%Y_%-m_%-d")

    # columns, table_data = get_table_data(ip, table_name)

    # filtered_data = []

    # for row in table_data:
    #     if row[10] == today_date:
    #         filtered_data.append(row)

    #         existing_row = FilteredData.objects.filter(id=row[0]).first()

    #         if not existing_row:
    #             filtered_row = FilteredData(
    #                 id=row[0],
    #                 year=row[1],
    #                 month=row[2],
    #                 day=row[3],
    #                 hour=row[4],
    #                 min=row[5],
    #                 room=row[6],
    #                 percentage=row[7],
    #                 duration=row[8],
    #                 image=row[9],
    #                 date=row[10],
    #                 status=row[11],
    #             )
    #             filtered_row.save()

def run_dis(request):
    ros_master_uri = request.POST.get('ros_master_uri', 'http://default-ros-master-uri:11311')
    os.environ['ROS_MASTER_URI'] = ros_master_uri
    os.environ['ROS_IP'] = '172.16.2.66'

    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ip_address = re.findall(ip_pattern, ros_master_uri)
    ip = ip_address[0]
    # ip = request.POST.get('ip')

    ros_thread = threading.Thread(target=run_ros_node)
    ros_thread.start()
    input_number = int(request.POST.get('number', 0))
    robot_name = rospy.get_param('/haystack/Robot_name', default='NONE')
    if request.method == 'POST':
        try:
            num_runs = int(request.POST.get('num_runs'))
            room_setup_number = int(request.POST.get('room_setup'))
            table_name = "HAYSTACK_DISINFECT_REPORT"

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

                    disinfection_run = DisinfectionRun(
                        room_number=input_number,
                        room_setup=room_setup_number,
                        run_count=run +1,
                        master_ip=request.POST.get('ros_master_uri', ''),
                        robot_name = robot_name,
                    )
                    disinfection_run.save()

                    run += 1
                    print("fffffffffffffffffffff",run)
                    # input_number += 1

                    # filter_and_save_data(ip, table_name)

                    if table_name:
                        columns, table_data = get_table_data(ip, table_name)

                    # Date filter
                    today = datetime.date.today()
                    today_date = today.strftime("%Y_%-m_%-d")

                    # Retrieve the last data row from the table
                    last_data_row = table_data[-1]

                    # Check if the last data row already exists in the FilteredData table
                    existing_row = FilteredData.objects.filter(id=last_data_row[0]).first()

                    # If the last data row doesn't exist in the FilteredData table, add it
                    if not existing_row:
                        filtered_row = FilteredData(
                            id=last_data_row[0],
                            year=last_data_row[1],
                            month=last_data_row[2],
                            day=last_data_row[3],
                            hour=last_data_row[4],
                            min=last_data_row[5],
                            room=last_data_row[6],
                            percentage=last_data_row[7],
                            duration=last_data_row[8],
                            image=last_data_row[9],
                            date=last_data_row[10],
                            status=last_data_row[11],
                            ip_address=ip  # Add the IP address to the database
                        )
                        filtered_row.save()

                    # Store the filtered data and non-filtered data in separate lists
                    filtered_data = [last_data_row] if last_data_row[10] == today_date else []
                    

                    # today = datetime.date.today()
                    # today_date = today.strftime("%Y_%-m_%-d")

                    # table_name = "HAYSTACK_DISINFECT_REPORT" 
                    # columns, table_data = get_table_data(ip, table_name)

                    # filtered_data = []

                    # for row in table_data:
                    #     if row[10] == today_date:
                    #         filtered_data.append(row)

                    #         existing_row = FilteredData.objects.filter(id=row[0]).first()

                    #         if not existing_row:
                    #             filtered_row = FilteredData(
                    #                 id=row[0],  
                    #                 year=row[1],
                    #                 month=row[2],
                    #                 day=row[3],
                    #                 hour=row[4],
                    #                 min=row[5],
                    #                 room=row[6],
                    #                 percentage=row[7],
                    #                 duration=row[8],
                    #                 image=row[9],
                    #                 date=row[10],
                    #                 status=row[11],
                    #                 # room_number=input_number,
                    #             )
                    #             filtered_row.save()

                else:
                    rospy.loginfo("Mode is not IDLE. Waiting for 5 seconds...")
                    rospy.sleep(duration=5.0)

            rospy.loginfo("All runs completed. Mode changed back to IDLE.")
            mode1 = rospy.get_param('/haystack/mode', default='IDLE')
            if mode1 == 'IDLE':
                rospy.sleep(duration=5.0)
            # if run < num_runs:
            #     today = datetime.date.today()
            #     today_date = today.strftime("%Y_%-m_%-d")

            #     table_name = "HAYSTACK_DISINFECT_REPORT" 
            #     columns, table_data = get_table_data(ip, table_name)

            #     filtered_data = []

            #     for row in table_data:
            #         if row[10] == today_date:
            #             filtered_data.append(row)

            #             existing_row = FilteredData.objects.filter(id=row[0]).first()

            #             if not existing_row:
            #                 filtered_row = FilteredData(
            #                     id=row[0],  
            #                     year=row[1],
            #                     month=row[2],
            #                     day=row[3],
            #                     hour=row[4],
            #                     min=row[5],
            #                     room=row[6],
            #                     percentage=row[7],
            #                     duration=row[8],
            #                     image=row[9],
            #                     date=row[10],
            #                     status=row[11],
            #                     # room_number=input_number,
            #                 )
            #                 filtered_row.save()
            
                filter_and_save_data(ip, table_name)
                return HttpResponse("Last Run !!!.")

        except Exception as e:
            return HttpResponse(f"Error: {e}")
    else:
        previous_runs = DisinfectionRun.objects.all()
        return render(request, 'home.html', {'runs': previous_runs})


# def run_dis(request):

#     ros_master_uri = request.POST.get('ros_master_uri', 'http://default-ros-master-uri:11311')
#     os.environ['ROS_MASTER_URI'] = ros_master_uri
#     os.environ['ROS_IP'] = '172.16.2.66'

#     ros_thread = threading.Thread(target=run_ros_node)
#     ros_thread.start()
#     input_number = int(request.POST.get('number', 0))
    

#     if request.method == 'POST':
#         try:
#             num_runs = int(request.POST.get('num_runs'))
#             room_setup_number = int(request.POST.get('room_setup'))
            

#             if num_runs <= 0:
#                 return HttpResponse("Error: Invalid number of runs.")
            
#             run = 0
#             while run < num_runs:
#                 mode = rospy.get_param('/haystack/mode', default='IDLE')
#                 if mode == 'IDLE':
#                     rospy.loginfo("Mode is IDLE. Waiting for 10 seconds...")
#                     rospy.sleep(duration=10.0)
#                     rospy.set_param('/disinfect_room_number', input_number)
#                     change_mode_to_disinfect()
#                     rospy.loginfo("Mode changed to DISINFECT.")

#                     disinfection_run = DisinfectionRun(
#                         room_number=input_number,
#                         room_setup=room_setup_number,
#                         run_count=run + 1,
#                         master_ip=request.POST.get('ros_master_uri', ''),
#                     )
#                     disinfection_run.save()

#                     run += 1
#                     input_number += 1  

#                 else:
#                     rospy.loginfo("Mode is not IDLE. Waiting for 5 seconds...")
#                     rospy.sleep(duration=5.0)
            

#             rospy.loginfo("All runs completed. Mode changed back to IDLE.")

#             return HttpResponse("Runs started successfully.")

#         except Exception as e:
#             return HttpResponse(f"Error: {e}")
#     else:
#         previous_runs = DisinfectionRun.objects.all()
#         return render(request, 'home.html', {'runs': previous_runs})




def reports(request):
    runs = DisinfectionRun.objects.all()

    ip_filter = request.GET.get('ip_filter')
    if ip_filter:
        if 'http://' not in ip_filter:
            ip_filter = 'http://' + ip_filter
        if ':11311' not in ip_filter:
            ip_filter += ':11311'
        
        runs = runs.filter(master_ip__icontains=ip_filter)

    date_filter = request.GET.get('date_filter')
    if date_filter:
        runs = runs.filter(created_at__date=date_filter)

    paginator = Paginator(runs, 10)
    page_number = request.GET.get('page') 
    page_runs = paginator.get_page(page_number)
    
    return render(request, 'reports.html', {'runs': page_runs})



def export_reports(request):
    runs = DisinfectionRun.objects.all()
    
    ip_filter = request.GET.get('ip_filter')
    if ip_filter:
        if 'http://' not in ip_filter:
            ip_filter = 'http://' + ip_filter
        if ':11311' not in ip_filter:
            ip_filter += ':11311'
        runs = runs.filter(master_ip__icontains=ip_filter)

    date_filter = request.GET.get('date_filter')
    if date_filter:
        runs = runs.filter(created_at__date=date_filter)
    
    wb = Workbook()
    ws = wb.active
    ws.append(['Room Number', 'Room Setup Number', 'Run Count', 'Master IP', 'Created At'])
    for run in runs:
        created_at_naive = run.created_at.astimezone(timezone.utc).replace(tzinfo=None)
        ws.append([run.room_number, run.room_setup, run.run_count, run.master_ip, created_at_naive])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reports.xlsx'
    wb.save(response)

    return response

####newly added


def display_filtered_data(request):
    filtered_data = FilteredData.objects.all() 
    return render(request, 'filtered_data.html', {'filtered_data': filtered_data})



def connect_to_device(ip):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

        with ssh_client.open_sftp() as sftp:
            sftp.get(REMOTE_DB_PATH, LOCAL_DB_PATH)

        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cursor.fetchall()]

        conn.close()
        ssh_client.close()

        return table_names
    except Exception as e:
        return str(e)


def get_table_data(ip, table_name="HAYSTACK_DISINFECT_REPORT"):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

        with ssh_client.open_sftp() as sftp:
            sftp.get(REMOTE_DB_PATH, LOCAL_DB_PATH)

        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        conn.close()
        ssh_client.close()

        return columns, rows
    except Exception as e:
        return str(e)
################################


def new_model_template(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        table_name = request.POST.get('table_name')
        table_names = connect_to_device(ip)
        columns = []
        table_data = []
        non_filtered_data = []

        if table_name:
            columns, table_data = get_table_data(ip, table_name)

        # Date filter
        today = datetime.date.today()
        today_date = today.strftime("%Y_%-m_%-d")

        filtered_data = []
        for row in table_data:
            if row[10] == today_date:
                filtered_data.append(row)
            non_filtered_data.append(row)

        filtered_data_from_db = FilteredData.objects.all()

        return render(request, 'new_model_template.html', {'table_names': table_names, 'columns': columns, 'table_data': filtered_data, 'filtered_data': filtered_data_from_db, 'non_filtered_data': non_filtered_data})
    else:
        return render(request, 'new_model_template.html')
    

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #auth
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "welcome to haystack!")
            return redirect('home')
        else: 
            messages.success(request, "there was an error logging in, please try again latter...!")
            return redirect('home')
    else:
        #today = timezone.now().date()
        # runs = DisinfectionRun.objects.filter(created_at__date=today)
        runs = DisinfectionRun.objects.all()
        filtered_data = FilteredData.objects.all()

        # Calculate the remaining reports count
        #total_reports = runs.count()
        reports_per_page = 10
        current_page = request.GET.get('page')
        if current_page:
            current_page = int(current_page)
        else:
            current_page = 1
        displayed_reports = (current_page - 1) * reports_per_page
        #remaining_reports = total_reports - displayed_reports

        # Paginate the queryset to show 10 rows per page
        paginator = Paginator(runs, reports_per_page)
        page_number = request.GET.get('page')
        page_runs = paginator.get_page(page_number)
        ####

        paginator_filtered_data = Paginator(filtered_data, reports_per_page)
        page_number = request.GET.get('page')
        page_filtered_data = paginator_filtered_data.get_page(page_number)


        return render(request, 'home.html', {'runs': page_runs, 'filtered_data': page_filtered_data, 'remaining_reports': displayed_reports})


def logout_user(request):
    logout(request)
    messages.success(request, "Sucessfully loged out...")
    return redirect('home')
