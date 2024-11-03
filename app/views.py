from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from app.models import Review, UserProfile, Category, Message, Room, Roommessage, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, login as auth_login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from app.forms import RegisterForm, UserProfileForm, ReviewForm, MessageForm
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware, now
from django.db.models import Q
from django.db.models.functions import Lower

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
        contact_email = request.POST['contact_email']
        contact_subject = request.POST['contact_subject']
        contact_message = request.POST['contact_message']

        context = {
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_subject": contact_subject,
            "contact_message": contact_message
        }

        html_content = render_to_string('email.html', context)

        try:
            send_mail(
                subject=contact_subject,
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
        subject = "Welcome to ProductReview.com.ng"
        admin_email = "info@productreview.com.ng"

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
                html_message = html_content,
                from_email = admin_email,
                recipient_list = [email],
                fail_silently = False,
            )

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


        