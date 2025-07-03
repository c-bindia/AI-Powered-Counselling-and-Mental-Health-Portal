from collections import defaultdict
from datetime import date, datetime, time, timedelta
from django.utils.dateparse import parse_time
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
import random
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from counsellingapp.form import  CounselorForm, LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required
from counsellingapp.models import Appointment, CounselorAvailability, Feedback, User, VerifyEmailLinkCounter,Conversation, Message
from django.contrib.auth import authenticate, login as auth_login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from counsellingapp.services.ai_assistant import MentalHealthAIAssistant
from counsellingapp.serializers import MessageSerializer, ConversationSerializer 
import logging
from django.contrib.auth import logout as auth_logout

def home(request):
    return render(request, 'home.html')

def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = form.cleaned_data.get('is_admin', False)
            user.is_counselor = form.cleaned_data.get('is_counselor', False)
            user.is_student = form.cleaned_data.get('is_student', False)
            user.save()
            msg = 'User created successfully'
            return redirect('login')
        else:
            msg = 'Form is not valid: ' + str(form.errors)  # Include form errors in the message
    else:
        form = SignUpForm()
    
    return render(request, 'register.html', {'form': form, 'msg': msg})

def login(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')

            user = authenticate(email=email, password=password)  # Use email here

            if user is not None:
                if role == 'admin' and getattr(user, 'is_admin', False):
                    auth_login(request, user)
                    return redirect('dashboard1')

                elif role == 'counselor' and getattr(user, 'is_counselor', False):
                    auth_login(request, user)
                    return redirect('dashboard2')

                elif role == 'student' and getattr(user, 'is_student', False):
                    auth_login(request, user)
                    return redirect('home')
                else:
                    msg = 'You do not have permission to access this role.'
            else:
                msg = 'Invalid credentials.'
        else:
            print(form.errors)
            msg = 'Error validating form.'

    return render(request, 'login.html', {'form': form, 'msg': msg})


@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('login')  # Redirect to the login page after logout

@login_required(login_url='login')
def admin_home(request):
    total_counselors = User.objects.filter(is_counselor=True).count()
    total_students = User.objects.filter(is_student=True).count()
    total_appointments = Appointment.objects.count()

    context = {
        'total_counselors': total_counselors,
        'total_students': total_students,
        'total_appointments': total_appointments
    }
    return render(request, 'admin/dashboard1.html',context)

@login_required(login_url='login')
def counselor_home(request):
    total_students = User.objects.filter(is_student=True).count()
    
    # Count only the appointments assigned to the logged-in counselor
    total_appointments = Appointment.objects.filter(counselor=request.user).count()
    # Get feedback related to the logged-in counselor
    total_feedbacks = Feedback.objects.filter(counselor=request.user).count()

    context = {
        'total_students': total_students,
        'total_appointments': total_appointments,  # Specific to logged-in counselor
        'total_feedbacks': total_feedbacks  # Feedback count for logged-in counselor
    }
    return render(request, 'counsellor/dashboard2.html', context)


@login_required
def add_counsellor(request):
    form = CounselorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            counselor = form.save()
            
            # Default availability for the next 5 days starting today
            today = datetime.today().date()
            for i in range(5):  # Adjust to however many days you want
                date = today + timedelta(days=i)
                CounselorAvailability.objects.get_or_create(
                    counselor=counselor,
                    date=date,
                    defaults={'start_time': time(9, 0), 'end_time': time(17, 0)}  # 9 AM to 5 PM
                )

            messages.success(request, "Counselor and default availability created.")
            return redirect('clist')
        else:
            print(form.errors)  # Debugging: print form errors if invalid

    return render(request, 'admin/addcounsellor.html', {'form': form})

def delete_availability(request, availability_id):
    availability = get_object_or_404(availability, id=availability_id)
    availability.delete()
    messages.success(request, "Availability deleted successfully.")
    return redirect('view') 

@login_required
def delete_counselor(request, counselor_id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('clist')

    # Retrieve the counselor object
    counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)
    
    # Delete their availability first
    CounselorAvailability.objects.filter(counselor=counselor).delete()
    
    # Delete the counselor
    counselor.delete()

    messages.success(request, f"Counselor {counselor.username} has been deleted.")
    return redirect('clist')

@login_required
def delete(request, student_id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('slist')

    # Get the student object
    student = get_object_or_404(User, id=student_id, is_student=True)

    # Delete related VerifyEmailLinkCounter entries
    VerifyEmailLinkCounter.objects.filter(requester=student).delete()

    # Now delete the student
    student.delete()

    messages.success(request, f"Student {student.username} has been deleted.")
    return redirect('slist')


@login_required
def counsellor_list(request):
    counselors = User.objects.filter(is_counselor=True)  # Filter users with is_counselor=True
    return render(request, 'admin/clist.html', {'counselors': counselors})

@login_required
def student_list(request):
    student = User.objects.filter(is_student=True)  # Filter users with is_counselor=True
    return render(request, 'admin/slist.html', {'students': student})

def add_availability(request, counselor_id):
    if not request.user.is_admin:  # Use is_staff instead of is_admin
        return redirect('dashboard1')

    counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        print(f"Received data - Date: {date}, Start Time: {start_time}, End Time: {end_time}")  # Debugging

        if date and start_time and end_time:
            obj, created = CounselorAvailability.objects.update_or_create(
                counselor=counselor,
                date=date,
                defaults={'start_time': start_time, 'end_time': end_time}
            )
            print(f"Availability {'created' if created else 'updated'} for {counselor.username} on {date}")  # Debugging
        
        return redirect('view', counselor_id=counselor.id)

    return render(request, 'admin/availability.html', {'counselor': counselor})


@login_required
def edit_availability(request, counselor_id, availability_id):
    if not request.user.is_admin:  # Ensuring only admins can edit availability
        return redirect('dashboard1')

    counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)
    availability = get_object_or_404(CounselorAvailability, id=availability_id, counselor=counselor)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        print(f"Updating Availability - Date: {availability.date}, Start: {start_time}, End: {end_time}")  # Debugging

        if start_time and end_time:
            availability.start_time = start_time
            availability.end_time = end_time
            availability.save()
            print(f"Updated availability for {counselor.username} on {availability.date}")  # Debugging
        
        return redirect('view', counselor_id=counselor.id)

    return render(request, 'admin/edit.html', {
        'counselor': counselor,
        'availability': availability,
    })

@login_required
def view_availability(request, counselor_id):
    counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)
    availability_list = CounselorAvailability.objects.filter(counselor=counselor)  # Get all availability

    return render(request, 'admin/view.html', {
        'counselor': counselor,
        'availability_list': availability_list,  # Ensure it's passed as a list
    })


