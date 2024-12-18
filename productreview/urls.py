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
from app.views import (index, aboutus, contactus, terms, privacypolicy, user_login, load_comments, signup, send, getmessages, profile, 
                       edit_profile, room, room_list, checkroom, submit_review, user_logout, submissions, category_reviews, search_reviews, 
                       inbox, conversation, joinroom, user_profile, send_message, post_comment, password_reset_sent, reset_password, forgot_password,
                       newsletter)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
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
    path('search/', search_reviews, name='search'),
    path('inbox/', inbox, name='inbox'),
    path('conversation/<str:username>/', conversation, name='conversation'),
    path('profile/<str:username>/', user_profile, name='user_profile'),
    path('send_message/<str:username>/', send_message, name='send_message'),
    path('join-room/', joinroom, name="joinroom"),
    path('join/<str:room>/', room, name='room'),
    path('checkroom', checkroom, name='checkroom'),
    path('send/', send, name="send"),
    path('getmessages/<str:room>/', getmessages, name='getmessages'),
    path('rooms/', room_list, name="room_list"),
    path('reviews/<int:review_id>/comments/', load_comments, name='load_comments'),
    path('reviews/<int:review_id>/comment/', post_comment, name='post_comment'),
    path("forgot_password", forgot_password, name="forgot_password"), 
    path("reset_password/<str:reset_id>", reset_password, name="reset_password"),
    path("password_reset_sent/<str:reset_id>", password_reset_sent, name="password_reset_sent"),
    path("subscription/", newsletter, name="newsletter")

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
