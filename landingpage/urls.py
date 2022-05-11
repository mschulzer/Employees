from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/csv/', views.upload_csv, name='upload_csv'),
    path('employees/', views.employees, name="employees"),
    path('addemployee/', views.add_employee, name='addemployee'),
    path('<id>/delete/', views.employee_delete, name='delete'),
    path('logon/', views.logon_view, name='logonview'),
]