responses = {
    "hello": ["Hi there! How can I help you today?", "Hello! What’s on your mind?"],
    "how are you": ["I'm just a bot, but I'm here to help!", "I'm doing well, thanks for asking!"],
    "stress": ["I'm sorry to hear that. Do you want to talk about what’s causing your stress?"],
    "stress": [
            "Practice deep breathing exercises and progressive muscle relaxation.",
            "Develop a time management plan to reduce overwhelm.",
            "Identify and challenge negative thought patterns using cognitive behavioral techniques.",
            "Ensure you are getting enough sleep, regular exercise, and a healthy diet.",
            "Consider seeking support from friends, family, or support groups."
        ],
        "anxiety": [
            "Practice mindfulness and meditation to focus on the present moment.",
            "Learn and practice coping mechanisms for panic attacks.",
            "Gradually expose yourself to feared situations with the guidance of a professional.",
            "Explore the root causes of your anxiety with your counselor.",
            "Engage in relaxing activities like yoga, listening to music, or spending time in nature."
        ],
        "career": [
            "Explore career assessments to identify your strengths and interests.",
            "Research different career paths and their required qualifications.",
            "Network with professionals in your field of interest.",
            "Practice your resume writing and interview skills.",
            "Set realistic career goals and develop a plan to achieve them."
        ],
        "depression": [
            "Engage in regular physical activity, even if it's just a short walk.",
            "Maintain a consistent sleep schedule."
            "Challenge negative thinking patterns.",
            "Discuss treatment options, including therapy and medication, with a healthcare professional."
        ],
        "relationship": [
            "Practice active listening and empathy in your interactions.",
            "Communicate your needs and feelings clearly and respectfully.",
            "Learn conflict resolution skills to manage disagreements.",
            "Seek couples counseling to improve communication and intimacy.",
            "Set healthy boundaries in your relationships."
        ],
        "academic": [
            "Develop effective study habits and time management skills.",
            "Seek help from academic advisors or tutors.",
            "Manage test anxiety through relaxation techniques.",
            "Set realistic academic goals and track your progress.",
            "Identify your learning style and adapt your study methods accordingly."
        ],
     "default": ["I'm here to help. Can you tell me more?"]
        }

def get_response(user_input):
    user_input = user_input.lower()
    for key in responses.keys():
        if key in user_input:
            return random.choice(responses[key])
    return random.choice(responses["default"])
@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            response = get_response(user_message)
            return JsonResponse({"response": response})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    return JsonResponse({"message": "Welcome to the chatbot! Please send a POST request."})

def chatbot_page(request):
    return render(request, "chatbot.html")


