from FinFlow_main import FinanceBot
import os
import json

def test_init_positive_valid_token():
    """Тест 1: Инициализация с валидным токеном"""
    test_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    bot = FinanceBot(test_token)
    assert bot.token == test_token


def test_init_negative_none_token():
    """Негативный тест 1: Инициализация с None вместо токена"""
    bot = FinanceBot(None)
    assert bot.token is None


def test_load_data_returns_dict():
    """Тест 2: проверяем что load_data() возвращает словарь"""
    bot = FinanceBot("test_token")
    result = bot.load_data()
    assert isinstance(result, dict)

def test_load_data_returns_list():
    """Негативный тест 2: проверяем что load_data() НЕ словарь """
    bot = FinanceBot("test_token")
    result = bot.load_data()
    assert not isinstance(result, list)


def test_save_data_positive():
    """Тест 3: сохраняем нормальные данные"""
    bot = FinanceBot("test_token")
    bot.data = {
        "user123": [
            {"type": "income", "amount": 1000, "category": "Зарплата"}
        ]
    }
    bot.save_data()
    assert os.path.exists("data.json")
    with open("data.json", "r", encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data == bot.data


def test_save_data_empty_dict():
    """Негативный тест: сохраняем пустые данные"""
    bot = FinanceBot("test_token")
    bot.data = {}
    bot.save_data()
    assert os.path.exists("data.json")
    with open("data.json", "r", encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data == {}