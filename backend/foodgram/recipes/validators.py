from django.core.exceptions import ValidationError


def validate_amount(value):
    if value <= 0:
        raise ValidationError(
        'Количество ингредиентов не может быть меньше или равно нулю.',
            params={'value', value}
        )
