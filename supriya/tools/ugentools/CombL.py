# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.CombN import CombN


class CombL(CombN):
    r'''Linear interpolating comb delay line unit generator.

    ::

        >>> from supriya.tools import ugentools
        >>> source = ugentools.In.ar(bus=0)
        >>> ugentools.CombL.ar(source=source)
        CombL.ar()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Delay UGens'

    __slots__ = ()

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        decay_time=1.0,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create an audio-rate linear-interpolating comb delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> source = ugentools.In.ar(bus=0)
            >>> ugentools.CombL.ar(
            ...     decay_time=1.0,
            ...     delay_time=0.2,
            ...     maximum_delay_time=0.2,
            ...     source=source,
            ...     )
            CombL.ar()

        Returns unit generator graph.
        '''
        return super(CombL, cls).ar(
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    @classmethod
    def kr(
        cls,
        decay_time=1.0,
        delay_time=0.2,
        maximum_delay_time=0.2,
        source=None,
        ):
        r'''Create a control-rate linear-interpolating comb delay line.

        ::

            >>> from supriya.tools import ugentools
            >>> source = ugentools.In.kr(bus=0)
            >>> ugentools.CombL.kr(
            ...     decay_time=1.0,
            ...     delay_time=0.2,
            ...     maximum_delay_time=0.2,
            ...     source=source,
            ...     )
            CombL.ar()

        Returns unit generator graph.
        '''
        return super(CombL, cls).kr(
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )

    ### PUBLIC PROPERTIES ###

    @property
    def decay_time(self):
        r'''Gets `decay_time` input of CombL.

        ::

            >>> decay_time = None
            >>> comb_l = ugentools.CombL.ar(
            ...     decay_time=decay_time,
            ...     )
            >>> comb_l.decay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('decay_time')
        return self._inputs[index]

    @property
    def delay_time(self):
        r'''Gets `delay_time` input of CombL.

        ::

            >>> delay_time = None
            >>> comb_l = ugentools.CombL.ar(
            ...     delay_time=delay_time,
            ...     )
            >>> comb_l.delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('delay_time')
        return self._inputs[index]

    @property
    def maximum_delay_time(self):
        r'''Gets `maximum_delay_time` input of CombL.

        ::

            >>> maximum_delay_time = None
            >>> comb_l = ugentools.CombL.ar(
            ...     maximum_delay_time=maximum_delay_time,
            ...     )
            >>> comb_l.maximum_delay_time

        Returns input.
        '''
        index = self._ordered_input_names.index('maximum_delay_time')
        return self._inputs[index]

    @property
    def source(self):
        r'''Gets `source` input of CombL.

        ::

            >>> source = None
            >>> comb_l = ugentools.CombL.ar(
            ...     source=source,
            ...     )
            >>> comb_l.source

        Returns input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]