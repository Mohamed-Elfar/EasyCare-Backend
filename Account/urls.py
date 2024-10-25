from django.urls import path
from .views import UserRegistrationView, UserProfileView
from Account.views import SetNewPasswordView,CustomTokenObtainPairView,RequestPasswordResetView,VerifyOTPView,PatientSearchView,DoctorListView,PharmacistListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('search-patient/<str:national_id>/', PatientSearchView.as_view(), name='search-patient'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set_new_password'),
    path('doctors-categories/', DoctorListView.as_view(), name='doctor-list'),
    path('pharmacists-categories/', PharmacistListView.as_view(), name='pharmacist-list'),

]
