# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.BufDelayN import BufDelayN


class BufDelayC(BufDelayN):
    r'''Buffer-based cubic-interpolating delay line unit generator.

    ::

        >>> from supriya.tools import ugentools
        >>> buffer_id = 0
        >>> source = ugentools.In.ar(bus=0)
        >>> ugentools.BufDelayC.ar(
        ...     buffer_id=buffer_id,
        ...     source=source,
        ...     )
        BufDelayC.ar()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Delay UGens'

    __slots__ = ()

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        buffer_id=None,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create an audio-rate buffer-based cubic-interpolating delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> buffer_id = 0
            >>> source = ugentools.In.ar(bus=0)
            >>> ugentools.BufDelayC.ar(
            ...     buffer_id=buffer_id,
            ...     delay_time=0.5,
            ...     maximum_delay_time=1.0,
            ...     source=source,
            ...     )
            BufDelayC.ar()

        Returns unit generator graph.
        '''
        return super(BufDelayC, cls).ar(
            buffer_id=buffer_id,
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    @classmethod
    def kr(
        cls,
        buffer_id=None,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create a control-rate buffer-based cubic-interpolating delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> buffer_id = 0
            >>> source = ugentools.In.kr(bus=0)
            >>> ugentools.BufDelayC.kr(
            ...     buffer_id=buffer_id,
            ...     delay_time=0.5,
            ...     maximum_delay_time=1.0,
            ...     source=source,
            ...     )
            BufDelayC.ar()

        Returns unit generator graph.
        '''
        return super(BufDelayC, cls).kr(
            buffer_id=buffer_id,
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    ### PUBLIC PROPERTIES ###

    @property
    def buffer_id(self):
        r'''Gets `buffer_id` input of BufDelayC.

        ::

            >>> buffer_id = None
            >>> buf_delay_c = ugentools.BufDelayC.ar(
            ...     buffer_id=buffer_id,
            ...     )
            >>> buf_delay_c.buffer_id

        Returns input.
        '''
        index = self._ordered_input_names.index('buffer_id')
        return self._inputs[index]

    @property
    def delay_time(self):
        r'''Gets `delay_time` input of BufDelayC.

        ::

            >>> delay_time = None
            >>> buf_delay_c = ugentools.BufDelayC.ar(
            ...     delay_time=delay_time,
            ...     )
            >>> buf_delay_c.delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('delay_time')
        return self._inputs[index]

    @property
    def maximum_delay_time(self):
        r'''Gets `maximum_delay_time` input of BufDelayC.

        ::

            >>> maximum_delay_time = None
            >>> buf_delay_c = ugentools.BufDelayC.ar(
            ...     maximum_delay_time=maximum_delay_time,
            ...     )
            >>> buf_delay_c.maximum_delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('maximum_delay_time')
        return self._inputs[index]

    @property
    def source(self):
        r'''Gets `source` input of BufDelayC.

        ::

            >>> source = None
            >>> buf_delay_c = ugentools.BufDelayC.ar(
            ...     source=source,
            ...     )
            >>> buf_delay_c.source

        Returns input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]