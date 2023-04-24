from django.core.exceptions import ValidationError


def validate_amount(value):
    if value <= 0:
        raise ValidationError(
            'Коичество ингредиентов не может быть меньше/равным: %(value)s',
            params={'value': value}
        )
