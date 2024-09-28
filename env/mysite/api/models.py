from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import json
class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20, 
        choices=[('Admin', 'Admin'), ('User', 'User')],
        default='User'  
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    avatar = models.TextField(blank=True, null=True)  # Store base64 string here
    fackbook_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Price(models.Model):
    id = models.AutoField(primary_key=True)
    value_min = models.FloatField()
    value_max = models.FloatField()

    def __str__(self):
        return f"Price from {self.value_min} to {self.value_max}"

class Class(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    example_image = models.TextField()        # Base64-encoded image data
    extra_value = models.FloatField()
    description = models.TextField()
    care_instructions = models.TextField(default="Handle with care")
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return self.name

class HistoryPredictions(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.TextField()                # Base64-encoded image data
    total_min = models.FloatField(null=True, blank=True)
    total_max = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)        # DateTime field for timestamp
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"HistoryPrediction {self.id} at {self.timestamp}"

class Predictions(models.Model):
    history_predictions = models.ForeignKey(HistoryPredictions, on_delete=models.CASCADE, related_name='predictions')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"Prediction for {self.class_name.name} in HistoryPrediction {self.history_predictions.id}"

class Role(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name
class Style(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name
class HistoryPrompt(models.Model):
    id = models.AutoField(primary_key=True) 
    prompt = models.TextField()             
    result = models.TextField()           
    classes = models.TextField()           
    image = models.TextField()             
    price = models.FloatField(null=True, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  
    history_predictions = models.ForeignKey('HistoryPredictions', on_delete=models.SET_NULL, null=True, blank=True, related_name='history_predictions') 
    role_id = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)  
    style_id = models.ForeignKey('Style', on_delete=models.SET_NULL, null=True, blank=True)

    def set_classes(self, classes_list):
        if isinstance(classes_list, list) and all(isinstance(i, str) for i in classes_list):
            self.classes = json.dumps(classes_list)  # Serialize to JSON string

    def get_classes(self):
        try:
            return json.loads(self.classes)  # Deserialize to Python list
        except json.JSONDecodeError:
            return [] 
    
    def __str__(self):
        return f"HistoryPrompt {self.id} at {self.timestamp}"

