def add_test_managers_stub(token, api_url, managers_list):
    """
    Заглушка для функции, которая добавляет тестовых менеджеров через API AMOCRM.

    Параметры:
        token (str): Токен для аутентификации в API.
        api_url (str): URL-адрес API.
        managers_list (list): Список имен тестовых менеджеров, которых нужно добавить.

    Возвращает:
        list: Список добавленных тестовых менеджеров с их идентификаторами.
    """
    added_test_managers = []

    for i, manager_name in enumerate(managers_list):
        added_test_managers.append({'name': f"Тестовый {manager_name}", 'id': i + 1})

    return added_test_managers