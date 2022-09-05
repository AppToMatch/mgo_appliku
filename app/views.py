import imp
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from random import random
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
import smtplib
import socket
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
import os
import base64
from django.forms import ModelForm
from django.conf import settings
from django import forms
import datetime
from django.contrib.auth.decorators import login_required
from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template import loader
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.mail import send_mail




