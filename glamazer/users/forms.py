import string
import random
import os
import shutil
import base64
import re

from io import BytesIO
from PIL import Image

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from glamazer.users.models import Profile
from glamazer.core.helpers import get_object_or_None
from glamazer.settings import MEDIA_FOLDER, MEDIA_ROOT


class ProfileForm(ModelForm):

    name = forms.CharField(required=True, widget=forms.TextInput())
    email = forms.EmailField(required=True, widget=forms.TextInput())
    password = forms.CharField(widget=(forms.PasswordInput()))
    confirm_password = forms.CharField(widget=(forms.PasswordInput()))

    class Meta:
        model = Profile
        fields = ['confirm_password', ]

    def clean_email(self):

        email = self.cleaned_data['email']

        check_email = get_object_or_None(User, email=email)

        if check_email and get_object_or_None(Profile, user=check_email, auto_created=True):
            raise forms.ValidationError(
                _("A user associated with this email address already exists"))

        return email

    def clean_password(self):

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if not password == confirm_password:
            raise forms.ValidationError(_("Password mismatch"))

        elif len(password) < 6:
            raise forms.ValidationError(_("Password is too short (6 symbols)"))

        elif password.isalpha() or password.isdigit():
            raise forms.ValidationError(_("Password should contain at least one alphabetic and one non-alphabetic character"))

        return password

    def save(self):

        data = self.cleaned_data

        check_email = get_object_or_None(User, email=data['email'])

        if not check_email:
            username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))

            new_user = User.objects.create_user(username=username,
                                                first_name=data['name'],
                                                email=data['email'],
                                                password=data['password'],
                                                related_with="profiles")
            profile = Profile.objects.create(user=new_user)
        else:
            check_email.first_name = data['name']
            check_email.set_password(data['password'])
            check_email.save()

            profile = Profile.objects.get(user=check_email)
            profile.auto_created = False
            profile.save()

        return profile


class LoginUserForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput())
    password = forms.CharField(
        required=True, widget=forms.PasswordInput(render_value=False))
    remember_me = forms.BooleanField(required=False)

    def clean(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user and user.is_active:
                return self.cleaned_data

        raise forms.ValidationError("Invalid login details")


class ChangePasswordForm(forms.Form):

    new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        render_value=False))
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(
        render_value=False))

    def clean(self):

        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError(_("Password mismatch"))

        return self.cleaned_data


class ForgottenPasswordForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput())


class EditProfile(ModelForm):

    name = forms.CharField(required=True, widget=forms.TextInput())
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    cropped_image = forms.CharField(required=False, widget=forms.HiddenInput())
    mobile_number = forms.CharField(required=False, widget=forms.TextInput())
    enable_emails = forms.BooleanField(required=False)
    enable_sms = forms.BooleanField(required=False)

    class Meta:
        model = Profile
        exclude = ('user',)

    def clean_enable_sms(self):
        profile = self.instance
        enable_sms = self.cleaned_data.get('enable_sms')
        if enable_sms and not (profile.mobile_number or self.cleaned_data.get('mobile_number')):
            raise forms.ValidationError(_("Please enter your phone in order to receive sms."))

        return enable_sms

    def save(self):

        profile = self.instance
        user = profile.user
        data = self.cleaned_data

        user.first_name = data['name']
        user.save()
        profile.mobile_number = data['mobile_number']
        profile.enable_emails = data['enable_emails']
        profile.enable_sms = data['enable_sms']
        profile.save()

        my_file = data['cropped_image']

        if my_file:

            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(my_file).group(2)

            hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
            path = '/' + MEDIA_FOLDER + '/users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
            full_path = MEDIA_ROOT + 'users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
            profile.avatar = path
            profile.save()

            #if the folder doesn't exist, create one
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)
            else:
                shutil.rmtree(d)
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file)))
            im.save(full_path, 'JPEG')

        return profile
