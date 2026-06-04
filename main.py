import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import VK_TOKEN, GROUP_ID
from extensions import CurrencyConverter, APIException

def main():
    # Инициализация бота
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
    vk = vk_session.get_api()

    # Доступные валюты
    AVAILABLE_CURRENCIES = {
        'USD': 'доллар',
        'EUR': 'евро',
        'RUB': 'рубль'
    }

    def send_message(user_id: int, message: str):
        """Отправка сообщения пользователю"""
        vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=0
        )

    def handle_message(text: str, user_id: int):
        """Обработка входящих сообщений"""
        text = text.strip().lower()

        # Команды помощи
        if text in ['/start', '/help']:
            help_text = (
                "🤖 **Помощник по конвертации валют**\n\n"
                "Отправьте сообщение в формате:\n"
                "<валюта1> <валюта2> <количество>\n\n"
                "Пример: евро доллар 100\n\n"
                "Доступные команды:\n"
                "/start или /help — показать эту справку\n"
                "/values — показать доступные валюты"
            )
            send_message(user_id, help_text)
            return

        # Команда вывода доступных валют
        elif text == '/values':
            values_text = "💱 **Доступные валюты:**\n"
            for code, name in AVAILABLE_CURRENCIES.items():
                values_text += f"- {name} ({code})\n"
            send_message(user_id, values_text)
            return

        # Обработка конвертации валют
        else:
            try:
                # Разбираем сообщение
                parts = text.split()
                if len(parts) != 3:
                    raise APIException("Неверный формат сообщения. Используйте: <валюта1> <валюта2> <количество>")

                base_name, quote_name, amount_str = parts

                # Конвертируем названия валют в коды
                base_code = None
                quote_code = None

                for code, name in AVAILABLE_CURRENCIES.items():
                    if name == base_name:
                        base_code = code
                    if name == quote_name:
                        quote_code = code

                if not base_code:
                    raise APIException(f"Валюта '{base_name}' не найдена")
                if not quote_code:
                    raise APIException(f"Валюта '{quote_name}' не найдена")

                # Парсим количество
                try:
                    amount = float(amount_str)
                    if amount <= 0:
                        raise APIException("Количество должно быть положительным числом")
                except ValueError:
                    raise APIException("Количество должно быть числом")

                # Получаем цену
                result = CurrencyConverter.get_price(base_code, quote_code, amount)

                # Форматируем ответ
                base_display = AVAILABLE_CURRENCIES[base_code]
                quote_display = AVAILABLE_CURRENCIES[quote_code]

                response_text = f"{amount} {base_display} = {result} {quote_display}"
                send_message(user_id, response_text)

            except APIException as e:
                send_message(user_id, f"❌ Ошибка: {str(e)}")
            except Exception as e:
                send_message(user_id, f"❌ Неожиданная ошибка: {str(e)}")

    print("Бот запущен...")

    # Основной цикл обработки сообщений
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message
            text = message['text']
            user_id = message['from_id']

            handle_message(text, user_id)

if __name__ == '__main__':
    main()
