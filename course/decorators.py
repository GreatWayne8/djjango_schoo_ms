# from django.contrib.auth import REDIRECT_FIELD_NAME
# from django.http import Http404
from coursemanagement.models import Subjectsetting

# def student_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, calender_url=Http404):
#     """
#     Decorator for views that checks that the logged in user is a student,
#     redirects to the log-in page if necessary.
#     """
# 	obj = Subjectsetting.objects.get(add_drop=True)
#     if obj is not None:
#     if function:
#         return actual_decorator(function)
#     return actual_decorator

is_calender_on = Subjectsetting.objects.filter(add_drop=True).count() > 0
