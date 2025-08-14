# Django Querylizer 🚀

[![PyPI version](https://badge.fury.io/py/django-querylizer.svg)](https://badge.fury.io/py/django-querylizer)
[![Python versions](https://img.shields.io/pypi/pyversions/django-querylizer.svg)](https://pypi.org/project/django-querylizer/)
[![Django versions](https://img.shields.io/pypi/djversions/django-querylizer.svg)](https://pypi.org/project/django-querylizer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Django Querylizer** is a powerful, automatic query performance analyzer and logger for Django applications. It helps you identify slow queries, detect N+1 query problems, find duplicate queries, and monitor your database performance in real-time without any code changes to your views or models.

## ✨ Features

- 🔍 **Automatic Query Detection** - No code changes needed in your views/models
- ⚡ **Performance Monitoring** - Track slow queries and execution times
- 🔄 **N+1 Query Detection** - Automatically detect and log N+1 query patterns
- 📊 **Duplicate Query Detection** - Find and eliminate redundant database calls
- 📈 **Request-Level Analytics** - Monitor queries per request
- 🎯 **Smart Filtering** - Exclude migrations, admin queries, and other noise
- 📝 **Comprehensive Logging** - Detailed logs with customizable formats
- 🛠️ **Easy Configuration** - Flexible settings for different environments
- 🔧 **Development Friendly** - Include stack traces for debugging

## 📦 Installation

Install django-querylizer using pip:

```bash
pip install django-querylizer
```

## ⚙️ Quick Setup

### 1. Add to Installed Apps

Add `querylizer` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... your other apps
    'querylizer',  # Add this
]
```

### 2. Add Middleware

Add the middleware to track queries per request:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ... your other middleware
    'querylizer.middleware.QueryAnalyzerMiddleware',  # Add this
]
```

### 3. Configure Settings (Optional)

Add configuration to your `settings.py`:

```python
QUERY_ANALYZER = {
    'ENABLED': True,
    'SLOW_QUERY_THRESHOLD': 0.1,  # Log queries slower than 100ms
    'LOG_SLOW_QUERIES': True,
    'LOG_ALL_QUERIES': False,  # Set to True for development
    'LOG_DUPLICATE_QUERIES': True,
    'LOG_N_PLUS_ONE': True,
    'TRACK_QUERY_COUNT': True,
    'INCLUDE_TRACEBACK': True,  # Include stack traces for debugging
    'MAX_QUERY_LENGTH': 200,
}
```

That's it! Django Querylizer will automatically start monitoring your database queries.

## 📋 Example Output

### Slow Query Detection
```
2024-01-15 10:30:45 [WARNING] querylizer.queries: [default] SUCCESS 0.245s - SELECT * FROM products WHERE category_id = 1 ORDER BY created_at DESC LIMIT 20
```

### N+1 Query Detection
```
2024-01-15 10:31:20 [WARNING] querylizer.patterns: N+1 QUERY DETECTED: 25 similar queries | Path: /products/category/electronics/ | Pattern: SELECT * FROM reviews WHERE product_id = ?
```

### Request Summary
```
2024-01-15 10:32:10 [INFO] querylizer.requests: REQUEST SUMMARY: GET /products/ | Queries: 12 | Query Time: 0.156s | Total Time: 0.298s | User: 1001
```

### Duplicate Query Detection
```
2024-01-15 10:33:05 [WARNING] querylizer.patterns: DUPLICATE QUERIES DETECTED: 3 duplicates | Path: /dashboard/
  - SELECT COUNT(*) FROM orders WHERE user_id = 1001...
  - SELECT COUNT(*) FROM orders WHERE user_id = 1001...
  - SELECT COUNT(*) FROM orders WHERE user_id = 1001...
```

## ⚙️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `ENABLED` | `True` | Enable/disable the query analyzer |
| `AUTO_INSTRUMENT` | `True` | Automatically instrument database queries |
| `SLOW_QUERY_THRESHOLD` | `0.5` | Threshold for slow query detection (seconds) |
| `VERY_SLOW_QUERY_THRESHOLD` | `2.0` | Threshold for very slow queries (seconds) |
| `LOG_ALL_QUERIES` | `False` | Log every single query (can be noisy) |
| `LOG_SLOW_QUERIES` | `True` | Log only slow queries |
| `LOG_DUPLICATE_QUERIES` | `True` | Detect and log duplicate queries |
| `LOG_N_PLUS_ONE` | `True` | Detect and log N+1 query patterns |
| `ANALYZE_PATTERNS` | `True` | Enable query pattern analysis |
| `TRACK_QUERY_COUNT` | `True` | Track query count per request |
| `INCLUDE_TRACEBACK` | `True` | Include Python stack traces |
| `MAX_QUERY_LENGTH` | `200` | Maximum query length in logs |
| `EXCLUDE_MIGRATIONS` | `True` | Exclude Django migration queries |
| `DATABASES` | `['default']` | List of databases to monitor |
| `LOG_LEVEL` | `'INFO'` | Logging level for query analyzer |

## 🔧 Advanced Usage

### Programmatic Access

You can also access query statistics programmatically:

```python
from querylizer import QueryAnalyzer

# Get current request statistics
stats = QueryAnalyzer.get_current_request_stats()
print(f"Queries executed: {stats['query_count']}")
print(f"Total time: {stats['total_time']:.3f}s")
print(f"Slow queries: {len(stats['slow_queries'])}")

# Log custom metrics
QueryAnalyzer.log_custom_metric('cache_hits', 95, cache_type='redis')
```

### Custom Logging Configuration

You can customize the logging format and handlers:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'query_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'queries.log',
        },
    },
    'loggers': {
        'querylizer.queries': {
            'handlers': ['query_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'querylizer.patterns': {
            'handlers': ['query_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

## 🎯 Use Cases

### Development Environment
- **Debug Performance Issues**: Quickly identify slow queries during development
- **Optimize Query Patterns**: Detect N+1 queries and unnecessary duplicates
- **Monitor Query Count**: Keep track of queries per request to avoid database overload

### Staging Environment
- **Performance Testing**: Monitor query performance under realistic conditions
- **Pattern Analysis**: Identify potential performance bottlenecks before production
- **Optimization Verification**: Ensure optimizations are working as expected

### Production Environment (Careful Configuration Needed)
- **Slow Query Monitoring**: Track only the slowest queries to avoid log spam
- **Performance Regression Detection**: Get alerted when queries become slower
- **Database Health Monitoring**: Monitor overall database performance trends

## 📊 Performance Impact

Django Querylizer is designed to have minimal performance impact:

- **Lightweight**: Only adds microseconds to query execution time
- **Efficient**: Smart filtering avoids logging unnecessary queries
- **Configurable**: Disable features you don't need to reduce overhead
- **Production Ready**: Can be safely used in production with proper configuration

## 🔍 Common Patterns Detected

### N+1 Queries
```python
# This code will trigger N+1 detection
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # Triggers individual queries

# Fix: Use select_related
posts = Post.objects.select_related('author').all()
```

### Duplicate Queries
```python
# This will trigger duplicate query detection
def get_user_stats(user_id):
    order_count = Order.objects.filter(user_id=user_id).count()
    total_spent = Order.objects.filter(user_id=user_id).aggregate(Sum('total'))['total__sum']

# Fix: Use a single query
def get_user_stats(user_id):
    result = Order.objects.filter(user_id=user_id).aggregate(
        order_count=Count('id'),
        total_spent=Sum('total')
    )
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Django's built-in query debugging tools
- Built with ❤️ for the Django community

## 📞 Support

If you encounter any problems or have questions, please:

1. Check the [Issues](https://github.com/AvicennaJr/django-querylizer/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide as much detail as possible, including Django version and configuration

---

**Made with ❤️ by [Fuad Habib](https://github.com/AvicennaJr)**

⭐ Star this repo if it helped you optimize your Django queries!
