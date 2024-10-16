from django.contrib import admin
from app.models import GeneralInfo, UserProfile, Category, Review

# Register your models here.

@admin.register(GeneralInfo)
class GeneralInfoAdmin (admin.ModelAdmin):
    list_display = [
        "company_name",
        "company_email",
        "phone"
    ]

# @admin.register(Profile)
# class ProfileAdmin (admin.ModelAdmin):
#    list_display = ('user', 'phone', 'user_state', 'email')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'state']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'title',
        'category',
        'rating',
        'seller',
        
    ]