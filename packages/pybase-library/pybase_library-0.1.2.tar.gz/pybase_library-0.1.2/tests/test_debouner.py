import time
from unittest.mock import Mock

from pybase_library.core.debouner import (
    MemoryDebouner,
    ThrottleDebouner,
    debounce,
    throttle,
)


class TestMemoryDebouner:
    """Test cases for MemoryDebouner class."""

    def test_debounce_delays_execution(self):
        """Test that debounce delays function execution."""
        debouncer = MemoryDebouner()
        mock_func = Mock()

        @debouncer.debounce(0.1)
        def test_func():
            mock_func()

        # Call function multiple times quickly
        test_func()
        test_func()
        test_func()

        # Should not be called yet
        assert mock_func.call_count == 0

        # Wait for debounce delay
        time.sleep(0.15)

        # Should be called only once
        assert mock_func.call_count == 1

    def test_debounce_cancels_previous_calls(self):
        """Test that new calls cancel previous pending calls."""
        debouncer = MemoryDebouner()
        mock_func = Mock()

        @debouncer.debounce(0.2)
        def test_func(value):
            mock_func(value)

        # Call with different values
        test_func("first")
        time.sleep(0.1)  # Wait half the debounce time
        test_func("second")
        # Wait for debounce delay
        time.sleep(0.25)

        # Should only call with the last value
        mock_func.assert_called_once_with("second")

    def test_cancel_all(self):
        """Test canceling all pending debounced calls."""
        debouncer = MemoryDebouner()
        mock_func = Mock()

        @debouncer.debounce(0.2)
        def test_func():
            mock_func()

        test_func()
        debouncer.cancel_all()

        # Wait longer than debounce delay
        time.sleep(0.3)

        # Should not be called
        assert mock_func.call_count == 0

    def test_cancel_specific_key(self):
        """Test canceling a specific debounced call."""
        debouncer = MemoryDebouner()
        mock_func1 = Mock()
        mock_func2 = Mock()

        @debouncer.debounce(0.2, key="func1")
        def test_func1():
            mock_func1()

        @debouncer.debounce(0.2, key="func2")
        def test_func2():
            mock_func2()

        test_func1()
        test_func2()

        # Cancel only func1
        result = debouncer.cancel("func1")
        assert result is True

        # Wait for debounce delay
        time.sleep(0.25)

        # Only func2 should be called
        assert mock_func1.call_count == 0
        assert mock_func2.call_count == 1


class TestThrottleDebouner:
    """Test cases for ThrottleDebouner class."""

    def test_throttle_limits_execution_frequency(self):
        """Test that throttle limits function execution frequency."""
        throttler = ThrottleDebouner()
        mock_func = Mock()

        @throttler.debounce(0.1)
        def test_func():
            mock_func()

        # Call function multiple times quickly
        test_func()  # Should execute
        test_func()  # Should be ignored
        test_func()  # Should be ignored

        assert mock_func.call_count == 1

        # Wait for throttle delay
        time.sleep(0.15)

        test_func()  # Should execute again
        assert mock_func.call_count == 2

    def test_throttle_reset(self):
        """Test resetting throttle state."""
        throttler = ThrottleDebouner()
        mock_func = Mock()

        @throttler.debounce(0.2, key="test_func")
        def test_func():
            mock_func()

        test_func()  # Should execute
        assert mock_func.call_count == 1

        # Reset throttle state
        throttler.reset("test_func")

        test_func()  # Should execute immediately after reset
        assert mock_func.call_count == 2


class TestConvenienceDecorators:
    """Test cases for convenience decorators."""

    def test_debounce_decorator(self):
        """Test the convenience debounce decorator."""
        mock_func = Mock()

        @debounce(0.1)
        def test_func(value):
            mock_func(value)

        test_func("test")
        assert mock_func.call_count == 0

        time.sleep(0.15)
        mock_func.assert_called_once_with("test")

    def test_throttle_decorator(self):
        """Test the convenience throttle decorator."""
        mock_func = Mock()

        @throttle(0.1)
        def test_func():
            mock_func()

        test_func()  # Should execute
        test_func()  # Should be ignored

        assert mock_func.call_count == 1


class TestRealWorldUsage:
    """Test real-world usage scenarios."""

    def test_search_debounce_scenario(self):
        """Test a typical search debounce scenario."""
        search_calls = []

        @debounce(0.1)
        def search(query: str):
            search_calls.append(query)

        # Simulate user typing
        search("a")
        search("ap")
        search("app")
        search("appl")
        search("apple")

        # No searches should have been executed yet
        assert len(search_calls) == 0

        # Wait for debounce
        time.sleep(0.15)

        # Only the final search should execute
        assert search_calls == ["apple"]

    def test_api_throttle_scenario(self):
        """Test a typical API throttling scenario."""
        api_calls = []

        @throttle(0.1)
        def api_call(data):
            api_calls.append(data)

        # Simulate rapid API calls
        api_call("data1")  # Should execute
        api_call("data2")  # Should be ignored
        api_call("data3")  # Should be ignored

        assert api_calls == ["data1"]

        # Wait for throttle to reset
        time.sleep(0.15)

        api_call("data4")  # Should execute
        assert api_calls == ["data1", "data4"]
