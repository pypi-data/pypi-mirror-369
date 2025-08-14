from django.conf import settings

QUERY_ANALYZER_SETTINGS = {
    'ENABLED': True,
    'AUTO_INSTRUMENT': True,

    'SLOW_QUERY_THRESHOLD': 0.5,  # seconds
    'VERY_SLOW_QUERY_THRESHOLD': 2.0,  # seconds

    'LOG_ALL_QUERIES': False,
    'LOG_SLOW_QUERIES': True,
    'LOG_DUPLICATE_QUERIES': True,
    'LOG_N_PLUS_ONE': True,

    # Output settings
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    'INCLUDE_TRACEBACK': True,
    'INCLUDE_QUERY_PLAN': False,
    'MAX_QUERY_LENGTH': 200,

    # Analysis settings
    'ANALYZE_PATTERNS': True,
    'DETECT_MISSING_INDEXES': True,
    'TRACK_QUERY_COUNT': True,

    # Database settings
    'DATABASES': ['default'],
    'EXCLUDE_MIGRATIONS': True,
    'EXCLUDE_ADMIN': False,

    # Performance settings
    'BATCH_SIZE': 100,
    'MAX_STACK_DEPTH': 10,
}

user_settings = getattr(settings, 'QUERY_ANALYZER', {})
QUERY_ANALYZER_SETTINGS.update(user_settings)
