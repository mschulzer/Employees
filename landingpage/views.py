from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Employee, EmployeeAdd
import csv
import logging


def index(request):
	if request.user.is_authenticated:
		return HttpResponse("You're logged in.")
	else:
		return HttpResponse("Hello, friend. You're at the landing page - what now?")

def logon_view(request):
	if request.method == 'POST':
		my_username = request.POST['username']
		my_password = request.POST['password']
		user = authenticate(request, username=my_username, password=my_password)

		if user is not None:
			login(request, user)
			return HttpResponseRedirect(reverse("upload_csv"))
		else:
			return HttpResponse("Wrongo, my friend.")

	return render(request, template_name="logon.html", context={})
	#return HttpResponse("This is the logon-page.")

def upload_csv(request):
	data = {}

	if "GET" == request.method:
		return render(request, "upload_csv.html", data)
	# if not GET, then proceed
	try:
		csv_file = request.FILES["csv_file"]
		if not csv_file.name.endswith('.csv'):
			messages.error(request,'File is not CSV type')
			return HttpResponseRedirect(reverse("upload_csv"))
		#if file is too large, return
		if csv_file.multiple_chunks():
			messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
			return HttpResponseRedirect(reverse("upload_csv"))

		file_data = csv_file.read().decode("utf-8")		
		lines = file_data.split("\n")

		my_data = []

		""" This definitely seems redundant, no? """
		for line in lines:						
			fields = line.split(",")
			data_dict = {}
			data_dict["name"] = fields[0]
			data_dict["start_date_time"] = fields[1]
			data_dict["end_date_time"] = fields[2]

			my_data.append(data_dict)

		new_employees = [
			Employee(
				name = row['name'], 
				start_date_time = row['start_date_time'],
				end_date_time = row['end_date_time'],
			)
    		for row in my_data
		]
		
		Employee.objects.bulk_create(new_employees) # bulk add to DB
		

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))

	context = {
		'data_dict': my_data,
		'total': len(my_data),
	}

	#return HttpResponseRedirect(reverse("upload_csv"))
	return render(request, "upload_csv.html", context)

def employees(request):
	if request.user.is_authenticated:
		employees = Employee.objects.all()
		return render(request, template_name="employees.html", context={'employees': employees})
	else:
		return HttpResponse("Sorry - you need to be authorized to access page contents.")


""" ADD AN EMPLOYEE """
def add_employee(request):
	if request.method == 'POST':
		form = EmployeeAdd(request.POST)

		if form.is_valid():
			inst = form.my_save(request.user)
			#form.save()
			#data = form.cleaned_data

			""" SAVE CSV-FILE TO /static """
			header = ['id', 'name', 'start_date_time', 'end_date_time']
			data_id = inst.id
			data_name = request.POST.get("name")
			data_start = request.POST.get("start_date_time")
			data_end = request.POST.get("end_date_time")
			data = [data_id, data_name, data_start, data_end]

			with open('landingpage/static/employees.csv', 'w', encoding='UTF8') as f:
				writer = csv.writer(f)
				writer.writerow(header)
				writer.writerow(data)

			return HttpResponseRedirect('/landingpage/employees/')

	else:
		form = EmployeeAdd()

	return render(request, 'addemployee.html', { 'form': form }) # render HTML-form


def employee_delete(request, id=None):
	# instance = SomeModel.objects.get(id=id)
	employee = get_object_or_404(Employee, id=id)
	employee.delete()
	return HttpResponseRedirect('/landingpage/employees/')