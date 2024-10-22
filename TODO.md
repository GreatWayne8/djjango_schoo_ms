# TODO

- **Add and Drop**:
  - The add and drop page should only include Subjects offered by the department head.
  - Add and drop date should be restricted by the school calendar.
- **Auto generate username and password when adding students and teachers**
  - Instead of filling the username and password for the student/teacher, the system should automatically generate them and send to the student's/teacher's email.
- **Payment integration**:
  - Integrating PayPal and Stripe for students to pay their fees.
  - The system should be able to track payments and send reminders to students who haven't paid their
- **Integrate the dashboard with dynamic/live data**:
  - Overall attendance
  - School demographics
      - teacher qualification
      - Students' level
  - Students average grade per course:
    This helps to keep track of students' performance
  - Overall Course Resources
    - Total number of videos, Subjects, documentation
  - Event calendar:
    - A calendar that shows upcoming events
  - Enrollments per course
    - How many students enroll in each course 
  - Website traffic over a specific user type (Admin, Student, teacher, etc.)
- **Apply Filtering for all tables**:
  - This can be done using `django-filter` and other jQuery libraries
- **Apply data exporting for all tables**:
  - This can be done using jQuery libraries like `DataTables`
- **Using a template to PDF converter to generate reports**:
  - This can be done using the popular package `xhtml2pdf`
