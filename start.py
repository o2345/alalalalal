import config
from main import Bot

try:
    Bot(token=config.token)
except Exception as e:
    print(f'Произошла ошибка: {e}')