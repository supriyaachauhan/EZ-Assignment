from django.shortcuts import render
from .models import *
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json, os
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.core.signing import Signer, BadSignature

signer = Signer()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        # 'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@csrf_exempt
def login_user(request):
    try:
        if request.method == 'POST':
            request_data = json.loads(request.body)
            print("request_data --->> ", request_data)
            error_messages = {}

            if request_data.get('email') == None:
                error_messages['email'] = 'This field is required.'

            if request_data.get('password') == None:
                error_messages['password'] = 'This field is required.'

            if error_messages != {}:
                return JsonResponse({"error": True, "statusCode": 422, "message": error_messages}, status=422)

            email = request_data['email']
            password = request_data['password']

            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                access_token = get_tokens_for_user(user)

                return JsonResponse({"error": False, "statusCode": 200, "message": "Login Successful", "token": access_token}, status=200)

            else:
                return JsonResponse({"error": True, "statusCode": 422, "message": "Invalid credentials."}, status=422)

        else:
            return JsonResponse({
                "error": True,
                "statusCode": 405,
                "message": "Method Not Allowed"
            }, status=405)
        

    except Exception as e:
        print("error in login api --> ", e)
        return JsonResponse({"error": True, "statusCode": 422, "message": "Something went wrong"}, status=422)

@csrf_exempt
def upload_file(request):
    try:
        # request_data = json.loads(request.body)
        current_user = request.user

        # print("current_user -->>", current_user)

        user_data = User.objects.get(email=current_user)
        # print(user_data.role, '---------------------------------')

        if user_data.role == "ops":
            upload_file = request.FILES.get('file')
            extension = os.path.splitext(upload_file.name)[1][1:].lower()

            # print("upload_file --->> ", extension)

            allowed_extensions = ['pptx', 'docx', 'xlsx']

            if extension not in allowed_extensions:
                return JsonResponse({"error": True, "statusCode": 422, "message": "Only pptx, docx, and xlsx files are allowed."}, status=422)
            
            else:
                path = default_storage.save(os.path.join(settings.MEDIA_ROOT+'/uploaded_files/' + str(upload_file)), ContentFile(upload_file.read()))
                UploadedFiles.objects.create(
                    user = current_user,
                    file = path,
                )

                return JsonResponse({"error": False, "statusCode": 200, "message": "File uploaded successfully."}, status=200)

        else:
            return JsonResponse({"error": True, "statusCode": 422, "message": "You are not allowed to upload files"}, status=422)

    except User.DoesNotExist:
        return JsonResponse({"error": True, "statusCode": 404, "message": "User not registered."}, status=404)


    except Exception as e:
        print("error in upload file api --> ", e)
        return JsonResponse({"error": True, "statusCode": 422, "message": "Something went wrong!"}, status=422)

@csrf_exempt
def sign_up(request):
    try:
        if request.method == "POST":
            request_data = json.loads(request.body)
            error_messages = {}

            if request_data.get('username') == None:
                error_messages['username'] = 'This field is required.'

            if request_data.get('email') == None:
                error_messages['email'] = 'This field is required.'

            if request_data.get('password') == None:
                error_messages['password'] = 'This field is required.'

            if error_messages != {}:
                return JsonResponse({"error": True, "statusCode": 422, "message": error_messages}, status=422)

            username = request_data['username']
            email = request_data['email']
            password = request_data['password']

            get_email = User.objects.filter(email=email).exists()

            if get_email:
                return JsonResponse({"error": True, "statusCode": 422, "message": "This email is already registered."}, status=422)
            
            else:
                get_user = User(
                    username = username,
                    email = email,
                )

                get_user.set_password(password)
                get_user.save()

                # Generate encrypted url to verify email
                en_id = urlsafe_base64_encode(force_bytes(get_user.id))    # Encode userid
                # print("en_id -->", en_id)

                token = PasswordResetTokenGenerator().make_token(get_user)    # token generation
                print(token)

                reset_link = f"http://127.0.0.1:8000/verify-email/{en_id}/{token}"
                print('reset_link -->', reset_link)

                send_mail(
                   'Verify your Email',
                    f'Please click on the link to verify your email : {reset_link}',
                    'supriya.chauhan0509@gmail.com',
                    [email],
                    fail_silently=False,
                )

                return JsonResponse({
                    "error": False, 
                    "statusCode": 201, 
                    "message": "User registered successfully. Please verify your email.",
                    "encrypted_url": reset_link
                    }, status=201)

        else:
            return JsonResponse({
                "error": True,
                "statusCode": 405,
                "message": "Method Not Allowed"
            }, status=405)

    except Exception as e:
        # print("error in sign-up api --> ", e)
        return JsonResponse({"error": True, "statusCode": 422, "message": "Something went wrong!"}, status=422)


def verify_email(request, id , token):
    try:
        user_id = urlsafe_base64_decode(id).decode() 
        # print("user_id", user_id)

        user = User.objects.get(id=user_id)
        # print("user", user)

        
        # To check whether the token is true or false
        if PasswordResetTokenGenerator().check_token(user,token) == False: 
            return JsonResponse({"error": True, "statusCode": 422, "message": "Invalid link!"}, status=422)
        

        return JsonResponse({"error": False, "statusCode": 200, "message": "Email verified successfully."}, status=200)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({"error": True, "statusCode": 422, "message": "Invalid link!"}, status=422)

    except Exception as e:
        # print("error in verify-email api --> ", e)
        return JsonResponse({"error": True, "statusCode": 422, "message": "Something went wrong!"}, status=422)
    


# List all uploaded files
class FilesListing(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = UploadedFiles.objects.all()
        serializer = FileListingSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# Download-file 
def generate_download_url(file_id):
    encrypted_id = signer.sign(str(file_id))
    download_url = f"http://127.0.0.1:8000/download-fle/{encrypted_id}"
    return download_url


@login_required
def get_download_url(request, file_id):
    try:
        get_file = UploadedFiles.objects.get(id=file_id)
    except UploadedFiles.DoesNotExist:
        return JsonResponse({"error": True, "statusCode": 404, "message": "File not found"}, status=404)

    
    # Generate the secure download URL
    download_link = generate_download_url(get_file.id)
    
    return JsonResponse({"download-link": download_link, "message": "success"})


@login_required
def download_file(request, encrypted_id): 
    try:
        decrypted_id = signer.unsign(encrypted_id)
    except BadSignature:
        return JsonResponse({"error": True, "statusCode": 404, "message": "Invalid or tampered download link."}, status=404)


    try:
        get_file = UploadedFiles.objects.get(id=decrypted_id)

    except UploadedFiles.DoesNotExist:
        return JsonResponse({"error": True, "statusCode": 404, "message": "File not found"}, status=404)

 
    
    if request.user.role != 'client':
        return JsonResponse({"error": True, "statusCode": 403, "message": "Unauthorized"}, status=403)


    return JsonResponse({"error": False, "statusCode": 200, "message": "File downloaded successfully"}, status=200)
