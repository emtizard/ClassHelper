from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db import models
from CHproto.models import Course, Student, Roster, Attendance
from django import forms
from django.shortcuts import get_object_or_404
from CHproto.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


# displays the user homepage
@login_required
def profile(request):
    user = request.user
    all_user_courses = Course.objects.filter(teacher=user)
    template = loader.get_template('profile.html')
    context = {
        'all_user_courses': all_user_courses,
    }
    return HttpResponse(template.render(context, request))

# registers new user
def register(request):
    if request.method=="POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('/CHproto/login')
    else:
        form = UserCreationForm()
    return render(request, 'registration.html', {'form': form})

# displays student roster for selected course
@login_required
def roster(request, course_id):
    user = request.user
    curr_course = Course.objects.get(pk=course_id)
    query_results = Roster.objects.filter(course=curr_course) # query_results
    template = loader.get_template('roster.html')
    students = []
    for roster_entry in query_results:
        students.append(Student.objects.get(pk=roster_entry.student.pk))
    context = {
        'students': students,
        'course': curr_course,
    }
    return HttpResponse(template.render(context, request))

# adds new student to current roster
@login_required
def newstudent(request, course_id):
    user = request.user
    curr_course = Course.objects.get(pk=course_id)

    all_teacher_students = Student.objects.filter(teacher=user)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            user = get_user(request)
            student.teacher = user
            student.save()
            roster_entry = Roster.objects.create(teacher=request.user, course=curr_course, student=student)
            return HttpResponseRedirect('/CHproto/%i/roster/' % curr_course.id)
    else:
        form = StudentForm()
        curr_course = Course.objects.get(pk=course_id)
    context = {
        'course': curr_course,
        'form':form,
        'all_teacher_students': all_teacher_students,
    }
    return render(request, 'newstudent.html', context)


# edits student entry in current roster
@login_required
def editstudent(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    curr_course = get_object_or_404(Course, pk=course_id)
    if request.method =="POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()
            return HttpResponseRedirect('/CHproto/%i/roster/' % curr_course.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'editstudent.html', {'form': form})


# removes student entry from current roster
@login_required
def removefromroster(request, student_id, course_id):
    curr_student = get_object_or_404(Student, pk=student_id)
    curr_course = get_object_or_404(Course, pk=course_id)

    curr_roster = Roster.objects.filter(student=curr_student, course=curr_course)
    curr_roster.delete()

    return HttpResponseRedirect('/CHproto/%i/roster/' % curr_course.id)

# adds new course to user's homepage
@login_required
def newcourse(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            new_course = form.save(commit=False)
            user = get_user(request)
            new_course.teacher = user
            new_course.save()
            return HttpResponseRedirect('/CHproto/profile')
    else:
        form = CourseForm()

    context = {
        'form':form,
    }

    return render(request, 'newcourse.html', context)


# removes course
@login_required
def removecourse(request, course_id):
    curr_course = get_object_or_404(Course, pk=course_id)
    curr_course.delete()
    return HttpResponseRedirect('/CHproto/profile')


# edit course information
@login_required
def editcourse(request, course_id):
    course = Course.objects.get(pk=course_id)
    if request.method =="POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            course.save()
            return HttpResponseRedirect('/CHproto/profile/')
    else:
        form = CourseForm(instance=course)
    return render(request, 'editcourse.html', {'form': form, 'course': course})


# add attendance for specified student
@login_required
def addattendance(request, student_id, course_id):
    roster = Roster.objects.get(student=student_id, course=course_id)
    print("before: " + str(roster))
    course = Course.objects.get(pk=course_id)
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=True)
            attendance.roster = roster # sets roster value for attendance
            attendance.save() # saves attendance data.
            print("after: " + str(attendance.roster))
            return HttpResponseRedirect('/CHproto/%i/attendance/' % course.id)
    else:
        form = AttendanceForm()
    return render(request, 'addattendance.html', {'form': form})


# view all attendance in table for specified student
@login_required
def viewstudentattendance(request, student_id, course_id):
    roster = Roster.objects.get(student=student_id, course=course_id)
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)

    student_attendances = Attendance.objects.filter(roster=roster)

    return render(request, 'viewstudentattendance.html', {'student_attendances': student_attendances, 'student':student, 'course': course})


