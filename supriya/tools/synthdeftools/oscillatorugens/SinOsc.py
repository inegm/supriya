# -*- encoding: utf-8 -*-
from supriya.tools.synthdeftools.Argument import Argument
from supriya.tools.synthdeftools.UGen import UGen


class SinOsc(UGen):
    r'''A sinusoid oscillator unit generator.

    ::

        >>> from supriya.tools import synthdeftools
        >>> synthdeftools.SinOsc.ar()
        SinOsc.ar()

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        )

    _argument_specifications = (
        Argument('frequency', 440),
        Argument('phase', 0),
        )

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        frequency=440.,
        phase=0.,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            frequency=frequency,
            phase=phase,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        frequency=440,
        phase=0,
        ):
        r'''Creates an audio-rate sinusoid oscillator.

        ::

            >>> from supriya.tools import synthdeftools
            >>> synthdeftools.SinOsc.ar(
            ...     frequency=443,
            ...     phase=0.25,
            ...     )
            SinOsc.ar()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new(
            calculation_rate=calculation_rate,
            frequency=frequency,
            phase=phase,
            special_index=0,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        frequency=440,
        phase=0,
        ):
        r'''Creates a control-rate sinusoid oscillator.

        ::

            >>> from supriya.tools import synthdeftools
            >>> synthdeftools.SinOsc.kr(
            ...     frequency=443,
            ...     phase=0.25,
            ...     )
            SinOsc.kr()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new(
            calculation_rate=calculation_rate,
            frequency=frequency,
            phase=phase,
            special_index=0,
            )
        return ugen
