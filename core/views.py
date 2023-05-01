from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.models import CustomUser, Profile
from core.models import Location, Attendance, LeaveRequest
from core.forms import AttendanceForm, EmployeeForm
from core.decorators import authorize_manager_only
from datetime import date, datetime
from uuid import uuid4


'''
Non-interactive parts
1. The index page
'''


def index(request):
    return render(request, template_name='pages/index.html')


'''
Admin Dashboard
'''

'''
Admin Dashboard - Home
-Display numbers & display requests
-delete a leave request
'''


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
@require_GET
def render_admin_dashboard(request):
    employee_count = CustomUser.objects.filter(
        profile__is_manager=False).count()
    location_count = Location.objects.count()
    present_today_count = Attendance.objects.filter(
        date=datetime.today()).count()

    leave_requests = LeaveRequest.objects.all()

    context = {
        'employee_count': employee_count,
        'location_count': location_count,
        'present_today_count': present_today_count,
        'leave_requests': leave_requests
    }
    return render(request, template_name='pages/admin/home.html', context=context)


@authorize_manager_only(redirect_url='/employee/dashboard')
@login_required(login_url='/login')
def delete_leave_request(request, id):
    LeaveRequest.objects.filter(pk=id).delete()
    return HttpResponseRedirect('/manager/dashboard')


'''
Admin Dashboard - Attendances
-Display attendances
-Filter attendance by employee and by date
-view employee attendances on callendar
'''


@login_required(login_url='/login')
@require_GET
@authorize_manager_only(redirect_url='/employee/dashboard')
def attendances_view(request):
    attendances = Attendance.objects.all()
    return render(request, template_name='pages/admin/attendances.html', context={"attendances": attendances})


'''
Admin Dashboard - Locations
-main dashboard displaying locations
-create location
-update location
-delete location
'''


@login_required(login_url='/login')
@require_GET
@authorize_manager_only(redirect_url='/employee/dashboard')
def view_locations(request):
    locations = Location.objects.all()
    return render(request, template_name='pages/admin/locations.html', context={"locations": locations})


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
def create_locations(request):
    if request.method == "POST":
        name = None
        code = uuid4()
        longitude = None
        latitude = None
        radius = None
        # generate qr code and store in cloudinary

    return render(request, template_name='pages/admin/locations.html', context={"locations": locations})


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
def delete_locations(request, id):
    Location.objects.filter(pk=id).delete()
    return HttpResponseRedirect('/manager/dashboard/locations')


'''
Admin Dashboard - Employees
-main dashboard displaying employees
-create employee user account
-update user account
-delete account
'''


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
def view_employees(request):
    employees = CustomUser.objects.all()
    return render(request, template_name='pages/admin/locations.html', context={"employees": employees})


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
def create_employees(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            cpassword = form.cleaned_data["cpassword"]

            name = form.cleaned_data["name"]
            dob = form.cleaned_data["dob"]
            role = form.cleaned_data["role"]
            start_date = form.cleaned_data["start_date"]
            address = form.cleaned_data["address"]
            telephone = form.cleaned_data["telephone"]
            is_manager = form.cleaned_data["is_manager"]

            user = CustomUser.objects.create_user(
                email=email, password=password, cpassword=cpassword)
            profile = Profile(user=user, name=name, date_of_birth=dob,
                              role=role, start_date=start_date, telephone=telephone,
                              address=address, is_manager=is_manager)
            profile.save()
        else:
            context = {
                "error": "Invalid form. There was an error coming from the form"}
            return render(request, template_name='pages/admin/employees.html', context=context)
    return render(request, template_name='pages/admin/employees.html', )


@login_required(login_url='/login')
@authorize_manager_only(redirect_url='/employee/dashboard')
def delete_employees(request, id):
    CustomUser.objects.filter(pk=id).delete()
    return HttpResponseRedirect('/manager/dashboard/employees')


'''
User dashboard views and actions:

1. Deciding to put clock in or clockout on dash page. or nothing clocking if all are fulfilled
2. registering the attendance. ie doing the clocking
'''


def render_user_dashboard(request):
    attendance = Attendance.objects.filter(
        employee=request.user, date=date.today()).first()
    # cloked in only: True, clocked in but not out: false, clocked in and out: None
    clocked_in_state = True if attendance is None else None if attendance.clock_out_time is not None else False
    return render(request, template_name="pages/user/dashboard.html", content_type={"clocked_in_state": clocked_in_state})


@login_required(login_url='/login')
@csrf_exempt
def register_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            latitude = form.cleaned_data["latitude"]
            longitude = form.cleaned_data["latitude"]

            location = Location.objects.get(code=code)
            employee = request.user
            clock_out_time = datetime.now().time()

            attendance = Attendance.objects.filter(
                employee=employee, date=date.today()).first()

            if attendance is not None and attendance.clock_out_time:
                return JsonResponse({"success": True, "message": "You have already clocked in and out for today"})

            if attendance is not None:  # meaning the user has clocked in already
                attendance.clock_out_time = clock_out_time
                attendance.save()
                return JsonResponse({"success": True, "message": "You have successfully out for today"})

                # send clock out success message

            # check if all values are valid first
            attendance = Attendance.objects.create(
                location=location,
                employee=employee,
                latitude=latitude,
                longitude=longitude,
                # clocked in time is filled automatically
                clock_out_time=None
            )
            attendance.save()
            return JsonResponse({"success": True, "message": "You have successfully in for today"})
        return JsonResponse({"success": False, "errors": form.errors})
        # check that location matches geolocation of location with the current code
    return render(request, template_name='pages/user/clock-action.html')
