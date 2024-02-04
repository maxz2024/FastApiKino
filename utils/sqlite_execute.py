import sqlite3

def execute_query(query, params=None, fetch_one=False):
    """
    Выполняет SQL-запрос к базе данных SQLite3.

    Параметры:
    - query: строка с SQL-запросом
    - params: кортеж с параметрами запроса (опционально)
    - fetch_one: если True, возвращает одну строку результата (опционально)

    Возвращает:
    - Результат выполнения запроса (зависит от типа запроса и настроек)
    """
    # Подключение к базе данных (можно указать полный путь к файлу базы данных)
    connection = sqlite3.connect('mydatabase.db')
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    connection.row_factory = dict_factory

    # Создание объекта-курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    try:
        # Выполнение SQL-запроса с параметрами (если они предоставлены)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Получение результата запроса
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

        # Подтверждение изменений (если были)
        connection.commit()

        return True, result

    except sqlite3.Error as e:
        return False, f"Ошибка выполнения SQL-запроса: {e}"

    finally:
        # Закрытие курсора и соединения с базой данных
        cursor.close()
        connection.close()
