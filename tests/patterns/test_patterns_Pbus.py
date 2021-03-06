import time

import pytest
import uqbar.strings

import supriya.assets.synthdefs
import supriya.nonrealtime
import supriya.patterns
import supriya.ugens
from supriya import Parameter, SynthDefBuilder

pbus_01 = supriya.patterns.Pbus(
    pattern=supriya.patterns.Pbind(
        amplitude=1.0,
        duration=supriya.patterns.Pseq([1.0, 2.0, 3.0], 1),
        frequency=supriya.patterns.Pseq([440, 660, 880], 1),
    ),
    release_time=0.25,
)


pbus_02 = supriya.patterns.Pbus(
    supriya.patterns.Pmono(
        amplitude=1.0,
        duration=0.75,
        frequency=supriya.patterns.Pseq([222, 333, 444], 1),
    )
)


def test___iter___01():
    events = list(pbus_01)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        NoteEvent(
            amplitude=1.0,
            delta=1.0,
            duration=1.0,
            frequency=440,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        NoteEvent(
            amplitude=1.0,
            delta=2.0,
            duration=2.0,
            frequency=660,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('E'),
            )
        NoteEvent(
            amplitude=1.0,
            delta=3.0,
            duration=3.0,
            frequency=880,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('F'),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test___iter___02():
    events = list(pbus_02)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        NoteEvent(
            amplitude=1.0,
            delta=0.75,
            duration=0.75,
            frequency=222,
            is_stop=False,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        NoteEvent(
            amplitude=1.0,
            delta=0.75,
            duration=0.75,
            frequency=333,
            is_stop=False,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        NoteEvent(
            amplitude=1.0,
            delta=0.75,
            duration=0.75,
            frequency=444,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test_send_01a():
    events = pytest.helpers.setup_pattern_send(pbus_01, iterations=1)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test_send_01b():
    events = pytest.helpers.setup_pattern_send(pbus_01, iterations=2)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        NoteEvent(
            amplitude=1.0,
            delta=1.0,
            duration=1.0,
            frequency=440,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test_send_02a():
    events = pytest.helpers.setup_pattern_send(pbus_02, iterations=1)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test_send_02b():
    events = pytest.helpers.setup_pattern_send(pbus_02, iterations=2)
    assert pytest.helpers.get_objects_as_string(
        events, replace_uuids=True
    ) == uqbar.strings.normalize(
        """
        CompositeEvent(
            events=(
                BusEvent(
                    calculation_rate=CalculationRate.AUDIO,
                    channel_count=2,
                    uuid=UUID('A'),
                    ),
                GroupEvent(
                    uuid=UUID('B'),
                    ),
                SynthEvent(
                    add_action=AddAction.ADD_AFTER,
                    amplitude=1.0,
                    fade_time=0.25,
                    in_=UUID('A'),
                    synthdef=<SynthDef: system_link_audio_2>,
                    target_node=UUID('B'),
                    uuid=UUID('C'),
                    ),
                ),
            )
        NoteEvent(
            amplitude=1.0,
            delta=0.75,
            duration=0.75,
            frequency=222,
            is_stop=False,
            out=UUID('A'),
            target_node=UUID('B'),
            uuid=UUID('D'),
            )
        CompositeEvent(
            events=(
                SynthEvent(
                    is_stop=True,
                    uuid=UUID('C'),
                    ),
                NullEvent(
                    delta=0.25,
                    ),
                GroupEvent(
                    is_stop=True,
                    uuid=UUID('B'),
                    ),
                BusEvent(
                    calculation_rate=None,
                    channel_count=None,
                    is_stop=True,
                    uuid=UUID('A'),
                    ),
                ),
            is_stop=True,
            )
        """
    )


def test_manual_incommunicado():
    lists, deltas = pytest.helpers.manual_incommunicado(pbus_01)
    assert lists == [
        [
            10,
            [
                ["/g_new", 1000, 0, 1],
                [
                    "/s_new",
                    "system_link_audio_2",
                    1001,
                    3,
                    1000,
                    "fade_time",
                    0.25,
                    "in_",
                    0,
                ],
                [
                    "/s_new",
                    "default",
                    1002,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    440,
                    "out",
                    0,
                ],
            ],
        ],
        [
            11.0,
            [
                ["/n_set", 1002, "gate", 0],
                [
                    "/s_new",
                    "default",
                    1003,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    660,
                    "out",
                    0,
                ],
            ],
        ],
        [
            13.0,
            [
                ["/n_set", 1003, "gate", 0],
                [
                    "/s_new",
                    "default",
                    1004,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    880,
                    "out",
                    0,
                ],
            ],
        ],
        [16.0, [["/n_set", 1004, "gate", 0], ["/n_free", 1001]]],
        [16.25, [["/n_free", 1000]]],
    ]
    assert deltas == [1.0, 2.0, 3.0, 0.25, None]


def test_manual_communicado_pbind_01(server):
    player = supriya.patterns.EventPlayer(pbus_01, server=server)
    # Initial State
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
    """
    )
    # Step 1
    moment = pytest.helpers.make_moment(0)
    player(moment, moment)
    server.sync()
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1002 default
                        out: 16.0, amplitude: 1.0, frequency: 440.0, gate: 1.0, pan: 0.5
                1001 system_link_audio_2
                    done_action: 2.0, fade_time: 0.25, gate: 1.0, in_: 16.0, out: 0.0
    """
    )
    # Step 2
    moment = pytest.helpers.make_moment(0)
    player(moment, moment)
    server.sync()
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1003 default
                        out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 1.0, pan: 0.5
                    1002 default
                        out: 16.0, amplitude: 1.0, frequency: 440.0, gate: 0.0, pan: 0.5
                1001 system_link_audio_2
                    done_action: 2.0, fade_time: 0.25, gate: 1.0, in_: 16.0, out: 0.0
    """
    )
    # Wait for termination
    time.sleep(0.5)
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1003 default
                        out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 1.0, pan: 0.5
                1001 system_link_audio_2
                    done_action: 2.0, fade_time: 0.25, gate: 1.0, in_: 16.0, out: 0.0
    """
    )
    # Step 3
    moment = pytest.helpers.make_moment(0)
    player(moment, moment)
    server.sync()
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1004 default
                        out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 1.0, pan: 0.5
                    1003 default
                        out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 0.0, pan: 0.5
                1001 system_link_audio_2
                    done_action: 2.0, fade_time: 0.25, gate: 1.0, in_: 16.0, out: 0.0
    """
    )
    # Wait for termination
    time.sleep(0.5)
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1004 default
                        out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 1.0, pan: 0.5
                1001 system_link_audio_2
                    done_action: 2.0, fade_time: 0.25, gate: 1.0, in_: 16.0, out: 0.0
    """
    )
    # Step 4
    moment = pytest.helpers.make_moment(0)
    player(moment, moment)
    server.sync()
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
                    1004 default
                        out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 0.0, pan: 0.5
    """
    )
    # Wait for termination
    time.sleep(0.5)
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
                1000 group
    """
    )
    # Step 4
    moment = pytest.helpers.make_moment(0)
    player(moment, moment)
    server.sync()
    server_state = str(server.query_remote_nodes(include_controls=True))
    assert server_state == uqbar.strings.normalize(
        r"""
        NODE TREE 0 group
            1 group
    """
    )


def test_nonrealtime_01a():
    session = supriya.nonrealtime.Session()
    with session.at(0):
        final_offset = session.inscribe(pbus_01)
    d_recv_commands = pytest.helpers.build_d_recv_commands(
        [supriya.assets.synthdefs.system_link_audio_2, supriya.assets.synthdefs.default]
    )
    assert session.to_lists() == [
        [
            0.0,
            [
                *d_recv_commands,
                ["/g_new", 1000, 0, 0],
                [
                    "/s_new",
                    "38a2c79fc9d58d06e361337163a4e80f",
                    1001,
                    3,
                    1000,
                    "fade_time",
                    0.25,
                    "in_",
                    16,
                ],
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1002,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    440,
                    "out",
                    16,
                ],
            ],
        ],
        [
            1.0,
            [
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1003,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    660,
                    "out",
                    16,
                ],
                ["/n_set", 1002, "gate", 0],
            ],
        ],
        [
            3.0,
            [
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1004,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    880,
                    "out",
                    16,
                ],
                ["/n_set", 1003, "gate", 0],
            ],
        ],
        [6.0, [["/n_set", 1001, "gate", 0], ["/n_set", 1004, "gate", 0]]],
        [6.25, [["/n_free", 1000], [0]]],
    ]
    assert final_offset == 6.25


