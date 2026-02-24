from __future__ import annotations

import datetime
import typing

from ongaku.abc.routeplanner import IPBlockType
from ongaku.abc.routeplanner import RoutePlannerType
from ongaku.impl.routeplanner import FailingAddress
from ongaku.impl.routeplanner import IPBlock
from ongaku.impl.routeplanner import RoutePlannerDetails
from ongaku.impl.routeplanner import RoutePlannerStatus


def test_routeplanner_status():
    ip_block = IPBlock(IPBlockType.INET_4_ADDRESS, "size")
    failing_address = FailingAddress(
        "failing_address",
        datetime.datetime.now(),
        "failing_time",
    )
    routeplanner_details = RoutePlannerDetails(
        ip_block,
        [failing_address],
        "rotate_index",
        "ip_index",
        "current_address",
        "current_address_index",
        "block_index",
    )
    routeplanner_status = RoutePlannerStatus(
        RoutePlannerType.ROTATING_ROUTE_PLANNER,
        routeplanner_details,
    )

    assert routeplanner_status.cls == RoutePlannerType.ROTATING_ROUTE_PLANNER
    assert routeplanner_status.details == routeplanner_details


def test_routeplanner_details():
    ip_block = IPBlock(IPBlockType.INET_4_ADDRESS, "size")
    failing_address = FailingAddress(
        "failing_address",
        datetime.datetime.now(),
        "failing_time",
    )
    routeplanner_details = RoutePlannerDetails(
        ip_block,
        [failing_address],
        "rotate_index",
        "ip_index",
        "current_address",
        "current_address_index",
        "block_index",
    )

    assert routeplanner_details.ip_block == ip_block
    assert isinstance(routeplanner_details.failing_addresses, typing.Sequence)
    assert len(routeplanner_details.failing_addresses) == 1
    assert routeplanner_details.failing_addresses[0] == failing_address
    assert routeplanner_details.rotate_index == "rotate_index"
    assert routeplanner_details.ip_index == "ip_index"
    assert routeplanner_details.current_address == "current_address"
    assert routeplanner_details.current_address_index == "current_address_index"
    assert routeplanner_details.block_index == "block_index"


def test_ip_block():
    ip_block = IPBlock(IPBlockType.INET_4_ADDRESS, "size")

    assert ip_block.type == IPBlockType.INET_4_ADDRESS
    assert ip_block.size == "size"


def test_failing_address():
    time = datetime.datetime.now()
    failing_address = FailingAddress("failing_address", time, "failing_time")

    assert failing_address.address == "failing_address"
    assert failing_address.timestamp == time
    assert failing_address.time == "failing_time"
