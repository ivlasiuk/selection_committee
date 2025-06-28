from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.registration, name='registration'),
    path('logout', views.log_out, name='logout'),
    path('login/', views.log_in, name='login'),
    path('login/', views.log_in, name='/accounts/login/'),
    path('account/password_recovery', views.password_reset, name='password-recovery'),
    path('reset/<uidb64>/<token>/', views.new_pass, name='password_reset_confirm'),
    path('departments/', views.department, name='departments'),
    path('departments/<dep>', views.some_dep, name='some_dep'),
    path('departments/<dep>/<spec>', views.speciality, name='spec'),
    path('myapplications', views.my_applications, name='appls'),
    path('myrates', views.my_rates, name='scan')
]
