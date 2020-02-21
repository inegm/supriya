import asyncio
import logging
import random
import statistics

import pytest

from supriya.clock import AsyncTempoClock, TimeUnit

repeat_count = 5


@pytest.fixture(autouse=True)
def logger(caplog):
    caplog.set_level(logging.DEBUG, logger="supriya")


@pytest.fixture
async def tempo_clock(mocker):
    tempo_clock = AsyncTempoClock()
    tempo_clock.slop = 0.001
    mock = mocker.patch.object(AsyncTempoClock, "get_current_time")
    mock.return_value = 0.0
    yield tempo_clock
    await tempo_clock.stop()


def callback(
    current_moment,
    desired_moment,
    event,
    store,
    blow_up_at=None,
    delta=0.25,
    limit=4,
    time_unit=TimeUnit.BEATS,
    **kwargs,
):
    if event.invocations == blow_up_at:
        raise Exception
    store.append((current_moment, desired_moment, event))
    if limit is None:
        return delta, time_unit
    elif event.invocations < limit:
        return delta, time_unit
    return None


async def set_time_and_check(time_to_advance, tempo_clock, store):
    tempo_clock.get_current_time.return_value = time_to_advance
    await asyncio.sleep(tempo_clock.slop * 4)
    moments = []
    for current_moment, desired_moment, event in store:
        one = [
            "{}/{}".format(*current_moment.time_signature),
            current_moment.beats_per_minute,
        ]
        two = [
            current_moment.measure,
            round(current_moment.measure_offset, 10),
            current_moment.offset,
            current_moment.seconds,
        ]
        three = [
            desired_moment.measure,
            round(desired_moment.measure_offset, 10),
            desired_moment.offset,
            desired_moment.seconds,
        ]
        moments.append((one, two, three))
    return moments


