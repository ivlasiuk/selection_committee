import math
import os

from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN
from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import User, Department, Speciality, AdmissionList, BidState
from verify_email.email_handler import send_verification_email
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm, ResetPasswordEmail, ChangePasswordForm, AdmissionListForm
from verify_email import models
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)


def my_rates(request):
    if request.POST:
        if 'deleter' in request.POST:
            if request.user.rates:
                logger.info('користувач видалив свій скан атестату')
                os.remove(str(request.user.rates))
            request.user.rates = None
            request.user.save()
        elif 'changer' in request.POST:
            if request.FILES:
                request.user.rates = request.FILES['file']
                request.user.save()
                logger.info('користувач додав скан атестату')
    logger.debug('відкрито сторінку зі сканом атестату')
    return render(request, 'main/rates.html', {'img': str(request.user.rates)[7:]})


def my_applications(request):
    logger.debug('відкрито сторінку свої заяв')
    bids = AdmissionList.objects.filter(user=request.user.id)
    if len(bids) == 0:
        return render(request, 'main/applications.html', {'is_empty': True})
    else:
        return render(request, 'main/applications.html', {'bids': bids})


def speciality(request, dep, spec):
    if request.POST:
        form = AdmissionListForm(request.POST)
        bids = AdmissionList.objects.filter(
            speciality=Speciality.objects.get(code=spec, department=Department.objects.filter(url_slug=dep)[0].id),
            is_approved=True)
        if form.is_valid():
            bidss = AdmissionList.objects.filter(user=request.user.id)
            special = Speciality.objects.get(code=spec, department=Department.objects.filter(url_slug=dep)[0].id)
            summary = round((special.coefficient1 * form.cleaned_data.get('firstRate') +
                             special.coefficient2 * form.cleaned_data.get('secondRate') +
                             special.coefficient3 * form.cleaned_data.get('thirdRate') +
                             special.coefficient4 * form.cleaned_data.get('avgRate') * 1.667 * 10), 2)
            summary = 200 if summary > 200 else summary
            AdmissionList.objects.create(user=request.user, speciality=special,
                                         subject=form.cleaned_data.get('subject'),
                                         firstRate=form.cleaned_data.get('firstRate'),
                                         secondRate=form.cleaned_data.get('secondRate'),
                                         thirdRate=form.cleaned_data.get('thirdRate'),
                                         avgRate=form.cleaned_data.get('avgRate'),
                                         summaryRate=summary,
                                         priority=len(bidss) + 1)
            logger.info('створено заяву')
            spec = list(Speciality.objects.filter(code=spec, department=Department.objects.filter(url_slug=dep)[0]))
            return render(request, 'main/spec.html', {'form': AdmissionListForm(), 'is_ok': True, 'double': True,
                                                      'spec': spec[0], 'bids': bids})
        else:
            spec = list(Speciality.objects.filter(code=spec, department=Department.objects.filter(url_slug=dep)[0]))
            return render(request, 'main/spec.html', {'form': form, 'error': True, 'spec': spec[0], 'bids': bids})
    else:
        logger.debug('відкрито сторінку спеціальності')
        if Department.objects.filter(url_slug=dep).exists():
            if Speciality.objects.filter(code=spec, department=Department.objects.filter(url_slug=dep)[0].id):
                bids = AdmissionList.objects.filter(speciality=Speciality.objects.get(code=spec, department=Department.objects.filter(url_slug=dep)[0].id), is_approved=True)
                speclist = list(Speciality.objects.filter(code=spec, department=Department.objects.filter(url_slug=dep)[0]))
                if AdmissionList.objects.filter(state=BidState(id=2)):
                    return render(request, 'main/spec.html',
                                  {'spec': speclist[0], 'bids': bids, 'isFinal': True})
                if request.user.is_authenticated:
                    if AdmissionList.objects.filter(speciality=Speciality.objects.get(code=spec, department=
                                                    Department.objects.filter(url_slug=dep)[0].id), user=request.user):
                        return render(request, 'main/spec.html',
                                      {'form': AdmissionListForm(), 'double': True, 'spec': speclist[0], 'bids': bids})
                    if len(AdmissionList.objects.filter(user=request.user)) == 5:
                        return render(request, 'main/spec.html', {'form': AdmissionListForm(),
                                                                  'limit': True, 'spec': speclist[0], 'bids': bids})
                return render(request, 'main/spec.html', {'is_404': False, 'spec': speclist[0],
                                                          'form': AdmissionListForm(), 'bids': bids})
        return render(request, 'main/spec.html', {'is_404': True})


def some_dep(request, dep):
    if Department.objects.filter(url_slug=dep).exists():
        logger.debug('відкрито сторінку факультету: ' + str(Department.objects.get(url_slug=dep)))
        return render(request, 'main/some_dep.html', {'department': Department.objects.filter(url_slug=dep)[0],
                                                      'is_404': False,
                                                      'spec': Speciality.objects.filter(
                                                          department=Department.objects.filter(url_slug=dep)[0].id)})
    logger.info('не знайдено факультет: ' + str(dep))
    return render(request, 'main/some_dep.html', {'is_404': True})