# remove specified student attendance entry
@login_required
def removeattendance(request, student_id, course_id, attendance_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    attendance= get_object_or_404(Attendance, pk=attendance_id)
    attendance.delete()

    return HttpResponseRedirect('/CHproto/{0}/{1}/viewstudentattendance'.format(student.id, course.id))


# edits specified student attendance entry
@login_required
def editstudentattendance(request, student_id, course_id, attendance_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    attendance = get_object_or_404(Attendance, pk=attendance_id)

    if request.method =="POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.save()

            return HttpResponseRedirect('/CHproto/{0}/{1}/viewstudentattendance'.format(student.id, course.id))

    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'editstudentattendance.html', {'form': form})


# displays attendance page for course
@login_required
def attendance(request, course_id):
    course = Course.objects.get(pk=course_id)
    roster_entries = Roster.objects.filter(course=course)

# HOLDS ALL STUDENT ATTENDANCES FOR THIS MONTH
# student: attendance1, attendance2, etc.
    m1_a = {}
    m2_a = {}
    m3_a = {}
    m4_a = {}

# HOLDS ALL STUDENT ATTENDANCES FOR THIS WEEK
# student: attendance1, attendance2, etc.
    w1_a = {}
    w2_a = {}
    w3_a = {}
    w4_a = {}
    w5_a = {}
    w6_a = {}
    w7_a = {}
    w8_a = {}
    w9_a = {}
    w10_a = {}
    w11_a = {}
    w12_a = {}
    w13_a = {}
    w14_a = {}
    w15_a = {}
    w16_a = {}

    all_totals = {}
    week_totals = {}

    m_grand_total = {} # the 4 monthly totals for a single student
    w_grand_total = {} # the 16 weekly totals for a single student
    grand_total = {} # the semester total for a single student

    # monthly, weekly, overall total hours for all students
    m_grand_total = [0,0,0,0] # each month
    w_grand_total = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    grand_total = [0]

    students = []

    for roster_entry in roster_entries:
        curr_student = Student.objects.get(pk=roster_entry.student.pk)
        students.append(curr_student)

        #attendances[curr_student] = Attendance.objects.filter(roster=roster_entry.pk).order_by('date')
        m1_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, month_number=1).order_by('date')
        m2_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, month_number=2).order_by('date')
        m3_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, month_number=3).order_by('date')
        m4_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, month_number=4).order_by('date')

        w1_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=1).order_by('date')
        w2_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=2).order_by('date')
        w3_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=3).order_by('date')
        w4_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=4).order_by('date')
        w5_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=5).order_by('date')
        w6_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=6).order_by('date')
        w7_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=7).order_by('date')
        w8_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=8).order_by('date')
        w9_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=9).order_by('date')
        w10_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=10).order_by('date')
        w11_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=11).order_by('date')
        w12_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=12).order_by('date')
        w13_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=13).order_by('date')
        w14_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=14).order_by('date')
        w15_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=15).order_by('date')
        w16_a[curr_student] = Attendance.objects.filter(roster=roster_entry.pk, week_number=16).order_by('date')

        #m1_total[curr_student] = 0
        w1_total = 0
        w2_total = 0
        w3_total = 0
        w4_total = 0
        w5_total = 0
        w6_total = 0
        w7_total = 0
        w8_total = 0
        w9_total = 0
        w10_total = 0
        w11_total = 0
        w12_total = 0
        w13_total = 0
        w14_total = 0
        w15_total = 0
        w16_total = 0

        #m1_total[curr_student] = 0
        m1_total = 0
        m2_total = 0
        m3_total = 0
        m4_total = 0

        print ("attendances found " + str(len(Attendance.objects.filter(month_number=1))))

        for value in m1_a[curr_student]:
            m1_total += value.hours_attended
            print ("attendances found " )

        for value in m2_a[curr_student]:
            m2_total += value.hours_attended

        for value in m3_a[curr_student]:
            m3_total += value.hours_attended

        for value in m4_a[curr_student]:
            m4_total += value.hours_attended

        for value in w1_a[curr_student]:
            w1_total += value.hours_attended

        for value in w2_a[curr_student]:
            w2_total += value.hours_attended

        for value in w3_a[curr_student]:
            w3_total += value.hours_attended

        for value in w4_a[curr_student]:
            w4_total += value.hours_attended

        for value in w5_a[curr_student]:
            w5_total += value.hours_attended

        for value in w6_a[curr_student]:
            w6_total += value.hours_attended

        for value in w7_a[curr_student]:
            w7_total += value.hours_attended

        for value in w8_a[curr_student]:
            w8_total += value.hours_attended

        for value in w9_a[curr_student]:
            w9_total += value.hours_attended

        for value in w10_a[curr_student]:
            w10_total += value.hours_attended

        for value in w11_a[curr_student]:
            w11_total += value.hours_attended

        for value in w12_a[curr_student]:
            w12_total += value.hours_attended

        for value in w13_a[curr_student]:
            w13_total += value.hours_attended

        for value in w14_a[curr_student]:
            w14_total += value.hours_attended

        for value in w15_a[curr_student]:
            w15_total += value.hours_attended

        for value in w16_a[curr_student]:
            w16_total += value.hours_attended

        overall_hours = m1_total+m2_total+m3_total+m4_total

        all_totals[curr_student] = [m1_total, m2_total, m3_total, m4_total, overall_hours]
        week_totals[curr_student] = [w1_total, w2_total, w3_total, w4_total, w5_total, w6_total, w7_total, w8_total, w9_total, w10_total, w11_total, w12_total, w13_total, w14_total, w15_total, w16_total]

        m_grand_total[0] += m1_total
        m_grand_total[1] += m2_total
        m_grand_total[2] += m3_total
        m_grand_total[3] += m4_total

        w_grand_total[0] += w1_total
        w_grand_total[1] += w2_total
        w_grand_total[2] += w3_total
        w_grand_total[3] += w4_total
        w_grand_total[4] += w5_total
        w_grand_total[5] += w6_total
        w_grand_total[6] += w7_total
        w_grand_total[7] += w8_total
        w_grand_total[8] += w9_total
        w_grand_total[9] += w10_total
        w_grand_total[10] += w11_total
        w_grand_total[11] += w12_total
        w_grand_total[12] += w13_total
        w_grand_total[13] += w14_total
        w_grand_total[14] += w15_total
        w_grand_total[15] += w16_total

        grand_total[0] = m_grand_total[0] + m_grand_total[1] + m_grand_total[2] + m_grand_total[3]

        # loop ends

    context = {
        'course': course,
        'm_grand_total': m_grand_total,
        'w_grand_total': w_grand_total,
        'grand_total': grand_total,
        'all_totals': all_totals,
        'week_totals': week_totals,
        'roster_entries': roster_entries,
        'students': students,
    }

    template = loader.get_template('att.html')

    return HttpResponse(template.render(context, request))

