from celery import shared_task
from django.contrib.auth import get_user_model
from core.utils import send_html_email

@shared_task
def send_new_student_email(user_pk, password):
    user = get_user_model().objects.get(pk=user_pk)
    send_html_email(
        subject="Your Dj LMS account confirmation and credentials",
        recipient_list=[user.email],
        template="accounts/email/new_student_account_confirmation.html",
        context={"user": user, "password": password},
    )

@shared_task
def send_new_teacher_email(user_pk, password):  # Updated function name
    user = get_user_model().objects.get(pk=user_pk)
    send_html_email(
        subject="Your Dj LMS account confirmation and credentials",
        recipient_list=[user.email],
        template="accounts/email/new_teacher_account_confirmation.html",  # Updated template
        context={"user": user, "password": password},
    )
