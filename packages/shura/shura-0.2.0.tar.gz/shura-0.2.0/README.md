# Shura

A simple, colorful logging library for Python that makes your console output beautiful and easy to read.

## What is Shura?

Shura takes the boring, plain text logs that Python normally produces and makes them colorful and organized. Instead of hunting through walls of black and white text to find errors, you get color-coded messages that are easy to spot at a glance.

Perfect for developers who want clean, readable logs without spending time configuring complex logging systems.

## Features

- **Colorful output** - Different colors for different log levels (debug, info, warning, error, critical)
- **Zero setup** - Works immediately with just one line of code
- **File logging** - Optionally save logs to files in standard or JSON format
- **Cross-platform** - Works on Windows, Mac, and Linux


## Installation

Install Shura using pip:

```
pip install shura
```

That's it. No additional setup required.

## Quick Start

```python
from shura import get_logger

log = get_logger("my_app")

log.debug("Starting application")
log.info("User logged in successfully")
log.warning("Low disk space detected")
log.error("Failed to connect to database")
log.critical("System is shutting down")
```

## Usage Examples

### Basic Logging

```python
from shura import get_logger

# Create a logger for your application
log = get_logger("web_server")

# Log different types of messages
log.info("Server started on port 8080")
log.warning("High memory usage detected")
log.error("Database connection failed")
```

### Custom Logger Name

```python
# Use different names for different parts of your application
api_log = get_logger("api")
db_log = get_logger("database")
auth_log = get_logger("authentication")

api_log.info("Received API request")
db_log.error("Query execution failed")
auth_log.warning("Multiple failed login attempts")
```

### File Logging

Save your logs to a file for later review:

```python
from shura import get_logger

# Enable standard file logging
log = get_logger("my_service", to_file=True, filename="app.log")

log.info("This message appears in console AND gets saved to app.log")
log.error("Errors are saved to the file too")
```

### JSON File Logging

For modern applications that need structured logs:

```python
from shura import get_logger

# Enable JSON file logging
log = get_logger("api_service", to_file=True, filename="api.json", file_format="json")

log.info("User login successful")
log.error("Database connection failed")
```

**JSON output example:**
```json
{"timestamp": "2025-08-12T10:30:15.123456", "level": "INFO", "logger": "api_service", "message": "User login successful"}
{"timestamp": "2025-08-12T10:30:16.789012", "level": "ERROR", "logger": "api_service", "message": "Database connection failed"}
```

### Different Log Levels

```python
import logging
from shura import get_logger

# Only show warnings and errors (hide debug and info)
log = get_logger("production_app", level=logging.WARNING)

log.debug("This won't show")     # Hidden
log.info("This won't show")      # Hidden  
log.warning("This will show")    # Visible
log.error("This will show")      # Visible
```

## Configuration Options

The `get_logger()` function accepts these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | "shura" | Name of your logger (appears in log messages) |
| `level` | int | `logging.DEBUG` | Minimum log level to display |
| `to_file` | boolean | `False` | Whether to save logs to a file |
| `filename` | string | "shura.log" | Name of the log file (when `to_file=True`) |
| `file_format` | string | "log" | File format: "log" for standard format, "json" for structured JSON |
| `file_format` | string | "log" | File format: "log" for standard format, "json" for structured JSON |

### Log Levels

- **DEBUG** - Detailed information for diagnosing problems
- **INFO** - General information about program execution  
- **WARNING** - Something unexpected happened, but the program continues
- **ERROR** - A serious problem occurred
- **CRITICAL** - A very serious error occurred, program may stop



## Requirements

- Python 3.6 or higher
- colorama (automatically installed)

Works on all operating systems.
## Contributing

Found a bug or want to suggest a feature? Visit the project on GitHub and open an issue.

## License

MIT License - feel free to use Shura in your projects.

---

**Made by Guy Shaul** - A simple solution for better Python logging.