from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django_filters.views import FilterView

from accounts.models import User, Student
from core.models import Session, Semester
from result.models import TakenCourse
from accounts.decorators import teacher_required, student_required
from .forms import (
    ProgramForm,
    CourseAddForm,
    CourseAllocationForm,
    EditCourseAllocationForm,
    UploadFormFile,
    UploadFormVideo,
)
from .filters import ProgramFilter, CourseAllocationFilter
from .models import Program, Course, CourseAllocation, Upload, UploadVideo


@method_decorator([login_required], name="dispatch")
class ProgramFilterView(FilterView):
    filterset_class = ProgramFilter
    template_name = "course/program_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Programs"
        return context


@login_required
@teacher_required
def program_add(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, request.POST.get("title") + " program has been created."
            )
            return redirect("programs")
        else:
            messages.error(request, "Correct the error(S) below.")
    else:
        form = ProgramForm()

    return render(
        request,
        "course/program_add.html",
        {
            "title": "Add Program",
            "form": form,
        },
    )


@login_required
def program_detail(request, pk):
    program = Program.objects.get(pk=pk)
    Subjects = Course.objects.filter(program_id=pk).order_by("-year")
    credits = Course.objects.aggregate(Sum("credit"))

    paginator = Paginator(Subjects, 10)
    page = request.GET.get("page")

    Subjects = paginator.get_page(page)

    return render(
        request,
        "course/program_single.html",
        {
            "title": program.title,
            "program": program,
            "Subjects": Subjects,
            "credits": credits,
        },
    )


@login_required
@teacher_required
def program_edit(request, pk):
    program = Program.objects.get(pk=pk)

    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(
                request, str(request.POST.get("title")) + " program has been updated."
            )
            return redirect("programs")
    else:
        form = ProgramForm(instance=program)

    return render(
        request,
        "course/program_add.html",
        {"title": "Edit Program", "form": form},
    )


@login_required
@teacher_required
def program_delete(request, pk):
    program = Program.objects.get(pk=pk)
    title = program.title
    program.delete()
    messages.success(request, "Program " + title + " has been deleted.")

    return redirect("programs")


# ########################################################


# ########################################################
# Course views
# ########################################################
@login_required
def course_single(request, slug):
    course = Course.objects.get(slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)

    # teachers = User.objects.filter(allocated_teacher__pk=course.id)
    teachers = CourseAllocation.objects.filter(Subjects__pk=course.id)

    return render(
        request,
        "course/course_single.html",
        {
            "title": course.title,
            "course": course,
            "files": files,
            "videos": videos,
            "teachers": teachers,
            "media_url": settings.MEDIA_ROOT,
        },
    )


@login_required
@teacher_required
def course_add(request, pk):
    users = User.objects.all()
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        course_name = request.POST.get("title")
        course_code = request.POST.get("code")
        if form.is_valid():
            form.save()
            messages.success(
                request, (course_name + "(" + course_code + ")" + " has been created.")
            )
            return redirect("program_detail", pk=request.POST.get("program"))
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(initial={"program": Program.objects.get(pk=pk)})

    return render(
        request,
        "course/course_add.html",
        {
            "title": "Add Course",
            "form": form,
            "program": pk,
            "users": users,
        },
    )


@login_required
@teacher_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        course_name = request.POST.get("title")
        course_code = request.POST.get("code")
        if form.is_valid():
            form.save()
            messages.success(
                request, (course_name + "(" + course_code + ")" + " has been updated.")
            )
            return redirect("program_detail", pk=request.POST.get("program"))
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(instance=course)

    return render(
        request,
        "course/course_add.html",
        {
            "title": "Edit Course",
            # 'form': form, 'program': pk, 'course': pk
            "form": form,
        },
    )


@login_required
@teacher_required
def course_delete(request, slug):
    course = Course.objects.get(slug=slug)
    # course_name = course.title
    course.delete()
    messages.success(request, "Course " + course.title + " has been deleted.")

    return redirect("program_detail", pk=course.program.id)


# ########################################################


# ########################################################
# Course Allocation
# ########################################################
@method_decorator([login_required], name="dispatch")
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = "course/course_allocation_form.html"

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a staff has been allocated a course before update it else create new
        teacher = form.cleaned_data["teacher"]
        selected_Subjects = form.cleaned_data["Subjects"]
        Subjects = ()
        for course in selected_Subjects:
            Subjects += (course.pk,)
        # print(Subjects)

        try:
            a = CourseAllocation.objects.get(teacher=teacher)
        except:
            a = CourseAllocation.objects.create(teacher=teacher)
        for i in range(0, selected_Subjects.count()):
            a.Subjects.add(Subjects[i])
            a.save()
        return redirect("course_allocation_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Assign Course"
        return context


@method_decorator([login_required], name="dispatch")
class CourseAllocationFilterView(FilterView):
    filterset_class = CourseAllocationFilter
    template_name = "course/course_allocation_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Course Allocations"
        return context


@login_required
@teacher_required
def edit_allocated_course(request, pk):
    allocated = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == "POST":
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, "course assigned has been updated.")
            return redirect("course_allocation_view")
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(
        request,
        "course/course_allocation_form.html",
        {"title": "Edit Course Allocated", "form": form, "allocated": pk},
    )


@login_required
@teacher_required
def deallocate_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, "successfully deallocate!")
    return redirect("course_allocation_view")


# ########################################################


