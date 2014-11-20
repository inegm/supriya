# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.ChaosGen import ChaosGen


class LatoocarfianN(ChaosGen):
    r'''

    ::

        >>> latoocarfian_n = ugentools.LatoocarfianN.(
        ...     a=1,
        ...     b=3,
        ...     c=0.5,
        ...     d=0.5,
        ...     frequency=22050,
        ...     xi=0.5,
        ...     yi=0.5,
        ...     )
        >>> latoocarfian_n

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'frequency',
        'a',
        'b',
        'c',
        'd',
        'xi',
        'yi',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        a=1,
        b=3,
        c=0.5,
        d=0.5,
        frequency=22050,
        xi=0.5,
        yi=0.5,
        ):
        ChaosGen.__init__(
            self,
            calculation_rate=calculation_rate,
            a=a,
            b=b,
            c=c,
            d=d,
            frequency=frequency,
            xi=xi,
            yi=yi,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        a=1,
        b=3,
        c=0.5,
        d=0.5,
        frequency=22050,
        xi=0.5,
        yi=0.5,
        ):
        r'''Constructs an audio-rate LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            a=a,
            b=b,
            c=c,
            d=d,
            frequency=frequency,
            xi=xi,
            yi=yi,
            )
        return ugen

    # def equation(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def a(self):
        r'''Gets `a` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.a

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('a')
        return self._inputs[index]

    @property
    def b(self):
        r'''Gets `b` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.b

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('b')
        return self._inputs[index]

    @property
    def c(self):
        r'''Gets `c` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.c

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('c')
        return self._inputs[index]

    @property
    def d(self):
        r'''Gets `d` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.d

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('d')
        return self._inputs[index]

    @property
    def frequency(self):
        r'''Gets `frequency` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.frequency

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def xi(self):
        r'''Gets `xi` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.xi

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('xi')
        return self._inputs[index]

    @property
    def yi(self):
        r'''Gets `yi` input of LatoocarfianN.

        ::

            >>> latoocarfian_n = ugentools.LatoocarfianN.ar(
            ...     a=1,
            ...     b=3,
            ...     c=0.5,
            ...     d=0.5,
            ...     frequency=22050,
            ...     xi=0.5,
            ...     yi=0.5,
            ...     )
            >>> latoocarfian_n.yi

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('yi')
        return self._inputs[index]