def calculate_skew(store):
    skews = [
        abs(current_moment.seconds - desired_moment.seconds)
        for current_moment, desired_moment, event in store
    ]
    return {
        "min": min(skews),
        "mean": statistics.mean(skews),
        "median": statistics.median(skews),
        "stdev": statistics.stdev(skews),
        "max": max(skews),
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "schedule,start_clock_first,expected",
    [
        (True, True, [0.0, 0.25, 0.5, 0.75, 1.0]),
        (True, False, [0.0, 0.25, 0.5, 0.75, 1.0]),
        (False, True, [0.25, 0.5, 0.75, 1.0, 1.25]),
        (False, False, [0.0, 0.25, 0.5, 0.75, 1.0]),
    ],
)
@pytest.mark.timeout(5)
async def test_realtime_01(schedule, start_clock_first, expected):
    """
    Start clock, then schedule
    """
    store = []
    tempo_clock = AsyncTempoClock()
    assert not tempo_clock.is_running
    assert tempo_clock.beats_per_minute == 120
    if start_clock_first:
        await tempo_clock.start()
        assert tempo_clock.is_running
        assert tempo_clock.beats_per_minute == 120
    if schedule:
        tempo_clock.schedule(callback, schedule_at=0.0, args=[store])
    else:
        tempo_clock.cue(callback, quantization="1/4", args=[store])
    if not start_clock_first:
        await tempo_clock.start()
        assert tempo_clock.is_running
        assert tempo_clock.beats_per_minute == 120
    await asyncio.sleep(4)
    await tempo_clock.stop()
    assert not tempo_clock.is_running
    assert tempo_clock.beats_per_minute == 120
    assert len(store) == 5
    actual = [desired_moment.offset for current_moment, desired_moment, event in store]
    assert actual == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit,bpm_schedule,expected",
    [
        (2, [(0.375, 240)], [(0.0, 0.0), (0.25, 0.4375), (0.5, 0.6875)]),
        (2, [(0.5, 240)], [(0.0, 0.0), (0.25, 0.5), (0.5, 0.75)]),
    ],
)
async def test_realtime_02(limit, bpm_schedule, expected):
    store = []
    tempo_clock = AsyncTempoClock()
    tempo_clock.cue(
        callback, quantization="1/4", args=[store], kwargs=dict(limit=limit)
    )
    for schedule_at, beats_per_minute in bpm_schedule:
        tempo_clock.schedule_change(
            beats_per_minute=beats_per_minute,
            schedule_at=schedule_at,
            time_unit=TimeUnit.SECONDS,
        )
    await tempo_clock.start()
    await asyncio.sleep(2)
    await tempo_clock.stop()
    actual = [
        (
            desired_moment.offset,
            desired_moment.seconds - tempo_clock._state.initial_seconds,
        )
        for current_moment, desired_moment, event in store
    ]
    assert actual == expected


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_basic(tempo_clock):
    store = []
    await tempo_clock.start()
    tempo_clock.schedule(callback, schedule_at=0.0, args=[store])
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.75, 0.75, 1.5]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.75, 0.75, 1.5]),
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_two_procedures(tempo_clock):
    store_one = []
    store_two = []
    await tempo_clock.start()
    tempo_clock.schedule(callback, schedule_at=0.0, args=[store_one])
    tempo_clock.schedule(
        callback, schedule_at=0.1, args=[store_two], kwargs={"delta": 0.3}
    )
    assert await set_time_and_check(0.0, tempo_clock, store_one) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.0, tempo_clock, store_two) == []
    assert await set_time_and_check(0.5, tempo_clock, store_one) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(0.5, tempo_clock, store_two) == [
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.1, 0.1, 0.2])
    ]
    assert await set_time_and_check(1.0, tempo_clock, store_one) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
    ]
    assert await set_time_and_check(1.0, tempo_clock, store_two) == [
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.1, 0.1, 0.2]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.4, 0.4, 0.8]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store_one) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.75, 0.75, 1.5]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store_two) == [
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.1, 0.1, 0.2]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.4, 0.4, 0.8]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.7, 0.7, 1.4]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store_one) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.75, 0.75, 1.5]),
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store_two) == [
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.1, 0.1, 0.2]),
        (["4/4", 120.0], [1, 0.5, 0.5, 1.0], [1, 0.4, 0.4, 0.8]),
        (["4/4", 120.0], [1, 0.75, 0.75, 1.5], [1, 0.7, 0.7, 1.4]),
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_exception(tempo_clock):
    store = []
    await tempo_clock.start()
    tempo_clock.schedule(
        callback, schedule_at=0.0, args=[store], kwargs={"blow_up_at": 2}
    )
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_tempo(tempo_clock):
    store = []
    tempo_clock.schedule(callback, schedule_at=0.0, args=[store])
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    tempo_clock.change(beats_per_minute=60)
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.5], [1, 0.5, 0.5, 1.5]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.5], [1, 0.5, 0.5, 1.5]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_schedule_tempo_change(tempo_clock):
    store = []
    tempo_clock.schedule(callback, schedule_at=0.0, args=[store])
    tempo_clock.schedule_change(schedule_at=0.5, beats_per_minute=60)
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 60.0], [1, 0.75, 0.75, 2.0], [1, 0.75, 0.75, 2.0]),
    ]
    assert await set_time_and_check(2.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (["4/4", 60.0], [1, 0.5, 0.5, 1.0], [1, 0.5, 0.5, 1.0]),
        (["4/4", 60.0], [1, 0.75, 0.75, 2.0], [1, 0.75, 0.75, 2.0]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_cue_basic(tempo_clock):
    store = []
    await tempo_clock.start()
    tempo_clock.cue(callback, quantization=None, args=[store], kwargs={"limit": 0})
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.125, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.cue(callback, quantization="1/4", args=[store], kwargs={"limit": 0})
    tempo_clock.cue(callback, quantization="1M", args=[store], kwargs={"limit": 0})
    tempo_clock.cue(callback, quantization="1/2T", args=[store], kwargs={"limit": 0})
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
    ]
    assert await set_time_and_check(0.75, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (
            ["4/4", 120.0],
            [1, 0.375, 0.375, 0.75],
            [1, 0.3333333333, 0.3333333333333333, 0.6666666666666666],
        ),
    ]
    tempo_clock.cue(callback, quantization="1/2T", args=[store], kwargs={"limit": 0})
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (
            ["4/4", 120.0],
            [1, 0.375, 0.375, 0.75],
            [1, 0.3333333333, 0.3333333333333333, 0.6666666666666666],
        ),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (
            ["4/4", 120.0],
            [1, 0.375, 0.375, 0.75],
            [1, 0.3333333333, 0.3333333333333333, 0.6666666666666666],
        ),
        (
            ["4/4", 120.0],
            [1, 0.75, 0.75, 1.5],
            [1, 0.6666666667, 0.6666666666666666, 1.3333333333333333],
        ),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [1, 0.25, 0.25, 0.5], [1, 0.25, 0.25, 0.5]),
        (
            ["4/4", 120.0],
            [1, 0.375, 0.375, 0.75],
            [1, 0.3333333333, 0.3333333333333333, 0.6666666666666666],
        ),
        (
            ["4/4", 120.0],
            [1, 0.75, 0.75, 1.5],
            [1, 0.6666666667, 0.6666666666666666, 1.3333333333333333],
        ),
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_cue_measures(tempo_clock):
    """
    Measure-wise cueing aligns to offset 0.0
    """
    store = []
    await tempo_clock.start()
    tempo_clock.cue(callback, quantization="1M", args=[store], kwargs={"limit": 0})
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    assert await set_time_and_check(0.5, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.cue(callback, quantization="1M", args=[store], kwargs={"limit": 0})
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_cue_and_reschedule(tempo_clock):
    store = []
    await tempo_clock.start()
    assert await set_time_and_check(0.25, tempo_clock, store) == []
    tempo_clock.cue(callback, quantization="1M", args=[store], kwargs={"limit": 0})
    tempo_clock.cue(callback, quantization="2M", args=[store], kwargs={"limit": 0})
    tempo_clock.schedule_change(schedule_at=1.0, time_signature=(5, 4))
    assert await set_time_and_check(0.5, tempo_clock, store) == []
    assert await set_time_and_check(1.0, tempo_clock, store) == []
    assert await set_time_and_check(1.5, tempo_clock, store) == []
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0])
    ]
    assert await set_time_and_check(2.5, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0])
    ]
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0])
    ]
    assert await set_time_and_check(3.5, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0])
    ]
    assert await set_time_and_check(4.0, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0])
    ]
    assert await set_time_and_check(4.5, tempo_clock, store) == [
        (["5/4", 120.0], [2, 0.0, 1.0, 2.0], [2, 0.0, 1.0, 2.0]),
        (["5/4", 120.0], [3, 0.0, 2.25, 4.5], [3, 0.0, 2.25, 4.5]),
    ]


