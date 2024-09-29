from django.utils import timezone
import pytz
from rest_framework import generics, serializers,permissions,status
from rest_framework.response import Response
from .models import HistoryPredictions, Predictions, Class, Price,CustomUser
from .serializers import PriceSerializer, ClassSerializer, HistoryPredictionsSerializer, PredictionsSerializer,CustomUserSerializer
from .sevices.cactus_model_sevice import process_image,convert_image,specail_image
from .sevices.gemini_sevice import analyze_image
import logging
from rest_framework.authtoken.models import Token 
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .authentication import ExpiringTokenAuthentication
from .permissions import IsAdminOrReadOnly
from social_django.utils import load_strategy, load_backend
from social_core.backends.facebook import FacebookOAuth2
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions

logger = logging.getLogger('mylogger')
class ExampleView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Hello, authenticated user!'})
class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        logger.info("serializer: %s", serializer)
        if serializer.is_valid():
            user = serializer.save()

            user = authenticate(username=user.username, password=request.data.get('password'))
            logger.info("Authenticated user: %s", user)
            if user is not None:
                
                auth_login(request, user)
                logger.info("token user doing: %s", user)
                token, created = Token.objects.get_or_create(user=user)
                # Return token and user profile data
                logger.info("Token created: %s", token.key)
                return Response({
                    'token': token.key,
                    'user_profile': {
                    'user_name':user.username,
                    'avatar':user.avatar,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role  ,
                    'fackbook_name':user.fackbook_name
                    }
                }, status=status.HTTP_201_CREATED)
            logger.error("user errors: %s", user.errors)
            return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_profile': {
                    'user_name':user.username,
                    'avatar':user.avatar,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role  ,
                    'fackbook_name':user.fackbook_name

                }
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
class UserProfileCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        logger.debug(f"User role: {request.user.role}")  
        if request.user.role != 'Admin':
            return Response({'detail': 'Not authorized to create profiles'}, status=status.HTTP_403_FORBIDDEN)
        return self.create(request, *args, **kwargs)

class UserProfileRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()  # Ensure the queryset is set for retrieving users

    def get_object(self):
        # Return the user object based on the provided primary key (ID)
        return generics.get_object_or_404(CustomUser, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()

        # Allow deletion only for users with the 'Admin' role
        if request.user.role != 'Admin':
            return Response({'detail': 'Not authorized to delete profiles'}, status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Ensure only the user or staff can update the profile
        if request.user.id != self.get_object().id and request.user.role != 'Admin':
            return Response({'detail': 'Not authorized to update this profile'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user
class UserProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.all()
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete the auth token
        Token.objects.filter(user=request.user).delete()
        # Log out the user
        auth_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
class PriceListCreate(generics.ListCreateAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class PriceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class ClassListCreate(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class HistoryPredictionsListCreate(generics.ListCreateAPIView):
    queryset = HistoryPredictions.objects.all()
    serializer_class = HistoryPredictionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        if self.request.user.role == 'Admin':
            return HistoryPredictions.objects.all()
        else:
            return HistoryPredictions.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        logger.info("Request Headers: %s", request.headers)
        logger.info("Request Data: %s", request.data)
        image = request.data.get('image')
        if not image:
            raise serializers.ValidationError({"image": "This field is required."})
        
        image_new = convert_image(image)
        prediction_value,uploaded_file = analyze_image(image_new)
        logger.info("prediction_value: %s", prediction_value)
        # Respond based on the prediction value
        if prediction_value == 2000:
            pass
        elif prediction_value == 3000:
            return Response({
                'status': "Opp! Please upload Nudum Astro, not another class.",
                'id': None,
                'classes': [],
                'total_min': 0,
                'total_max': 0,
            }, status=status.HTTP_400_BAD_REQUEST)
        elif prediction_value == 3001:
            return Response({
                'status': "Opp! Please upload real Nudum Astro.",
                'id': None,
                'classes': [],
                'total_min': 0,
                'total_max': 0,
            }, status=status.HTTP_400_BAD_REQUEST)

        elif prediction_value == 4000:
            return Response({
                'status': "Opp! Please upload Nudum Astro image.",
                'id': None,
                'classes': [],
                'total_min': 0,
                'total_max': 0,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_min = 0
        total_max = 0
        className = []
        predictions = []

        className, predictions = self.process_image(image_new)
        logger.info(f"Predictions: {predictions}")
        logger.info(f"classNames: {className}")

        if className == "normal" :
            logger.info(f"pass: {className}")
            pass
        else :
            className = []
            predictions = []
            className, predictions = self.specail_image(image_new)
            logger.info(f"Predictions_special: {predictions}")
            logger.info(f"classNames_special: {className}")
        
        if predictions:
            total_min, total_max = self.calculate_total_price(total_min,total_max,predictions)

        logger.info(f"total_min: {total_min}")
        logger.info(f"total_max: {total_max}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        thailand_tz = pytz.timezone('Asia/Bangkok')
        user = request.user
        history_prediction = serializer.save(
            total_min=total_min,
            total_max=total_max,
            timestamp=timezone.now().astimezone(thailand_tz),
            user=user
        )

        if predictions:
            # auth_header = request.headers.get('Authorization')

            # if auth_header is None or not auth_header.startswith('Token '):
            #     return Response({'error': 'Token not provided or invalid format'}, status=status.HTTP_400_BAD_REQUEST)
            
            # token_key = auth_header.split(' ')[1]
            
            # try:
            #     # Get the user associated with the token
            #     token = Token.objects.get(key=token_key)
            #     user = token.user
            # except Token.DoesNotExist:
            #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            classes = self.create_predictions(predictions, history_prediction,user)
            # logger.info(f"create predictions classes: {classes}")
        else :
            logger.info(f"return in")
            return Response({
                'status': "none",
                'id': None,
                'classes': [],
                'total_min': 0,
                'total_max': 0,
            }, status=status.HTTP_201_CREATED)
        logger.info(f"return out")
        return Response({
            'status': "succese",
            'id': history_prediction.id,
            'classes': classes,
            'total_min': total_min,
            'total_max': total_max,
        }, status=status.HTTP_201_CREATED)
        


    def process_image(self, image_data):
        return process_image(image_data)
    
    def specail_image(self, image_data):
        return specail_image(image_data)
    
    def calculate_total_price(self, total_min,total_max, class_ids):
        total_min_cal = total_min
        total_max_cal = total_max
        for class_id in class_ids:
            try:
                class_obj = Class.objects.get(id=class_id)
                logger.info(f"class_obj: {class_obj}")
                price = class_obj.price
                logger.info(f"price: {price}")
                total_min_cal += price.value_min
                total_max_cal += price.value_max
            except Class.DoesNotExist:
                logger.warning(f"Class not found for class_id: {class_id}")
                continue
        return total_min_cal, total_max_cal
    
    def create_predictions(self, class_ids, history_prediction,user):
        classes = []
        for class_id in class_ids:
            try:
                class_obj = Class.objects.get(id=class_id)
                # user_obj = CustomUser.objects.get()
                Predictions.objects.create(
                    history_predictions=history_prediction,
                    class_name=class_obj,
                    user = user
                )
                
                serialized_class = ClassSerializer(class_obj).data
                classes.append(serialized_class)
            except Class.DoesNotExist:
                logger.warning(f"Class not found for class_id: {class_id}")
                continue
        return classes
    
class HistoryPredictionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HistoryPredictions.objects.all()
    serializer_class = HistoryPredictionsSerializer
    permission_classes = [permissions.IsAuthenticated]

class PredictionsListCreate(generics.ListCreateAPIView):
    queryset = Predictions.objects.all()
    serializer_class = PredictionsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Predictions.objects.filter(user=self.request.user)
        history_predictions_id = self.kwargs.get('history_predictions_id')

        if history_predictions_id is not None:
            queryset = queryset.filter(history_predictions_id=history_predictions_id)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PredictionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Predictions.objects.all()
    serializer_class = PredictionsSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacebookLogin(APIView):
    def post(self, request):
        token = request.data.get('access_token')
        strategy = load_strategy(request)
        backend = load_backend(strategy=strategy, name='facebook', redirect_uri=None)
        try:
            user = backend.do_auth(token)
            if user and user.is_active:
                login(request, user)  # Log the user in
                # Return a token or user data
                return Response({'token': 'your-generated-jwt-or-session-token'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

