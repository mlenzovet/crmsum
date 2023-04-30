def add_test_customers_stub(token, api_url, customers_list):
    """
    Заглушка для функции, которая добавляет тестовых заказчиков через API AMOCRM.

    Параметры:
        token (str): Токен для аутентификации в API.
        api_url (str): URL-адрес API.
        customers_list (list): Список имен тестовых заказчиков, которых нужно добавить.

    Возвращает:
        list: Список добавленных тестовых заказчиков с их идентификаторами.
    """
    added_test_customers = []

    for i, customer_name in enumerate(customers_list):
        added_test_customers.append({'name': f"Тестовый {customer_name}", 'id': i + 1})

    return added_test_customers
