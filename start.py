# -*- coding: utf-8 -*-

import config
from main import Bot

try:
    Bot(phone=config.number, token=config.token, admin_id=config.admin_id, qiwiApi=config.tokenQiwi)
except Exception as e:
    print(f'Произошла ошибка: {e}')