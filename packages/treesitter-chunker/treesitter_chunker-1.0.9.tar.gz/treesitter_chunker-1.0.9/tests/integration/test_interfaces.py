"""Tests for the integration test interfaces."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.integration.interfaces import (
    ConfigChangeObserver,
    ErrorPropagationMixin,
    ResourceTracker,
)


class TestErrorPropagationMixin:
    """Test the ErrorPropagationMixin interface."""

    @classmethod
    def test_capture_cross_module_error(cls):
        """Test capturing errors with full context."""
        mixin = ErrorPropagationMixin()
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            context = mixin.capture_cross_module_error(
                source_module="test.source",
                target_module="test.target",
                error=e,
            )
        assert context["source_module"] == "test.source"
        assert context["target_module"] == "test.target"
        assert context["error_type"] == "ValueError"
        assert context["error_message"] == "Test error message"
        assert isinstance(context["timestamp"], float)
        assert "traceback" in context["context_data"]
        assert "call_stack" in context["context_data"]
        traceback_str = "".join(context["context_data"]["traceback"])
        assert "ValueError: Test error message" in traceback_str

    @classmethod
    def test_verify_error_context(cls):
        """Test error context verification."""
        mixin = ErrorPropagationMixin()
        context = {
            "source_module": "test.source",
            "target_module": "test.target",
            "error_type": "RuntimeError",
            "timestamp": time.time(),
        }
        mixin.verify_error_context(
            context,
            {"source_module": "test.source", "error_type": "RuntimeError"},
        )
        with pytest.raises(AssertionError):
            mixin.verify_error_context(context, {"source_module": "wrong.module"})
        mixin.verify_error_context(context, {"timestamp": 12345.0})

    @classmethod
    def test_thread_safety(cls):
        """Test thread safety of error capture."""
        mixin = ErrorPropagationMixin()
        errors = []

        def capture_error(i):
            try:
                raise RuntimeError(f"Error {i}")
            except RuntimeError as e:
                context = mixin.capture_cross_module_error(
                    source_module=f"module_{i}",
                    target_module="target",
                    error=e,
                )
                errors.append(context)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(capture_error, i) for i in range(100)]
            for future in futures:
                future.result()
        assert len(errors) == 100
        sources = {e["source_module"] for e in errors}
        assert len(sources) == 100


class TestConfigChangeObserver:
    """Test the ConfigChangeObserver interface."""

    @classmethod
    def test_basic_config_change(cls):
        """Test recording configuration changes."""
        observer = ConfigChangeObserver()
        event = observer.on_config_change(
            config_key="parser_timeout",
            old_value=30,
            new_value=60,
        )
        assert event["config_path"] == "parser_timeout"
        assert event["old_value"] == 30
        assert event["new_value"] == 60
        assert "parser" in event["affected_modules"]
        assert "factory" in event["affected_modules"]
        assert isinstance(event["timestamp"], float)

    @classmethod
    def test_affected_modules_mapping(cls):
        """Test module impact determination."""
        observer = ConfigChangeObserver()
        modules = observer.get_affected_modules("chunk_types")
        assert "chunker" in modules
        assert "languages" in modules
        modules = observer.get_affected_modules("languages.python.chunk_types")
        assert "chunker" in modules
        assert "languages" in modules
        modules = observer.get_affected_modules("unknown.config.key")
        assert len(modules) == 5

    @classmethod
    def test_observer_pattern(cls):
        """Test observer registration and notification."""
        observer = ConfigChangeObserver()
        events_received = []

        def callback(event):
            events_received.append(event)

        observer.register_observer(callback)
        observer.on_config_change("test1", "old", "new")
        observer.on_config_change("test2", 10, 20)
        assert len(events_received) == 2
        assert events_received[0]["config_path"] == "test1"
        assert events_received[1]["config_path"] == "test2"

    @classmethod
    def test_change_log(cls):
        """Test change log retrieval."""
        observer = ConfigChangeObserver()
        observer.on_config_change("key1", "a", "b")
        observer.on_config_change("key2", 1, 2)
        observer.on_config_change("key3", True, False)
        log = observer.get_change_log()
        assert len(log) == 3
        log.append({"fake": "event"})
        assert len(observer.get_change_log()) == 3

    @classmethod
    def test_concurrent_changes(cls):
        """Test thread safety of config changes."""
        observer = ConfigChangeObserver()

        def make_changes(thread_id):
            for i in range(10):
                observer.on_config_change(f"key_{thread_id}_{i}", i, i + 1)

        threads = []
        for i in range(10):
            t = threading.Thread(target=make_changes, args=(i,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        log = observer.get_change_log()
        assert len(log) == 100


class TestResourceTracker:
    """Test the ResourceTracker interface."""

    @classmethod
    def test_track_and_release_resource(cls):
        """Test basic resource tracking."""
        tracker = ResourceTracker()
        resource = tracker.track_resource(
            module="test.module",
            resource_type="process",
            resource_id="proc_123",
        )
        assert resource["resource_id"] == "proc_123"
        assert resource["resource_type"] == "process"
        assert resource["owner_module"] == "test.module"
        assert resource["state"] == "active"
        assert isinstance(resource["created_at"], float)
        tracker.release_resource("proc_123")
        state = tracker.get_resource_state("proc_123")
        assert state["state"] == "released"
        assert "released_at" in state

    @classmethod
    def test_verify_cleanup(cls):
        """Test resource leak detection."""
        tracker = ResourceTracker()
        tracker.track_resource("module1", "file", "file1")
        tracker.track_resource("module1", "lock", "lock1")
        tracker.track_resource("module2", "process", "proc1")
        tracker.release_resource("file1")
        module1_leaks = tracker.verify_cleanup("module1")
        assert len(module1_leaks) == 1
        assert module1_leaks[0]["resource_id"] == "lock1"
        module2_leaks = tracker.verify_cleanup("module2")
        assert len(module2_leaks) == 1
        assert module2_leaks[0]["resource_id"] == "proc1"
        assert tracker.verify_cleanup("module3") == []

    @classmethod
    def test_resource_filtering(cls):
        """Test resource query filtering."""
        tracker = ResourceTracker()
        tracker.track_resource("mod1", "file", "f1")
        tracker.track_resource("mod1", "lock", "l1")
        tracker.track_resource("mod2", "file", "f2")
        tracker.track_resource("mod2", "process", "p1")
        tracker.release_resource("f1")
        tracker.release_resource("p1")
        mod1_resources = tracker.get_all_resources(module="mod1")
        assert len(mod1_resources) == 2
        active_resources = tracker.get_all_resources(state="active")
        assert len(active_resources) == 2
        assert all(r["state"] == "active" for r in active_resources)
        released_resources = tracker.get_all_resources(state="released")
        assert len(released_resources) == 2
        assert all(r["state"] == "released" for r in released_resources)
        mod1_active = tracker.get_all_resources(module="mod1", state="active")
        assert len(mod1_active) == 1
        assert mod1_active[0]["resource_id"] == "l1"

    @classmethod
    def test_allocation_order(cls):
        """Test that allocation order is preserved."""
        tracker = ResourceTracker()
        for i in range(10):
            tracker.track_resource("test", "resource", f"res_{i}")
        all_resources = tracker.get_all_resources()
        for i, resource in enumerate(all_resources):
            assert resource["resource_id"] == f"res_{i}"

    @classmethod
    def test_concurrent_resource_tracking(cls):
        """Test thread safety of resource tracking."""
        tracker = ResourceTracker()

        def track_resources(thread_id):
            for i in range(20):
                tracker.track_resource(
                    module=f"module_{thread_id}",
                    resource_type="thread_resource",
                    resource_id=f"res_{thread_id}_{i}",
                )
                if i % 2 == 0:
                    tracker.release_resource(f"res_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(track_resources, i) for i in range(5)]
            for future in futures:
                future.result()
        all_resources = tracker.get_all_resources()
        assert len(all_resources) == 100
        released = tracker.get_all_resources(state="released")
        assert len(released) == 50
