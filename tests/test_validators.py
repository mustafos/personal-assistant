import pytest

from assistant.utils.validators import is_valid_email, is_valid_phone


# Тест: правильні номери в E.164, пробіли і дефіси ігноруються.
@pytest.mark.parametrize(
    "phone",
    [
        "+380671234567",
        "+380 67 123 45 67",
        "+380-67-123-45-67",
        "+12345678",  # мінімум: 8 цифр
        "+123456789012345",  # максимум: 15 цифр
    ],
)
def test_valid_phone_numbers(phone):
    assert is_valid_phone(phone) is True


# Тест: некоректні номери мають бути відхилені.
@pytest.mark.parametrize(
    "phone",
    [
        "380671234567",  # немає знака +
        "+1234567",  # лише 7 цифр, занадто коротко
        "+1234567890123456",  # 16 цифр, занадто довго
        "+38abc1234567",  # літери
        "++380671234567",  # подвійний +
        "+38 (067) 123",  # дужки не дозволені правилом
        "",  # порожній рядок
        "   ",  # лише пробіли
    ],
)
def test_invalid_phone_numbers(phone):
    assert is_valid_phone(phone) is False


# Тест: якщо на вхід прийшло не рядок, має бути TypeError.
def test_phone_must_be_string():
    with pytest.raises(TypeError):
        is_valid_phone(380671234567)


# Тест: коректні адреси мають проходити.
@pytest.mark.parametrize(
    "email",
    [
        "ada@example.com",
        "ivan_petrenko@example.ua",
        "anna-maria@mail.example.com",
        "ada+news@example.com",
        "  ada@example.com  ",  # пробіли по краях прибираються
    ],
)
def test_valid_email_addresses(email):
    assert is_valid_email(email) is True


# Тест: некоректні адреси мають бути відхилені.
@pytest.mark.parametrize(
    "email",
    [
        "ada.example.com",  # немає @
        "@example.com",  # немає локальної частини
        "ada@",  # немає домену
        "ada@example",  # немає зони з крапкою
        "ada@example.c",  # зона з однієї літери
        "ada smith@example.com",  # пробіл всередині
        "",  # порожній рядок
    ],
)
def test_invalid_email_addresses(email):
    assert is_valid_email(email) is False


# Тест: на вхід не рядок має бути TypeError.
def test_email_must_be_string():
    with pytest.raises(TypeError):
        is_valid_email(None)
