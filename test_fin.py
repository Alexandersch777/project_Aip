from FinFlow_main import FinanceBot
from unittest.mock import patch


def test_init():
    with patch('os.path.exists', return_value=False):
        bot = FinanceBot("test_token")
        assert bot.token == "test_token"
        assert bot.data == {}


def test_init_neg():
    with patch('os.path.exists', return_value=False):
        bot = FinanceBot(None)
        assert bot.token is None
        assert bot.data == {}


def test_add_data():
    with patch('os.path.exists', return_value=False):
        bot = FinanceBot("test_token")
    bot.data["user1"] = []
    bot.data["user1"].append({"type": "income", "amount": 100,
                              "category": "Тест1"})
    bot.data["user1"].append({"type": "expense", "amount": 50,
                              "category": "Тест2"})

    assert len(bot.data["user1"]) == 2
    assert bot.data["user1"][0]["amount"] == 100
    assert bot.data["user1"][1]["amount"] == 50


def test_calculate():

    with patch('os.path.exists', return_value=False):
        bot = FinanceBot("test_token")
    bot.data = {
        "user1": [
            {"type": "income", "amount": 1000, "category": "Зарплата"},
            {"type": "expense", "amount": 500, "category": "Еда"},
            {"type": "income", "amount": 200, "category": "Премия"}
        ]
    }
    user_id = "user1"
    income = sum(r['amount'] for r in bot.data[user_id]
                 if r['type'] == 'income')
    expense = sum(r['amount'] for r in bot.data[user_id]
                  if r['type'] == 'expense')

    assert income == 1200
    assert expense == 500


def test_calculate_empty():
    with patch('os.path.exists', return_value=False):
        bot = FinanceBot("test_token")

    bot.data = {}

    assert "user999" not in bot.data


def test_calculate_wrong_type():
    with patch('os.path.exists', return_value=False):
        bot = FinanceBot("test_token")

    bot.data = {
        "user1": [
            {"type": "unknown", "amount": 100, "category": "Тест"}
        ]
    }

    user_id = "user1"

    income = sum(r['amount'] for r in bot.data[user_id]
                 if r['type'] == 'income')
    expense = sum(r['amount'] for r in bot.data[user_id]
                  if r['type'] == 'expense')

    assert income == 0
    assert expense == 0
