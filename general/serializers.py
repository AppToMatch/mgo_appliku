from rest_framework import serializers
from app import models as cmodels
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from app.models import *
from knox.models import AuthToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password','id')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # securities = Security.objects.all()
        # for security in securities:
        #     security.delete()
        # profiles = Profile.objects.all()
        # for profile in profiles:
        #     profile.delete()
        # users = User.objects.all()
        # for user in users:
        #     user.delete()

        user = User.objects.create(email=str(validated_data['email']).lower(),
        username=str(validated_data['email']).lower()
        )
        user.set_password(validated_data['password'])
        user.save()
        # tokens = AuthToken.objects.filter(user=user)
        # for token in tokens:
        #     token.delete()
        try:
            token = AuthToken.objects.get(user=user)
        except ObjectDoesNotExist:
            token = AuthToken.objects.create(user=user)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        user.is_superuser  = True
        user.save()
        return user, token[1]


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'


class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'



class InterestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'
    
class UserTwoFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)


class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields =  '__all__'



class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields =  '__all__'



class RepliesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields =  '__all__'



class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True},}