def department(request):
    object_list = Department.objects.all()
    obj_per_page = 6
    pages = [i + 1 for i in range(math.ceil(len(object_list) / obj_per_page))]
    paginator = Paginator(object_list, obj_per_page)
    page = request.GET.get('page')
    try:
        departments = paginator.page(page)
    except PageNotAnInteger:
        departments = paginator.page(1)
    except EmptyPage:
        departments = paginator.page(paginator.num_pages)
        logger.debug('відкрито сторінку факультетів')
    return render(request, 'main/departments.html', {'page': page, 'departments': departments,
                                                     'spec': Speciality.objects.order_by('code'),
                                                     'pages': pages, 'has_next': departments.has_next(),
                                                     'has_prev': departments.has_previous()})


def new_pass(request, *args, **kwargs):
    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password1')
            user = User.objects.get(email=urlsafe_base64_decode(kwargs['uidb64']).decode())
            user.set_password(password)
            user.save()
            logger.debug('змінено пароль')
            return render(request, 'main/password-change-done.html')
        else:
            return render(request, 'main/password-reset-confirm.html', {'change_password_form': form})
    else:
        logger.debug('відкрито сторінку зміни паролю')
        try:
            uid = urlsafe_base64_decode(kwargs['uidb64']).decode()
        except(
            TypeError,
            ValueError,
            OverflowError,
        ):
            uid = None
        if User.objects.filter(email=uid).exists():
            token = kwargs['token']
            if token == 'set-password':
                session_token = request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if default_token_generator.check_token(User.objects.filter(email=uid)[0], session_token):
                    return render(request, 'main/password-reset-confirm.html',
                                  {'change_password_form': ChangePasswordForm()})
            else:
                if default_token_generator.check_token(User.objects.filter(email=uid)[0], token):
                    request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = request.path.replace(token, 'set-password')
                    return HttpResponseRedirect(redirect_url)
    return render(request, 'main/reset_url_used.html')


def password_reset(request):
    context = {}
    if request.user.is_authenticated:
        logger.info('Авторизований користувач намагався відкрити сторінку відновлення паролю')
        return redirect('home')
    if request.POST:
        logger.debug('відправлено запит для відновлення паролю')
        form = ResetPasswordEmail(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                subject = 'Password Reset Requested'
                email_template_name = 'main/reser_email.txt'
                c = {
                    'email': email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'Selection Committee',
                    'uid': urlsafe_base64_encode(force_bytes(email)),
                    'user': User.objects.filter(email=email),
                    'token': default_token_generator.make_token(User.objects.filter(email=email)[0]),
                    'protocol': 'http',
                }
                mail = render_to_string(email_template_name, c)
                send_mail(subject, mail, None, [email], fail_silently=False)
                logger.debug('відправлено лист для зміни паролю')
                return render(request, 'main/password-reset-done.html')
            else:
                context['password_reset_form'] = form
                context['error'] = True
                return render(request, 'main/password-reset.html', context)
        else:
            context['password_reset_form'] = form
    else:
        logger.debug('відкрито сторінку відновлення паролю')
        form = ResetPasswordEmail()
        context['password_reset_form'] = form
    return render(request, 'main/password-reset.html', context)


def index(request):
    logger.debug('відкрито головну сторінку')
    return render(request, 'main/layout.html')


def log_in(request):
    context = {}
    if request.user.is_authenticated:
        logger.info('Авторизований користувач намагався відкрити сторінку авторизації')
        return redirect('home')
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            logger.debug('спроба авторизації')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            account = authenticate(email=email, password=password)
            if account is not None:
                if account.is_active:
                    logger.debug('вдала спроба авторизації')
                    login(request, account)
                    return redirect('home')
                else:
                    if models.LinkCounter.objects.filter(requester=account.id).exists():
                        logger.debug('спроба авторизації при не підтвердженому email')
                        return render(request, 'main/login.html', {'login_form': LoginForm(), 'verify': True})
                    else:
                        logger.debug('спроба авторизації при бані')
                        return render(request, 'main/login.html', {'login_form': LoginForm(), 'is_banned': True})
            else:
                return render(request, 'main/login.html', {'login_form': LoginForm(), 'invalid_login': True})
        else:
            context['login_form'] = form
    else:
        logger.debug('відкрито сторінку авторизації')
        form = LoginForm()
        context['login_form'] = form
    return render(request, 'main/login.html', context)


def registration(request):
    context = {}
    if request.user.is_authenticated:
        logger.info('Авторизований користувач намагався відкрити сторінку реєстрації')
        return redirect('home')
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            inactive_user = send_verification_email(request, form)
            logger.info('відправлено лист верифікації на пошту')
            logger.debug('користувач створив обліковий запис в системі')
            return render(request, 'main/reg.html', {'registration_form': RegistrationForm(), 'lolka': 'lolka'})
        else:
            context['registration_form'] = form
    else:
        logger.debug('відкрито сторінку реєстрації')
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'main/reg.html', context)


def log_out(request):
    logger.debug('Користувач вийшов з системи')
    logout(request)
    return redirect('home')
