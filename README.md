# EasyCare-Backend

EasyCare-Backend is a Django-based RESTful API backend project designed to manage user registrations, password resets, prescriptions, contact messages, and other related functionalities. The project utilizes Django REST framework and Simple JWT for authentication and authorization.

## Features

- User registration with a custom user model
- Password reset functionality
- Authentication using Simple JWT
- Prescription management
- Contact message management
- API endpoints for user management, prescription management, and contact message management

## API Endpoints

### User Management

- **User Registration**: 
  - **POST** `/api/register/`
  
- **Password Reset**: 
  - **POST** `/api/password-reset/`

- **Token Obtain Pair**: 
  - **POST** `/api/token/`

### Prescription Management

1. **Create Prescription**: 
   - **POST** `/api/patients/<str:patient_national_id>/prescriptions/`
   
2. **Get Prescriptions for a Patient**: 
   - **GET** `/api/patients/<str:patient_national_id>/prescriptions/`

### Contact Us Message Management

1. **Create Contact Us Message**: 
   - **POST** `/api/contact-us/`

## Views

The project includes the following view files:

- **Account/views.py**: Handles user registration, password reset, and token obtain pair.
- **Prescription/views.py**: Manages prescriptions, including creating and retrieving prescriptions for patients.
- **ContactUs/views.py**: Manages contact messages, including creating contact messages.

## Models

- **CustomUser**: A custom user model with fields for national ID, email, phone number, and more.
- **Prescription**: A model for prescriptions, including fields for patient, doctor, medicine name, dosage, and instructions.
- **ContactUs**: A model for contact messages, including fields for user, name, national ID, and message.

## Serializers

- **CustomUserSerializer**: A serializer for the CustomUser model.
- **CustomTokenObtainPairSerializer**: A serializer for token obtain pair.
- **PrescriptionSerializer**: A serializer for the Prescription model.
- **ContactUsSerializer**: A serializer for the ContactUs model.
