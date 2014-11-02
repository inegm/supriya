# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.PureUGen import PureUGen


class LFTri(PureUGen):
    r'''A non-band-limited triangle oscillator unit generator.

    ::

        >>> from supriya.tools import ugentools
        >>> ugentools.LFTri.ar()
        LFTri.ar()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Oscillator UGens'

    __slots__ = ()

    _ordered_input_names = (
        'frequency',
        'initial_phase',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        rate=None,
        frequency=440.,
        initial_phase=0.,
        ):
        PureUGen.__init__(
            self,
            rate=rate,
            frequency=frequency,
            initial_phase=initial_phase,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        frequency=440,
        initial_phase=0,
        ):
        r'''Creates an audio-rate non-band-limited triangle oscillator.

        ::

            >>> from supriya.tools import ugentools
            >>> ugentools.LFTri.ar(
            ...     frequency=443,
            ...     initial_phase=0.25,
            ...     )
            LFTri.ar()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        rate = synthdeftools.Rate.AUDIO
        ugen = cls._new_expanded(
            rate=rate,
            frequency=frequency,
            initial_phase=initial_phase,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        frequency=440,
        initial_phase=0,
        ):
        r'''Creates a control-rate non-band-limited triangle oscillator.

        ::

            >>> from supriya.tools import ugentools
            >>> ugentools.LFTri.kr(
            ...     frequency=443,
            ...     initial_phase=0.25,
            ...     )
            LFTri.kr()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        rate = synthdeftools.Rate.CONTROL
        ugen = cls._new_expanded(
            rate=rate,
            frequency=frequency,
            initial_phase=initial_phase,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def frequency(self):
        r'''Gets `frequency` input of LFTri.

        ::

            >>> frequency = None
            >>> lftri = ugentools.LFTri.ar(
            ...     frequency=frequency,
            ...     )
            >>> lftri.frequency

        Returns input.
        '''
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def initial_phase(self):
        r'''Gets `initial_phase` input of LFTri.

        ::

            >>> initial_phase = None
            >>> lftri = ugentools.LFTri.ar(
            ...     initial_phase=initial_phase,
            ...     )
            >>> lftri.initial_phase

        Returns input.
        '''
        index = self._ordered_input_names.index('initial_phase')
        return self._inputs[index]