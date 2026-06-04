import requests
import json

class APIException(Exception):
    """Собственное исключение для ошибок API"""
    pass

class CurrencyConverter:
    """Класс для работы с конвертацией валют"""

    @staticmethod
    def get_price(base: str, quote: str, amount: float) -> float:
        """
        Статический метод для получения цены валюты

        Args:
            base (str): валюта, цену которой надо узнать
            quote (str): валюта, в которой надо узнать цену
            amount (float): количество переводимой валюты

        Returns:
            float: сумма в целевой валюте

        Raises:
            APIException: при ошибках конвертации
        """
        # Нормализуем входные данные
        base = base.upper()
        quote = quote.upper()

        # Проверяем, что валюты разные
        if base == quote:
            raise APIException("Нельзя конвертировать одну и ту же валюту")

        # Список доступных валют
        available_currencies = ['USD', 'EUR', 'RUB']

        if base not in available_currencies:
            raise APIException(f"Валюта {base} не поддерживается")
        if quote not in available_currencies:
            raise APIException(f"Валюта {quote} не поддерживается")

        try:
            # Получаем курсы валют
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base}")
            response.raise_for_status()  # Проверяем статус ответа

            data = json.loads(response.text)

            if 'rates' not in data:
                raise APIException("Ошибка при получении данных о курсах валют")

            rates = data['rates']

            if quote not in rates:
                raise APIException(f"Курс для валюты {quote} недоступен")

            rate = rates[quote]
            result = amount * rate

            return round(result, 2)

        except requests.exceptions.RequestException as e:
            raise APIException(f"Ошибка при запросе к API: {str(e)}")
        except json.JSONDecodeError as e:
            raise APIException(f"Ошибка при парсинге JSON: {str(e)}")
        except KeyError as e:
            raise APIException(f"Некорректный формат данных от API: {str(e)}")
