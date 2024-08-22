from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm
from django_filters.views import FilterView
from core.models import Session, Semester
from course.models import Course
from result.models import TakenCourse
from .decorators import admin_required
from .models import User, Student, Parent,Teacher
from .filters import TeacherFilter, StudentFilter
from .forms import TeacherAddForm, StudentAddForm, ProfileUpdateForm, ParentAddForm

# To generate pdf from template we need the following
from django.http import HttpResponse
from django.template.loader import get_template  # To get template which render as pdf
from xhtml2pdf import pisa
from django.template.loader import render_to_string  # To render a template into a string
# from .filters import ProgramFilter
# from .models import Program


class TeacherFilterView(FilterView):
    model = User
    filterset_class = TeacherFilter
    template_name = 'accounts/teacher_list.html'

class StudentListView(FilterView):
    model = User
    filterset_class = StudentFilter
    template_name = 'accounts/student_list.html' 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = context['object_list']  # This is the filtered queryset

        # Print each user's fields dynamically
        for student in students:
            print("User details:")
            for key, value in vars(student).items():
                if not key.startswith('_'):  # Skip private attributes
                    print(f"{key}: {value}")
            print("----------")  # Separator betw

# def program_list(request):
#     filter = ProgramFilter(request.GET, queryset=Program.objects.all())
#     return render(request, 'program_list.html', {'filter': filter})


def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)

def register(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Account created successfully.")
        else:
            messages.error(
                request, f"Something is not correct, please fill all fields correctly."
            )
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    """Show profile of any user that fires out the request"""
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    if request.user.is_teacher:
        Subjects = Course.objects.filter(
            allocated_course__teacher__pk=request.user.id
        ).filter(semester=current_semester)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "Subjects": Subjects,
                "current_session": current_session,
                "current_semester": current_semester,
            },
        )
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=level)
        except:
            parent = "no parent set"
        Subjects = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=level.level
        )
        context = {
            "title": request.user.get_full_name,
            "parent": parent,
            "Subjects": Subjects,
            "level": level,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile.html", context)
    else:
        staff = User.objects.filter(is_teacher=True)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "staff": staff,
                "current_session": current_session,
                "current_semester": current_semester,
            },
        )

