from django.forms import TextInput, Select, NumberInput
from django import forms
from .validators import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User, Region, AdmissionList


class AdmissionListForm(forms.ModelForm):
    class Meta:
        model = AdmissionList
        fields = ('firstRate', 'secondRate', 'thirdRate', 'avgRate', 'subject')
        widgets = {
            'firstRate': NumberInput(attrs={
                'class': 'form-control'
            }),
            'secondRate': NumberInput(attrs={
                'class': 'form-control'
            }),
            'thirdRate': NumberInput(attrs={
                'class': 'form-control'
            }),
            'avgRate': NumberInput(attrs={
                'class': 'form-control'
            }),
        }
        error_messages = {
            'subject': {'invalid_choice': _('Оберіть предмет на вибір.')}
        }

    def clean_firstRate(self):
        firstRate = self.cleaned_data['firstRate']
        if firstRate < 100:
            raise ValidationError(_('Мінімальний бал екзамену - 100.'))
        if firstRate > 200:
            raise ValidationError(_('Максимальний бал екзамену - 200.'))
        return firstRate

    def clean_secondRate(self):
        firstRate = self.cleaned_data['secondRate']
        if firstRate < 100:
            raise ValidationError(_('Мінімальний бал екзамену - 100.'))
        if firstRate > 200:
            raise ValidationError(_('Максимальний бал екзамену - 200.'))
        return firstRate

    def clean_thirdRate(self):
        firstRate = self.cleaned_data['thirdRate']
        if firstRate < 100:
            raise ValidationError(_('Мінімальний бал екзамену - 100.'))
        if firstRate > 200:
            raise ValidationError(_('Максимальний бал екзамену - 200.'))
        return firstRate

    def clean_avgRate(self):
        firstRate = self.cleaned_data['avgRate']
        if firstRate < 1:
            raise ValidationError(_('Середній бал атестату не може бути менше за 1.'))
        if firstRate > 12:
            raise ValidationError(_('Середній бал атестату не може бути більший за 12.'))
        return firstRate

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if subject == _('Оберіть...'):
            raise ValidationError(_('Оберіть предмет на вибір.'))
        return subject


class UserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _("Ваші паролі не співпадають."),
    }


class ChangePasswordForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password1.label = _('Новий пароль')
    password2.label = _('Підтвердіть пароль')

    class Meta:
        model = User
        fields = ('password1', 'password2')


class ResetPasswordEmail(forms.Form):
    email = forms.EmailField(max_length=60, widget=forms.EmailInput(attrs={'class': 'form-control'}),
                             error_messages={'invalid': _('Введіть коректний email.')})
    email.label = _('Ваша електронна скриня')


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    email.label = _('Електронна скриня')
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password.label = _('Пароль')


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text=_("Обов'язкове поле. Введіть коректні дані"),
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    email.label = _('Електронна скриня')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password1.label = _('Пароль')
    password2.label = _('Підтвердіть пароль')
    region = forms.ModelChoiceField(queryset=Region.objects.order_by('region'), label=_('Область'),
                                    widget=forms.Select(attrs={'class': 'form-control'}), empty_label='')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'full_name', 'city', 'region', 'school')
        widgets = {
            'full_name': TextInput(attrs={
                'class': 'form-control'
            }),
            'city': TextInput(attrs={
                'class': 'form-control'
            }),
            'region': Select(attrs={
                'class': 'form-control'
            }),
            'school': TextInput(attrs={
                'class': 'form-control'
            })
        }
