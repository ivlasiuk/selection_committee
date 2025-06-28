from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    title = models.CharField(max_length=35)

    def __str__(self):
        return self.title


class Department(models.Model):
    title = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=11)
    dean = models.CharField(max_length=45)
    url_slug = models.CharField(max_length=10, unique=True)
    text = models.TextField(null=True)

    def __str__(self):
        return self.title


class Speciality(models.Model):
    title = models.CharField(max_length=70)
    subject1 = models.ManyToManyField(Subject, verbose_name=_('Перший предмет'), related_name='+')
    subject2 = models.ManyToManyField(Subject, verbose_name=_('Другий предмет'), related_name='+')
    subject3 = models.ManyToManyField(Subject, verbose_name=_('Третій предмет'), related_name='+')
    coefficient1 = models.FloatField()
    coefficient2 = models.FloatField()
    coefficient3 = models.FloatField()
    coefficient4 = models.FloatField()
    amount = models.IntegerField()
    budget_amount = models.IntegerField()
    department = models.ForeignKey(Department, verbose_name=_('Факультет'), on_delete=models.CASCADE)
    code = models.IntegerField(default=0)
    abit = models.ManyToManyField('AdmissionList', verbose_name=_('Заявки'), related_name='+', blank=True)

    def __str__(self):
        return str(self.code)


class Region(models.Model):
    region = models.CharField(max_length=30)

    def __str__(self):
        return self.region


class MyUserManager(BaseUserManager):
    def create_user(self, email, full_name, city, region, school, password=None):
        if not email:
            raise ValueError('Users must have an email')
        if not full_name:
            raise ValueError('Users must have a full name')
        if not city:
            raise ValueError('Users must have a city')
        if not region:
            raise ValueError('Users must have a region')
        if not school:
            raise ValueError('Users must have a school')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            city=city,
            region=region,
            school=school
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, city, region, school, password):
        user = self.create_user(
            email=self.normalize_email(email),
            full_name=full_name,
            city=city,
            region=region,
            school=school,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name=_('Електронна скриня'), unique=True, max_length=60, error_messages={
        'unique': _('Обліковий запис с таким email вже існує.')
    })
    full_name = models.CharField(verbose_name=_('ПІБ'), max_length=60)
    city = models.CharField(verbose_name=_('Місто'), max_length=20)
    region = models.ForeignKey(Region, verbose_name=_('Область'), on_delete=models.CASCADE)
    school = models.CharField(verbose_name=_('Назва навчального закладу'), max_length=60)
    rates = models.ImageField(verbose_name=_('Скан оцінок'), upload_to='static/img', blank=True)

    date_joined = models.DateTimeField(verbose_name=_('Дата регістрації'), auto_now_add=True)
    last_login = models.DateTimeField(verbose_name=_('Останній вхід'), auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'city', 'region', 'school']

    objects = MyUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class BidState(models.Model):
    value = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.value


class AdmissionList(models.Model):
    priority = models.IntegerField(default=1)
    state = models.ForeignKey(BidState, verbose_name=_('Стан'), default=1, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_('Абітурієнт'), on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, verbose_name=_('Спеціальність'), on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    firstRate = models.IntegerField(default=0)
    secondRate = models.IntegerField(default=0)
    thirdRate = models.IntegerField(default=0)
    avgRate = models.FloatField(default=0)
    summaryRate = models.FloatField(default=0)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name
