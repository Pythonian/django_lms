from django import forms
from django.forms.utils import ValidationError

from .models import (
    Course, Announcement, Assignment, Question, Answer, Module,
    StudentAnswer, User, InstructorProfile, StudentProfile)
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction


class InstructorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user


class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_instructor = False
        user.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ['about']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['level']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'overview']


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'detail']


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'detail']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError(
                'Mark at least one answer as correct.',
                code='no_correct_answer')


class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)
