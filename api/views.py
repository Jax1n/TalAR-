from django.shortcuts import render
from rest_framework.views import APIView
from django.core.mail import send_mail

from api.models import Profile, User
from api.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer, PasswordResetRequestSerializer, OTPVerificationSerializer, PasswordResetSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = ([AllowAny])
    serializer_class = RegisterSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    if request.method == "GET":
        response = f'Hey {request.user}, You are seeing a GET response'
        return Response({'response': response}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        text = request.POST.get("text")
        response = f'Hey {request.user}, your text is {text}'
        return Response({'response': response}, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)   


class PasswordResetRequestView(APIView):
    permission_classes = ([AllowAny])

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP sent to email."}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class OTPVerificationView(APIView):
    permission_classes = ([AllowAny])

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )



class PasswordResetView(APIView):
    permission_classes = ([AllowAny])

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )