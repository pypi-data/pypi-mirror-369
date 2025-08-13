"""
Quick test to verify HyperLog works correctly
"""

import time

from hyperlog import log

print("HyperLog powered by Loguru!")
print("-" * 50)

# Test 1: Basic logging
log.info("Basic logging works!")

# Test 2: Custom levels
log.add_level("SUCCESS", 25)
log.success("Custom level works!")

# Test 3: Timing
log.mark("test")
time.sleep(0.1)
log.elapsed("test", log_level="INFO")

# Test 4: Timer context
with log.timer("operation", log_level="INFO"):
    time.sleep(0.05)


# Test 5: Decorator
@log()
def my_function():
    log.info("Inside decorated function")
    return "done"


result = my_function()
print(f"Function returned: {result}")

print("-" * 50)
print("✅ All basic tests passed!")
