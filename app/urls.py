from email.policy import default
import imp
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from app import views as cviews
from app import apiviews as capiviews
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'deposits',capiviews.Deposits,basename='deposits')

urlpatterns = [
   

]

urlpatterns+=router.urls