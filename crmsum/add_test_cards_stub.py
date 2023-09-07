def add_test_cards_stub(token, api_url, test_cards_data):
    """
    Заглушка для функции, которая добавляет тестовые карточки через API AMOCRM.

    Параметры:
        token (str): Токен для аутентификации в API.
        api_url (str): URL-адрес API.
        test_cards_data (list): Список словарей с данными тестовых карточек.

    Возвращает:
        list: Список добавленных тестовых карточек с их идентификаторами.
    """
    added_test_cards = []

    for i, card_data in enumerate(test_cards_data):
        added_test_cards.append({'data': card_data, 'id': i + 1})

    return added_test_cards