"""

STUDENT ATTENDANCE GRAPHING

"""

# graphs specified student attendance for specified month
@login_required
def GraphStudentAttendanceMonth(request, student_id, course_id, month_number):
    course = Course.objects.get(pk=course_id)
    student = Student.objects.get(pk=student_id)
    roster_entries = Roster.objects.filter(course=course, student=student)

    time_period = "month " + month_number

    month_attendances = []

    for roster in roster_entries:
        month_attendances.append(Attendance.objects.filter(roster=roster,
        month_number=month_number))


    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in month_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'student': student,
        'time_period': time_period,
    }

    template = loader.get_template('graph.html')

    return HttpResponse(template.render(context, request))


# graphs specified student attendance for specified week
@login_required
def GraphStudentAttendanceWeek(request, student_id, course_id, week_number):
    course = Course.objects.get(pk=course_id)
    student = Student.objects.get(pk=student_id)
    roster_entries = Roster.objects.filter(course=course, student=student)

    time_period = "week " + week_number

    week_attendances = []

    for roster in roster_entries:
        week_attendances.append(Attendance.objects.filter(roster=roster,
         week_number=week_number))


    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in week_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'student': student,
        'time_period': time_period,
    }

    template = loader.get_template('graph.html')

    return HttpResponse(template.render(context, request))


# graphs specified student attendance for entire semester
@login_required
def GraphStudentAttendanceOverall(request, student_id, course_id):
    course = Course.objects.get(pk=course_id)
    student = Student.objects.get(pk=student_id)
    roster_entries = Roster.objects.filter(course=course, student=student)

    time_period = "semester"

    total_attendances = []

    for roster in roster_entries:
        total_attendances.append(Attendance.objects.filter(roster=roster))


    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in total_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'student': student,
        'time_period': time_period,
    }

    template = loader.get_template('graph.html')

    return HttpResponse(template.render(context, request))

"""

CLASS ATTENDANCE GRAPHING

"""

# graphs course attendance for entire semester
@login_required
def GraphClassAttendanceOverall(request, course_id):
    course = Course.objects.get(pk=course_id)
    roster_entries = Roster.objects.filter(course=course)

    time_period = "semester"

    total_attendances = []

    for roster in roster_entries:
        total_attendances.append(Attendance.objects.filter(roster=roster))

    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in total_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'time_period': time_period,
    }

    template = loader.get_template('classgraph.html')

    return HttpResponse(template.render(context, request))


# graphs course attendance for specified month
@login_required
def GraphClassAttendanceMonth(request, course_id, month_number):
    course = Course.objects.get(pk=course_id)
    roster_entries = Roster.objects.filter(course=course)

    time_period = "month " + month_number

    month_attendances = []

    for roster in roster_entries:
        month_attendances.append(Attendance.objects.filter(roster=roster,
        month_number=month_number))


    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in month_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'time_period': time_period,
    }

    template = loader.get_template('classgraph.html')

    return HttpResponse(template.render(context, request))

# graphs course attendance for specified week
@login_required
def GraphClassAttendanceWeek(request, course_id, week_number):
    course = Course.objects.get(pk=course_id)
    roster_entries = Roster.objects.filter(course=course)

    time_period = "week " + week_number

    week_attendances = []

    for roster in roster_entries:
        week_attendances.append(Attendance.objects.filter(roster=roster,
         week_number=week_number))

    f_a_t = {}
    f_a_t = [0,0,0,0]

    for item in week_attendances:
        for mark in item:
            if mark.attendance_mark == 'FULL':
                f_a_t[0] += 1

            elif mark.attendance_mark == 'TARDY':
                f_a_t[3] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == True:
                f_a_t[1] += 1

            elif mark.attendance_mark == 'ABSENT' and mark.absent_excused == False:
                f_a_t[2] += 1

    context = {
        'f_a_t': f_a_t,
        'course': course,
        'time_period': time_period,
    }

    template = loader.get_template('classgraph.html')

    return HttpResponse(template.render(context, request))


# displays help page documentation
def help(request):
    template = loader.get_template('help.html')
    return HttpResponse(template.render(request))
