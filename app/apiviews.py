from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics,viewsets,status
from app import serializers, views



