import logging
import traceback
from typing import Dict, Any, List
from .settings import QUERY_ANALYZER_SETTINGS

class QueryLogger:
    """Handles all query-related logging"""

    def __init__(self):
        self.logger = logging.getLogger('querylizer.queries')
        self.request_logger = logging.getLogger('querylizer.requests')
        self.pattern_logger = logging.getLogger('querylizer.patterns')

    def log_query(self, query_info: Dict[str, Any], level: str = 'INFO'):
        """Log individual query"""
        sql = query_info['sql']
        execution_time = query_info['execution_time']
        database = query_info['database']
        success = query_info['success']

        max_length = QUERY_ANALYZER_SETTINGS['MAX_QUERY_LENGTH']
        if len(sql) > max_length:
            sql = sql[:max_length] + '...'

        status = "SUCCESS" if success else "ERROR"
        message = f"[{database}] {status} {execution_time:.3f}s - {sql}"

        if query_info.get('params'):
            message += f" | Params: {query_info['params']}"

        if not success and query_info.get('error'):
            message += f" | Error: {query_info['error']}"

        if (QUERY_ANALYZER_SETTINGS['INCLUDE_TRACEBACK'] and
            execution_time >= QUERY_ANALYZER_SETTINGS['SLOW_QUERY_THRESHOLD']):
            message += f"\n{self._get_filtered_traceback()}"

        log_method = getattr(self.logger, level.lower())
        log_method(message)

    def log_request_summary(self, summary: Dict[str, Any], level: str = 'INFO'):
        """Log request performance summary"""
        message = (
            f"REQUEST SUMMARY: {summary['method']} {summary['path']} | "
            f"Queries: {summary['query_count']} | "
            f"Query Time: {summary['total_query_time']:.3f}s | "
            f"Total Time: {summary['total_request_time']:.3f}s"
        )

        if summary.get('user_id'):
            message += f" | User: {summary['user_id']}"

        log_method = getattr(self.request_logger, level.lower())
        log_method(message)

    def log_n_plus_one_detected(self, pattern: str, queries: List[Dict], context):
        """Log N+1 query detection"""
        message = (
            f"N+1 QUERY DETECTED: {len(queries)} similar queries | "
            f"Path: {context.request_path} | "
            f"Pattern: {pattern[:100]}..."
        )

        if QUERY_ANALYZER_SETTINGS['INCLUDE_TRACEBACK']:
            message += f"\n{self._get_filtered_traceback()}"

        self.pattern_logger.warning(message)

    def log_duplicate_queries(self, duplicates: List[Dict], context):
        """Log duplicate queries"""
        message = (
            f"DUPLICATE QUERIES DETECTED: {len(duplicates)} duplicates | "
            f"Path: {context.request_path}"
        )

        for dup in duplicates[:3]:
            query = dup['query']['sql'][:100]
            message += f"\n  - {query}..."

        if len(duplicates) > 3:
            message += f"\n  ... and {len(duplicates) - 3} more"

        self.pattern_logger.warning(message)

    def _get_filtered_traceback(self) -> str:
        """Get filtered traceback excluding Django internals"""
        stack = traceback.extract_stack()

        filtered_stack = []
        for frame in stack:
            if not any(pattern in frame.filename for pattern in [
                'django/', 'querylizer/', 'site-packages/'
            ]):
                filtered_stack.append(frame)

        max_depth = QUERY_ANALYZER_SETTINGS['MAX_STACK_DEPTH']
        filtered_stack = filtered_stack[-max_depth:]

        return ''.join(traceback.format_list(filtered_stack))
