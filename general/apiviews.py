from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.models import *
from app.serializers import *
from .serializers import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from rest_framework import generics,viewsets,status
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from django.contrib.auth import login, authenticate,logout
from .permissions import Check_API_KEY_Auth
# from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from app.email_sender import sendmail
from django.views.decorators.csrf import csrf_exempt
from knox.auth import TokenAuthentication 
from knox.models import AuthToken

from general import permissions

from django.core.mail import send_mail
from django.conf import settings


def getuser(request,):
    try:
        user = User.objects.get(pk=request.user.pk)
    except Exception:
        user = []
    return user


def getprofile(request,**filters):
    try:
        profile = Profile.objects.get(user=User.objects.get(pk = int(request.user.pk)),**filters)
    except Exception:
        profile = []
    return profile


def accepttc(request):
    profile = getprofile(request)
    if profile:
        profile.tc_accepted = True
        profile.save()
        return {'status':'success',}
    else:
        return {'status':'No profile',}



def getkeys(obj):
    try:
        obj = dict(obj[0])
        return list(obj.keys())
    except Exception:
        return []


def getfilters(request,*args,**kwargs):
    if request.method == 'POST':
        generalfilters = dict(request.POST)
    else:
        generalfilters = dict(request.GET)
    exclude_contain_words = []
    filters = {}
    try:
        model_fields = kwargs['model_fields']
    except KeyError:
        model_fields = []
    try:
        exclude_list = kwargs['exclude']
    except KeyError:
        exclude_list = []

    try:
        contain_words_list = kwargs['contain_words']
    except KeyError:
        contain_words_list =[]
    for filter in generalfilters:
        if filter =='format':
            exclude_contain_words.append(filter)
        elif filter in exclude_list:
            exclude_contain_words.append(filter)
        elif not generalfilters[filter][0]:
            exclude_contain_words.append(filter)
        elif filter not in model_fields:
            for word in model_fields:
                    if filter.find(word) != -1:                
                        exclude_contain_words.append(filter)
        else:
            for word in contain_words_list:
                if (word and filter not in exclude_contain_words):
                    if filter.find(word) != -1:                
                        exclude_contain_words.append(filter)
        if filter in exclude_contain_words:
            pass
        else:
            # exist = (filter in args) or (filter in kwargs['model_fields'])
            filter = str(filter)
            filters[filter] = generalfilters[filter][0]
    return filters

class checkapipermission(APIView,):
    permission_classes = (Check_API_KEY_Auth,)
    def get(self, request, format=None):
        content = {
        'status': 'request was permitted'
        }
        return Response(content)

class UserList(viewsets.ModelViewSet,):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListPaginated(viewsets.ModelViewSet,PageNumberPagination):
    pagination_class = LimitOffsetPagination
    page_size = 10
    page_size_query_param = 'page_size'
    queryset = User.objects.all()
    serializer_class = UserSerializer



