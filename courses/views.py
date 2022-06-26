from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import (TakenQuiz,
    Course, Announcement, Assignment, Answer, Question, Quiz, User)
from .forms import CourseForm, AnnouncementForm, AssignmentForm, ModuleForm

from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  UpdateView, ListView, View, FormView)
from .decorators import instructor_required, student_required
from .forms import (
    BaseAnswerInlineFormSet, QuestionForm,
    StudentSignUpForm, InstructorSignUpForm, StudentProfileForm,
    UserForm, InstructorProfileForm, CourseEnrollForm)


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'an instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('instructor_dashboard')


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'a student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('student_dashboard')


@login_required
def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html')


@login_required
def instructor_update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = InstructorProfileForm(
            request.POST, instance=request.user.instructor_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successully updated.')
            return redirect('instructor_dashboard')
        else:
            messages.error(
                request, 'Error updating your profile. Please check below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = InstructorProfileForm(
            instance=request.user.instructor_profile)

    return render(request,
                  'instructor_profile_form.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


@login_required
def instructor_course(request):
    course = Course.objects.filter(
        instructor=request.user.instructor_profile).first()
    return render(request,
                  'instructor_course.html',
                  {'course': course})


# @login_required
# def instructor_course_create(request):
#     if request.method == 'POST':
#         form = CourseForm(request.POST)
#         if form.is_valid():
#             course = form.save(commit=False)
#             course.instructor = request.user.instructor_profile
#             course.save()
#             messages.success(
#                 request, "Your course has been successully created.")
#             return redirect('instructor_course')
#     else:
#         form = CourseForm()

#     return render(request, 'instructor_course_form.html', {'form': form})


@method_decorator([login_required, instructor_required], name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'code', 'overview']
    template_name = 'instructor_course_form.html'

    def form_valid(self, form):
        course = form.save(commit=False)
        course.instructor = self.request.user.instructor_profile
        course.save()
        messages.success(
            self.request,
            'The course was created! Go ahead and add course modules now.')
        return redirect('course_change', course.pk)


@method_decorator([login_required, instructor_required], name='dispatch')
class CourseUpdateView(UpdateView):
    model = Course
    fields = ['title', 'code', 'overview']
    context_object_name = 'course'
    template_name = 'course_change_form.html'

    # def get_context_data(self, **kwargs):
    #     kwargs['questions'] = self.get_object().questions.annotate(
    #         answers_count=Count('answers'))
    #     return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the id of existing course that belongs
        to the logged in user.
        '''
        return self.request.user.instructor_profile.courses_created.all()

    def get_success_url(self):
        return reverse('course_change', kwargs={'pk': self.object.pk})


@login_required
@instructor_required
def module_add(request, pk):
    # By filtering the course by the url keyword argument `pk` and
    # by the instructor, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the instructor of
    # course will be able to add modules to it.
    course = get_object_or_404(
        Course, pk=pk, instructor=request.user.instructor_profile)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(
                request, 'You have successfully added a module.')
            return redirect('course_change', course.pk)
    else:
        form = ModuleForm()

    return render(
        request, 'module_add_form.html', {'course': course, 'form': form})

# @login_required
# def instructor_course_module(request, course_pk, module_pk):
#     course = get_object_or_404(
#         Course, pk=course_pk, instructor=request.user.instructor_profile)
#     module = get_object_or_404(Module, pk=course_pk, course=course)

#     return render(
#         request, 'instructor_course_module_form.html',
#         {'form': form})


@login_required
def instructor_course_update(request, pk):
    course = get_object_or_404(
        Course, id=pk, instructor=request.user.instructor_profile)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your course has been successully updated.")
            return redirect('instructor_course')
    else:
        form = CourseForm(instance=course)

    return render(
        request, 'instructor_course_form.html',
        {'form': form, 'course': course, 'edit': True})


# @method_decorator([login_required, instructor_required], name='dispatch')
# class DeleteCourse(DeleteView):
#     model = Course
#     success_url = reverse_lazy('instructor_course')


@login_required
def instructor_announcements(request):
    announcements = Announcement.objects.filter(
        instructor=request.user.instructor_profile)
    return render(
        request, 'instructor_announcements.html',
        {'announcements': announcements})


@login_required
def create_announcement(request):
    instructor = request.user.instructor_profile
    course = None
    try:
        course = Course.objects.get(instructor=instructor)
    except Course.DoesNotExist:
        messages.warning(request, "Create a course before adding announcement.")
        return redirect('instructor_course_create')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.instructor = instructor
            announcement.course = course
            announcement.save()
            messages.success(request, "Announcement successully created.")
            return redirect('instructor_announcements')
    else:
        form = AnnouncementForm()

    return render(
        request, 'announcement_form.html',
        {'form': form, 'course': course})


@login_required
def instructor_assignments(request):
    assignments = Assignment.objects.filter(
        instructor=request.user.instructor_profile)
    return render(
        request, 'instructor_assignments.html',
        {'assignments': assignments})


@login_required
def create_assignment(request):
    instructor = request.user.instructor_profile
    course = None
    try:
        course = Course.objects.get(instructor=instructor)
    except Course.DoesNotExist:
        messages.warning(request, "Create a course before adding assignment.")
        return redirect('instructor_course_create')
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.instructor = instructor
            assignment.course = course
            assignment.save()
            messages.success(request, "Assignment successully created.")
            return redirect('instructor_assignments')
    else:
        form = AssignmentForm()

    return render(request, 'assignment_form.html', {'form': form})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        Assignment, id=pk)

    return render(
        request, 'assignment_detail.html', {'assignment': assignment})


@login_required
def instructor_quizzes(request):
    quizzes = Quiz.objects.filter(
        instructor=request.user.instructor_profile).select_related(
        'course').annotate(questions_count=Count('questions', distinct=True))
                 # .annotate(taken_count=Count('taken_quizzes', distinct=True))
    return render(
        request, 'instructor_quizzes.html', {'quizzes': quizzes})


# @method_decorator([login_required, instructor_required], name='dispatch')
# class QuizListView(ListView):
#     model = Quiz
#     ordering = ('name', )
#     context_object_name = 'quizzes'
#     template_name = 'instructor_quizzes.html'

#     def get_queryset(self):
#         queryset = self.request.user.instructor_profile.quizzes \
#             .select_related('course') \
#             .annotate(questions_count=Count('questions', distinct=True)) \
#             .annotate(taken_count=Count('taken_quizzes', distinct=True))
#         return queryset


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ['name']
    template_name = 'instructor_create_quiz.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.instructor = self.request.user.instructor_profile
        quiz.course = Course.objects.get(
            instructor=self.request.user.instructor_profile)
        quiz.save()
        messages.success(
            self.request,
            'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('quiz_change', quiz.pk)


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ['name']
    context_object_name = 'quiz'
    template_name = 'quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(
            answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.instructor_profile.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(
            request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related(
            'student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@login_required
@instructor_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the instructor, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the instructor of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(
        Quiz, pk=pk, instructor=request.user.instructor_profile)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(
                request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(
        request, 'question_add_form.html', {'quiz': quiz, 'form': form})


@login_required
@instructor_required
def question_change(request, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the instructor of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(
        Quiz, pk=quiz_pk, instructor=request.user.instructor_profile)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(
                request, 'Question and answers saved with success!')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, instructor_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(
            request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(
            quiz__instructor=self.request.user.instructor_profile)

    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})


@login_required
def student_dashboard(request):
    return render(
        request, 'student_dashboard.html')


@login_required
def student_update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(
            request.POST, instance=request.user.student_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successully updated.')
            return redirect('student_dashboard')
        else:
            messages.error(
                request, 'Error updating your profile. Please check below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = StudentProfileForm(
            instance=request.user.student_profile)

    return render(request,
                  'student_profile_form.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


@login_required
def student_courses(request):
    courses = Course.objects.filter(
        students__in=[request.user.student_profile])
    all_courses = Course.objects.all()

    return render(request, 'student_courses.html',
                  {'courses': courses,
                   'all_courses': all_courses})


# def enroll_course(request, pk):

#     form = CourseEnrollForm()

@method_decorator([login_required, student_required], name='dispatch')
class StudentEnrollCourseView(FormView):
    course = None
    form_class = CourseEnrollForm
    template_name = 'student_courses.html'

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user.student_profile)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'student_course_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user.student_profile])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                                    id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context


# class StudentCourseListView(LoginRequiredMixin, ListView):
#     model = Course
#     template_name = 'students/course/list.html'

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(students__in=[self.request.user])


# class StudentCourseDetailView(DetailView):
#     model = Course
#     template_name = 'students/course/detail.html'

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(students__in=[self.request.user])

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # get course object
#         course = self.get_object()
#         if 'module_id' in self.kwargs:
#             # get current module
#             context['module'] = course.modules.get(
#                                     id=self.kwargs['module_id'])
#         else:
#             # get first module
#             context['module'] = course.modules.all()[0]
#         return context


@method_decorator([login_required, student_required], name='dispatch')
class StudentQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'student_quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class QuizResultsView(View):
    template_name = 'classroom/students/quiz_result.html'

    def get(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(id=kwargs['pk'])
        taken_quiz = TakenQuiz.objects.filter(
            student=request.user.student, quiz=quiz)
        if not taken_quiz:
            """
            Don't show the result if the user didn't attempted the quiz
            """
            return render(request, '404.html')
        questions = Question.objects.filter(quiz=quiz)

        # questions = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'questions': questions,
                                                    'quiz': quiz, 'percentage': taken_quiz[0].percentage})


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'classroom/students/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset


@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('students:take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(
                        answer__question__quiz=quiz, answer__is_correct=True).count()
                    percentage = round(
                        (correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(
                        student=student, quiz=quiz, score=correct_answers, percentage=percentage)
                    student.score = TakenQuiz.objects.filter(
                        student=student).aggregate(Sum('score'))['score__sum']
                    student.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (
                            quiz.name, percentage))
                    else:
                        messages.success(
                            request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, percentage))
                    return redirect('students:quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'classroom/students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })
