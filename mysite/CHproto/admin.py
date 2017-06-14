from django.contrib import admin

from .models import Course, Attendance, Roster, Student

class AttendanceInline(admin.TabularInline):
    model = Attendance

class CourseAdmin(admin.ModelAdmin):
    model = Course #StudentInLine, AttendanceInLine

admin.site.register(Course, CourseAdmin)

class StudentAdmin(admin.ModelAdmin):
    model = Student

admin.site.register(Student, StudentAdmin)

class RosterAdmin(admin.ModelAdmin):
    model = Roster
    inlines = [ AttendanceInline ]

admin.site.register(Roster, RosterAdmin)
