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
from sensorTest import views

urlpatterns = [
    path('TestSensor/', views.TestSensor, name='TestSensor'),
    
    path('TouchSwitchTest/',views.TestTouchSwitch, name='TouchTest'),
    path('TouchSwitchResults/',views.TouchSwitchResults.as_view(), name='TouchResult'),
    
    path('BallTiltSwitchTest/',views.TestBallTiltSwitch, name='BallTiltTest'),
    path('BallTiltSwitchResults/',views.BallTiltResults.as_view(), name='BallTiltResult'),
    
    path('MagneticSwitchTest/',views.TestMagneticSwitch, name='MagneticTest'),
    path('MagneticSwitchResults/',views.MagneticSwitchResults.as_view(), name='MagneticResult'),
    
    path('PressureSwitchTest/',views.TestPressureSwitch, name='PressureTest'),
    path('PressureSwitchResults/',views.PressureSwitchResults.as_view(), name='PressureResult'),
    
    path('CompressionTest/', views.CompressionTest, name='CompressionTest'),
    path('CompressionResults',views.CompressionSystemResults.as_view(), name='CompressionResult'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
