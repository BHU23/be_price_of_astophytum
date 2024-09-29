"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api import views 
from api.view.historyPrompt import (
    HistoryPromptDetail, 
    HistoryPromptListCreate,
    RoleListCreate, 
    RoleDetail, 
    StyleListCreate, 
    StyleDetail, 
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/prices/', views.PriceListCreate.as_view(), name='price-list-create'),
    path('api/prices/<int:pk>/', views.PriceDetail.as_view(), name='price-detail'),
    path('api/classes/', views.ClassListCreate.as_view(), name='class-list-create'),
    path('api/classes/<int:pk>/', views.ClassDetail.as_view(), name='class-detail'),
    path('api/history-predictions/', views.HistoryPredictionsListCreate.as_view(), name='history-predictions-list-create'),
    path('api/history-predictions/<int:pk>/', views.HistoryPredictionsDetail.as_view(), name='history-predictions-detail'),
    path('api/predictions/', views.PredictionsListCreate.as_view(), name='predictions-list-create'),
    path('api/predictions/<int:pk>/', views.PredictionsDetail.as_view(), name='predictions-detail'),
    path('predictions/<int:history_predictions_id>/',  views.PredictionsListCreate.as_view(), name='predictions-list-create-by-history'),
    path('api/register/', views.RegisterUserView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/profiles/', views.UserProfileListView.as_view(), name='user-profile-list'),  # New endpoint for listing profiles
    path('api/user/profile/', views.UserProfileView.as_view(), name='user-profile-detail'),
    path('api/profile/create/', views.UserProfileCreateView.as_view(), name='user-profile-create'),
    path('api/profile/<int:pk>/', views.UserProfileRetrieveUpdateDeleteView.as_view(), name='user-profile-retrieve-update-delete'),
    path('api/history-prompts/', HistoryPromptListCreate.as_view(), name='history-prompt-list-create'),
    path('api/history-prompts/<int:pk>/', HistoryPromptDetail.as_view(), name='history-prompt-detail'),
    path('api/roles/', RoleListCreate.as_view(), name='role-list-create'),
    path('api/roles/<int:pk>/', RoleDetail.as_view(), name='role-detail'),
    path('api/styles/', StyleListCreate.as_view(), name='style-list-create'),
    path('api/styles/<int:pk>/', StyleDetail.as_view(), name='style-detail'),
    path('auth/facebook/', views.FacebookLogin.as_view(), name='facebook-login'),
]
