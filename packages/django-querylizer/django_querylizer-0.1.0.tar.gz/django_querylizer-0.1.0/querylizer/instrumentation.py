import time
import threading
from functools import wraps
from typing import Dict, Any, List, Optional
from django.db import connections
from .loggers import QueryLogger
from .settings import QUERY_ANALYZER_SETTINGS

_local = threading.local()

class QueryContext:
    """Store context information for the current request"""
    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.request_path: Optional[str] = None
        self.user_id: Optional[int] = None

def get_query_context() -> QueryContext:
    """Get or create query context for current thread"""
    if not hasattr(_local, 'context'):
        _local.context = QueryContext()
    return _local.context

def clear_query_context():
    """Clear query context"""
    if hasattr(_local, 'context'):
        del _local.context

class DatabaseInstrumentation:
    """Database instrumentation for automatic query logging"""

    def __init__(self):
        self.logger = QueryLogger()
        self.original_execute = {}
        self.original_executemany = {}
        self.installed = False

    def install(self):
        """Install instrumentation on all configured databases"""
        if self.installed:
            return

        databases = QUERY_ANALYZER_SETTINGS['DATABASES']

        for db_alias in databases:
            if db_alias in connections:
                self._instrument_database(db_alias)

        self.installed = True

    def _instrument_database(self, db_alias: str):
        """Instrument a specific database connection"""
        connection = connections[db_alias]

        cursor_class = connection.cursor().__class__

        if cursor_class not in self.original_execute:
            self.original_execute[cursor_class] = cursor_class.execute
            self.original_executemany[cursor_class] = cursor_class.executemany

        cursor_class.execute = self._wrap_execute(
            self.original_execute[cursor_class], db_alias
        )
        cursor_class.executemany = self._wrap_executemany(
            self.original_executemany[cursor_class], db_alias
        )

    def _wrap_execute(self, original_execute, db_alias: str):
        """Wrap cursor.execute method"""
        @wraps(original_execute)
        def execute_wrapper(cursor, sql, params=None):
            return self._execute_with_logging(
                original_execute, cursor, sql, params, db_alias, many=False
            )
        return execute_wrapper

    def _wrap_executemany(self, original_executemany, db_alias: str):
        """Wrap cursor.executemany method"""
        @wraps(original_executemany)
        def executemany_wrapper(cursor, sql, param_list):
            return self._execute_with_logging(
                original_executemany, cursor, sql, param_list, db_alias, many=True
            )
        return executemany_wrapper

    def _execute_with_logging(self, original_method, cursor, sql, params, db_alias: str, many: bool):
        """Execute query with logging"""
        start_time = time.time()

        try:
            result = original_method(cursor, sql, params)

            execution_time = time.time() - start_time

            self._log_query(sql, params, execution_time, db_alias, many, success=True)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._log_query(sql, params, execution_time, db_alias, many, success=False, error=str(e))
            raise

    def _log_query(self, sql: str, params, execution_time: float,
                   db_alias: str, many: bool, success: bool, error: str = None):
        """Log query information"""

        if not QUERY_ANALYZER_SETTINGS['ENABLED']:
            return

        if QUERY_ANALYZER_SETTINGS['EXCLUDE_MIGRATIONS'] and self._is_migration_query(sql):
            return

        query_info = {
            'sql': sql,
            'params': params,
            'execution_time': execution_time,
            'database': db_alias,
            'many': many,
            'success': success,
            'error': error,
            'timestamp': time.time(),
        }

        context = get_query_context()
        context.queries.append(query_info)

        should_log = False
        log_level = 'INFO'

        if not success:
            should_log = True
            log_level = 'ERROR'
        elif QUERY_ANALYZER_SETTINGS['LOG_ALL_QUERIES']:
            should_log = True
        elif (QUERY_ANALYZER_SETTINGS['LOG_SLOW_QUERIES'] and
              execution_time >= QUERY_ANALYZER_SETTINGS['SLOW_QUERY_THRESHOLD']):
            should_log = True
            if execution_time >= QUERY_ANALYZER_SETTINGS['VERY_SLOW_QUERY_THRESHOLD']:
                log_level = 'WARNING'

        if should_log:
            self.logger.log_query(query_info, log_level)

    def _is_migration_query(self, sql: str) -> bool:
        """Check if query is related to migrations"""
        migration_patterns = [
            'django_migrations',
            'django_content_type',
            'auth_permission',
        ]
        sql_lower = sql.lower()
        return any(pattern in sql_lower for pattern in migration_patterns)

_instrumentation = DatabaseInstrumentation()

def install_instrumentation():
    """Install database instrumentation"""
    _instrumentation.install()
