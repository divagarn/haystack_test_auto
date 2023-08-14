from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    #we integrated this login to home page so we commented here 
    # path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_user, name = 'logout'),   
    path('run_dis/', views.run_dis, name='run_dis'),
    path('reports/', views.reports, name='reports'),
    path('export-reports/', views.export_reports, name='export_reports'),
    path('check_sensor_status/', views.check_sensor_status, name='check_sensor_status'),
    path('robot_report/', views.new_page_view, name='robot_report'),
]


