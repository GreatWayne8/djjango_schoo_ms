# Generated by Django 4.0.8 on 2024-08-09 16:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figure', models.ImageField(blank=True, help_text="Add an image for the question if it's necessary.", null=True, upload_to='uploads/%Y/%m/%d', verbose_name='Figure')),
                ('content', models.CharField(help_text='Enter the question text that you want displayed', max_length=1000, verbose_name='Question')),
                ('explanation', models.TextField(blank=True, help_text='Explanation to be shown after the question has been answered.', max_length=2000, verbose_name='Explanation')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, verbose_name='Title')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField(blank=True, help_text='A detailed description of the quiz', verbose_name='Description')),
                ('category', models.TextField(blank=True, choices=[('assignment', 'Assignment'), ('exam', 'Exam'), ('practice', 'Practice Quiz')])),
                ('random_order', models.BooleanField(default=False, help_text='Display the questions in a random order or as they are set?', verbose_name='Random Order')),
                ('answers_at_end', models.BooleanField(default=False, help_text='Correct answer is NOT shown after question. Answers displayed at the end.', verbose_name='Answers at end')),
                ('exam_paper', models.BooleanField(default=False, help_text='If yes, the result of each attempt by a user will be stored. Necessary for marking.', verbose_name='Exam Paper')),
                ('single_attempt', models.BooleanField(default=False, help_text='If yes, only one attempt by a user will be permitted.', verbose_name='Single Attempt')),
                ('pass_mark', models.SmallIntegerField(blank=True, default=50, help_text='Percentage required to pass exam.', validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Pass Mark')),
                ('draft', models.BooleanField(blank=True, default=False, help_text='If yes, the quiz is not displayed in the quiz list and can only be taken by users who can edit quizzes.', verbose_name='Draft')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course.course')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.CreateModel(
            name='EssayQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='quiz.question')),
            ],
            options={
                'verbose_name': 'Essay style question',
                'verbose_name_plural': 'Essay style questions',
            },
            bases=('quiz.question',),
        ),
        migrations.CreateModel(
            name='MCQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='quiz.question')),
                ('choice_order', models.CharField(blank=True, choices=[('content', 'Content'), ('random', 'Random'), ('none', 'None')], help_text='The order in which multichoice choice options are displayed to the user', max_length=30, null=True, verbose_name='Choice Order')),
            ],
            options={
                'verbose_name': 'Multiple Choice Question',
                'verbose_name_plural': 'Multiple Choice Questions',
            },
            bases=('quiz.question',),
        ),
        migrations.CreateModel(
            name='Sitting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question Order')),
                ('question_list', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question List')),
                ('incorrect_questions', models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Incorrect questions')),
                ('current_score', models.IntegerField(verbose_name='Current Score')),
                ('complete', models.BooleanField(default=False, verbose_name='Complete')),
                ('user_answers', models.TextField(blank=True, default='{}', verbose_name='User Answers')),
                ('start', models.DateTimeField(auto_now_add=True, verbose_name='Start')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='End')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course.course', verbose_name='Course')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz', verbose_name='Quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'permissions': (('view_sittings', 'Can see completed exams.'),),
            },
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ManyToManyField(blank=True, to='quiz.quiz', verbose_name='Quiz'),
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Score')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Progress',
                'verbose_name_plural': 'User progress records',
            },
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(help_text='Enter the choice text that you want displayed', max_length=1000, verbose_name='Content')),
                ('correct', models.BooleanField(default=False, help_text='Is this a correct answer?', verbose_name='Correct')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.mcquestion', verbose_name='Question')),
            ],
            options={
                'verbose_name': 'Choice',
                'verbose_name_plural': 'Choices',
            },
        ),
    ]
