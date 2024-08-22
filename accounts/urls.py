from django.urls import path, include

from .views import (
    profile,
    profile_single,
    admin_panel,
    profile_update,
    change_password,
    TeacherFilterView,  
    StudentListView,
    staff_add_view,
    edit_staff,
    delete_staff,
    student_add_view,
    edit_student,
    delete_student,
    ParentAdd,
    validate_username,
    register,
    render_teacher_pdf_list,  
    render_student_pdf_list
)

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("admin_panel/", admin_panel, name="admin_panel"),
    path("profile/", profile, name="profile"),
    path("profile/<int:id>/detail/", profile_single, name="profile_single"),
    path("setting/", profile_update, name="edit_profile"),
    path("change_password/", change_password, name="change_password"),
    path("teachers/", TeacherFilterView.as_view(), name="teacher_list"), 
    path("teacher/add/", staff_add_view, name="add_teacher"),
    path("staff/<int:pk>/edit/", edit_staff, name="staff_edit"),
    path("teachers/<int:pk>/delete/", delete_staff, name="teacher_delete"),  
    path("students/", StudentListView.as_view(), name="student_list"),
    path("student/add/", student_add_view, name="add_student"),
    path("student/<int:pk>/edit/", edit_student, name="student_edit"),
    path("students/<int:pk>/delete/", delete_student, name="student_delete"),
    path("parents/add/", ParentAdd, name="add_parent"),
    path("ajax/validate-username/", validate_username, name="validate_username"),
    path("register/", register, name="register"),
    # Paths to PDF
    path("create_teachers_pdf_list/", render_teacher_pdf_list, name="teacher_list_pdf"),   
    path("create_students_pdf_list/", render_student_pdf_list, name="student_list_pdf"),
]
