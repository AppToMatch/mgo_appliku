from hashlib import blake2b
from django.core.exceptions import ValidationError
import math
from django.contrib.auth.hashers import make_password,check_password
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
import os
import base64
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# from admin.views import savedproducts
# from users import models as apmodels
from django.utils.timezone import now


def getid(strength,length):
    nums = '0123456789'
    tempnums = ''
    lalph = 'abcdefghijklmnopqrstuvwxyz'
    templalph=''
    ualph = lalph.upper()
    tempualph = ''

    for num in range(0,len(nums)):
        tempnums +=nums[round((random()-0.5)*len(nums))]
    for num in range(0,len(lalph)):
        templalph +=lalph[round((random()-0.5)*len(lalph))]
    for num in range(0,len(ualph)):
        tempualph +=ualph[round((random()-0.5)*len(ualph))]
    temporary_id = tempnums[0:strength] + templalph[0:strength]+tempualph[0:strength]
    generated_id= []
    for char in temporary_id:
        generated_id.insert(round(random()*len(temporary_id)),char)
    generated_id = ''.join(generated_id)[0:length]
    return generated_id



class Security(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,blank=True,null= True,)
    secret_question = models.CharField(max_length=225,blank=True,default='')
    secret_answer = models.CharField(max_length=225,blank=True,default='')
    previous_email = models.CharField(max_length=225,blank=True,default='')
    last_token = models.CharField(max_length=225,blank=True,default='')
    profile_updated = models.BooleanField(default=False,blank=True)
    suspension_count = models.IntegerField(default=0,blank=True)
    briefly_suspended = models.BooleanField(default=False,blank=True)
    time_suspended = models.DateTimeField(auto_now_add=False,default=now, blank=True)
    time_suspended_timestamp = models.IntegerField(default=0,blank=True)
    locked = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=45, blank=True, default ='')
    email_confirmed = models.BooleanField(default=False)
    two_factor_auth_enabled = models.BooleanField(default=False)
    email_change_request = models.BooleanField(default=False)
    pending_email = models.EmailField(default='',blank=True)
    login_attempt_count = models.IntegerField(default=0)
    class Meta:
        db_table = 'security'


    def save(self,*args, **kwargs):

        if self.suspension_count>2:
            self.briefly_suspended = True
            self.time_suspended =  datetime.datetime.now()
            self.time_suspended_timestamp = datetime.datetime.now().timestamp()
        secret_question=''
        for char in self.secret_question:
            if char ==  '?':
                continue
            else:
                secret_question = secret_question +char
        self.secret_question = secret_question+'?'
        super(Security,self).save()


class Interest(models.Model):
    name = models.CharField(max_length=100,blank=False,default = '')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING,blank=True,null= True,editable= False)
    first_name = models.CharField(max_length = 100, blank=True, default ='')
    last_name = models.CharField(max_length=100, blank=True, default ='')
    likes_me = models.ManyToManyField(User, blank=True,related_name= 'likes_me')
    liked_mangos = models.ManyToManyField(User, blank=True,related_name= 'i_like')
    about = models.TextField(max_length=1000,blank=True,default='')
    rating = models.IntegerField(default=5)
    age = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    gender = models.CharField(max_length =225, choices=(('M','Male'), ('F','Female')), default='',blank=True)
    photo = models.ImageField(blank=True)
    profile_edit_date = models.DateField(auto_now=True)
    date_time_added = models.DateTimeField(default=now)
    date_of_birth = models.DateField(default=now)
    occupation = models.CharField(max_length=100, blank=True, default ='')
    call_code = models.CharField(max_length=5, blank=True, default ='')
    trybe = models.CharField(max_length = 100, blank=True, default ='')
    state = models.CharField(max_length=100, blank=True, default ='')
    country = models.CharField(max_length = 100, blank=True, default ='')
    location = models.CharField(max_length=200, blank=True, default ='')
    deleted = models.BooleanField(default=False)
    tc_accepted = models.BooleanField(default=False)
    interested_in = models.CharField(max_length=200, default='',choices=(('male','male'),('female','female')))
    interests = models.ManyToManyField(Interest,default='',blank=True,)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return str(self.pk) + ' ' +str(self.pk)
       

    # def save(self,*args, **kwargs):
    #     self.first_name= self.user.first_name
    #     self.last_name = self.user.last_name
    #     super(Profile,self).save()


class Help(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,blank=True,null= True,editable= False)
    category = models.CharField(max_length =225, default='',blank=True)
    subject = models.CharField(max_length =225, default='',blank=True)
    entity_id = models.CharField(max_length =225, default='',blank=True)
    message = models.TextField(max_length =1000, default='',blank=True)

    class Meta:
        db_table = 'help'

    def __str__(self):
        return str(self.pk) + ' ' +str(self.user.first_name)


class Picture(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,blank=True,null= True,editable= False)
    image = models.ImageField(blank=True)
    is_profile_picture = models.BooleanField(default=False,)
    class Meta:
        db_table = 'pictures'
        unique_together = ('user','is_profile_picture',)


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING,default='')
    to = models.ForeignKey(User, on_delete=models.DO_NOTHING,default='', related_name="chatto")
    message = models.TextField(max_length=1000,default='')
    image = models.ImageField(blank=True)
    is_read = models.BooleanField(default=False,)
    is_sent = models.BooleanField(default=True,)
    is_delivered = models.BooleanField(default=False,)
    deleted = models.BooleanField(default=False,)

    class Meta:
        db_table = 'chats'




class Reply(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE,default='')
    reply_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,default='',)
    message = models.TextField(max_length=1000,default='')
    image = models.ImageField(blank=True)
    is_read = models.BooleanField(default=False,)
    is_sent = models.BooleanField(default=True,)
    is_delivered = models.BooleanField(default=False,)
    deleted = models.BooleanField(default=False,)

    class Meta:
        db_table = 'replies'