@login_required
def booking(request):
    counselors = User.objects.filter(is_counselor=True)
    
    if request.method == 'POST':
        counselor_id = request.POST.get('counselor')
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        notes = request.POST.get('notes')

        counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)

        # ✅ Save appointment to the database (Fixed)
        appointment = Appointment.objects.create(
            user=request.user,  # Assuming `student` is the field for users who book
            counselor=counselor,
            date=selected_date,
            time=selected_time,
            notes=notes or "No notes provided",
            status="Pending"
        )

        # Save session data (optional)
        request.session['appointment_info'] = {
            'counselor': counselor.username,
            'date': selected_date,
            'time': selected_time,
            'notes': notes or "No notes provided"
        }

        messages.success(request, 'Appointment booked successfully!')
        return redirect('appointment_success')

    today = date.today().isoformat()
    return render(request, 'booking.html', {'counselors': counselors, 'today': today})


@login_required
def get_availability(request):
    counselor_id = request.GET.get('counselor_id')
    date_str = request.GET.get('date')
    counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)

    # Get counselor availability for the date
    availability = CounselorAvailability.objects.filter(counselor=counselor, date=date_str)
    booked_times = Appointment.objects.filter(counselor=counselor, date=date_str).values_list('time', flat=True)

    time_slots = []
    for slot in availability:
     current_time = slot.start_time
     while current_time < slot.end_time:
        if current_time.strftime('%H:%M') not in booked_times:
            time_slots.append(current_time.strftime('%H:%M'))
        # Ensure correct time incrementation
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=60)).time()
    
    return JsonResponse({'time_slots': time_slots or []})  # Ensure empty list is sent



@login_required
def appointment_success(request):
    appointment_info = request.session.get('appointment_info', None)
    if not appointment_info:
        messages.error(request, "No appointment found. Please book again.")
        return redirect('booking')

    return render(request, 'success.html', {'appointment_info': appointment_info})

@login_required
def view_appointments(request):
    if request.user.is_counselor:
        appointments = Appointment.objects.filter(counselor=request.user)
        user_role = 'counselor'
    else:
        appointments = Appointment.objects.filter(student=request.user)  # Corrected from `user=request.user`
        user_role = 'student'

    return render(request, 'counsellor/view_appointments.html', {
        'appointments': appointments,
        'user_role': user_role
    })

def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user.is_counselor:  # Ensure only counselors can approve
        appointment.status = 'Confirmed'
        appointment.save()
        messages.success(request, "Appointment approved successfully!")
    return redirect('view_appointments')

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user.is_counselor:  # Ensure only counselors can cancel
        appointment.status = 'Cancelled'
        appointment.save()
        messages.warning(request, "Appointment cancelled.")
    return redirect('view_appointments')

@login_required
def booking_history(request):
    if request.user.is_student:
        appointments = Appointment.objects.filter(user=request.user).order_by('-date', '-time')  
        print("DEBUG - Appointments Found:", appointments.count())  # Debugging
        return render(request, 'history.html', {'appointments': appointments})
    else:
        return redirect('home')  # or show a 403 page


@login_required
def submit_feedback(request):
    counselor_id = request.GET.get("counselor_id") or request.POST.get("counselor")  # Get from both GET & POST
    counselor = None

    if counselor_id:
        counselor = get_object_or_404(User, id=counselor_id, is_counselor=True)

    if request.method == "POST":
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback")

        if counselor and rating:
            Feedback.objects.create(
                student=request.user,
                counselor=counselor,
                rating=int(rating),
                message=feedback_text
            )
            return redirect("home")  # Redirect after submission

    counselors = User.objects.filter(is_counselor=True)
    return render(request, "feedback_form.html", {
        "counselors": counselors, 
        "selected_counselor": counselor
    })

@login_required
def view_feedback(request):
    feedbacks = Feedback.objects.filter(counselor=request.user)
    return render(request, "counsellor/view_feedback.html", {"feedbacks": feedbacks})

logger = logging.getLogger(__name__)


# counsellingapp/views.py
# ... other imports ...

class AIChatView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            conversation_id = request.session.get('conversation_id')

            if not message:
                return JsonResponse({'error': 'No message provided.'}, status=400)

            # Retrieve or create conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    # Create conversation, associating with user if logged in, otherwise null
                    conversation = Conversation.objects.create(user=request.user if request.user.is_authenticated else None)
                    request.session['conversation_id'] = str(conversation.id)
            else:
                # Create conversation, associating with user if logged in, otherwise null
                conversation = Conversation.objects.create(user=request.user if request.user.is_authenticated else None)
                request.session['conversation_id'] = str(conversation.id)

            # ... rest of your code ... # Store as string if UUI

            # Save user message to database
            # This line will now work because 'sender_type' field is defined
            Message.objects.create(conversation=conversation, sender_type='user', text=message)

            assistant = MentalHealthAIAssistant(conversation_id=conversation_id)
            ai_response_text = assistant.get_ai_response(message)

            # Save AI response to database
            Message.objects.create(conversation=conversation, sender_type='ai', text=ai_response_text)


            return JsonResponse({'response': ai_response_text})

        except Exception as e:
            logger.error(f"Error in AIChatView: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
        
class ConversationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        conversations = Conversation.objects.filter(user=request.user).order_by('-start_time')
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)