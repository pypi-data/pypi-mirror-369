"""Module for decorators used in the MSPac GUI model."""
import functools


def fallback(fallback_func):
    """Handle exceptions and call a fallback function."""

    def decorator(func):
        """Wrap a function to handle exceptions and call a fallback function."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self = args[0]  # assuming the first argument is `self`
                self.logger.log.error(f"Failed to execute {func.__name__}: {e}")
                return fallback_func(self)

        return wrapper

    return decorator
