from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings

def generate_password():
    return get_user_model().objects.make_random_password()

def generate_student_id():
    # Generate a username based on first and last name and registration date
    registered_year = datetime.now().strftime("%Y")
    students_count = get_user_model().objects.filter(is_student=True).count()
    return f"{settings.STUDENT_ID_PREFIX}-{registered_year}-{students_count}"

def generate_teacher_id():  
    # Generate a username based on first and last name and registration date
    registered_year = datetime.now().strftime("%Y")
    teachers_count = get_user_model().objects.filter(is_teacher=True).count()  
    return f"{settings.TEACHER_ID_PREFIX}-{registered_year}-{teachers_count}"  

def generate_student_credentials():
    return generate_student_id(), generate_password()

def generate_teacher_credentials():  
    return generate_teacher_id(), generate_password()  
