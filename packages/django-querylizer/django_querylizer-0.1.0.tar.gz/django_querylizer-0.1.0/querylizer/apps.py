from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class QueryAnalyzerConfig(AppConfig):
    name = 'querylizer'
    verbose_name = 'Django Query Analyzer'

    def ready(self):
        """Initialize query analyzer when Django starts"""
        from .settings import QUERY_ANALYZER_SETTINGS

        if not QUERY_ANALYZER_SETTINGS['ENABLED']:
            return

        if QUERY_ANALYZER_SETTINGS['AUTO_INSTRUMENT']:
            self._setup_instrumentation()

        self._setup_logging()

        logger.info("Django Query Analyzer initialized")

    def _setup_instrumentation(self):
        """Set up automatic query instrumentation"""
        try:
            from .instrumentation import install_instrumentation
            install_instrumentation()
            logger.info("Query instrumentation installed")
        except Exception as e:
            logger.error(f"Failed to install query instrumentation: {e}")

    def _setup_logging(self):
        """Configure query analyzer logging"""
        from .settings import QUERY_ANALYZER_SETTINGS

        analyzer_logger = logging.getLogger('querylizer.queries')

        if not analyzer_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                QUERY_ANALYZER_SETTINGS['LOG_FORMAT']
            )
            handler.setFormatter(formatter)
            analyzer_logger.addHandler(handler)
            analyzer_logger.setLevel(
                getattr(logging, QUERY_ANALYZER_SETTINGS['LOG_LEVEL'])
            )
