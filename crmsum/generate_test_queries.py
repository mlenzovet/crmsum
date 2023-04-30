import random

def generate_test_queries(num_queries, managers_list, customers_list):
    query_templates = [
        "расскажи, что {manager} делала сегодня по {customer}.",
        "что {manager} делал с {start_date} по {end_date} по заказу от {customer}?",
        "каковы результаты работы {manager} с {customer} на {start_date}?",
        "события между {start_date} и {end_date} для {manager} и заказчика {customer}",
        "Работа {manager} над проектом {customer} с {start_date} до {end_date}"
    ]

    test_queries_with_answers = []
    for _ in range(num_queries):
        query_template = random.choice(query_templates)
        manager = random.choice(managers_list)
        customer = random.choice(customers_list)
        start_date = f"2023-0{random.randint(1, 9)}-{random.randint(10, 28)}"
        end_date = f"2023-0{random.randint(1, 9)}-{random.randint(10, 28)}"
        query = query_template.format(manager=manager, customer=customer, start_date=start_date, end_date=end_date)

        correct_manager = manager
        correct_customer = customer
        correct_dates = (start_date, end_date)
        test_queries_with_answers.append((query, correct_manager, correct_customer, correct_dates))

    return test_queries_with_answers
