"""
URL configuration for productreview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import index, aboutus, contactus, terms, privacypolicy, user_login, signup, profile, edit_profile, submit_review, user_logout, submissions, category_reviews, search_reviews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", index, name="home"),
    path("about-us/", aboutus, name="aboutus"),
    path("contact-us/", contactus, name="contactus"),
    path("terms-of-service/", terms, name="terms"),
    path("privacy-policy/", privacypolicy, name="privacypolicy"),
    path("login/", user_login, name="user_login"),
    path("logout/", user_logout, name="user_logout"),
    path("signup/", signup, name="signup"),
    path("profile/", profile, name="profile"),
    path("edit-profile/<str:field>/", edit_profile, name="edit_profile"),
    path("review/", submit_review, name="review"),
    path("submissions/", submissions, name="submissions"),
    path('category/<int:category_id>/', category_reviews, name='category_detail'),
     path('search/', search_reviews, name='search')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
