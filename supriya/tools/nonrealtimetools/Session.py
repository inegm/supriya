# -*- encoding: utf-8 -*-
import bisect
import collections
import hashlib
import os
import shutil
import struct
import subprocess
import tempfile
from abjad.tools import timespantools
from supriya.tools import osctools
from supriya.tools import servertools
from supriya.tools import soundfiletools
from supriya.tools import synthdeftools
from supriya.tools.osctools.OscMixin import OscMixin


class Session(OscMixin):
    r'''A non-realtime session.

    ::

        >>> from supriya.tools import nonrealtimetools
        >>> session = nonrealtimetools.Session()

    ::

        >>> from supriya.tools import synthdeftools
        >>> from supriya.tools import ugentools
        >>> builder = synthdeftools.SynthDefBuilder(frequency=440)
        >>> with builder:
        ...     out = ugentools.Out.ar(
        ...         source=ugentools.SinOsc.ar(
        ...             frequency=builder['frequency'],
        ...             )
        ...         )
        ...
        >>> synthdef = builder.build()

    ::

        >>> with session.at(0):
        ...     synth_a = session.add_synth(duration=10, synthdef=synthdef)
        ...     synth_b = session.add_synth(duration=15, synthdef=synthdef)
        ...
        >>> with session.at(5):
        ...     synth_c = session.add_synth(duration=10, synthdef=synthdef)
        ...

    ::

        >>> session.to_osc_bundles()
        []

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_active_moments',
        '_audio_input_bus_group',
        '_audio_output_bus_group',
        '_buses',
        '_input_count',
        '_nodes',
        '_offsets',
        '_output_count',
        '_root_node',
        '_states',
        )

    ### INITIALIZER ###

    def __init__(self, input_count=0, output_count=2):
        from supriya.tools import nonrealtimetools
        self._active_moments = []
        self._states = {}
        self._nodes = set()
        self._offsets = []
        self._root_node = nonrealtimetools.RootNode(self)
        self._setup_initial_states()
        self._setup_buses(input_count, output_count)

    ### PRIVATE METHODS ###

    def _build_bus_id_mapping(self):
        input_count = self._input_count or 0
        output_count = self._output_count or 0
        first_private_bus_id = input_count + output_count
        audio_bus_allocator = servertools.BlockAllocator(
            heap_minimum=first_private_bus_id,
            )
        control_bus_allocator = servertools.BlockAllocator()
        mapping = {}
        if output_count:
            bus_group = self.audio_output_bus_group
            for bus_id, bus in enumerate(bus_group):
                mapping[bus] = bus_id
        if input_count:
            bus_group = self.audio_input_bus_group
            for bus_id, bus in enumerate(bus_group, output_count):
                mapping[bus] = bus_id
        for bus in self._buses:
            if bus in mapping:
                continue
            if bus.calculation_rate == synthdeftools.CalculationRate.AUDIO:
                allocator = audio_bus_allocator
            else:
                allocator = control_bus_allocator
            if bus.bus_group is None:
                mapping[bus] = allocator.allocate(1)
            else:
                block_id = allocator.allocate(len(bus.bus_group))
                mapping[bus.bus_group] = block_id
                for bus_id in range(block_id, block_id + len(bus.bus_group)):
                    mapping[bus] = bus_id
        return mapping

    def _build_command(
        self,
        output_filename,
        input_filename=None,
        sample_rate=44100,
        header_format=soundfiletools.HeaderFormat.AIFF,
        sample_format=soundfiletools.SampleFormat.INT24,
        **kwargs
        ):
        r'''Builds non-realtime rendering command.

        ::

            >>> session._build_command('output.aiff')
            'scsynth -N {} _ output.aiff 44100 aiff int24'

        '''
        parts = ['scsynth', '-N', '{}']
        if input_filename:
            parts.append(os.path.expanduser(input_filename))
        else:
            parts.append('_')
        parts.append(os.path.expanduser(output_filename))
        parts.append(str(int(sample_rate)))
        header_format = soundfiletools.HeaderFormat.from_expr(header_format)
        parts.append(header_format.name.lower())  # Must be lowercase.
        sample_format = soundfiletools.SampleFormat.from_expr(sample_format)
        parts.append(sample_format.name.lower())  # Must be lowercase.
        server_options = servertools.ServerOptions(**kwargs)
        server_options = server_options.as_options_string(realtime=False)
        if server_options:
            parts.append(server_options)
        command = ' '.join(parts)
        return command

    def _build_id_mapping(self):
        id_mapping = {}
        id_mapping.update(self._build_bus_id_mapping())
        id_mapping.update(self._build_synth_id_mapping())
        return id_mapping

    def _build_synth_id_mapping(self):
        allocator = servertools.NodeIdAllocator()
        mapping = {self.root_node: 0}
        for offset in self.offsets[1:]:
            state = self.states[offset]
            for start_node in state.start_nodes:
                mapping[start_node] = allocator.allocate_node_id()
        return mapping

    def _collect_bus_settings(self, id_mapping):
        bus_settings = {}
        for bus in self._buses:
            if bus.calculation_rate != synthdeftools.CalculationRate.CONTROL:
                continue
            bus_id = id_mapping[bus]
            for offset, value in bus._events:
                bus_settings.setdefault(offset, {})[bus_id] = value
        return bus_settings

    def _find_state_after(self, offset, with_node_tree=None):
        index = bisect.bisect(self.offsets, offset)
        if with_node_tree:
            while index < len(self.offsets):
                state = self.states[self.offsets[index]]
                if state.nodes_to_children is not None:
                    return state
                index += 1
            return None
        if index < len(self.offsets):
            old_offset = self.offsets[index]
            if offset < old_offset:
                return self.states[old_offset]
        return None

    def _find_state_at(self, offset):
        return self.states.get(offset, None)

    def _find_state_before(self, offset, with_node_tree=None):
        index = bisect.bisect_left(self.offsets, offset)
        if index == len(self.offsets):
            index -= 1
        old_offset = self.offsets[index]
        if offset <= old_offset:
            index -= 1
        if index < 0:
            return None
        if with_node_tree:
            while 0 <= index:
                state = self.states[self.offsets[index]]
                if state.nodes_to_children is not None:
                    return state
                index -= 1
            return None
        return self.states[self.offsets[index]]

    def _process_timespan(self, timespan):
        if self.duration == float('inf'):
            assert isinstance(timespan, timespantools.Timespan)
            assert 0 <= timespan.start_offset
            assert 0 < timespan.duration < float('inf')
        elif timespan is not None and timespan.duration == float('inf'):
            timespan = timespan & timespantools.Timespan(0, self.duration)
        offset_delta = 0
        states = []
        if timespan is None:
            offset_delta = 0
            offsets = self.offsets[1:]
            states = [self.states[offset] for offset in offsets]
        else:
            offset_delta = timespan.start_offset
            offsets = [_ for _ in self.offsets if
                timespan.start_offset <= _ < timespan.stop_offset]
            states = [self.states[offset] for offset in offsets]
            initial_state = states[0]
            start_offset = timespan.start_offset
            if start_offset < initial_state.offset:
                initial_state = self._find_state_before(start_offset)
                initial_state = initial_state._clone(
                    start_offset,
                    is_instantaneous=True,
                    )
                states.insert(0, initial_state)
            elif states:
                states[0] = states[0]._clone(
                    start_offset,
                    is_instantaneous=True,
                    )
            if states[-1].offset != timespan.stop_offset:
                terminal_state = states[-1]._clone(timespan.stop_offset)
                states.append(terminal_state)
        return offset_delta, states

    def _setup_buses(self, input_count, output_count):
        from supriya.tools import nonrealtimetools
        self._buses = collections.OrderedDict()
        input_count = int(input_count or 0)
        assert 0 <= input_count
        self._input_count = input_count
        output_count = int(output_count or 0)
        assert 0 <= output_count
        self._output_count = output_count
        audio_input_bus_group = None
        if self._input_count:
            audio_input_bus_group = nonrealtimetools.AudioInputBusGroup(self)
        self._audio_input_bus_group = audio_input_bus_group
        audio_output_bus_group = None
        if self._output_count:
            audio_output_bus_group = nonrealtimetools.AudioOutputBusGroup(self)
        self._audio_output_bus_group = audio_output_bus_group

    def _setup_initial_states(self):
        from supriya.tools import nonrealtimetools
        offset = float('-inf')
        state = nonrealtimetools.State(self, offset)
        state._nodes_to_children = {self.root_node: None}
        state._nodes_to_parents = {self.root_node: None}
        self.states[offset] = state
        self.offsets.append(offset)
        offset = 0
        state = state._clone(offset)
        self.states[offset] = state
        self.offsets.append(offset)

    ### PUBLIC METHODS ###

    def at(self, offset):
        from supriya.tools import nonrealtimetools
        assert 0 <= offset
        # Using this should return a moment, not a state.
        # No state should be created until after an edit.
        state = self._find_state_at(offset)
        if not state:
            old_state = self._find_state_before(offset)
            state = old_state._clone(offset)
            self.states[offset] = state
            self.offsets.insert(
                self.offsets.index(old_state.offset) + 1,
                offset,
                )
        return nonrealtimetools.Moment(self, offset, state)

    def add_bus(self, calculation_rate='control'):
        from supriya.tools import nonrealtimetools
        bus = nonrealtimetools.Bus(self, calculation_rate=calculation_rate)
        self._buses[bus] = None
        return bus

    def add_bus_group(self, bus_count=1, calculation_rate='control'):
        from supriya.tools import nonrealtimetools
        bus_group = nonrealtimetools.BusGroup(
            self,
            bus_count=bus_count,
            calculation_rate=calculation_rate,
            )
        for bus in bus_group:
            self._buses[bus] = None
        return bus_group

    def add_group(
        self,
        add_action=None,
        ):
        return self.root_node.add_group(add_action=add_action)

    def add_synth(
        self,
        add_action=None,
        duration=None,
        synthdef=None,
        **synth_kwargs
        ):
        return self.root_node.add_synth(
            add_action=add_action,
            duration=duration,
            synthdef=synthdef,
            **synth_kwargs
            )

    def move_node(
        self,
        node,
        add_action=None,
        ):
        self.root_node.move_node(node, add_action=add_action)

    def render(
        self,
        output_filename,
        input_filename=None,
        timespan=None,
        sample_rate=44100,
        header_format=soundfiletools.HeaderFormat.AIFF,
        sample_format=soundfiletools.SampleFormat.INT24,
        debug=False,
        **kwargs
        ):
        datagram = self.to_datagram(timespan=timespan)
        md5 = hashlib.md5()
        md5.update(datagram)
        md5 = md5.hexdigest()
        temp_directory_path = tempfile.mkdtemp()
        file_path = os.path.join(temp_directory_path, '{}.osc'.format(md5))
        with open(file_path, 'wb') as file_pointer:
            file_pointer.write(datagram)
        command = self._build_command(
            output_filename,
            input_filename=None,
            sample_rate=sample_rate,
            header_format=header_format,
            sample_format=sample_format,
            **kwargs
            )
        command = command.format(file_path)
        exit_code = subprocess.call(command, shell=True)
        if debug:
            return exit_code, file_path
        else:
            shutil.rmtree(temp_directory_path)
            return exit_code, None

    def report(self):
        states = []
        for offset in self.offsets[1:]:
            state = self.states[offset]
            states.append(state.report())
        return states

    def to_datagram(self, timespan=None):
        osc_bundles = self.to_osc_bundles(timespan=timespan)
        datagrams = []
        for osc_bundle in osc_bundles:
            datagram = osc_bundle.to_datagram(realtime=False)
            size = len(datagram)
            size = struct.pack('>i', size)
            datagrams.append(size)
            datagrams.append(datagram)
        datagram = b''.join(datagrams)
        return datagram

    def to_osc_bundles(self, timespan=None):
        id_mapping = self._build_id_mapping()
        bus_settings = self._collect_bus_settings(id_mapping)
        offset_delta, states = self._process_timespan(timespan)
        # Need to strip out no-op states, so they don't gum things up.
        osc_bundles = []
        visited_synthdefs = set()
        print('State Count:', len(states))
        for i, state in enumerate(states, 1):
            offset = float(state.offset - offset_delta)
            force_start = i == 1 and timespan is not None
            force_stop = i == len(states) and timespan is not None
            print('    At state:', i, offset, force_start, force_stop)
            requests = state.to_requests(
                id_mapping,
                bus_settings=bus_settings,
                force_start=force_start,
                force_stop=force_stop,
                visited_synthdefs=visited_synthdefs,
                )
            print('        Requests?', len(requests))
            osc_messages = [request.to_osc_message(True)
                for request in requests]
            if i == len(states):
                osc_message = osctools.OscMessage(0)
                osc_messages.append(osc_message)
            if osc_messages:
                osc_bundle = osctools.OscBundle(
                    timestamp=offset,
                    contents=osc_messages,
                    )
                osc_bundles.append(osc_bundle)
        return osc_bundles

    ### PUBLIC PROPERTIES ###

    @property
    def active_moments(self):
        return self._active_moments

    @property
    def audio_input_bus_group(self):
        return self._audio_input_bus_group

    @property
    def audio_output_bus_group(self):
        return self._audio_output_bus_group

    @property
    def buses(self):
        return self._buses

    @property
    def duration(self):
        if 1 < len(self.offsets):
            return self.offsets[-1]
        return 0

    @property
    def input_count(self):
        return self._input_count

    @property
    def nodes(self):
        return self._nodes

    @property
    def offsets(self):
        return self._offsets

    @property
    def output_count(self):
        return self._output_count

    @property
    def root_node(self):
        return self._root_node

    @property
    def states(self):
        return self._states