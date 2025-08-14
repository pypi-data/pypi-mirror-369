import logging
from typing import Dict, Any
from .loggers import QueryLogger
from .instrumentation import get_query_context

class QueryAnalyzer:
    """Enhanced query analyzer with automatic logging integration"""

    def __init__(self):
        self.logger = QueryLogger()

    @classmethod
    def get_current_request_stats(cls) -> Dict[str, Any]:
        """Get statistics for current request"""
        context = get_query_context()

        if not context.queries:
            return {'query_count': 0, 'total_time': 0}

        return {
            'query_count': len(context.queries),
            'total_time': sum(q['execution_time'] for q in context.queries),
            'slow_queries': [
                q for q in context.queries
                if q['execution_time'] >= 0.1
            ],
            'failed_queries': [
                q for q in context.queries
                if not q['success']
            ]
        }

    @classmethod
    def log_custom_metric(cls, metric_name: str, value: Any, **metadata):
        """Log custom performance metric"""
        logger = logging.getLogger('query_analyzer.metrics')
        message = f"METRIC: {metric_name} = {value}"

        if metadata:
            message += f" | {metadata}"

        logger.info(message)
