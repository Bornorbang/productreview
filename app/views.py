from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from app.models import Review, UserProfile, Category, Message, Room, Roommessage, Comment, PasswordReset, Newsletter
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, login as auth_login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from app.forms import RegisterForm, UserProfileForm, ReviewForm, MessageForm
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware, now
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now

def index(request):
    # Fetch all categories with their related reviews
    categories = Category.objects.prefetch_related('reviews').all()
    
    # Initialize user_profile to None for anonymous users
    user_profile = None  

    # Get UserProfile only if the user is authenticated
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)

    # Fetch the latest reviews and calculate hours since creation
    reviews = Review.objects.all().order_by('-created_at')
    for review in reviews:
        delta = now() - review.created_at
        review.hours_since = int(delta.total_seconds() // 3600)

    context = {
        'categories': categories,  # Pass categories to template
        'reviews': reviews,
        'user_profile': user_profile,
    }
    return render(request, 'index.html', context)


def submissions(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    for review in reviews:
        delta = now() - review.created_at
        review.hours_since = int(delta.total_seconds() // 3600)
    
    context = {
        'reviews': reviews
    }
    return render(request, 'submissions.html', context)


# @login_required(login_url='user_login')
# def submit_review(request):
#     categories = Category.objects.all()
#     rating_range = range(1, 6)

#     if request.method == 'POST':
#         product_name = request.POST.get("product_name")
#         category_id = request.POST.get("category")
#         brand = request.POST.get('brand')
#         title = request.POST.get('title')
#         seller = request.POST.get("seller")
#         picture = request.FILES.get('picture')
#         review_text = request.POST.get('review')
#         rating = int(request.POST.get('rating', 1))  # Convert to integer

#         category = get_object_or_404(Category, id=category_id)

#         Review.objects.create(
#             user=request.user,
#             product_name=product_name,
#             category=category,
#             brand=brand,
#             title=title,
#             seller=seller,
#             picture=picture,
#             review=review_text,
#             rating=rating
#         )

#         return redirect('home')

#     return render(request, 'review.html', {'categories': categories, 'rating_range': rating_range})

@login_required(login_url='user_login')
def submit_review(request):
    categories = Category.objects.all()
    services_category = get_object_or_404(Category, name="Services")

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.save(commit=False)  # Delay saving to set user and IP
            data.user = request.user  # Set the logged-in user
            data.ip = request.META.get("REMOTE_ADDR")  # Capture IP address
            data.save()  # Save the review after setting all necessary fields
            messages.success(request, "Thank you! Your review has been created.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'review.html', {'categories': categories, 'services_category_id': services_category.id, 'form': ReviewForm()})


def category_reviews(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    reviews = Review.objects.filter(category=category).order_by('-created_at')

    for review in reviews:
        delta = now() - review.created_at
        review.hours_since = int(delta.total_seconds() // 3600)
        
        # Access comments directly using the related manager
        review.comments_list = review.comments.all().order_by('-created_at')
    
    context = {
        'category': category,
        'reviews': reviews,
    }
    
    return render(request, 'category_reviews.html', context)


def load_comments(request, review_id):
    review = Review.objects.get(id=review_id)
    comments = review.comment.objects.all()

    context = {
        'review': review,
        'comments': comments,
    }

    # return JsonResponse({'comments': list(comments)})
    return render(request, 'category_detail', context)

@login_required(login_url='user_login')
def post_comment(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        
        # Only proceed if the user is authenticated
        if request.user.is_authenticated:
            comment = Comment.objects.create(
                created_at=timezone.now(),
                user=request.user,  # This will now be a User instance
                content=request.POST['content'],
                review = review,
            )
            comment.save()

            return redirect('category_detail', review.category.id)
        
        else:
            return redirect('user_login')

def search_reviews(request):
    query = request.GET.get('query', '')  # Get the search term from the request
    results = []

    if query:
        # Filter reviews by product_name, category name, or seller
        results = Review.objects.filter(
            product_name__icontains=query
        ) | Review.objects.filter(
            category__name__icontains=query
        ) | Review.objects.filter(
            seller__icontains=query
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_results.html', context)

# def submissions(request):
#     reviews = Review.objects.all().order_by('-created_at')
    
#     context = {
#         'reviews': reviews
#     }
    
#     return render(request, 'submissions.html', context)

def aboutus(request):
    context = {
    }

    return render(request, "about.html", context)

def contactus(request):
    if request.method == 'POST':
        contact_name = request.POST['contact_name']
        contact_phone = request.POST['contact_phone']
        contact_email = request.POST['contact_email']
        contact_subject = request.POST['contact_subject']
        contact_message = request.POST['contact_message']
        admin_email = "info@productreview.com.ng"

        context = {
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_subject": contact_subject,
            "contact_message": contact_message,
            "contact_phone": contact_phone,
            "admin_email": admin_email,
        }

        html_content = render_to_string('email/contactus.html', context)

        try:
            send_mail(
                subject=f"{contact_subject} from {contact_name}",
                message=None,
                html_message = html_content,
                from_email = contact_email,
                recipient_list = [settings.EMAIL_HOST_USER],
                fail_silently = False,
            )

            messages.success(request, "Message was sent successfully")
            return render(request, "contact.html")
            
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return render(request, "contact.html")

    return render(request, "contact.html")

def signup(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        subject = "Welcome to ProductReview.com.ng"
        admin_email = "info@productreview.com.ng"

        user_data_has_error = False

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists.")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "An account already exists with this email address.")

        # Check password length
        if len(password) < 6:
            user_data_has_error = True
            messages.error(request, "Password must be longer than 6 characters and contain symbols.")

        # Redirect to signup page if there are errors
        if user_data_has_error:
            return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})

        # Send welcome email
        context = {
            "username": username,
            "subject": subject,
            "email": email,
            "admin_email": admin_email,
        }
        html_content = render_to_string('email/signup.html', context)

        send_mail(
            subject=subject,
            message=None,
            html_message=html_content,
            from_email=admin_email,
            recipient_list=[email],
            fail_silently=False,
        )

        # Save user and profile if forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "Registration successful!")
            return redirect('user_login')

    else:
        user_form = RegisterForm()
        profile_form = UserProfileForm()

    return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        subject = "Reset Your Password"

        try:
            user = User.objects.get(email=email)

            new_password = PasswordReset(user=user)
            new_password.save()

            password_reset_url = reverse('reset_password', kwargs={'reset_id': new_password.reset_id})

            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

            context = {
            "email": email,
            "subject": subject,
            "full_password_reset_url": full_password_reset_url,
            }
            html_content = render_to_string('email/forgot_password.html', context)

            send_mail(
                subject=subject,
                message=None,
                html_message=html_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect("password_reset_sent", reset_id=new_password.reset_id)

        
        except User.DoesNotExist:
            messages.error(request, f"Email address is not registered on this website.")
            return redirect('forgot_password')


    return render(request, "forgot_password.html")

def password_reset_sent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, "password_reset_sent.html")
    
    else:
        messages.error(request, "Reset Link is invalid")
        return redirect('forgot_password')

def reset_password(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            reset_password = request.POST.get("reset_password")
            confirm_reset_password = request.POST.get("confirm_reset_password")

            password_have_error = False

            if reset_password != confirm_reset_password:
                password_have_error = True
                messages.error(request, "Password do not match")
            
            if len(reset_password) < 6:
                password_have_error = True
                messages.error(request,  "Password must be longer than 6 characters and contain symbols.")

            expiration_time = password_reset_id.created_at + timezone.timedelta(minutes=30)

            if timezone.now() > expiration_time:
                password_have_error =  True
                password_reset_id.delete()
                messages.error(request, "Reset Link has expired.")

            if not password_have_error:
                user = password_reset_id.user
                user.set_password(reset_password)
                user.save()

                password_reset_id.delete()

                messages.success(request, "Password reset. Proceed to login")
                return redirect('user_login')

            else:
                return redirect("reset_password", reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid Reset Link")
        return redirect('forgot_password')


    return render(request, "reset_password.html")

def terms(request):

    context = {
    }

    return render(request, "terms.html", context)

def privacypolicy(request):

    context = {
    }

    return render(request, "privacypolicy.html", context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, "login.html", {'username': username})

    return render(request, "login.html")

def user_logout(request):
    logout(request)  # Log out the user
    messages.success(request, "You have been logged out successfully.")
    return redirect('user_login') 

# def signup(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST, request.FILES)

#         if form.is_valid():
#             try:
#                 user = form.save()  # Save the user and create a new User instance
#                 messages.success(request, "Registration successful! You can now log in.")
#                 return redirect('user_login')  # Redirect to the login page or any other page
#             except Exception as e:
#                 # Handle the exception
#                 messages.error(request, f"An error occurred during registration: {str(e)}")
#         else:
#             # If the form is not valid, render errors
#             messages.error(request, "Please correct the errors below.")

#     else:
#         form = RegisterForm()

#     return render(request, "signup.html", {"form": form})




@login_required(login_url='user_login')
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required(login_url='user_login')
def edit_profile(request, field):
    # Get the UserProfile instance associated with the logged-in user
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        value = request.POST.get(field)

        if field == 'username':
            request.user.username = value
        elif field == 'email':
            request.user.email = value
        elif field == 'phone':
            profile.phone = value
        elif field == 'state':
            profile.state = value
        elif field == 'profile_picture' and 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        # Save changes
        request.user.save()
        profile.save()

        return redirect('profile')  # Redirect to profile page after saving changes

    return render(request, 'edit_profile_field.html', {'field': field, 'profile': profile})


@login_required(login_url='user_login')
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).select_related('sender')
    return render(request, 'messaging/inbox.html', {'messages': messages})

@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    # Query for messages between the two users
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.receiver = other_user
            new_message.save()
            return redirect('conversation', username=other_user.username)
    else:
        form = MessageForm()

    return render(request, 'messaging/conversation.html', {
        'messages': messages, 'form': form, 'other_user': other_user
    })

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    other_user = get_object_or_404(User, username=username)
    
    # If a message is sent via POST, create a new message object
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=user,
                content=content
            )
            return redirect('user_profile', username=username)  # Stay on the profile page after sending

    # Fetch existing conversation between the logged-in user and the profile owner
    conversation = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    context = {
        'profile': profile,
        'conversation': conversation,
    }
    return render(request, 'user_profile.html', context)

def send_message(request, username):
    if request.method == 'POST':
        receiver = get_object_or_404(User, username=username)
        Message.objects.create(sender=request.user, receiver=receiver, content='Hi!')
        return redirect('inbox')
    
@login_required(login_url='user_login')
def joinroom(request):
    username = request.user.username
    rooms = Room.objects.all().annotate(name_lower=Lower('name')).order_by('name_lower')

    context = {
        "username": username,
        "rooms": rooms,
    }

    return render(request, 'room/join.html', context)

@login_required(login_url='user_login')
def room(request, room):
    username = request.user.username
    room_details = Room.objects.get(name=room)

    context = {
        "username": username,
        "room_details": room_details,
        "room": room
    }

    return render(request, 'room/room.html', context)

@login_required(login_url='user_login')
def checkroom(request):
    room = request.POST['room_name']
    username = request.POST['your_username']

    if Room.objects.filter(name=room).exists():
        return redirect('/join/' +room+ '/?username=' +username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/join/' +room+ '/?username=' +username)
    
@login_required(login_url='user_login')
def send(request):
        send_message = request.POST['send_message']
        room_name = request.POST['room']
        username = request.POST['username']

        # Fetch the user and room objects
        user = User.objects.get(username=username)
        room = Room.objects.get(name=room_name)

        # Create and save the message
        new_message = Roommessage.objects.create(value=send_message, user=user, room=room)
        new_message.save()

        return HttpResponse('Message sent successfully')


@login_required(login_url='user_login')
def getmessages(request, room):
    room_details = Room.objects.get(name=room)
    messages = Roommessage.objects.filter(room=room_details.id)

    # Create a list of messages with username instead of user ID
    messages_list = []
    for message in messages:
        messages_list.append({
            'user': message.user.username,  # Fetch the username
            'value': message.value,
            'date': message.date.strftime('%Y-%m-%d %H:%M'),  # Format the date as needed
        })

    return JsonResponse({'messages': messages_list})

def room_list(request):
    rooms = Room.objects.all().annotate(name_lower=Lower('name')).order_by('name_lower')
    return render(request, 'room/room_list.html', {'rooms': rooms})

def newsletter(request):
    if request.method == "POST":
        email_news =  request.POST.get("email_news")

        if email_news:
            if not Newsletter.objects.filter(email=email_news).exists():
                Newsletter.objects.create(email=email_news)
                messages.success(request, "You've successfully subscribed to our newsletter!")

            else:
                messages.info(request, "You're already subscribed.")
            return redirect('home')
    return redirect('home')




        