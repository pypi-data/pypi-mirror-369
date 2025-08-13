"""
HyperLog - One import. Better logging. No bullshit.

A dead simple, beautiful logging library that works as both a decorator and logger.
No configuration needed. Just import and use.

Powered by Loguru under the hood, simplified for humans.
"""

__version__ = "0.2.0"
__author__ = "HyperLog Contributors"
__license__ = "MIT"

import asyncio
import functools
import inspect  # Added for dynamic depth calculation
import sys
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, overload

from loguru import logger

# Type definitions
F = TypeVar("F", bound=Callable[..., Any])
LogLevel = Union[int, str]
TimeUnit = Union[str, None]


class TimingMark:
    """Represents a timing mark for performance monitoring."""

    def __init__(self, name: str, timestamp: float):
        self.name = name
        self.timestamp = timestamp


class HyperLog:
    """
    The main HyperLog class that acts as both a logger and decorator.
    Powered by Loguru for robust logging with a dead-simple API.

    Usage:
        from hyperlog import log

        @log()
        def my_function():
            log.info("Hello!")
    """

    def __init__(self):
        """Initialize the HyperLog instance."""
        self.prefix = ""
        self._marks: Dict[str, float] = {}
        self._checkpoints: List[TimingMark] = []
        self._checkpoint_start: Optional[float] = None  # Track sequence start time
        self._checkpoint_step: int = 0  # Track current step number
        self._custom_levels: Dict[str, str] = {}  # Track custom levels we've added
        self._bound_fields: Dict[str, Any] = {}  # Store bound fields
        self._lock = threading.Lock()  # Thread safety for field operations
        self._checkpoint_lock = (
            threading.Lock()
        )  # Thread safety for checkpoint operations

        # Remove default handler and add our beautiful one
        logger.remove()

        # Beautiful colored output for development
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss.SSS}</green> <level>{level: <8}</level> {message}",
            colorize=True,
            backtrace=True,
            diagnose=True,  # Show locals in tracebacks!
        )

        # Expose loguru methods directly with our wrapper
        for method in ["debug", "info", "warning", "error", "critical"]:
            if hasattr(logger, method):
                setattr(self, method, self._create_level_method(method.upper()))

        # Check if SUCCESS level exists in loguru (newer versions have it)
        try:
            logger.level("SUCCESS")
            self.success = self._create_level_method("SUCCESS")
        except ValueError:
            # SUCCESS doesn't exist, we'll add it when needed
            pass

        # Additional useful methods from loguru
        self.add = logger.add
        self.remove = logger.remove
        self.catch = logger.catch  # Exception catcher decorator
        self.patch = logger.patch
        self.level = logger.level
        self.disable = logger.disable
        self.enable = logger.enable
        self.configure = logger.configure

    def bind(self, **fields) -> "HyperLog":
        """
        Bind additional fields to this logger instance.
        Existing fields are preserved, duplicate keys are overwritten.

        Args:
            **fields: Key-value pairs to bind to all subsequent logs

        Returns:
            self for chaining

        Example:
            log.bind(service="api", version="1.0")
            log.info("Request received")  # Includes service=api version=1.0

            # Overwrite existing field
            log.bind(version="2.0")  # version is now 2.0
        """
        with self._lock:
            self._bound_fields.update(fields)
        return self

    def unbind(self, *keys) -> "HyperLog":
        """
        Remove specified bound fields from this logger instance.

        Args:
            *keys: Field names to remove

        Returns:
            self for chaining

        Example:
            log.bind(service="api", user="john")
            log.unbind("user")  # Only service=api remains
        """
        with self._lock:
            for key in keys:
                self._bound_fields.pop(key, None)
        return self

    def unbind_all(self) -> "HyperLog":
        """
        Remove all bound fields from this logger instance.

        Returns:
            self for chaining
        """
        with self._lock:
            self._bound_fields.clear()
        return self

    def get_bound_fields(self) -> Dict[str, Any]:
        """
        Get currently bound fields.

        Returns:
            Dictionary of bound field names and values
        """
        with self._lock:
            return self._bound_fields.copy()

    def has_bound_field(self, key: str) -> bool:
        """
        Check if a field is currently bound.

        Args:
            key: Field name to check

        Returns:
            True if field is bound, False otherwise
        """
        with self._lock:
            return key in self._bound_fields

    # --- Caller attribution core ------------------------------------
    def _find_external_frame(self):
        for frame_info in inspect.stack()[2:]:  # skip _emit + wrapper
            filename = frame_info.filename
            if filename != __file__ and "loguru" not in filename:
                module = inspect.getmodule(frame_info.frame)
                module_name = module.__name__ if module else "__main__"
                return module_name, frame_info.function, frame_info.lineno
        # Fallback to first frame after skip
        f = inspect.stack()[2]
        module = inspect.getmodule(f.frame)
        return (module.__name__ if module else "__main__", f.function, f.lineno)

    def _emit(self, level: LogLevel, message: str, *args, **kwargs):
        if isinstance(level, str):
            level = level.upper()
        if self.prefix:
            message = f"{self.prefix}{message}"

        # Merge bound fields with kwargs (kwargs take precedence)
        merged_kwargs = {}
        with self._lock:
            merged_kwargs.update(self._bound_fields)
        merged_kwargs.update(kwargs)

        module_name, function_name, line_no = self._find_external_frame()

        # Use loguru's bind if we have bound fields, otherwise use regular logger
        if self._bound_fields:
            bound_logger = logger.bind(**self._bound_fields)
            patched = bound_logger.patch(
                lambda r, m=module_name, f=function_name, ln=line_no: r.update(
                    {"name": m, "function": f, "line": ln}
                )
            )
        else:
            patched = logger.patch(
                lambda r, m=module_name, f=function_name, ln=line_no: r.update(
                    {"name": m, "function": f, "line": ln}
                )
            )

        patched.opt(depth=0).log(level, message, *args, **kwargs)
        return self

    def _create_level_method(self, level_name: str):
        def level_method(message, *args, **kwargs):
            return self._emit(level_name, message, *args, **kwargs)

        return level_method

    def _wrap_log_method(self, method, level_name: Optional[str] = None):
        # Deprecated path retained for backward compatibility; now using _emit
        if level_name is None:
            level_name = getattr(method, "__name__", "INFO").upper()

        def wrapped(message, *args, **kwargs):
            return self._emit(level_name, message, *args, **kwargs)

        return wrapped

    # Internal helpers -------------------------------------------------
    def _internal_log(
        self, level: LogLevel, message: str, *, depth_offset: int = 0, **kwargs
    ):
        # Route through unified emitter so format consistent
        return self._emit(level, message, **kwargs)

    def _log_for_function(
        self, func: Callable, level: LogLevel, message: str, **kwargs
    ):
        if isinstance(level, str):
            level = level.upper()
        if self.prefix:
            message = f"{self.prefix}{message}"

        # Merge bound fields with kwargs (kwargs take precedence)
        merged_kwargs = {}
        with self._lock:
            merged_kwargs.update(self._bound_fields)
        merged_kwargs.update(kwargs)

        module_name = getattr(func, "__module__", "__main__")
        line_no = getattr(func.__code__, "co_firstlineno", 0)
        function_name = func.__name__

        # Use loguru's bind if we have bound fields, otherwise use regular logger
        if self._bound_fields:
            bound_logger = logger.bind(**self._bound_fields)
            patched = bound_logger.patch(
                lambda r, m=module_name, f=function_name, ln=line_no: r.update(
                    {"name": m, "function": f, "line": ln}
                )
            )
        else:
            patched = logger.patch(
                lambda r, m=module_name, f=function_name, ln=line_no: r.update(
                    {"name": m, "function": f, "line": ln}
                )
            )

        patched.opt(depth=0).log(level, message, **kwargs)

    def add_file(
        self,
        path: str,
        rotation: Optional[str] = "10 MB",
        retention: Optional[str] = "1 week",
        compression: Optional[str] = "zip",
        level: str = "DEBUG",
        **kwargs,
    ) -> int:
        """
        Add file logging with automatic rotation.

        Args:
            path: Path to the log file
            rotation: When to rotate (e.g., "10 MB", "daily", "1 week")
            retention: How long to keep old logs (e.g., "1 week", "30 days")
                      Or number of files (e.g., 3)
            compression: Compress rotated logs (e.g., "zip", "gz", "bz2")
            level: Minimum level to log to this file
            **kwargs: Additional arguments passed to logger.add()

        Returns:
            Handler ID that can be used with remove()
        """

        # Convert "N files" to integer for retention
        if isinstance(retention, str) and retention.endswith(" files"):
            try:
                retention = int(retention.split()[0])
            except ValueError:
                pass

        # Set sensible defaults that can be overridden
        kwargs.setdefault(
            "format",
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        kwargs.setdefault("backtrace", True)
        kwargs.setdefault("diagnose", True)

        return logger.add(
            path,
            rotation=rotation,
            retention=retention,
            compression=compression,
            level=level,
            **kwargs,
        )

    def add_level(self, name: str, severity: int, color: str = "<cyan>") -> None:
        """
        Add a custom log level.

        Args:
            name: The name of the log level (e.g., "SUCCESS")
            severity: The numeric severity (e.g., 25)
            color: The color to use when colorized output is enabled
        """
        # Check if level already exists
        try:
            existing_level = logger.level(name.upper())
            if existing_level.no != severity:
                # Level exists with different severity, can't change it
                return
        except ValueError:
            # Level doesn't exist, add it
            logger.level(name.upper(), no=severity, color=color)

        # Add method to self
        self._custom_levels[name.upper()] = name.lower()
        setattr(self, name.lower(), self._create_level_method(name.upper()))

    def log(self, level: LogLevel, message: str, *args, **kwargs) -> "HyperLog":
        """Log a message at the specified level using depth=1 for correct caller attribution."""
        # Unified emitter path
        return self._emit(level, message, *args, **kwargs)

    # Timing methods
    def mark(self, name: str = "default") -> "HyperLog":
        """
        Mark the current time with a name.

        Args:
            name: The name of the timing mark

        Returns:
            self for chaining
        """
        self._marks[name] = time.perf_counter()
        return self

    def elapsed(
        self,
        name: str = "default",
        unit: TimeUnit = None,
        log_level: Optional[str] = None,
    ) -> float:
        """
        Get elapsed time since a mark and optionally log it.

        Args:
            name: The name of the timing mark
            unit: The unit to display (auto, μs, ms, s, m)
            log_level: If provided, log the elapsed time at this level

        Returns:
            The elapsed time in seconds
        """
        if name not in self._marks:
            raise ValueError(f"No timing mark named '{name}' found")

        elapsed = time.perf_counter() - self._marks[name]

        if log_level is not None:
            formatted = self._format_duration(elapsed, unit)
            self.log(log_level, f"Elapsed ({name}): {formatted}")

        return elapsed

    def checkpoint(self, name: str, reset: bool = False) -> "HyperLog":
        """
        Create a timing checkpoint for sequential operations with analytical output.

        Shows step-by-step timing analysis:
        → Step 1: 10.5ms | Total: 10.5ms
        → Step 2: 45.2ms | Total: 55.7ms
        → Step 3: 23.1ms | Total: 78.8ms

        Args:
            name: The name of the checkpoint step
            reset: Whether to reset the checkpoint sequence and start fresh

        Returns:
            self for chaining
        """
        current_time = time.perf_counter()

        with self._checkpoint_lock:
            if reset:
                # Start a new checkpoint sequence
                self._checkpoints.clear()
                self._checkpoint_start = current_time
                self._checkpoint_step = 0  # Will be incremented to 1 below

            # Handle first step (either after reset or first ever call)
            if self._checkpoint_start is None or reset:
                if self._checkpoint_start is None:
                    self._checkpoint_start = current_time
                    self._checkpoints.clear()
                    self._checkpoint_step = 0

                self._checkpoint_step += 1
                self._checkpoints.append(TimingMark(name, current_time))

                # For the very first checkpoint, show 0ms as step time
                self._internal_log(
                    "INFO", f"→ Step {self._checkpoint_step}: 0.0ms | Total: 0.0ms"
                )

            else:
                # Calculate step time and total time for subsequent checkpoints
                last_checkpoint = self._checkpoints[-1]
                step_elapsed = current_time - last_checkpoint.timestamp
                total_elapsed = current_time - self._checkpoint_start

                self._checkpoint_step += 1
                step_formatted = self._format_duration(step_elapsed)
                total_formatted = self._format_duration(total_elapsed)

                self._internal_log(
                    "INFO",
                    f"→ Step {self._checkpoint_step}: {step_formatted} | Total: {total_formatted}",
                )
                self._checkpoints.append(TimingMark(name, current_time))

        return self

    @contextmanager
    def timer(self, name: str, log_level: str = "info", unit: TimeUnit = None):
        """
        Context manager for timing a block of code.

        Args:
            name: The name for this timing
            log_level: The level to log at (default: info)
            unit: The unit to display

        Usage:
            with log.timer("database"):
                db.query("SELECT * FROM users")
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            formatted = self._format_duration(elapsed, unit)
            self._internal_log(log_level, f"{name}: {formatted}")

    # Decorator functionality
    @overload
    def __call__(self) -> Callable[[F], F]:
        """Use as decorator without arguments."""
        pass

    @overload
    def __call__(
        self,
        level: Optional[LogLevel] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        threshold_ms: Optional[float] = None,
        verbose: bool = False,
        catch: bool = True,
    ) -> Callable[[F], F]:
        """Use as decorator with arguments."""
        pass

    def __call__(self, *args, **kwargs):
        """
        Use HyperLog as a decorator.

        Args:
            level: Override log level for this function
            prefix: Add a prefix for this function's logs
            tags: Tags to categorize this function
            threshold_ms: Only log if execution time exceeds this threshold
            verbose: Log function arguments
            catch: Automatically catch and log exceptions with context

        Usage:
            @log()
            def simple_function():
                pass

            @log(level="DEBUG", tags=["api", "critical"], threshold_ms=100)
            def complex_function():
                pass
        """
        # Handle both @log and @log() syntax
        if len(args) == 1 and callable(args[0]) and not kwargs:
            # Called as @log
            return self._create_decorator()(args[0])
        else:
            # Called as @log() or @log(...)
            return self._create_decorator(**kwargs)

    def _create_decorator(
        self,
        level: Optional[LogLevel] = None,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        threshold_ms: Optional[float] = None,
        verbose: bool = False,
        catch: bool = True,
    ):
        """Create the actual decorator."""

        def decorator(func: F) -> F:
            # Apply exception catcher if requested
            if catch:
                func = logger.catch(reraise=True)(func)

            if asyncio.iscoroutinefunction(func):
                return self._wrap_async_function(
                    func, level, prefix, tags, threshold_ms, verbose
                )
            else:
                return self._wrap_sync_function(
                    func, level, prefix, tags, threshold_ms, verbose
                )

        return decorator

    def _wrap_sync_function(
        self, func: F, level, prefix, tags, threshold_ms, verbose
    ) -> F:
        """Wrap a synchronous function with logging."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()

            try:
                if verbose:
                    verbose_template = f"{prefix}→ {func.__name__}({{!r}}, {{!r}})"
                    self._internal_log("DEBUG", verbose_template.format(args, kwargs))
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                if threshold_ms is None or elapsed_ms >= threshold_ms:
                    extra = {
                        "duration_ms": elapsed_ms,
                        "function": func.__name__,
                        "tags": tags,
                    }
                    self._log_for_function(
                        func,
                        (level or "INFO"),
                        f"{prefix}✓ {func.__name__} completed in {elapsed_ms:.2f}ms",
                        **extra,
                    )
                return result
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                extra = {
                    "duration_ms": elapsed_ms,
                    "function": func.__name__,
                    "tags": tags,
                }
                self._log_for_function(
                    func,
                    "ERROR",
                    f"{prefix}✗ {func.__name__} failed after {elapsed_ms:.2f}ms",
                    exc_info=True,
                    **extra,
                )
                raise

        return wrapper

    def _wrap_async_function(
        self, func: F, level, prefix, tags, threshold_ms, verbose
    ) -> F:
        """Wrap an asynchronous function with logging."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()

            try:
                if verbose:
                    verbose_template = f"{prefix}→ {func.__name__}({{!r}}, {{!r}})"
                    self._internal_log("DEBUG", verbose_template.format(args, kwargs))
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                if threshold_ms is None or elapsed_ms >= threshold_ms:
                    extra = {
                        "duration_ms": elapsed_ms,
                        "function": func.__name__,
                        "tags": tags,
                    }
                    self._log_for_function(
                        func,
                        (level or "INFO"),
                        f"{prefix}✓ {func.__name__} completed in {elapsed_ms:.2f}ms",
                        **extra,
                    )
                return result
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                extra = {
                    "duration_ms": elapsed_ms,
                    "function": func.__name__,
                    "tags": tags,
                }
                self._log_for_function(
                    func,
                    "ERROR",
                    f"{prefix}✗ {func.__name__} failed after {elapsed_ms:.2f}ms",
                    exc_info=True,
                    **extra,
                )
                raise

        return wrapper

    def _format_duration(self, seconds: float, unit: TimeUnit = None) -> str:
        """
        Format a duration intelligently.

        Args:
            seconds: The duration in seconds
            unit: Force a specific unit, or None for auto

        Returns:
            Formatted string like "123ms" or "1m 23s"
        """
        if unit == "μs":
            return f"{seconds * 1_000_000:.1f}μs"
        elif unit == "ms":
            return f"{seconds * 1000:.1f}ms"
        elif unit == "s":
            return f"{seconds:.2f}s"
        elif unit == "m":
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            # Auto format
            if seconds < 0.001:
                return f"{seconds * 1_000_000:.1f}μs"
            elif seconds < 1:
                return f"{seconds * 1000:.1f}ms"
            elif seconds < 60:
                return f"{seconds:.2f}s"
            else:
                minutes = int(seconds // 60)
                remaining_seconds = seconds % 60
                return f"{minutes}m {remaining_seconds:.1f}s"

    def _determine_caller_depth(self) -> int:
        """Compute how many frames to skip so logging points to user code, not HyperLog internals."""
        frame = inspect.currentframe()
        depth = 0
        try:
            if frame:
                frame = frame.f_back
            while frame and frame.f_code.co_filename == __file__:
                depth += 1
                frame = frame.f_back
            return max(depth, 1)
        finally:
            del frame


# Create the global instance
log = HyperLog()

# Make common methods available at module level
debug = log.debug
info = log.info
warning = log.warning
error = log.error
critical = log.critical
mark = log.mark
elapsed = log.elapsed
checkpoint = log.checkpoint
timer = log.timer
add_level = log.add_level
add_file = log.add_file

# Export the main interface
__all__ = [
    "log",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "mark",
    "elapsed",
    "checkpoint",
    "timer",
    "add_level",
    "add_file",
    "HyperLog",
]
