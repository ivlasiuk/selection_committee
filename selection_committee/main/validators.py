from difflib import SequenceMatcher
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import MinimumLengthValidator, UserAttributeSimilarityValidator, \
    exceeds_maximum_length_ratio, CommonPasswordValidator, NumericPasswordValidator
from django.core.exceptions import ValidationError, FieldDoesNotExist
import re


class MinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError('Мінімальна довжина паролю - 8 символів.', code='password_too_short',
                                  params={'min_length': self.min_length})


class UserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    try:
                        verbose_name = str(
                            user._meta.get_field(attribute_name).verbose_name
                        )
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("Пароль дуже схожий на '%(verbose_name)s'."),
                        code="password_too_similar",
                        params={"verbose_name": verbose_name},
                    )


class CommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Цей пароль занадто простий."),
                code="password_too_common",
            )


class NumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Пароль не може складатися лише з цифр."),
                code="password_entirely_numeric",
            )
