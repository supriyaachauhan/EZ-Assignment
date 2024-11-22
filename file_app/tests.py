from django.test import TestCase, Client
from .models import *
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


class LoginUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password123')

    def test_login_success(self):
        response = self.client.post('/login-user/', data=json.dumps({
            'email': 'test@test.com',
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login-user/', data=json.dumps({
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 422)

    def test_login_missing_email(self):
        response = self.client.post('/login-user/', data=json.dumps({
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('email', response.json()['message'])




class UploadFileTestCase(TestCase):
    def setUp(self):
        # Create users for testing
        self.ops_user = User.objects.create_user(
            username='opsuser',
            email='ops_user@example.com', 
            password='password123', 
            role='ops'
        )
        self.client_user = User.objects.create_user(
            username='clientuser',
            email='client_user@example.com', 
            password='password123', 
            role='client'
        )
        
        self.client = Client()
        self.upload_url = reverse('upload-file')

    def test_upload_valid_file(self):
        # Log in as 'ops' user
        self.client.login(username = 'testuser',email='ops_user@example.com', password='password123')
        
        # Create a dummy file
        valid_file = SimpleUploadedFile("file.xlsx", b"dummy content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        response = self.client.post(self.upload_url, {'file': valid_file}, format='multipart')
        

    def test_upload_invalid_file_extension(self):
        # Log in as 'ops' user
        self.client.login(email='ops_user@example.com', password='password123')
        
        # Create a dummy invalid file
        invalid_file = SimpleUploadedFile("file.txt", b"dummy content", content_type="text/plain")
        
        # Send POST request to upload the file
        response = self.client.post(self.upload_url, {'file': invalid_file}, format='multipart')
        
        # Assert error for invalid file extension
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["message"], "Only pptx, docx, and xlsx files are allowed.")

    def test_upload_file_unauthorized_user(self):
        # Log in as 'client' user
        self.client.login(email='client_user@example.com', password='password123')
        
        # Create a dummy file
        valid_file = SimpleUploadedFile("file.docx", b"dummy content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        # Send POST request to upload the file
        response = self.client.post(self.upload_url, {'file': valid_file}, format='multipart')
        
        # Assert error for unauthorized user
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["message"], "You are not allowed to upload files")

    def test_upload_file_user_does_not_exist(self):
        # Log in with a non-existent user
        self.client.logout()
        
        # Create a dummy file
        valid_file = SimpleUploadedFile("file.pptx", b"dummy content", content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        
        # Send POST request to upload the file without logging in
        response = self.client.post(self.upload_url, {'file': valid_file}, format='multipart')
        
        # Assert error for non-existent user
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["message"], "User not registered.")

    def test_upload_file_without_authentication(self):
        # Create a dummy file
        valid_file = SimpleUploadedFile("file.pptx", b"dummy content", content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        
        # Send POST request without logging in
        response = self.client.post(self.upload_url, {'file': valid_file}, format='multipart')
        




class SignUpTestCase(TestCase):
    def test_signup_success(self):
        response = self.client.post('/sign-up/', data=json.dumps({
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_signup_missing_email(self):
        response = self.client.post('/sign-up/', data=json.dumps({
            'username': 'newuser',
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('email', response.json()['message'])






