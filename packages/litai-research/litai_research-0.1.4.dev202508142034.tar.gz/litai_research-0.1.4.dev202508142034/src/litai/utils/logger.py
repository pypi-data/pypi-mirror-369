"""Logging configuration for LitAI."""

import logging
import sys
from pathlib import Path
from typing import Any

import orjson
import structlog
from structlog.types import Processor


class LogConfig:
    """Centralized logging configuration."""
    
    def __init__(self, debug: bool = False, log_file: Path | None = None):
        self.debug = debug
        self.log_level = logging.DEBUG if debug else logging.INFO
        self.log_file = log_file or (Path.home() / ".litai" / "logs" / "litai.log")
        
    def get_shared_processors(self) -> list[Processor]:
        """Get processors shared between dev and prod."""
        return [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ],
            ),
            structlog.processors.format_exc_info,
        ]
    
    def get_dev_processors(self) -> list[Processor]:
        """Get development-specific processors."""
        return self.get_shared_processors() + [
            structlog.dev.ConsoleRenderer(colors=True, exception_formatter=structlog.dev.RichTracebackFormatter()),
        ]
    
    def get_prod_processors(self) -> list[Processor]:
        """Get production-specific processors."""
        return self.get_shared_processors() + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ]
    
    def setup(self) -> None:
        """Configure structured logging based on environment."""
        # Create logs directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure standard logging
        logging.basicConfig(
            level=self.log_level,
            format="%(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout) if self.debug else logging.NullHandler(),
            ],
        )
        
        # Determine environment and select processors
        if sys.stderr.isatty() and self.debug:
            processors = self.get_dev_processors()
        else:
            processors = self.get_prod_processors()
        
        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(self.log_level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging (legacy interface)."""
    config = LogConfig(debug=debug)
    config.setup()


def get_logger(name: str) -> Any:
    """Get a configured logger instance."""
    return structlog.get_logger(name)
