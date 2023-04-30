# __init__.py

from .find_manager_name import find_manager_name
from .find_customer_name import find_customer_name
from .find_date_range import find_date_range
from .get_records_data import get_records_data
from .summarize_records_texts import summarize_records_texts

__all__ = ['find_manager_name', 'find_customer_name', 'find_date_range', 'get_records_data', 'summarize_records_texts']

# Тестовые функции
from .generate_test_queries import generate_test_queries
from .add_test_managers_stub import add_test_managers_stub
from .add_test_customers_stub import add_test_customers_stub
from .add_test_cards_stub import add_test_cards_stub  
from .add_test_records_stub import add_test_records_stub
from .generate_test_managers_stub import generate_test_managers_stub
from .generate_test_customers_stub import generate_test_customers_stub

__all__ += ['generate_test_queries', 'add_test_managers_stub', 'add_test_customers_stub', 'add_test_cards_stub', 'add_test_records_stub', 'generate_test_managers_stub', 'generate_test_customers_stub']


'''
Продакшн функции:

find_manager_name: принимает на вход текстовую строку и список менеджеров, ищет в тексте имя менеджера из списка, и возвращает это имя.
find_customer_name: принимает на вход текстовую строку и список заказчиков, ищет в тексте название заказчика из списка, и возвращает это название.
find_date_range: принимает на вход текстовую строку, ищет в ней диапазон дат и возвращает его в виде кортежа (start_date, end_date).
get_records_data: принимает на вход токен, путь для API, имя менеджера, название заказчика и диапазон дат, и возвращает список текстов из карточек, которые соответствуют этому фильтру.
summarize_records_texts: принимает на вход список текстов записей и возвращает список суммаризированных текстов.
Тестовые функции:

generate_test_queries: генерирует список тестовых запросов с правильными ответами.
add_test_managers_stub: добавляет тестовых менеджеров через API AMOCRM.
add_test_customers_stub: добавляет тестовых заказчиков через API AMOCRM.
add_test_cards_stub: добавляет тестовые карточки через API AMOCRM.
add_test_records_stub: добавляет тестовые записи в карточку тестового заказчика от имени тестового менеджера через API AMOCRM.
generate_test_managers_stub: генерирует список тестовых менеджеров.
generate_test_customers_stub: генерирует список тестовых заказчиков.
'''