class tokenAuth(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        return Response({'detail': "I suppose you are authenticated"})

# @csrf_exempt
class LoginView(APIView):
    permission_classes = ()
    serializer_class = UserSerializer
    def get(self,request):
        return Response(status=status.HTTP_202_ACCEPTED)

    def post(self, request,):
        logout(request)
        email = request.data.get("email")
        password = request.data.get("password")
        # user = authenticate(request,email=email, password=password)
        try:
            user = User.objects.get(email=email)
            if check_password(password,user.password):
                serialized_data = UserSerializer(user)
                token=AuthToken.objects.create(user=user)[1]
                # generated=AuthToken.objects.filter(user=request.user)
                # request.session['token']=token.key
                # print(token.key)
                return Response({'status':'success','token':token},status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"error": "Wrong credentials"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:

            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class RequestChangePasswordView(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self,request):
        email =request.POST.copy().get('email')
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                security_serializer_class = SecuritySerializer(security)
                db_token = str(round(9999999 * random()))[0:6]
                security.last_token= make_password(db_token)
                security.save()
                data = {'status':'success','6_digits':db_token}
                
            except ObjectDoesNotExist:
                security = Security.objects.create(user=user)
                security.refresh_from_db()
                db_token = str(round(9999999 * random()))[0:6]
                print(db_token)
                security.last_token= make_password(db_token)
                security.save()
                data = {'status':'success','6_digits':db_token}
            message = """<p>Hi there!, <br> <br>You have requested to change your password. <br> <br>
            <b>Use """ + db_token + """ as your verification code</b></p>"""
            subject = 'Password Change Request'
            sendmail([user.email],message,message,subject)
            return Response(data,status=status.HTTP_202_ACCEPTED)
        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


class VerifyPasswordRequestCode(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        verification_code = request.POST.copy().get('code')
        email = request.POST.copy().get('email')
        # '154914'
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                if check_password(verification_code,security.last_token):
                    user.set_password(request.data.get('password'))
                    user.save()
                    data = {'success':True}
                    security.last_token = ''
                    security.save()
                else:
                    data= {'invalid_verification_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            except ObjectDoesNotExist:
                return Response({'invalid_request':True},status=status.HTTP_404_NOT_FOUND)


        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)



class HelpView(APIView):

    queryset = Help.objects.all()
    serializer_class = HelpSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        helps = Help.objects.filter(user=user,**filters)
        serializer_class = HelpSerializer(helps,many=True)
        data = {'status':'success','helps':serializer_class.data,}
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        serializer_class = HelpSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            help_request = serializer_class.instance
            help_request.user = user
            help_request.save()
            # profile.help= help
            # profile.save()
            help_serializer_class = HelpSerializer(help_request)
            data = {'status':'success','help':help_serializer_class.data}
        else:
            data = {'status':'failed',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)



    def put(self,request):
        user = getuser(request)
        help_request = Help.objects.get(id=request.GET.get('id'))
        serializer_class = HelpSerializer(instance =help_request, data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            # help = serializer_class.instance
            # help.save()
            # profile.help= help
            # profile.save()
            help_serializer_class = HelpSerializer(help_request)
            data = {'status':'success','help':help_serializer_class.data}
        else:
            data = {'status':'failed',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)

class ProfileView(APIView):

    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication,]
    # permission_classed=[IsAuthenticated]

    def get(self,request):
        # token=request.session['token']
        # print(token.key)
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            profile_serializer_class = ProfilesSerializer(profile)
            data = {'status':'success','profile':profile_serializer_class.data}
        except ObjectDoesNotExist:
            data = {'profile':''}
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            serializer_class = ProfilesSerializer(profile,instance=profile,data=request.data)
        except ObjectDoesNotExist:
            serializer_class = ProfilesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            profile = serializer_class.instance
            profile.user= getuser(request)
            profile.save()
            profile_serializer_class = ProfilesSerializer(profile)
            data = {'status':'success','profile':profile_serializer_class.data}
        else:

            data = {'status':'failed','description':'Invalid data',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)


class VerifyPhone(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def get(self,request):
        phone_number =request.GET.get('phone_number')
        try:
            security = Security.objects.get(phone_number=phone_number)
            security_serializer_class = SecuritySerializer(security)
            db_token = str(round(9999999 * random()))[0:6]
            print(db_token)
            security.last_token= make_password(db_token)
            security.save()
            data = {'status':'success','security':security_serializer_class.data}
            
        except ObjectDoesNotExist:
            security = Security.objects.create(phone_number=phone_number)
            security.refresh_from_db()
            db_token = str(round(9999999 * random()))[0:6]
            print(db_token)
            security.last_token= make_password(db_token)
            security.save()
            security_serializer_class = SecuritySerializer(security)
            data = {'status':'success','security':security_serializer_class.data}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        try:
            security = Security.objects.get(phone_number=request.data['phone_number'])
            digits = request.data['last_token']
            if check_password(digits, security.last_token):
                security.last_token = ''
                security.save()
                print('Password matched')
            else:
                print('Worng password')
            data = {'status':'success',}

        except ObjectDoesNotExist:

            data = {'status':'failed','description':'Invalid data',}
            
        return Response(data,status=status.HTTP_202_ACCEPTED)





class AllUserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()
    # authentication_classes =[TokenAuthentication,]

    def get(self,request):

        user = User.objects.all()
        user = UserSerializer(user,many = True )
        if len(user.data) > 0:
            return Response(user.data,status=status.HTTP_200_OK)

        return Response({'invalid_token':True},status=status.HTTP_400_BAD_REQUEST)



class UserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes =[TokenAuthentication,]

    def get(self,request):

        user = getuser(request)
        user = UserSerializer(user)
        if len(user.data) > 0:
            return Response(user.data,status=status.HTTP_200_OK)

        return Response({'invalid_token':True},status=status.HTTP_400_BAD_REQUEST)



class CreateUserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()

    def post(self,request):
        try:
            user = UserSerializer(User.objects.get(email = str(request.data['email']).lower()))
            return Response({'email_already_exist':True},status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.save()
                user = data[0]
                serialized_data = UserSerializer(user)
                # login(request,user)
                user= User.objects.get(email=user.email)
                
                token= data[1]
                # if len(token) > 0:
                #     token = token[0]
                # else:
                #     token=AuthToken.objects.create(user=user)
                #     token.refresh_from_db()

                security = Security.objects.get_or_create(user=user)[0]
                security_serializer_class = SecuritySerializer(security)
                db_token = str(round(9999999 * random()))[0:6]
                security.last_token= make_password(db_token)
                security.save()
                data = {'status':'success','6_digits':db_token,'token':token}

                message = """<p>Hi there!, <br> <br>Thank you for joing <b>Mango</>. <br> <br>
                <b>Use """ + db_token + """ as your activation code</b></p>"""
                subject = 'Mango - Account creation'
                sendmail([user.email],message,message,subject)
                return Response(data,status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error':'invalid data'},status=status.HTTP_400_BAD_REQUEST)


# class CreateUser(APIView):

#     queryset = User.objects.all()
#     serializer_class = UsersSerializer
#     authentication_classes = ()
#     permission_classes = ()


#     def get(self,request):
#         user = getuser(request)
#         try:
#             user = UsersSerializer(user)
#             data = {'status':'success','user':user.data}
#         except ObjectDoesNotExist:
#             data = {'user':''}
#         return Response(data,status=status.HTTP_202_ACCEPTED)


#     def post(self,request):
#         first_name = request.data['first_name']
#         last_name = request.data['last_name']
#         phone_number =request.GET.get('phone_number')
#         try:
#             security = Security.objects.get(phone_number=phone_number)
#             user = User.objects.create(first_name=first_name,last_name=last_name)
#             try:
#                 profile = Profile.objects.get(user=user)
#             except ObjectDoesNotExist:
#                 profile = Profile.objects.create(user=user)
#             try:
#                 wallet = Wallet.objects.get(user=user)
#             except ObjectDoesNotExist:
#                 wallet = Wallet.objects.create(user=user)
#             profile.security = security
#             profile.wallet=wallet
#             profile.save()
#             user_serializer_class = UsersSerializer(user)
#             login(request, user)
#             data = {'status':'success','user':user_serializer_class.data}
#         except ObjectDoesNotExist:
#             data = {'status':'failed','description':'Verify phone number',}
            
#         return Response(data,status=status.HTTP_202_ACCEPTED)




class SecurityView(APIView):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
            serializer_class = SecuritySerializer(instance=security, data=request.data)
        except ObjectDoesNotExist:
            serializer_class = SecuritySerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            security = serializer_class.instance
        serializer_class = SecuritySerializer(security)
        data = {'status':'success','security':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class UserTwoFactorEnableView(APIView):
    queryset = User.objects.all()
    serializer_class = UserTwoFactorSerializer

    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        user.set_password(request.data['password'])
        user.save()
        security.two_factor_auth_enabled = True
        security.save()
        login(request,user)
        serializer_class = SecuritySerializer(security)
        data = {'status':'success','security':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)

class UserTwoFactorDisableView(APIView):
    queryset = User.objects.all()
    serializer_class = UserTwoFactorSerializer


    def get(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        serializer_class = SecuritySerializer(security)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            security = Security.objects.get(user=user)
        except ObjectDoesNotExist:
            security = Security.objects.create(user=user)
        if check_password(request.data['password'], user.password):
            user.password=''
            user.save()
            security.two_factor_auth_enabled = False
            security.save()
            serializer_class = SecuritySerializer(security)
            login(request,user)

            data = {'status':'success','security':serializer_class.data}
        else:
            serializer_class = SecuritySerializer(security)
            security.save()
            if security.login_attempt_count == 3:
                logout(request)
            else:
                security.login_attempt_count +=1
                login(request,user)
            data = {'status':'failed','incorrect':True,'security':serializer_class.data}    
        return Response(data,status=status.HTTP_202_ACCEPTED)



class PictureView(APIView):
    queryset = Picture.objects.all()
    serializer_class = PicturesSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        picture = Picture.objects.filter(user=user,**filters)
        serializer_class = PicturesSerializer(picture,many = True)
        return Response({'pictures':serializer_class.data},status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)
        serializer_class = PicturesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            picture = serializer_class.instance
            picture.user=user
            try:
                picture.save()
                serializer_class = PicturesSerializer(picture)
                data = {'status':'success','picture':serializer_class.data}   
                res_status= status.HTTP_202_ACCEPTED         
            except Exception:
                picture.delete()
                data = {'status':'failed','err':'duplicate entry'}            
                res_status= status.HTTP_400_BAD_REQUEST
        return Response(data,status = res_status)


    def delete(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        try:
            picture = Picture.objects.get(**filters)
            picture.delete()
            data = {'status':'success'}
            res_status=status.HTTP_202_ACCEPTED

        except ObjectDoesNotExist:
            data = {'status':'failed'}
            res_status =status.HTTP_404_NOT_FOUND
        return Response(data,status=res_status)




class ProfileView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication]

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        serializer_class = ProfilesSerializer(profile)
        return Response(serializer_class.data)


    def post(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            serializer_class = ProfilesSerializer(instance=profile, data=request.data)
        except ObjectDoesNotExist:
            serializer_class = ProfilesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            profile = serializer_class.instance
        interests = request.POST.copy().getlist('interests')
        for interest in interests:
            interest_instance = Interest.objects.create(name = interest)
            profile.interests.add(interest_instance)
        serializer_class = ProfilesSerializer(profile)
        data = {'status':'success','profile':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)




class InterestsView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication]

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
            interests = profile.interests.all()
            serializer_class = InterestsSerializer(interests,many = True)
            return Response(serializer_class.data)
        except ObjectDoesNotExist:
            profile = ''
            return Response({'error':'profile does not exist'})


    def post(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            serializer_class = ProfilesSerializer(data=request.data)
            if serializer_class.is_valid():
                serializer_class.save()
                profile = serializer_class.instance
                profile.user = user
                profile.save()
        interests = request.POST.copy().getlist('interests')
        for interest in interests:
            interest_instance = Interest.objects.create(name = interest)
            profile.interests.add(interest_instance)
        profile.refresh_from_db()
        serializer_class = InterestsSerializer(profile.interests.all(),many= True)
        data = {'status':'success','interests':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class SwipeView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        all_mangos = list(Profile.objects.all())
        current_profile= list(filter(lambda x:x.user == user,all_mangos))[0]
        mangos = list(filter(lambda x:x.interested_in == current_profile.interested_in and x.id != current_profile.id ,all_mangos))
        page = request.GET.get('page')
        paginator = Paginator(mangos, 1)
        try:
            mangos = paginator.page(page)
        except PageNotAnInteger:
            mangos = paginator.page(1)
        except EmptyPage:
            mangos = paginator.page(paginator.num_pages)
        print(mangos.object_list)
        serializer_class = ProfilesSerializer(mangos.object_list,many=True)
        data = {'status':'success',
        'mangos':serializer_class.data,
        'has_next':mangos.has_next()}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class FilterSwipe(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        profiles = Profile.objects.filter(**filters)

        serializer_class = ProfilesSerializer(profiles,many=True)
        data = {'status':'success','profiles':serializer_class.data}

        return Response(data,status=status.HTTP_202_ACCEPTED)



class LikeUnlikeMango(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfilesSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        likedmangos = Profile.objects.filter(user__in=profile.liked_mangos.all())
        serializer_class = ProfilesSerializer(likedmangos,many=True)
        return Response(serializer_class.data)


    def post(self,request):
        action = request.data.get('action')
        mango_id= request.data.get('mango_id')
        user = getuser(request)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        try:
            mango = User.objects.get(id=mango_id)
        except ObjectDoesNotExist:
            return Response({'action':action,'success':False,},status=status.HTTP_404_NOT_FOUND)
        if action == 'like':
            profile.liked_mangos.add(mango)
        elif action == 'unlike':
            profile.liked_mangos.remove(mango)
        return Response({'action':action,'success':True},status=status.HTTP_202_ACCEPTED)



class ChatView(APIView):
    queryset = Chat.objects.all()
    serializer_class = ChatsSerializer
    authentication_classes =[TokenAuthentication,]

    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        chat = Chat.objects.filter(sender=user,**filters)
        serializer_class = ChatsSerializer(chat,many=True)
        return Response(serializer_class.data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)

        serializer_class = ChatsSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            chat = serializer_class.instance
            serializer_class = ChatsSerializer(chat)
            data = {'status':'success','chat':serializer_class.data}        
        else:
            data = {'status':'failed','error':'invalid data'}


        return Response(data,status=status.HTTP_202_ACCEPTED)


class ReplyView(APIView):
    queryset = Reply.objects.all()
    serializer_class = RepliesSerializer
    authentication_classes =[TokenAuthentication,]


    def get(self,request):
        user = getuser(request)
        filters = getfilters(request,exclude=[''],contain_words=['',])
        reply = Reply.objects.filter(**filters)
        serializer_class = RepliesSerializer(reply,many=True)
        return Response(serializer_class.data,status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        user = getuser(request)

        serializer_class = RepliesSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            reply = serializer_class.instance
        serializer_class = RepliesSerializer(reply)
        data = {'status':'success','reply':serializer_class.data}
        return Response(data,status=status.HTTP_202_ACCEPTED)


class ConfirmEmail(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    # def get(self,request):
    #     email =request.GET.get('email')
    #     try:
    #         user= User.objects.get(email=email)
    #         try:
    #             security = Security.objects.get(user=user)
    #             security_serializer_class = SecuritySerializer(security)
    #             db_token = str(round(9999999 * random()))[0:6]
    #             print(db_token)
    #             security.last_token= make_password(db_token)
    #             security.save()
    #             data = {'status':'success'}
                
    #         except ObjectDoesNotExist:
    #             security = Security.objects.create(user=user)
    #             security.refresh_from_db()
    #             db_token = str(round(9999999 * random()))[0:6]
    #             print(db_token)
    #             security.last_token= make_password(db_token)
    #             security.save()
    #             security_serializer_class = SecuritySerializer(security)
    #             data = {'status':'success'}
    #         # message = '<p><b>Use ' + db_token + ' as your verification code</b></p>'
    #         # subject = 'Password Change Request'
    #         # sendmail([user.email],message,message,subject)
    #         return Response(data,status=status.HTTP_202_ACCEPTED)
    #     except ObjectDoesNotExist:
    #         return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        verification_code = request.data.get('last_token')
        email = request.data.get('email')
        # '154914'
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                if check_password(verification_code,security.last_token):
                    user.set_password(request.data.get('secret_answer'))
                    user.save()
                    data = {'success':True}
                    security.last_toke = ''
                    security.save()
                    user.is_active = True
                    security.email_confirmed = True
                    user.save()
                    security.save()
                    login(request,user)
                else:
                    data= {'invalid_verification_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            except ObjectDoesNotExist:
                return Response({'invalid_request':True},status=status.HTTP_404_NOT_FOUND)


        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)

