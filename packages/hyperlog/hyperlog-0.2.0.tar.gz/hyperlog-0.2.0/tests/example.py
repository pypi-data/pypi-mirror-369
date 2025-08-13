"""
Example demonstrating HyperLog with Loguru power.
"""

import random
import time

from hyperlog import log

# Set a prefix for this module
log.prefix = "[DataPipeline] "

# Add a custom log level
log.add_level("SUCCESS", 25, color="<green>")
log.add_level("TRACE", 5, color="<magenta>")

# Add file logging with rotation
log.add_file("pipeline.log", rotation="100 MB", retention="1 week")
log.add_file("errors.log", level="ERROR", rotation="10 MB")


@log(level="DEBUG", tags=["etl", "critical"], threshold_ms=100, catch=True)
def process_data(source: str, multiplier: float = 1.5):
    """Process data from the given source with automatic exception handling."""
    log.mark("start")
    log.debug(f"Starting data processing from {source}")

    # Add context that will be included in all logs within this function
    bound_log = log.bind(source=source, multiplier=multiplier)

    # Simulate fetching data with structured logging
    with log.timer("fetch"):
        bound_log.info("Fetching data...", phase="fetch", source=source)
        time.sleep(random.uniform(0.1, 0.3))
        data = {"records": 1000, "source": source, "items": list(range(10))}

    # Process in batches with checkpoints
    log.checkpoint("Processing", reset=True)

    for i in range(5):
        time.sleep(random.uniform(0.05, 0.1))
        log.checkpoint(f"Batch {i + 1}/5")

        # Simulate a potential error to show exception context
        if i == 3 and random.random() > 0.7:
            batch_size = len(data["items"])
            current_index = i * batch_size
            # This will show all local variables in the traceback!
            raise ValueError(
                f"Simulated batch processing error at index {current_index}"
            )

    # Transform data with timing
    log.mark("transform")
    bound_log.info("Transforming data...", phase="transform")
    time.sleep(random.uniform(0.1, 0.2))

    # Calculate result - locals will be visible if this fails
    result = {
        "transformed": True,
        "records": data["records"],
        "final_value": data["records"] * multiplier,
    }

    log.elapsed("transform", unit="ms", log_level="trace")

    log.success(
        "✨ Pipeline complete!",
        records_processed=result["records"],
        final_value=result["final_value"],
    )
    log.elapsed("start", unit="s", log_level="info")

    return result


@log(verbose=True)  # Show function arguments
def simple_task(task_name: str, priority: int = 1):
    """A simple task that logs normally."""
    log.info(f"Executing {task_name}", priority=priority)
    time.sleep(0.05)
    return f"{task_name} completed"


def demonstrate_context():
    """Show context binding for request tracking."""
    # Use Loguru's context manager
    with log.context(request_id="req-123", user_id=456):
        log.info("Request started")

        with log.context(component="auth"):
            log.info("Checking authentication")
            time.sleep(0.05)
            log.info("Authentication successful")

        with log.context(component="database"):
            with log.timer("query"):
                log.info("Querying user data")
                time.sleep(0.1)

        log.info("Request completed")


def demonstrate_lazy_evaluation():
    """Show lazy evaluation for expensive operations."""

    def expensive_serialization():
        log.trace("Computing expensive value...")
        time.sleep(0.1)  # Simulate expensive operation
        return {"data": list(range(1000))}

    # This only runs if TRACE level is enabled
    log.trace("Expensive data: {}", lambda: expensive_serialization())
    log.debug("This always runs")


def main():
    """Run the example."""
    log.info("🚀 Starting HyperLog demonstration")

    # Show different log levels
    log.trace("Trace level message")
    log.debug("Debug level message")
    log.info("Info level message")
    log.success("Success level message")
    log.warning("[yellow]Warning level message[/yellow]")
    log.error("Error level message")

    # Demonstrate context management
    demonstrate_context()

    # Run simple task with verbose logging
    result = simple_task("data_cleanup", priority=5)
    log.debug(f"Simple task returned: {result}")

    # Run data pipeline
    try:
        data = process_data("database", multiplier=2.0)
        log.info(
            f"Processed {data['records']} records, final value: {data['final_value']}"
        )
    except Exception as e:
        # The decorator with catch=True already logged this with full context
        log.error(f"Pipeline failed: {e}")

    # Show manual timing
    log.mark("cleanup")
    log.info("Cleaning up resources...")
    time.sleep(0.1)
    log.elapsed("cleanup", log_level="debug")

    # Demonstrate lazy evaluation
    demonstrate_lazy_evaluation()

    # Method chaining
    log.mark("final").info("Preparing final report").checkpoint("Stage 1", reset=True)
    time.sleep(0.05)
    log.checkpoint("Stage 2").elapsed("final", unit="ms", log_level="trace")

    log.success("✅ Application finished successfully!")


if __name__ == "__main__":
    # Configure for more verbose output in the example
    log.level("TRACE")

    main()
