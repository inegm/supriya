# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.DelayN import DelayN


class DelayL(DelayN):
    r'''Linear-interpolating delay line unit generator.

    ::

        >>> from supriya.tools import ugentools
        >>> source = ugentools.In.ar(bus=0)
        >>> ugentools.DelayL.ar(source=source)
        DelayL.ar()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Delay UGens'

    __slots__ = ()

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create an audio-rate linear-interpolating delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> source = ugentools.In.ar(bus=0)
            >>> ugentools.DelayL.ar(
            ...     delay_time=0.5,
            ...     maximum_delay_time=1.0,
            ...     source=source,
            ...     )
            DelayL.ar()

        Returns unit generator graph.
        '''
        return super(DelayL, cls).ar(
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    @classmethod
    def kr(
        cls,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create a control-rate linear-interpolating delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> source = ugentools.In.kr(bus=0)
            >>> ugentools.DelayL.kr(
            ...     delay_time=0.5,
            ...     maximum_delay_time=1.0,
            ...     source=source,
            ...     )
            DelayL.ar()

        Returns unit generator graph.
        '''
        return super(DelayL, cls).kr(
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    ### PUBLIC PROPERTIES ###

    @property
    def delay_time(self):
        r'''Gets `delay_time` input of DelayL.

        ::

            >>> delay_time = None
            >>> delay_l = ugentools.DelayL.ar(
            ...     delay_time=delay_time,
            ...     )
            >>> delay_l.delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('delay_time')
        return self._inputs[index]

    @property
    def maximum_delay_time(self):
        r'''Gets `maximum_delay_time` input of DelayL.

        ::

            >>> maximum_delay_time = None
            >>> delay_l = ugentools.DelayL.ar(
            ...     maximum_delay_time=maximum_delay_time,
            ...     )
            >>> delay_l.maximum_delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('maximum_delay_time')
        return self._inputs[index]

    @property
    def source(self):
        r'''Gets `source` input of DelayL.

        ::

            >>> source = None
            >>> delay_l = ugentools.DelayL.ar(
            ...     source=source,
            ...     )
            >>> delay_l.source

        Returns input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]