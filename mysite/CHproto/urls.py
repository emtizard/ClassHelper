from django.conf.urls import url, include

from . import views

from django.conf import settings


urlpatterns = [
    url('^register/', views.register, name='register'),

    url('^help/', views.help, name='help'),

    url(r'^(?P<course_id>[0-9]+)/GraphClassAttendanceOverall/$', views.GraphClassAttendanceOverall, name='GraphClassAttendanceOverall'),
    url(r'^(?P<course_id>[0-9]+)/(?P<week_number>[0-9]+)/GraphClassAttendanceWeek/$', views.GraphClassAttendanceWeek, name='GraphClassAttendanceWeek'),
    url(r'^(?P<course_id>[0-9]+)/(?P<month_number>[0-9]+)/GraphClassAttendanceMonth/$', views.GraphClassAttendanceMonth, name='GraphClassAttendanceMonth'),

    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/addattendance/$', views.addattendance, name='addattendance'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/viewstudentattendance/$', views.viewstudentattendance, name='viewstudentattendance'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/(?P<attendance_id>[0-9]+)/editstudentattendance/$', views.editstudentattendance, name='editstudentattendance'),

    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/(?P<attendance_id>[0-9]+)/removeattendance/$', views.removeattendance, name='removeattendance'),


    url(r'^(?P<course_id>[0-9]+)/attendance/$', views.attendance, name='attendance'),
    url(r'^(?P<course_id>[0-9]+)/removecourse/$', views.removecourse, name='removecourse'),
    url(r'^newcourse/$', views.newcourse, name='newcourse'),
    url(r'^(?P<course_id>[0-9]+)/editcourse/$', views.editcourse, name='editcourse'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/removefromroster/$', views.removefromroster, name='removefromroster'),
    url(r'^(?P<course_id>[0-9]+)/roster/newstudent/$', views.newstudent, name='newstudent'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/editstudent/$', views.editstudent, name='editstudent'),
    url(r'^(?P<course_id>[0-9]+)/roster/$', views.roster, name='roster'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/GraphStudentAttendanceOverall/$', views.GraphStudentAttendanceOverall, name='GraphStudentAttendanceOverall'),
    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/(?P<month_number>[0-9]+)/GraphStudentAttendanceMonth/$', views.GraphStudentAttendanceMonth, name='GraphStudentAttendanceMonth'),

    url(r'^(?P<student_id>[0-9]+)/(?P<course_id>[0-9]+)/(?P<week_number>[0-9]+)/GraphStudentAttendanceWeek/$', views.GraphStudentAttendanceWeek, name='GraphStudentAttendanceWeek'),

    url(r'^profile/$', views.profile, name='profile'),
    url('^', include('django.contrib.auth.urls')),

]