@pytest.mark.asyncio
async def test_cue_invalid(tempo_clock):
    await tempo_clock.start()
    with pytest.raises(ValueError):
        tempo_clock.cue(callback, quantization="BOGUS")


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_reschedule_earlier(tempo_clock):
    store = []
    await tempo_clock.start()
    assert await set_time_and_check(0.5, tempo_clock, store) == []
    event_id = tempo_clock.cue(
        callback, quantization="1M", args=[store], kwargs={"limit": 0}
    )
    await asyncio.sleep(tempo_clock.slop * 2)
    assert tempo_clock.peek().seconds == 2.0
    tempo_clock.reschedule(event_id, schedule_at=0.5)
    await asyncio.sleep(tempo_clock.slop * 2)
    assert tempo_clock.peek().seconds == 1.0
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 120.0], [2, 0.0, 1.0, 2.0], [1, 0.5, 0.5, 1.0])
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_reschedule_later(tempo_clock):
    store = []
    await tempo_clock.start()
    assert await set_time_and_check(0.5, tempo_clock, store) == []
    event_id = tempo_clock.cue(
        callback, quantization="1M", args=[store], kwargs={"limit": 0}
    )
    await asyncio.sleep(tempo_clock.slop * 2)
    assert tempo_clock.peek().seconds == 2.0
    tempo_clock.reschedule(event_id, schedule_at=1.5)
    await asyncio.sleep(tempo_clock.slop * 2)
    assert tempo_clock.peek().seconds == 3.0
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 120.0], [2, 0.5, 1.5, 3.0], [2, 0.5, 1.5, 3.0])
    ]


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_change_tempo_not_running(tempo_clock):
    assert tempo_clock.beats_per_minute == 120
    assert tempo_clock.time_signature == (4, 4)
    tempo_clock.change(beats_per_minute=135, time_signature=(3, 4))
    assert tempo_clock.beats_per_minute == 135
    assert tempo_clock.time_signature == (3, 4)


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_on_downbeat(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=2, time_signature=(3, 4))
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [3, 0.0, 2.0, 2.0], [3, 0.0, 2.0, 2.0]),
    ]
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [3, 0.0, 2.0, 2.0], [3, 0.0, 2.0, 2.0]),
        (["3/4", 240], [4, 0.25, 3.0, 3.0], [4, 0.0, 2.75, 2.75]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_on_downbeat_laggy(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=2, time_signature=(3, 4))
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [4, 0.0, 3.0, 3.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [4, 0.25, 3.0, 3.0], [3, 0.0, 2.0, 2.0]),
        (["3/4", 240], [4, 0.25, 3.0, 3.0], [4, 0.0, 2.75, 2.75]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_late(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=1.875, time_signature=(3, 4))
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
    ]
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [3, 0.125, 2.0, 2.0], [3, 0.0, 1.875, 1.875]),
    ]
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [3, 0.125, 2.0, 2.0], [3, 0.0, 1.875, 1.875]),
        (["3/4", 240], [4, 0.375, 3.0, 3.0], [4, 0.0, 2.625, 2.625]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_late_laggy(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=1.875, time_signature=(3, 4))
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [4, 0.0, 3.0, 3.0], [2, 0.0, 1.0, 1.0]),
        (["3/4", 240], [4, 0.375, 3.0, 3.0], [3, 0.0, 1.875, 1.875]),
        (["3/4", 240], [4, 0.375, 3.0, 3.0], [4, 0.0, 2.625, 2.625]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_early(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=1.125, time_signature=(5, 4))
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
    ]
    assert tempo_clock.time_signature == (4, 4)
    assert await set_time_and_check(2.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
    ]
    assert tempo_clock.time_signature == (5, 4)
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["5/4", 240], [3, 0.75, 3.0, 3.0], [3, 0.0, 2.25, 2.25]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_early_laggy(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=0.0,
        args=[store],
        kwargs={"delta": 1, "time_unit": TimeUnit.MEASURES},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0])
    ]
    tempo_clock.schedule_change(schedule_at=1.125, time_signature=(5, 4))
    assert await set_time_and_check(3.0, tempo_clock, store) == [
        (["4/4", 240], [1, 0.0, 0.0, 0.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [4, 0.0, 3.0, 3.0], [2, 0.0, 1.0, 1.0]),
        (["5/4", 240], [3, 0.75, 3.0, 3.0], [3, 0.0, 2.25, 2.25]),  # time travel
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_change_time_signature_shrinking(tempo_clock):
    """
    When shifting to a smaller time signature, if the desired measure offset is
    within that smaller time signature, maintain the desired measure and
    measure offset.
    """
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(callback, schedule_at=0.0, args=[store], kwargs={"limit": 12})
    tempo_clock.schedule_change(schedule_at=1.125, time_signature=(2, 4))
    await tempo_clock.start()
    assert await set_time_and_check(1.0, tempo_clock, store) == [
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.25, 0.25, 0.25]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.5, 0.5, 0.5]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.75, 0.75, 0.75]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
    ]
    assert await set_time_and_check(1.25, tempo_clock, store) == [
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.25, 0.25, 0.25]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.5, 0.5, 0.5]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.75, 0.75, 0.75]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["2/4", 240], [2, 0.25, 1.25, 1.25], [2, 0.25, 1.25, 1.25]),
    ]
    assert await set_time_and_check(1.5, tempo_clock, store) == [
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.0, 0.0, 0.0]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.25, 0.25, 0.25]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.5, 0.5, 0.5]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [1, 0.75, 0.75, 0.75]),
        (["4/4", 240], [2, 0.0, 1.0, 1.0], [2, 0.0, 1.0, 1.0]),
        (["2/4", 240], [2, 0.25, 1.25, 1.25], [2, 0.25, 1.25, 1.25]),
        (["2/4", 240], [3, 0.0, 1.5, 1.5], [3, 0.0, 1.5, 1.5]),
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_schedule_measure_relative(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=3,
        time_unit=TimeUnit.MEASURES,
        args=[store],
        kwargs={"limit": 0},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == []
    assert await set_time_and_check(4.0, tempo_clock, store) == [
        (["4/4", 240], [5, 0.0, 4.0, 4.0], [3, 0.0, 2.0, 2.0])
    ]


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
@pytest.mark.timeout(5)
async def test_schedule_seconds_relative(tempo_clock):
    store = []
    tempo_clock.change(beats_per_minute=240)
    tempo_clock.schedule(
        callback,
        schedule_at=1.234,
        time_unit=TimeUnit.SECONDS,
        args=[store],
        kwargs={"limit": 0},
    )
    await tempo_clock.start()
    assert await set_time_and_check(0.0, tempo_clock, store) == []
    assert await set_time_and_check(4.0, tempo_clock, store) == [
        (["4/4", 240], [5, 0.0, 4.0, 4.0], [2, 0.234, 1.234, 1.234])
    ]


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_cancel_invalid(tempo_clock):
    await tempo_clock.start()
    assert tempo_clock.cancel(1) is None


@pytest.mark.asyncio
async def test_slop(tempo_clock):
    assert tempo_clock.slop == 0.001
    tempo_clock.slop = 0.1
    assert tempo_clock.slop == 0.1
    with pytest.raises(ValueError):
        tempo_clock.slop = 0
    with pytest.raises(ValueError):
        tempo_clock.slop = -1.0


@pytest.mark.asyncio
async def test_start_and_restart(tempo_clock):
    assert not tempo_clock.is_running
    await tempo_clock.start()
    assert tempo_clock.is_running
    with pytest.raises(RuntimeError):
        await tempo_clock.start()
    assert tempo_clock.is_running


@pytest.mark.asyncio
async def test_stop_and_restop(tempo_clock):
    assert not tempo_clock.is_running
    await tempo_clock.start()
    assert tempo_clock.is_running
    await tempo_clock.stop()
    assert not tempo_clock.is_running
    await tempo_clock.stop()
    assert not tempo_clock.is_running


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=5)
async def test_clock_skew():
    tempo_clock = AsyncTempoClock()
    tempo_clock.slop = 0.001
    all_stats = []
    for _ in range(5):
        store = []
        for _ in range(20):
            delta = random.random() / 100
            tempo_clock.schedule(
                callback,
                schedule_at=random.random(),
                args=[store],
                kwargs={"limit": 100, "delta": delta, "time_unit": TimeUnit.SECONDS},
            )
        await tempo_clock.start()
        await asyncio.sleep(5.0)
        await tempo_clock.stop()
        stats = calculate_skew(store)
        print(" ".join(f"{key}: {value:f}" for key, value in stats.items()))
        all_stats.append(stats)
    threshold = tempo_clock.slop * 2.0
    assert all(stats["median"] < threshold for stats in all_stats)