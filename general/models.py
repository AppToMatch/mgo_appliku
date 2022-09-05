from operator import imod
from pyexpat import model
from django.core.exceptions import ValidationError
from functools import reduce
import math
from django.contrib.auth.hashers import make_password,check_password
from typing import Text
from django.db.models.enums import Choices
from django.db.models.fields import TextField
# from django.utils.translation import Trans
from django_countries.fields import CountryField
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import (
    get_available_image_extensions,
    FileExtensionValidator,
)
from django.contrib.auth.models import AnonymousUser, User
from django.forms import ModelForm
from django import forms
import datetime
from django.shortcuts import get_object_or_404
from imagekit.models import ImageSpecField # < here
from pilkit.processors import ResizeToFill
from random import random
from tinymce.models import HTMLField
import os
import base64
from django.core.exceptions import ObjectDoesNotExist
# from admin.views import savedproducts
# from users import models as apmodels
from django.utils.timezone import now

