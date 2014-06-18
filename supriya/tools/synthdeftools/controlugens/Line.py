# -*- encoding: utf-8 -*-
from supriya.tools.synthdeftools.Argument import Argument
from supriya.tools.synthdeftools.UGen import UGen


class Line(UGen):
    r'''A line generating unit generator.

    ::

        >>> from supriya.tools import synthdeftools
        >>> synthdeftools.Line.ar()
        Line.ar()

    '''

    ### CLASS VARIABLES ###

    __slots__ = ()

    _argument_specifications = (
        Argument('start', 0),
        Argument('stop', 1),
        Argument('duration', 1),
        Argument('done_action', 0),
        )

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        done_action=0.,
        duration=1.,
        start=0.,
        stop=1.,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            done_action=done_action,
            duration=duration,
            start=start,
            stop=stop,
            )

    ### PRIVATE METHODS ###

    @classmethod
    def _new(
        cls,
        calculation_rate=None,
        done_action=None,
        duration=None,
        stop=None,
        start=None,
        ):
        from supriya.tools import synthdeftools
        done_action = synthdeftools.DoneAction.from_expr(done_action)
        return super(Line, cls)._new(
            calculation_rate=calculation_rate,
            done_action=done_action,
            duration=duration,
            stop=stop,
            start=start,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        done_action=0,
        duration=1,
        stop=1,
        start=0,
        ):
        r'''Creates an audio-rate line generator.

        ::

            >>> from supriya.tools import synthdeftools
            >>> synthdeftools.Line.ar(
            ...     done_action=synthdeftools.DoneAction.FREE_SYNTH,
            ...     duration=5.5,
            ...     stop=12.1,
            ...     start=0.1,
            ...     )
            Line.ar()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        return cls._new(
            calculation_rate=calculation_rate,
            done_action=done_action,
            duration=duration,
            stop=stop,
            start=start,
            )

    @classmethod
    def kr(
        cls,
        done_action=0,
        duration=1,
        stop=1,
        start=0,
        ):
        r'''Creates an audio-rate line generator.

        ::

            >>> from supriya.tools import synthdeftools
            >>> synthdeftools.Line.kr(
            ...     done_action=synthdeftools.DoneAction.FREE_SYNTH,
            ...     duration=5.5,
            ...     stop=12.1,
            ...     start=0.1,
            ...     )
            Line.kr()

        Returns unit generator graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        return cls._new(
            calculation_rate=calculation_rate,
            done_action=done_action,
            duration=duration,
            stop=stop,
            start=start,
            )
