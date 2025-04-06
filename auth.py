
# Простая авторизация (скелет)
users = {"admin": {"password": "admin123", "plan": "pro"}}
def check_login(username, password):
    return users.get(username, {}).get("password") == password
