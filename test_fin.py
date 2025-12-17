from FinFlow_main import FinanceBot
import pytest


def test_init():
    """Позитивный тест инициализации"""
    bot = FinanceBot("test_token")
    assert bot.token == "test_token"
    assert bot.data == {}


def test_init_neg():
    """Негативный тест: инициализация с некорректным токеном"""
    # Проверяем, что бот создается даже с нестандартным токеном
    bot = FinanceBot(None)  # None вместо строки
    assert bot.token is None
    assert bot.data == {}


def test_add_dt():
    """Позитивный тест добавления данных"""
    bot = FinanceBot("test_token")
    bot.data["user1"] = []
    bot.data["user1"].append({"type": "income", "amount": 100, "category": "Тест1"})
    assert len(bot.data["user1"]) == 1
    assert bot.data["user1"][0]["amount"] == 100


def test_add_dt_neg():
    """Негативный тест: добавление без инициализации списка"""
    bot = FinanceBot("test_token")
    # Не создаем список для пользователя
    # Проверяем, что списка нет (KeyError при прямом доступе)
    assert "user1" not in bot.data
    # Это аналогично тесту очереди на пустую очередь


def test_calc():
    """Позитивный тест расчета"""
    bot = FinanceBot("test_token")
    bot.data = {
        "user1": [
            {"type": "income", "amount": 1000, "category": "Зарплата"},
            {"type": "expense", "amount": 500, "category": "Еда"}
        ]
    }
    user_id = "user1"
    income = sum(r['amount'] for r in bot.data[user_id] if r['type'] == 'income')
    expense = sum(r['amount'] for r in bot.data[user_id] if r['type'] == 'expense')
    assert income == 1000
    assert expense == 500


def test_calc_neg():
    """Негативный тест: расчет для несуществующего пользователя"""
    bot = FinanceBot("test_token")
    bot.data = {}  # Пустые данные, нет пользователей
    try:
        user_id = "ghost_user"
        # Прямой доступ к несуществующему ключу
        transactions = bot.data[user_id]
        # Если дошли сюда - тест должен упасть
        assert False, "Ожидался KeyError!"
    except KeyError:
        # Это ожидаемое поведение - пользователя нет
        assert True