def test_nonrealtime_01b():
    session = supriya.nonrealtime.Session()
    with session.at(0):
        final_offset = session.inscribe(pbus_01, duration=3)
    d_recv_commands = pytest.helpers.build_d_recv_commands(
        [supriya.assets.synthdefs.system_link_audio_2, supriya.assets.synthdefs.default]
    )
    assert session.to_lists() == [
        [
            0.0,
            [
                *d_recv_commands,
                ["/g_new", 1000, 0, 0],
                [
                    "/s_new",
                    "38a2c79fc9d58d06e361337163a4e80f",
                    1001,
                    3,
                    1000,
                    "fade_time",
                    0.25,
                    "in_",
                    16,
                ],
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1002,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    440,
                    "out",
                    16,
                ],
            ],
        ],
        [
            1.0,
            [
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1003,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    660,
                    "out",
                    16,
                ],
                ["/n_set", 1002, "gate", 0],
            ],
        ],
        [3.0, [["/n_set", 1001, "gate", 0], ["/n_set", 1003, "gate", 0]]],
        [3.25, [["/n_free", 1000], [0]]],
    ]
    assert final_offset == 3.25


def test_nonrealtime_01c():
    session = supriya.nonrealtime.Session()
    with session.at(0):
        final_offset = session.inscribe(pbus_01, duration=2)
    d_recv_commands = pytest.helpers.build_d_recv_commands(
        [supriya.assets.synthdefs.system_link_audio_2, supriya.assets.synthdefs.default]
    )
    assert session.to_lists() == [
        [
            0.0,
            [
                *d_recv_commands,
                ["/g_new", 1000, 0, 0],
                [
                    "/s_new",
                    "38a2c79fc9d58d06e361337163a4e80f",
                    1001,
                    3,
                    1000,
                    "fade_time",
                    0.25,
                    "in_",
                    16,
                ],
                [
                    "/s_new",
                    "da0982184cc8fa54cf9d288a0fe1f6ca",
                    1002,
                    0,
                    1000,
                    "amplitude",
                    1.0,
                    "frequency",
                    440,
                    "out",
                    16,
                ],
            ],
        ],
        [1.0, [["/n_set", 1001, "gate", 0], ["/n_set", 1002, "gate", 0]]],
        [1.25, [["/n_free", 1000], [0]]],
    ]
    assert final_offset == 1.25


