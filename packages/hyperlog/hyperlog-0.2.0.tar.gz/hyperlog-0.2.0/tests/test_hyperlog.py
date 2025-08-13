"""
Test file demonstrating HyperLog functionality.
"""

import asyncio
import os
import tempfile
import time

import pytest

from hyperlog import log, HyperLog


def test_basic_logging():
    """Test basic logging functionality."""
    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")

    log.success("Success message with Loguru!")


def test_custom_level():
    """Test adding custom log levels."""
    log.add_level("SUCCESS", 25, color="<green>")
    log.add_level("TRACE", 5, color="<magenta>")

    log.log("SUCCESS", "✨ Custom level works!")
    log.success("Using the convenience method")
    log.trace("Very detailed debugging")


def test_prefix():
    """Test prefix functionality."""
    original_prefix = log.prefix
    log.prefix = "[TestModule] "
    log.info("This should have a prefix")
    log.prefix = original_prefix  # Reset


def test_decorator_simple():
    """Test simple decorator usage."""

    @log()
    def simple_function():
        time.sleep(0.1)
        return "done"

    result = simple_function()
    assert result == "done"


def test_decorator_with_options():
    """Test decorator with options."""

    @log(level="DEBUG", tags=["test", "timing"], threshold_ms=50, verbose=True)
    def slow_function(name: str, value: int = 42):
        log.info(f"Inside {name}")
        time.sleep(0.1)
        return f"completed: {value}"

    result = slow_function("test_func", value=100)
    assert result == "completed: 100"


def test_decorator_with_exception():
    """Test decorator exception handling."""

    @log(catch=True)
    def failing_function(x: int, y: int):
        result = x / y  # Shows x, y in traceback diagnostics
        return result

    try:
        failing_function(10, 0)
    except ZeroDivisionError:
        log.info("Exception was caught and re-raised as expected")


def test_manual_timing():
    """Test manual timing with mark/elapsed."""
    log.mark("operation")
    time.sleep(0.1)
    duration = log.elapsed("operation", log_level="INFO")
    assert duration > 0.1


def test_timer_context():
    """Test timer context manager."""
    with log.timer("database_query", log_level="INFO", unit="ms"):
        time.sleep(0.05)
        # Simulate database work
        pass


def test_checkpoints():
    """Test checkpoint functionality."""
    log.checkpoint("Start", reset=True)

    for i in range(3):
        time.sleep(0.05)
        log.checkpoint(f"Step {i + 1}")


@pytest.mark.asyncio
async def test_async_decorator():
    """Test decorator with async functions."""

    @log(threshold_ms=10, tags=["async", "api"])
    async def async_function(delay: float):
        await asyncio.sleep(delay)
        log.info("Async work done")
        return "async result"

    result = await async_function(0.05)
    assert result == "async result"


def test_structured_logging():
    """Test structured logging with extra fields."""
    # Structured logging with extra fields
    log.info("User action", user_id=123, action="login", ip="1.2.3.4")

    # Binding context
    bound_log = log.bind(request_id="xyz-789")
    bound_log.info("This includes request_id")
    bound_log.warning("So does this")


def test_bind_basic():
    """Test basic bind functionality."""
    # Create a new instance for testing to avoid pollution
    test_log = HyperLog()
    test_log.bind(service="api", version="1.0")
    test_log.info("Request received")
    
    # Test that fields are stored
    bound_fields = test_log.get_bound_fields()
    assert bound_fields["service"] == "api"
    assert bound_fields["version"] == "1.0"
    
    # Clean up
    test_log.unbind_all()


def test_bind_overwrite():
    """Test overwriting bound fields."""
    test_log = HyperLog()
    test_log.bind(service="api", version="1.0")
    test_log.bind(version="2.0")  # Overwrite version
    
    bound_fields = test_log.get_bound_fields()
    assert bound_fields["service"] == "api"
    assert bound_fields["version"] == "2.0"
    
    # Clean up
    test_log.unbind_all()


def test_unbind_specific():
    """Test unbinding specific fields."""
    test_log = HyperLog()
    test_log.bind(service="api", user="john", session="123")
    test_log.unbind("user")
    
    bound_fields = test_log.get_bound_fields()
    assert "service" in bound_fields
    assert "session" in bound_fields
    assert "user" not in bound_fields
    
    # Clean up
    test_log.unbind_all()


