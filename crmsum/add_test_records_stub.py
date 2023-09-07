def add_test_records_stub(token, api_url, test_records_data):
    """
    Заглушка для функции, которая добавляет тестовые записи в карточку тестового заказчика
    от имени тестового менеджера через API AMOCRM.

    Параметры:
        token (str): Токен для аутентификации в API.
        api_url (str): URL-адрес API.
        test_records_data (list): Список словарей с данными тестовых записей.

    Возвращает:
        list: Список добавленных тестовых записей с их идентификаторами.
    """
    added_test_records = []

    for i, record_data in enumerate(test_records_data):
        added_test_records.append({'data': record_data, 'id': i + 1})

    return added_test_records

