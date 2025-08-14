# my-nalog

<img src="https://img.shields.io/pypi/v/my-nalog?style=flat-square" alt="PyPI version"> 
<img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">

Python клиент для работы с API сервиса "Мой Налог" (lknpd.nalog.ru)

## 🔥 Основные возможности

- Авторизация по SMS или логину/паролю

- Создание чеков (приходных ордеров)

- Получение ссылок на печатные формы

- Сохранение сессии между запусками

## 📦 Установка

```bash
pip install my-nalog
```

## 🚀 Пример использования
```python
from my_nalog import NalogRuAPI

api = NalogRuAPI()
api.auth_by_sms("79991234567")
user = api.verify_sms("123456", "...") 

receipt = api.create_receipt(100.50, "Услуги")
print(f"Ссылка на чек: {receipt.link}")
```
## 📚 Подробная документация
Полная документация и исходный код доступны в [GitHub репозитории](https://github.com/S1qwy/my-nalog/).