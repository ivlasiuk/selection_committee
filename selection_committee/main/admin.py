from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import *
from django.contrib.auth.models import Group
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _


class BidStateAdmin(TranslationAdmin):
    list_display = ('id', 'value',)


@admin.action(description=_('Підтвердити заявки'))
def check_adm_list(model, request, qs):
    for row in qs:
        row.is_approved = True
        row.save()


class AdmissionListAdmin(admin.ModelAdmin):
    list_display = ('speciality', 'user', 'firstRate', 'secondRate', 'thirdRate', 'avgRate', 'is_approved', 'state')
    list_display_links = ('speciality', 'user')
    search_fields = ('speciality__code', 'user__full_name')
    actions = [check_adm_list]


class SpecialityAdmin(TranslationAdmin):
    list_display = ('code', 'title', 'amount', 'budget_amount')
    list_display_links = ('code', 'title')

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        if request.POST:
            if AdmissionList.objects.filter(state=BidState(id=2)):
                extra_context['is_finalized'] = False
                for row in AdmissionList.objects.all():
                    row.state = BidState(id=1)
                    row.save()
            else:
                extra_context['is_finalized'] = True
                subject = 'Ви прийняті на бюджетну форму навчання!'
                email_template_name = 'main/grats_email.txt'
                # loop for every priority
                for i in range(5):
                    while True:
                        is_over = True
                        for row in Speciality.objects.all():
                            spec_min = AdmissionList.objects.filter(speciality=row,
                                                                    is_approved=True,
                                                                    state=BidState(id=1)).order_by('-summaryRate')[
                                       :row.budget_amount - len(
                                           AdmissionList.objects.filter(speciality=row, state=BidState(id=2)))]
                            if spec_min.first() is not None:
                                print(row.title)
                                spec_min_rate = spec_min[len(spec_min) - 1].summaryRate
                                print(spec_min_rate)
                                prior = AdmissionList.objects.filter(speciality=row, is_approved=True, priority=i + 1,
                                                                     state=BidState(id=1)).order_by(
                                    '-summaryRate')[:row.budget_amount - len(AdmissionList.objects.filter(speciality=row,
                                                                                                          state=BidState(
                                                                                                              id=2)))]
                                for col in prior:
                                    if col.summaryRate >= spec_min_rate:
                                        col.state = BidState(id=2)
                                        col.save()
                                        c = {
                                            'fullname': col.user.full_name,
                                            'form': 'бюджетну',
                                            'dep': col.speciality.department
                                        }
                                        mail = render_to_string(email_template_name, c)
                                        send_mail(subject, mail, None, [col.user.email], fail_silently=False)
                                        for bid in AdmissionList.objects.filter(is_approved=True, user=col.user,
                                                                                state=BidState(id=1)):
                                            bid.state = BidState(id=4)
                                            bid.save()
                                        is_over = False
                        if is_over:
                            break
                subject = 'Ви прийняті на контрактну форму навчання!'
                for i in range(5):
                    while True:
                        is_over = True
                        for row in Speciality.objects.all():
                            spec_min = AdmissionList.objects.filter(speciality=row,
                                                                    is_approved=True,
                                                                    state=BidState(id=1)).order_by(
                                '-summaryRate')[:row.amount - row.budget_amount -
                                                 len(AdmissionList.objects.filter(speciality=row, state=BidState(id=3)))]
                            if spec_min.first() is not None:
                                spec_min_rate = spec_min[len(spec_min) - 1].summaryRate
                                prior = AdmissionList.objects.filter(speciality=row,
                                                                     state=BidState(id=1),
                                                                     is_approved=True,
                                                                     priority=i + 1).order_by(
                                    '-summaryRate')[:row.amount - row.budget_amount -
                                                     len(AdmissionList.objects.filter(speciality=row,
                                                                                      state=BidState(id=3)))]
                                for col in prior:
                                    if col.summaryRate >= spec_min_rate:
                                        col.state = BidState(id=3)
                                        col.save()
                                        c = {
                                            'fullname': col.user.full_name,
                                            'form': 'контрактну',
                                            'dep': col.speciality.department
                                        }
                                        mail = render_to_string(email_template_name, c)
                                        send_mail(subject, mail, None, [col.user.email], fail_silently=False)
                                        for bid in AdmissionList.objects.filter(is_approved=True, user=col.user,
                                                                                state=BidState(id=1)):
                                            bid.state = BidState(id=4)
                                            bid.save()
                                        is_over = False
                        if is_over:
                            break
                for row in AdmissionList.objects.filter(is_approved=True, state=BidState(id=1)):
                    row.state = BidState(id=5)
                    row.save()
            return super(SpecialityAdmin, self).changelist_view(request, extra_context)
        if AdmissionList.objects.filter(state=BidState(id=2)):
            extra_context['is_finalized'] = True
            return super(SpecialityAdmin, self).changelist_view(request, extra_context)
        else:
            return super(SpecialityAdmin, self).changelist_view(request, {'is_finalized': False})


class SubjectAdmin(TranslationAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


class DepartmentAdmin(TranslationAdmin):
    list_display = ('id', 'abbreviation', 'title', 'dean')
    list_display_links = ('id', 'abbreviation', 'title')


class RegionAdmin(TranslationAdmin):
    list_display = ('id', 'region',)
    ordering = ('region',)
    list_display_links = ('id', 'region',)


class MyUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'city', 'date_joined', 'last_login', 'is_active', 'is_admin')
    search_fields = ('email', 'full_name', 'city')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password', 'full_name', 'city', 'region', 'school', 'rates',
                           'date_joined', 'last_login', 'is_active', 'is_admin',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'full_name', 'city', 'region', 'school', 'rates')}),
    )
    ordering = ('email',)
    filter_horizontal = ()
    list_filter = ()


admin.site.register(User, MyUserAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(AdmissionList, AdmissionListAdmin)
admin.site.register(BidState, BidStateAdmin)
admin.site.register(Speciality, SpecialityAdmin)
admin.site.unregister(Group)