def test_nonrealtime_releasetime():
    with SynthDefBuilder(out=Parameter(parameter_rate="SCALAR", value=0)) as builder:
        supriya.ugens.Line.kr(duration=2),
        supriya.ugens.Out.ar(bus=builder["out"], source=supriya.ugens.DC.ar(1))
    dc_synthdef = builder.build()
    pattern = supriya.patterns.Pbus(
        supriya.patterns.Pbind(delta=1, duration=1, synthdef=dc_synthdef),
        release_time=1,
    )
    session = supriya.nonrealtime.Session(0, 1)
    with session.at(0):
        session.inscribe(pattern, duration=1)
    d_recv_commands = pytest.helpers.build_d_recv_commands(
        [supriya.assets.synthdefs.system_link_audio_1, dc_synthdef]
    )
    assert session.to_lists() == [
        [
            0.0,
            [
                *d_recv_commands,
                ["/g_new", 1000, 0, 0],
                [
                    "/s_new",
                    supriya.assets.synthdefs.system_link_audio_1.anonymous_name,
                    1001,
                    3,
                    1000,
                    "fade_time",
                    1.0,
                    "in_",
                    1,
                ],
                ["/s_new", dc_synthdef.anonymous_name, 1002, 0, 1000, "out", 1],
            ],
        ],
        [1.0, [["/n_free", 1002], ["/n_set", 1001, "gate", 0]]],
        [2.0, [["/n_free", 1000], [0]]],
    ]
