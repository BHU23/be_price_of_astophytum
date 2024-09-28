from rest_framework import serializers
from .models import Price, Class, HistoryPredictions, Predictions,CustomUser,HistoryPrompt, Role, Style
import logging
logger = logging.getLogger('mylogger')
class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False)  # Handle password separately

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar', 'password', 'email', 'role', 'first_name', 'last_name', 'fackbook_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False},
            'fackbook_name': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        avatar_data = validated_data.pop('avatar', None)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'User'),
            first_name=validated_data.get('first_name', ''),
            fackbook_name=validated_data.get('fackbook_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        if avatar_data:
            user.avatar = avatar_data  

        if password:
            user.set_password(password) 
        
        user.save()  

        return user

    def update(self, instance, validated_data):
        avatar_data = validated_data.pop('avatar', None)
        password = validated_data.pop('password', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update avatar if provided
        if avatar_data is not None:
            instance.avatar = avatar_data

        # Update password if provided
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance



class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('id', 'value_min', 'value_max')

class ClassSerializer(serializers.ModelSerializer):
    price = PriceSerializer()  # This is for serialization

    class Meta:
        model = Class
        fields = ['id', 'name', 'description','care_instructions', 'extra_value', 'price', 'example_image']
    def create(self, validated_data):
        price_data = validated_data.pop('price', None)
        if price_data:
            value_min = price_data.get('value_min')
            value_max = price_data.get('value_max')

            try:
                price_instance = Price.objects.get(value_min=value_min, value_max=value_max)
            except Price.DoesNotExist:
                price_instance = Price.objects.create(**price_data)
            except Price.MultipleObjectsReturned:
                raise serializers.ValidationError("Multiple Price objects found with the provided value_min and value_max.")

            validated_data['price'] = price_instance

        class_instance = Class.objects.create(**validated_data)
        return class_instance
    
    def update(self, instance, validated_data):
   
        price_data = validated_data.pop('price', None)
        logger.info(price_data)
        if price_data:
    
            value_min = price_data.get('value_min')
            value_max = price_data.get('value_max')
            logger.info("value_min {value_min}")
            try:
                price_instance = Price.objects.get(value_min=value_min, value_max=value_max)
                logger.info(price_instance)
                price_instance.value_min = value_min
                price_instance.value_max = value_max
        
                price_instance.save()
    
                instance.price = price_instance
            except Price.DoesNotExist:
                raise serializers.ValidationError("No Price object found with the provided value_min and value_max.")
            except Price.MultipleObjectsReturned:
                raise serializers.ValidationError("Multiple Price objects found with the provided value_min and value_max.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'avatar', 'first_name', 'last_name', 'email', 'role', 'fackbook_name']
    
# class HistoryPredictionsSerializer(serializers.ModelSerializer):
#     user_profile = UserProfileSerializer(source='user', read_only=True)
#     class Meta:
#         model = HistoryPredictions
#         fields = ['id', 'image', 'total_min', 'total_max', 'timestamp', 'user_profile']

class PredictionsSerializer(serializers.ModelSerializer):
    class_name = ClassSerializer() 
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)

    class Meta:
        model = Predictions
        fields = ('id', 'class_name', 'user') 
class HistoryPredictionsSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user', read_only=True)
    predictions = PredictionsSerializer(many=True, read_only=True)  # Nested Predictions
    
    class Meta:
        model = HistoryPredictions
        fields = ['id', 'image', 'total_min', 'total_max', 'timestamp', 'user_profile', 'predictions']

# Serializer for Role model
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

# Serializer for Style model
class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = ['id', 'name']
class HistoryPromptSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user', read_only=True) 
    role = RoleSerializer(source='role_id', read_only=True)  
    style = StyleSerializer(source='style_id', read_only=True)  
    history_predictions = HistoryPredictionsSerializer(read_only=True) 

    class Meta:
        model = HistoryPrompt
        fields = ['id', 'prompt', 'result', 'image', 'classes', 'price', 'timestamp', 'user_profile', 'role', 'style', 'history_predictions']
