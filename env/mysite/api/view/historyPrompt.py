from django.utils import timezone
import pytz
from rest_framework import generics, serializers,permissions,status
from rest_framework.response import Response
from ..models import HistoryPrompt,Role,Style,HistoryPredictions
from ..serializers import HistoryPromptSerializer,StyleSerializer,RoleSerializer
from ..sevices.cactus_model_sevice import convert_image
from ..sevices.gemini_sevice import analyze_image,generated_post
import logging
from rest_framework.authtoken.models import Token 
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from ..authentication import ExpiringTokenAuthentication
from ..permissions import IsAdminOrReadOnly
from social_django.utils import load_strategy, load_backend
from social_core.backends.facebook import FacebookOAuth2
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions

logger = logging.getLogger('mylogger')


class HistoryPromptListCreate(generics.ListCreateAPIView):
    queryset = HistoryPrompt.objects.all()
    serializer_class = HistoryPromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_role = self.request.user.role

        # Filter by role if the user is not an Admin
        if user_role != 'Admin':
            queryset = queryset.filter(user=self.request.user)

        role_id = self.request.query_params.get('role_id')
        style_id = self.request.query_params.get('style_id')

        if role_id:
            queryset = queryset.filter(role_id=role_id)
        if style_id:
            queryset = queryset.filter(style_id=style_id)

        return queryset

    def create(self, request, *args, **kwargs):
        logger.info("Request Headers: %s", request.headers)
        logger.info("Request Data: %s", request.data)

        image = request.data.get('image')
        if not image:
            raise serializers.ValidationError({"image": "This field is required."})

        image_new = convert_image(image)
        prediction_value, uploaded_file = analyze_image(image_new)
        logger.info("Prediction value: %s", prediction_value)
        
        history_prompt = self.set_history_prompt(request)

        if prediction_value == 2000:
            response_data = generated_post(history_prompt, uploaded_file)  
            response = self.save_history_prompt(history_prompt, response_data)  
            logger.info("Response: %s", response)
            return Response(response, status=status.HTTP_201_CREATED)

        elif prediction_value in [3000, 3001, 4000]:
            messages = {
                3000: "Oops! Please upload Nudum Astro, not another class.",
                3001: "Oops! Please upload real Nudum Astro.",
                4000: "Oops! Please upload a Nudum Astro image."
            }
            return Response({'status': messages[prediction_value]}, status=status.HTTP_400_BAD_REQUEST)

    def save_history_prompt(self, history_prompt, generated_response):
        history_prompt.result = generated_response
        
        history_prompt.save()
        
        serializer = HistoryPromptSerializer(history_prompt)
        return {"status": "History prompt saved successfully!", "history_prompt": serializer.data}

    def set_history_prompt(self, request):
       
        role_id = request.data.get('role_id')
        style_id = request.data.get('style_id')
        history_prediction_id = request.data.get('history_prediction_id')

        # Initialize variables for foreign key assignments
        role_instance = None
        style_instance = None
        history_prediction_instance = None

        # Handle role_id lookup
        if role_id:
            try:
                role_instance = Role.objects.get(id=role_id)
            except Role.DoesNotExist:
                raise serializers.ValidationError({"role": "Role does not exist."})

        if style_id:
            try:
                style_instance = Style.objects.get(id=style_id)
            except Style.DoesNotExist:
                raise serializers.ValidationError({"style": "Style does not exist."})

        if history_prediction_id:
            try:
                history_prediction_instance = HistoryPredictions.objects.get(id=history_prediction_id)
            except HistoryPredictions.DoesNotExist:
                raise serializers.ValidationError({"history_prediction": "History prediction does not exist."})

        # Initialize the HistoryPrompt instance
        history_prompt = HistoryPrompt(
            prompt=request.data.get('prompt'),
            result="", 
            classes=request.data.get('classes'),
            image=request.data.get('image'),
            price=request.data.get('price'),
            user=request.user,
            history_predictions=history_prediction_instance, 
            role_id=role_instance, 
            style_id=style_instance  
        )

        return history_prompt  
class HistoryPromptDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HistoryPrompt.objects.all()
    serializer_class = HistoryPromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_role = self.request.user.role
        if user_role == 'Admin':
            return queryset
        return queryset.filter(user=self.request.user)
    
class RoleListCreate(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed

    def get_queryset(self):
        return super().get_queryset()

class StyleListCreate(generics.ListCreateAPIView):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed

class StyleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed

    def get_queryset(self):
        return super().get_queryset()