def test_unbind_all():
    """Test unbinding all fields."""
    test_log = HyperLog()
    test_log.bind(service="api", user="john", session="123")
    test_log.unbind_all()
    
    bound_fields = test_log.get_bound_fields()
    assert len(bound_fields) == 0


def test_bind_mutability():
    """Test that bind modifies current instance."""
    test_log = HyperLog()
    result = test_log.bind(service="api")
    
    # Should return same instance
    assert result is test_log
    
    # Add another field
    test_log.bind(version="1.0")
    
    # Should have both fields
    bound_fields = test_log.get_bound_fields()
    assert bound_fields["service"] == "api"
    assert bound_fields["version"] == "1.0"
    
    # Clean up
    test_log.unbind_all()




def test_has_bound_field():
    """Test checking for bound field existence."""
    test_log = HyperLog()
    test_log.bind(service="api")
    
    assert test_log.has_bound_field("service")
    assert not test_log.has_bound_field("version")
    
    # Clean up
    test_log.unbind_all()


def test_file_logging():
    """Test file logging with rotation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test.log")

        # Add file handler with correct retention format
        handler_id = log.add_file(
            log_file,
            rotation="10 KB",  # Small size for testing
            retention=3,  # Keep 3 files
            level="DEBUG",
        )

        # Log some messages
        for i in range(100):
            log.info(f"Test message {i}")

        # Remove handler
        log.remove(handler_id)

        # Check that log file exists
        assert os.path.exists(log_file)


def test_method_chaining():
    """Test method chaining."""
    # All logging methods should return self for chaining
    result = log.mark("chain").info("Message 1").debug("Message 2").checkpoint("Done")
    assert result is log


def test_lazy_evaluation():
    """Test lazy evaluation of expensive operations."""
    log.add_level("TRACE", 5, color="<dim>")

    call_count = 0

    def expensive_operation():
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)
        return {"expensive": "data"}

    # This should not call expensive_operation if TRACE is not enabled
    log.trace("Data: {}", lambda: expensive_operation())

    # If TRACE is not enabled, call_count should still be 0
    trace_level = log.level("TRACE")
    current_level = log.level("INFO")
    if trace_level.no > current_level.no:
        assert call_count == 0


def test_exception_catching():
    """Test the catch decorator."""

    @log.catch
    def dangerous_function():
        raise ValueError("This is caught and logged")

    # This should not raise
    dangerous_function()


def test_performance_threshold():
    """Test performance threshold filtering."""
    log_count = [0]  # Use list to avoid nonlocal in older Python

    # Patch the _log_for_function method to count calls
    original_log_for_function = log._log_for_function

    def counting_log_for_function(func, level, msg, *args, **kwargs):
        if "completed in" in msg:
            log_count[0] += 1
        return original_log_for_function(func, level, msg, *args, **kwargs)

    log._log_for_function = counting_log_for_function

    @log(threshold_ms=100)
    def sometimes_slow(delay: float):
        time.sleep(delay)
        return "done"

    # Fast execution - should not log
    sometimes_slow(0.05)
    fast_count = log_count[0]

    # Slow execution - should log
    sometimes_slow(0.15)
    slow_count = log_count[0]

    # Restore original
    log._log_for_function = original_log_for_function

    # Should have logged once more for the slow execution
    assert slow_count == fast_count + 1


if __name__ == "__main__":
    # Run all tests
    print("Testing HyperLog functionality...\n")

    # Basic tests
    test_basic_logging()
    test_custom_level()
    test_prefix()
    test_decorator_simple()
    test_decorator_with_options()
    test_decorator_with_exception()

    # Timing tests
    test_manual_timing()
    test_timer_context()
    test_checkpoints()

    # Advanced tests
    test_structured_logging()
    test_bind_basic()
    test_bind_overwrite()
    test_unbind_specific()
    test_unbind_all()
    test_bind_mutability()
    test_has_bound_field()
    test_file_logging()
    test_method_chaining()
    test_lazy_evaluation()
    test_exception_catching()
    test_performance_threshold()

    # Async test
    asyncio.run(test_async_decorator())

    print("\n✅ All tests completed!")
