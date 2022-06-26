from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    is_instructor = models.BooleanField(default=True)


class InstructorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='instructor_profile')
    about = models.TextField(blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='student_profile')
    level = models.PositiveIntegerField(
        blank=True, null=True)
    quizzes = models.ManyToManyField('Quiz', through='TakenQuiz')
    score = models.IntegerField(default=0)  # User reputation score.

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(
            pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return f"Profile for {self.user.username}"


class Course(models.Model):
    instructor = models.ForeignKey(
        InstructorProfile, related_name='courses_created',
        on_delete=models.CASCADE,
        help_text='The instructor who created this course')
    title = models.CharField(
        'Course title',
        max_length=50)
    code = models.PositiveIntegerField(
        'Course code')
    slug = models.SlugField(
        max_length=50, unique=True,
        help_text='A human readable URL')
    overview = models.TextField('Course overview')
    students = models.ManyToManyField(StudentProfile,
                                      related_name='courses_enrolled',
                                      blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Module(models.Model):
    course = models.ForeignKey(
        Course, related_name='modules',
        on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'{self.title}'


# class Content(models.Model):
#     module = models.ForeignKey(Module,
#                                related_name='contents',
#                                on_delete=models.CASCADE)
#     text = models.TextField()
#     video = models.URLField(blank=True)
#     image = models.ImageField(blank=True)
#     file = models.FileField(blank=True)
#     order = OrderField(blank=True, for_fields=['module'])

#     class Meta:
#         ordering = ['order']


class Announcement(models.Model):
    title = models.CharField(max_length=100)
    detail = models.TextField()
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='announcements')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    detail = models.TextField()
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments')
    # due_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']


class Quiz(models.Model):
    instructor = models.ForeignKey(
        InstructorProfile, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='quizzes')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class StudentAnswer(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='+')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']


class TakenQuiz(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.IntegerField()
    percentage = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
