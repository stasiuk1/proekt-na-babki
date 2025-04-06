
# Оплата через Stripe (скелет)
# Использовать Flask-Stripe webhook в продакшене
def charge_user(user_id, amount):
    print(f"Чарджинг {user_id} на {amount}$")
