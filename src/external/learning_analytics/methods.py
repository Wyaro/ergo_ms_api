import logging
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

logger = logging.getLogger(__name__)

def handle_db_errors(func):
    """Декоратор для обработки ошибок БД"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def get_table_info(cursor, table_name):
    """Получает информацию о конкретной таблице"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, [table_name])
    return cursor.fetchall()

def check_table_exists(cursor, table_name):
    """Проверяет существование таблицы"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, [table_name])
    return cursor.fetchone()[0]

@handle_db_errors
def get_tables_info(cursor):
    """
    Получает информацию о всех таблицах аналитического модуля.
    Возвращает список таблиц с количеством колонок и записей.
    """
    try:
        # Получаем список таблиц с количеством колонок
        cursor.execute("""
            WITH table_info AS (
                SELECT 
                    t.table_name,
                    COUNT(c.column_name) as column_count
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c 
                    ON c.table_name = t.table_name 
                    AND c.table_schema = 'public'
                WHERE t.table_schema = 'public'
                    AND t.table_name LIKE 'learning_analytics_%%'
                GROUP BY t.table_name
            )
            SELECT table_name, column_count
            FROM table_info;
        """)
        
        tables_info = cursor.fetchall()
        result_tables = []
        
        # Для каждой таблицы получаем количество записей
        for table in tables_info:
            table_name = table[0]
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cursor.fetchone()[0]
            result_tables.append({
                'name': table_name,
                'columns_count': table[1],
                'rows_count': row_count
            })
        
        return result_tables
    except Exception as e:
        logger.error(f"Error in get_tables_info: {str(e)}")
        raise