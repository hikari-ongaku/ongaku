from __future__ import annotations

from unittest import mock

from ongaku.routeplanner import FailingAddress
from ongaku.routeplanner import IPBlock
from ongaku.routeplanner import IPBlockType
from ongaku.routeplanner import RoutePlannerDetails
from ongaku.routeplanner import RoutePlannerStatus
from ongaku.routeplanner import RoutePlannerType


def test_routeplanner_status():
    mock_routeplanner_details = mock.Mock()

    routeplanner_status = RoutePlannerStatus(
        cls=RoutePlannerType.ROTATING_ROUTE_PLANNER,
        details=mock_routeplanner_details,
    )

    assert routeplanner_status.cls == RoutePlannerType.ROTATING_ROUTE_PLANNER
    assert routeplanner_status.details == mock_routeplanner_details


def test_routeplanner_details():
    mock_ip_block = mock.Mock()
    mock_failing_address = mock.Mock()

    routeplanner_details = RoutePlannerDetails(
        ip_block=mock_ip_block,
        failing_addresses=[mock_failing_address],
        rotate_index="rotate_index",
        ip_index="ip_index",
        current_address="current_address",
        current_address_index="current_address_index",
        block_index="block_index",
    )

    assert routeplanner_details.ip_block == mock_ip_block
    assert routeplanner_details.failing_addresses == [mock_failing_address]
    assert routeplanner_details.rotate_index == "rotate_index"
    assert routeplanner_details.ip_index == "ip_index"
    assert routeplanner_details.current_address == "current_address"
    assert routeplanner_details.current_address_index == "current_address_index"
    assert routeplanner_details.block_index == "block_index"


def test_ip_block():
    ip_block = IPBlock(
        type=IPBlockType.INET_4_ADDRESS,
        size="size",
    )

    assert ip_block.type == IPBlockType.INET_4_ADDRESS
    assert ip_block.size == "size"


def test_failing_address():
    mock_time = mock.Mock()
    failing_address = FailingAddress(
        address="failing_address",
        timestamp=mock_time,
        time="failing_time",
    )

    assert failing_address.address == "failing_address"
    assert failing_address.timestamp == mock_time
    assert failing_address.time == "failing_time"
