from modeltranslation.translator import translator, TranslationOptions
from .models import Region, Subject, BidState, Department, Speciality


class RegionTranslationOptions(TranslationOptions):
    fields = ('region',)


class SubjectTranslationOptions(TranslationOptions):
    fields = ('title',)


class BidStateTranslationOptions(TranslationOptions):
    fields = ('value',)


class DepartmentTranslationOptions(TranslationOptions):
    fields = ('title', 'abbreviation', 'dean', 'text')


class SpecialityTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(Region, RegionTranslationOptions)
translator.register(Subject, SubjectTranslationOptions)
translator.register(BidState, BidStateTranslationOptions)
translator.register(Department, DepartmentTranslationOptions)
translator.register(Speciality, SpecialityTranslationOptions)
