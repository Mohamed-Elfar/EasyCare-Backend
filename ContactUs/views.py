from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from .serializers import ContactUsSerializer
from django.conf import settings

class ContactUsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        if user.national_id != data.get('national_id'):
            return Response({"error": "National ID does not match the authenticated user's national ID."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ContactUsSerializer(data=data)
        if serializer.is_valid():
            contact_message = serializer.save(user=user)

            subject = f"New Contact Us Message from {contact_message.name}"
            message_body = f"""
            You have received a new message from {contact_message.name} 
            (National ID: {contact_message.national_id}) 
            Message: 
            {contact_message.message}
            """

            recipient_email = settings.EMAIL_HOST_USER

            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False
            )

            return Response({"message": "Your message has been received and emailed."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
