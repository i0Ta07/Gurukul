from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# All the URLs of different views of Users app should be stored here
# ULS as showed in 127.0.0.1:8000/URL

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/',views.loginPage, name='login'),
    path('logout/',views.logoutUser, name='logout'),
    path('',views.home,name= "home"),


    path('user_home/',views.user_home, name= "user_home"),
    path('profile/',views.profile, name= "profile"),
    path('profile/<str:username>/', views.profile, name='profile_with_username'),  # Profile with username

    path('friends/',views.user_friends_list, name= "user_friends_list"),

    path('announcement_list/',views.announcement_list, name= "announcement_list"),
    path('announcements/<str:class_id>/',views.announcement_class_list,name= "announcement_class_list"),


    path('class_list/',views.class_list, name= "class_list"),
    path('class/<str:class_id>/home',views.class_home, name= "class_home"),
    path('leave_class/<str:class_id>/',views.leave_class, name= "leave_class"),


    path('class_join/',views.class_join, name= "class_join"),
    path('add_friend/',views.add_friend, name= "add_friend"),
    path('search_resources/',views.search_resources, name= "search_resources"),
    path('search_quiz/',views.search_quiz, name= "search_quiz"),


    
    path('notes/<str:class_id>/',views.notes_class_list, name= "notes_class_list"),
    path('notes_created_list/',views.notes_created_list, name= "notes_created_list"),
    path('notes_saved_list/',views.notes_saved_list, name= "notes_saved_list"),

       
    path('books_created_list/',views.books_created_list, name= "books_created_list"),
    path('books_saved_list/',views.books_saved_list, name= "books_saved_list"),
   

    path('quiz_class_list/<str:class_id>/',views.quiz_class_list, name= "quiz_class_list"),
    
    path('quiz_created/',views.quiz_created,name= "quiz_created"),
    path('quiz_saved/', views.quiz_saved,name = "quiz_saved"),
    path('quiz/all_classes',views.quiz_user_all_classes,name= "quiz_user_all_classes"),
    path('quiz_assigned/',views.quiz_assigned,name= "quiz_assigned"),


    path('quiz_guidelines/<str:quiz_id>/',views.quiz_guidelines,name= "quiz_guidelines"),
    path('quiz_result/<str:quiz_id>/',views.quiz_result,name= "quiz_result"),
    path('quiz/review/<str:attempt_id>/',views.quiz_review,name= "quiz_review"),
    path('start_quiz/<str:quiz_id>/',views.start_quiz,name= "start_quiz"),
    path('confirm_quiz/',views.confirm_quiz,name="confirm_quiz"),

    path('quiz_submission/<str:attempt_id>/',views.quiz_submission,name= "quiz_submission"),
    path("fetch-quiz-data/<str:quiz_id>/", views.fetch_quiz_data, name="fetch_quiz_data"),
    path("check_results/", views.check_results, name="check_results"),
    path("grade_attempt/<str:attempt_id>", views.grade_attempt, name="grade_attempt"),
    path("attempts/<str:quiz_id>", views.quiz_attempts, name="quiz_attempts"),
    
    
    path('assignment/submit/<str:assignment_id>/',views.assignment_student, name= "assignment_student"),    
    path('assignment/responses/<str:assignment_id>/',views.assignment_teacher, name= "assignment_teacher"),  
    path('assignment/class/<str:class_id>/',views.assignment_user_list, name= "assignment_user_list"), 


    #FORMS

    path('create_announcement/', views.create_announcement, name='create_announcement'),  
    path('create_announcement/<str:class_id>/', views.create_announcement, name='create_class_announcement'),  

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)