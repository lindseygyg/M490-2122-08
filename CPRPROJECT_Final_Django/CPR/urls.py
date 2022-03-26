"""CPR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from RunCPR import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index, name='index'),
    path('aboutTeam/',views.aboutTeam, name='aboutTeam'),
    path('aboutCPR/',views.aboutCPR, name='aboutCPR'),
    path('start/', views.start, name='start'),
    path('CheckSurroundings/', views.CheckSurroundings, name='CheckSurroundings'),
    path('TouchSwitchinstructions/',views.TouchSwitchinstructions, name='TouchSwitchinstructions'),
    path('headtilt/',views.BallTiltSwitchView.as_view(), name='headtilt'),
    path('rescuebreath/',views.PressureSwitchView.as_view(), name='rescuebreath'),
    path('pulse/',views.TouchSwitchView.as_view(), name='pulse'),
    path('aed/',views.MagneticSwitchView.as_view(), name='aed'),
    path('compression/',views.CompressionSystemView.as_view(), name='compression'),
    path('CompressionInstructions/', views.CompressionInstructions, name='CompressionInstructions'),
    path('HeadTiltInstructions/', views.HeadTiltInstructions, name='HeadTiltInstructions'),
    path('RescueBreathInstructions/', views.RescueBreathInstructions, name= 'RescueBreathInstructions'),
    path('CompressionSet2/', views.CompressionSet2, name='CompressionSet2'),
    path('compression2/', views.CompressionSystemSet2View.as_view(), name='compression2'),
    path('AEDinstructions/', views.AEDinstructions, name='AEDinstructions'),
    path('end/', views.end, name='end'),
    path('sensorTest/', include('sensorTest.urls')),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
