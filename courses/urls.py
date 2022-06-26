from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (instructor_dashboard, instructor_course, StudentEnrollCourseView,
                    instructor_quizzes, CourseCreateView, CourseUpdateView,
                    instructor_update_profile, instructor_announcements,
                    create_announcement, create_assignment, module_add,
                    instructor_assignments, instructor_course_update,
                    QuizCreateView, QuizUpdateView, student_dashboard,
                    QuizDeleteView, QuizResultsView, question_add, student_update_profile,
                    question_change, QuestionDeleteView, assignment_detail,
                    StudentSignUpView, InstructorSignUpView, student_courses)

# app_label = 'courses'

urlpatterns = [
    path('login/',
         auth_views.LoginView.as_view(
             redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/student/',
         StudentSignUpView.as_view(), name='student_signup'),
    path('signup/instructor/',
         InstructorSignUpView.as_view(), name='instructor_signup'),

    path('instructor/dashboard/',
         instructor_dashboard,
         name='instructor_dashboard'),
    path('student/dashboard/',
         student_dashboard,
         name='student_dashboard'),
    path('student/update-profile/',
         student_update_profile,
         name='student_update_profile'),
    path('student/enroll-course/',
         StudentEnrollCourseView.as_view(),
         name='student_enroll_course'),

    path('instructor/course/',
         instructor_course,
         name='instructor_course'),
    path('student/courses/',
         student_courses,
         name='student_courses'),

    path('instructor/create-course/',
         CourseCreateView.as_view(),
         name='instructor_course_create'),
    path('instructor/course/<int:pk>/',
         CourseUpdateView.as_view(),
         name='course_change'),
    path('instructor/course/<int:pk>/update/',
         instructor_course_update,
         name='instructor_course_update'),
    path('instructor/course/<int:pk>/module/add/',
          module_add,
          name='module_add'),
#     path('instructor/course/<pk>/delete/',
#          DeleteCourse.as_view(),
#          name='instructor_course_delete'),
    path('instructor/update-profile/',
         instructor_update_profile,
         name='instructor_update_profile'),
    path('instructor/announcements/',
         instructor_announcements,
         name='instructor_announcements'),
    path('instructor/announcement/create/',
         create_announcement,
         name='create_announcement'),
    path('instructor/assignments/',
         instructor_assignments,
         name='instructor_assignments'),
    path('instructor/assignment/create/',
         create_assignment,
         name='create_assignment'),
    path('instructor/assignment/<int:pk>/',
         assignment_detail,
         name='assignment_detail'),
    # path('instructor/quizzes/',
    #      QuizListView.as_view(),
    #      name='quiz_change_list'),
    path('instructor/quizzes/',
         instructor_quizzes,
         name='instructor_quizzes'),
    path('instructor/quiz/add/',
         QuizCreateView.as_view(),
         name='quiz_add'),
    path('instructor/quiz/<int:pk>/',
         QuizUpdateView.as_view(),
         name='quiz_change'),
    path('instructor/quiz/<int:pk>/delete/',
         QuizDeleteView.as_view(),
         name='quiz_delete'),
    path('instructor/quiz/<int:pk>/results/',
         QuizResultsView.as_view(),
         name='quiz_results'),
    path('instructor/quiz/<int:pk>/question/add/',
         question_add,
         name='question_add'),
    path('instructor/quiz/<int:quiz_pk>/question/<int:question_pk>/',
         question_change, name='question_change'),
    path('instructor/quiz/<int:quiz_pk>/question/<int:question_pk>/delete/',
         QuestionDeleteView.as_view(), name='question_delete'),
]
