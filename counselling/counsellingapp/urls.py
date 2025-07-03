from django.urls import path
from . import views

urlpatterns = [
   
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('', views.home, name='home'),
    path('dashboard1/', views.admin_home, name='dashboard1'),
    path('dashboard2/', views.counselor_home, name='dashboard2'),
    path('booking/', views.booking, name='booking'),
    path('history/',views.booking_history, name='history'),

    path('get-availability/', views.get_availability, name='get_availability'),
    path('success/', views.appointment_success, name='appointment_success'),
    path("chat/", views.chatbot_response, name="chatbot_response"),
    path("chatbot/", views.chatbot_page, name="chatbot_page"), 
    path('addcounsellor/', views.add_counsellor, name='addcounsellor'),
    path('delete/<int:counselor_id>/', views.delete_counselor, name='delete_counselor'),
    path('del/<int:student_id>/', views.delete, name='delete'),
    path('delete_availability/<int:availability_id>/', views.delete_availability, name='delete_availability'),
    path('clist/', views.counsellor_list, name='clist'),
    path('slist/', views.student_list, name='slist'),

    path('availability/<int:counselor_id>', views. add_availability, name='availability'),
    path('counselor/<int:counselor_id>/availability/<int:availability_id>/edit/', views.edit_availability, name='edit_availability'),
    path('view/<int:counselor_id>', views.view_availability, name='view'),
    path('appointments/view/', views.view_appointments, name='view_appointments'),
     path('approve-appointment/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
     path("submit-feedback/", views.submit_feedback, name="submit_feedback"),
    path("view-feedback/",views.view_feedback, name="view_feedback"),

    path('api/chat/', views.AIChatView.as_view(), name='ai_chat'),
    path('api/conversations/', views.ConversationHistoryView.as_view(), name='conversation_history'),
]