# ########################################################
# File Upload views
# ########################################################
@login_required
@teacher_required
def handle_file_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.save()

            messages.success(
                request, (request.POST.get("title") + " has been uploaded.")
            )
            return redirect("course_detail", slug=slug)
    else:
        form = UploadFormFile()
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "File Upload", "form": form, "course": course},
    )


@login_required
@teacher_required
def handle_file_edit(request, slug, file_id):
    course = Course.objects.get(slug=slug)
    instance = Upload.objects.get(pk=file_id)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(
                request, (request.POST.get("title") + " has been updated.")
            )
            return redirect("course_detail", slug=slug)
    else:
        form = UploadFormFile(instance=instance)

    return render(
        request,
        "upload/upload_file_form.html",
        {"title": instance.title, "form": form, "course": course},
    )


def handle_file_delete(request, slug, file_id):
    file = Upload.objects.get(pk=file_id)
    # file_name = file.name
    file.delete()

    messages.success(request, (file.title + " has been deleted."))
    return redirect("course_detail", slug=slug)


# ########################################################
# Video Upload views
# ########################################################
@login_required
@teacher_required
def handle_video_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.save()

            messages.success(
                request, (request.POST.get("title") + " has been uploaded.")
            )
            return redirect("course_detail", slug=slug)
    else:
        form = UploadFormVideo()
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Video Upload", "form": form, "course": course},
    )


@login_required
# @teacher_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(request, "upload/video_single.html", {"video": video})


@login_required
@teacher_required
def handle_video_edit(request, slug, video_slug):
    course = Course.objects.get(slug=slug)
    instance = UploadVideo.objects.get(slug=video_slug)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, (request.POST.get("title") + " has been updated.")
            )
            return redirect("course_detail", slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(
        request,
        "upload/upload_video_form.html",
        {"title": instance.title, "form": form, "course": course},
    )


def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    # video = UploadVideo.objects.get(slug=video_slug)
    video.delete()

    messages.success(request, (video.title + " has been deleted."))
    return redirect("course_detail", slug=slug)


# ########################################################


# ########################################################
# Course Registration
# ########################################################
@login_required
@student_required
def course_registration(request):
    if request.method == "POST":
        student = Student.objects.get(student__pk=request.user.id)
        ids = ()
        data = request.POST.copy()
        data.pop("csrfmiddlewaretoken", None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.create(student=student, course=course)
            obj.save()
        messages.success(request, "Subjects registered successfully!")
        return redirect("course_registration")
    else:
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        if not current_semester:
            messages.error(request, "No active semester found.")
            return render(request, "course/course_registration.html")

        # student = Student.objects.get(student__pk=request.user.id)
        student = get_object_or_404(Student, student__id=request.user.id)
        taken_Subjects = TakenCourse.objects.filter(student__student__id=request.user.id)
        t = ()
        for i in taken_Subjects:
            t += (i.course.pk,)

        Subjects = (
            Course.objects.filter(
                program__pk=student.program.id,
                level=student.level,
                semester=current_semester,
            )
            .exclude(id__in=t)
            .order_by("year")
        )
        all_Subjects = Course.objects.filter(
            level=student.level, program__pk=student.program.id
        )

        no_course_is_registered = False  # Check if no course is registered
        all_Subjects_are_registered = False

        registered_Subjects = Course.objects.filter(level=student.level).filter(id__in=t)
        if (
            registered_Subjects.count() == 0
        ):  # Check if number of registered Subjects is 0
            no_course_is_registered = True

        if registered_Subjects.count() == all_Subjects.count():
            all_Subjects_are_registered = True

        total_first_semester_credit = 0
        total_sec_semester_credit = 0
        total_registered_credit = 0
        for i in Subjects:
            if i.semester == "First":
                total_first_semester_credit += int(i.credit)
            if i.semester == "Second":
                total_sec_semester_credit += int(i.credit)
        for i in registered_Subjects:
            total_registered_credit += int(i.credit)
        context = {
            "is_calender_on": True,
            "all_Subjects_are_registered": all_Subjects_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "Subjects": Subjects,
            "total_first_semester_credit": total_first_semester_credit,
            "total_sec_semester_credit": total_sec_semester_credit,
            "registered_Subjects": registered_Subjects,
            "total_registered_credit": total_registered_credit,
            "student": student,
        }
        return render(request, "course/course_registration.html", context)


@login_required
@student_required
def course_drop(request):
    if request.method == "POST":
        student = Student.objects.get(student__pk=request.user.id)
        ids = ()
        data = request.POST.copy()
        data.pop("csrfmiddlewaretoken", None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.get(student=student, course=course)
            obj.delete()
        messages.success(request, "Successfully Dropped!")
        return redirect("course_registration")


# ########################################################


@login_required
def user_course_list(request):
    if request.user.is_teacher:
        Subjects = Course.objects.filter(allocated_course__teacher__pk=request.user.id)

        return render(request, "course/user_course_list.html", {"Subjects": Subjects})

    elif request.user.is_student:
        student = Student.objects.get(student__pk=request.user.id)
        taken_Subjects = TakenCourse.objects.filter(
            student__student__id=student.student.id
        )
        Subjects = Course.objects.filter(level=student.level).filter(
            program__pk=student.program.id
        )

        return render(
            request,
            "course/user_course_list.html",
            {"student": student, "taken_Subjects": taken_Subjects, "Subjects": Subjects},
        )

    else:
        return render(request, "course/user_course_list.html")