def render_to_pdf(template_name, context):
    """Renders a given template to PDF format."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="profile.pdf"'  # Set default filename

    template = render_to_string(template_name, context)
    pdf = pisa.CreatePDF(
        template,
        dest=response
    )
    if pdf.err:
        return HttpResponse('We had some problems generating the PDF')
    
    return response


def create_teachers_pdf_list(request):
    teachers = Teacher.objects.all()
    template_path = 'pdf/teacher_pdf_list.html'
    context = {'teachers': teachers}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="teacher_list.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@admin_required
def profile_single(request, id):
    """Show profile of any selected user"""
    if request.user.id == id:
        return redirect("/profile/")

    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    user = User.objects.get(pk=id)
    """
    If download_pdf exists, instead of calling render_to_pdf directly, 
    pass the context dictionary built for the specific user type 
    (teacher, student, or superuser) to the render_to_pdf function.
    """
    if request.GET.get('download_pdf'):
        if user.is_teacher:
            Subjects = Course.objects.filter(allocated_course__teacher__pk=id).filter(
                semester=current_semester
            )
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Teacher",
                "Subjects": Subjects,
                "current_session": current_session,
                "current_semester": current_semester,
            }
        elif user.is_student:
            student = Student.objects.get(student__pk=id)
            Subjects = TakenCourse.objects.filter(
                student__student__id=id, course__level=student.level
            )
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Student",
                "Subjects": Subjects,
                "student": student,
                "current_session": current_session,
                "current_semester": current_semester,
            }
        else:
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Superuser",
                "current_session": current_session,
                "current_semester": current_semester,
            }
        return render_to_pdf("pdf/profile_single.html", context)

    else:
        if user.is_teacher:
            Subjects = Course.objects.filter(allocated_course__teacher__pk=id).filter(
                semester=current_semester
            )
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Teacher",
                "Subjects": Subjects,
                "current_session": current_session,
                "current_semester": current_semester,
            }
            return render(request, "accounts/profile_single.html", context)
        elif user.is_student:
            student = Student.objects.get(student__pk=id)
            Subjects = TakenCourse.objects.filter(
                student__student__id=id, course__level=student.level
            )
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Student",
                "Subjects": Subjects,
                "student": student,
                "current_session": current_session,
                "current_semester": current_semester,
            }
            return render(request, "accounts/profile_single.html", context)
        else:
            context = {
                "title": user.get_full_name,
                "user": user,
                "user_type": "Superuser",
                "current_session": current_session,
                "current_semester": current_semester,
            }
            return render(request, "accounts/profile_single.html", context)

@login_required
@admin_required
def admin_panel(request):
    return render(
        request, "setting/admin_panel.html", {"title": request.user.get_full_name}
    )

@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(
        request,
        "setting/profile_info_change.html",
        {
            "title": "Setting",
            "form": form,
        },
    )

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "setting/password_change.html",
        {
            "form": form,
        },
    )
# @login_required
# @admin_required
# def staff_add_view(request):
#     if request.method == "POST":
#         form = TeacherAddForm(request.POST)
#         if form.is_valid():
#             teacher, password = form.save()
#             # Optionally send the username and password via email or display on screen
#             messages.success(
#                 request,
#                 f"Account for teacher {teacher.first_name} {teacher.last_name} has been created."
#                 f" Username: {teacher.username}, Password: {password}."
#             )
#             return redirect("teacher_list")
#     else:
#         form = TeacherAddForm()

#     context = {
#         "title": "Teacher Add",
#         "form": form,
#     }

#     return render(request, "accounts/add_staff.html", context)

    
@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = TeacherAddForm(request.POST)
        if form.is_valid():
            teacher = form.save()  # No password return here
            # Optionally send the username and password via email or display on screen
            messages.success(
                request,
                f"Account for teacher {teacher.first_name} {teacher.last_name} has been created."
                f" Username: {teacher.username}."
            )
            return redirect("teacher_list")
    else:
        form = TeacherAddForm()

    context = {
        "title": "Teacher Add",
        "form": form,
    }

    return render(request, "accounts/add_staff.html", context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_teacher=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Teacher " + full_name + " has been updated.")
            return redirect("teacher_list")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=instance)

    context = {
        "form": form,
        "title": "Edit Teacher",
    }

    return render(request, "accounts/edit_staff.html", context)

@login_required
@admin_required
def delete_staff(request, pk):
    staff = get_object_or_404(User, is_teacher=True, pk=pk)
    staff.delete()
    messages.success(request, "Teacher " + staff.get_full_name + " has been deleted.")
    return redirect("teacher_list")


@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            student, password = form.save()
            # Optionally send the username and password via email or display on screen
            messages.success(
                request,
                f"Account for student {student.first_name} {student.last_name} has been created."
                f" Username: {student.username}, Password: {password}."
            )
            return redirect("student_list")
    else:
        form = StudentAddForm()

    context = {
        "title": "Student Add",
        "form": form,
    }

    return render(request, "accounts/add_student.html", context)
# @login_required
# @admin_required
# def student_add_view(request):
#     if request.method == "POST":
#         form = StudentAddForm(request.POST)
#         first_name = request.POST.get("first_name")
#         last_name = request.POST.get("last_name")
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request,
#                 "Account for " + first_name + " " + last_name + " has been created.",
#             )
#             return redirect("student_list")
#         else:
#             messages.error(request, "Correct the error(s) below.")
#     else:
#         form = StudentAddForm()

#     return render(
#         request,
#         "accounts/add_student.html",
#         {"title": "Add Student", "form": form},
#     )



# @login_required
# @admin_required
# def student_add_view(request):
#     if request.method == "POST":
#         form = StudentAddForm(request.POST)
#         first_name = request.POST.get("first_name")
#         last_name = request.POST.get("last_name")
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request,
#                 "Account for " + first_name + " " + last_name + " has been created.",
#             )
#             return redirect("student_list")
#         else:
#             messages.error(request, "Correct the error(s) below.")
#     else:
#         form = StudentAddForm()

#     return render(
#         request,
#         "accounts/add_student.html",
#         {"title": "Add Student", "form": form},
#     )



@login_required
@admin_required
def edit_student(request, pk):
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Student " + full_name + " has been updated.")
            return redirect("student_list")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=instance)

    context = {
        "form": form,
        "title": "Edit Student",
    }

    return render(request, "accounts/edit_student.html", context)

@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(User, is_student=True, pk=pk)
    student.delete()
    messages.success(request, "Student " + student.get_full_name + " has been deleted.")
    return redirect("student_list")

@login_required
@admin_required
def ParentAdd(request):
    if request.method == "POST":
        form = ParentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Parent information added successfully."
            )
            return redirect("student_list")
    else:
        form = ParentAddForm()

    context = {
        "title": "Add Parent",
        "form": form,
    }

    return render(request, "accounts/add_parent.html", context)

@login_required
@admin_required
def render_teacher_pdf_list(request):
    teachers = User.objects.filter(is_teacher=True)
    context = {
        "teachers": teachers,
        "title": "Teachers List",
    }
    return render_to_pdf("pdf/teacher_pdf_list.html", context)

@login_required
@admin_required
def render_student_pdf_list(request):
    students = User.objects.filter(is_student=True)
    context = {
        "students": students,
        "title": "Students List",
    }
    return render_to_pdf("pdf/student_pdf_list.html", context)
