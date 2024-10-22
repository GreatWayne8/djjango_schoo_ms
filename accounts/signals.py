from .tasks import send_new_student_email, send_new_teacher_email
from .utils import generate_student_credentials, generate_teacher_credentials


def post_save_account_receiver(sender, instance=None, created=False, *args, **kwargs):
    """
    Send email notification
    """
    if created:
        if instance.is_student:
            username, password = generate_student_credentials()
            instance.username = username
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_student_email.delay(instance.pk, password)

        if instance.is_teacher: 
            username, password = generate_teacher_credentials()  # Updated function call
            instance.username = username
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_teacher_email.delay(instance.pk, password)  # Updated task call
