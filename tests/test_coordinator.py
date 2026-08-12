"""Tests for the Geocaching Plus coordinator."""

from types import SimpleNamespace
from unittest.mock import Mock

from custom_components.geocaching_plus.const import EVENT_NEW_OWNED_CACHE_LOG
from custom_components.geocaching_plus.coordinator import (
    GeocachingPlusData,
    GeocachingPlusDataUpdateCoordinator,
    GeocachingPlusOwnedCacheData,
)


def _log(
    reference_code: str,
    *,
    log_type_id: int = 2,
    log_type_name: str = "Found It",
) -> dict:
    """Create test log data."""
    return {
        "referenceCode": reference_code,
        "owner": {"username": "Test logger"},
        "loggedDate": "2026-08-12T08:00:00",
        "text": "Test log",
        "geocacheLogType": {
            "id": log_type_id,
            "name": log_type_name,
        },
        "imageCount": 0,
        "usedFavoritePoint": False,
        "url": f"https://coord.info/{reference_code}",
    }


def _owned_cache(
    logs: list[dict],
    *,
    maintenance_required: bool = False,
) -> GeocachingPlusOwnedCacheData:
    """Create owned-cache test data."""
    return GeocachingPlusOwnedCacheData(
        cache={
            "referenceCode": "GC12345",
            "name": "Test cache",
        },
        logs=logs,
        maintenance_required=maintenance_required,
    )


def _coordinator(previous_logs: list[dict] | None):
    """Create a minimal coordinator test object."""
    bus = SimpleNamespace(async_fire=Mock())
    coordinator = SimpleNamespace(
        hass=SimpleNamespace(bus=bus),
        data=None,
    )

    if previous_logs is not None:
        coordinator.data = GeocachingPlusData(
            status=Mock(),
            recent_logs=[],
            owned_caches=[_owned_cache(previous_logs)],
        )

    return coordinator


def _fire_events(coordinator, owned_caches) -> None:
    """Call the event method with a minimal coordinator object."""
    GeocachingPlusDataUpdateCoordinator._fire_new_owned_cache_log_events(
        coordinator,
        owned_caches,
    )


def test_no_event_during_first_update() -> None:
    """Test that existing logs do not fire events during initial update."""
    coordinator = _coordinator(None)

    _fire_events(coordinator, [_owned_cache([_log("GL1")])])

    coordinator.hass.bus.async_fire.assert_not_called()


def test_one_new_log_fires_one_event() -> None:
    """Test that one new log fires one event."""
    coordinator = _coordinator([_log("GL1")])

    _fire_events(
        coordinator,
        [_owned_cache([_log("GL2"), _log("GL1")])],
    )

    coordinator.hass.bus.async_fire.assert_called_once()
    event_type, event_data = coordinator.hass.bus.async_fire.call_args.args

    assert event_type == EVENT_NEW_OWNED_CACHE_LOG
    assert event_data["cache_code"] == "GC12345"
    assert event_data["log_reference_code"] == "GL2"
    assert event_data["logger"] == "Test logger"


def test_multiple_new_logs_fire_oldest_first() -> None:
    """Test that multiple new logs fire events in chronological order."""
    coordinator = _coordinator([_log("GL1")])

    _fire_events(
        coordinator,
        [_owned_cache([_log("GL3"), _log("GL2"), _log("GL1")])],
    )

    calls = coordinator.hass.bus.async_fire.call_args_list

    assert len(calls) == 2
    assert calls[0].args[1]["log_reference_code"] == "GL2"
    assert calls[1].args[1]["log_reference_code"] == "GL3"


def test_maintenance_event_contains_problem_status() -> None:
    """Test that a maintenance log includes maintenance status."""
    coordinator = _coordinator([_log("GL1")])
    maintenance_log = _log(
        "GL2",
        log_type_id=45,
        log_type_name="Needs Maintenance",
    )

    _fire_events(
        coordinator,
        [
            _owned_cache(
                [maintenance_log, _log("GL1")],
                maintenance_required=True,
            )
        ],
    )

    event_data = coordinator.hass.bus.async_fire.call_args.args[1]

    assert event_data["log_type_id"] == 45
    assert event_data["maintenance_required"] is True
