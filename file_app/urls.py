from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Login API for both ops and client user
    path('login-user/', views.login_user, name='login'),

    # Upload file API 
    path('upload-file/', views.upload_file, name='upload-file'),

    # Sign-up and verify email for client user
    path('sign-up/', views.sign_up, name='sign-up'),
    path('verify-email/<str:id>/<str:token>',views.verify_email, name='verify-email'),

    # # Listing of all files
    path('files-list/', views.FilesListing.as_view()),


    # For downloading files
    path('get-download-url/<int:file_id>/', views.get_download_url, name='get_download_url'),
    path('download-fle/<str:encrypted_id>/', views.download_file, name='download_file'),

]