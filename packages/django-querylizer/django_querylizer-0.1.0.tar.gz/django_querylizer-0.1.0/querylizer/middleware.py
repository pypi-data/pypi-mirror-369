import time
from django.utils.deprecation import MiddlewareMixin
from .instrumentation import get_query_context, clear_query_context
from .loggers import QueryLogger
from .settings import QUERY_ANALYZER_SETTINGS

class QueryAnalyzerMiddleware(MiddlewareMixin):
    """Middleware to track queries per request and detect patterns"""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.logger = QueryLogger()

    def process_request(self, request):
        """Initialize query tracking for request"""
        if not QUERY_ANALYZER_SETTINGS['ENABLED']:
            return

        context = get_query_context()
        context.request_path = request.path
        context.start_time = time.time()

        if hasattr(request, 'user') and request.user.is_authenticated:
            context.user_id = request.user.id

    def process_response(self, request, response):
        """Log request summary and detect patterns"""
        if not QUERY_ANALYZER_SETTINGS['ENABLED']:
            return response

        context = get_query_context()

        total_time = time.time() - context.start_time
        query_count = len(context.queries)
        total_query_time = sum(q['execution_time'] for q in context.queries)

        self._log_request_summary(request, context, total_time, query_count, total_query_time)

        if QUERY_ANALYZER_SETTINGS['ANALYZE_PATTERNS']:
            self._analyze_query_patterns(context)

        clear_query_context()

        return response

    def _log_request_summary(self, request, context, total_time: float,
                           query_count: int, total_query_time: float):
        """Log summary of request performance"""

        is_slow = (query_count > 10 or
                  total_query_time > QUERY_ANALYZER_SETTINGS['SLOW_QUERY_THRESHOLD'] or
                  total_time > 2.0)

        if QUERY_ANALYZER_SETTINGS['TRACK_QUERY_COUNT'] or is_slow:
            summary = {
                'path': request.path,
                'method': request.method,
                'query_count': query_count,
                'total_query_time': total_query_time,
                'total_request_time': total_time,
                'user_id': context.user_id,
                'queries': context.queries if is_slow else []
            }

            log_level = 'WARNING' if is_slow else 'INFO'
            self.logger.log_request_summary(summary, log_level)

    def _analyze_query_patterns(self, context):
        """Analyze query patterns and detect issues"""
        queries = context.queries

        if len(queries) < 2:
            return

        if QUERY_ANALYZER_SETTINGS['LOG_N_PLUS_ONE']:
            self._detect_n_plus_one(queries, context)

        if QUERY_ANALYZER_SETTINGS['LOG_DUPLICATE_QUERIES']:
            self._detect_duplicates(queries, context)

    def _detect_n_plus_one(self, queries, context):
        """Detect potential N+1 query patterns"""
        query_patterns = {}

        for query in queries:
            normalized = self._normalize_query(query['sql'])
            if normalized not in query_patterns:
                query_patterns[normalized] = []
            query_patterns[normalized].append(query)

        for pattern, pattern_queries in query_patterns.items():
            if len(pattern_queries) > 5:
                self.logger.log_n_plus_one_detected(pattern, pattern_queries, context)

    def _detect_duplicates(self, queries, context):
        """Detect duplicate queries"""
        seen_queries = {}
        duplicates = []

        for query in queries:
            query_key = (query['sql'], str(query['params']))
            if query_key in seen_queries:
                duplicates.append({
                    'query': query,
                    'first_occurrence': seen_queries[query_key],
                    'duplicate_occurrence': query
                })
            else:
                seen_queries[query_key] = query

        if duplicates:
            self.logger.log_duplicate_queries(duplicates, context)

    def _normalize_query(self, sql: str) -> str:
        """Normalize SQL query to detect patterns"""
        import re
        normalized = re.sub(r'\b\d+\b', '?', sql)
        normalized = re.sub(r"'[^']*'", '?', normalized)
        normalized = re.sub(r'"[^"]*"', '?', normalized)
        return normalized.strip()
