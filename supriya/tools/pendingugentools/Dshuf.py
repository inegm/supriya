# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.ListDUGen import ListDUGen


class Dshuf(ListDUGen):
    r'''

    ::

        >>> dshuf = ugentools.Dshuf.(
        ...     repeats=1,
        ...     sequence=None,
        ...     )
        >>> dshuf

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'sequence',
        'repeats',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        repeats=1,
        sequence=None,
        ):
        ListDUGen.__init__(
            self,
            calculation_rate=calculation_rate,
            repeats=repeats,
            sequence=sequence,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def new(
        cls,
        repeats=1,
        sequence=None,
        ):
        r'''Constructs a Dshuf.

        ::

            >>> dshuf = ugentools.Dshuf.new(
            ...     repeats=1,
            ...     sequence=None,
            ...     )
            >>> dshuf

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = None
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            repeats=repeats,
            sequence=sequence,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def repeats(self):
        r'''Gets `repeats` input of Dshuf.

        ::

            >>> dshuf = ugentools.Dshuf.ar(
            ...     repeats=1,
            ...     sequence=None,
            ...     )
            >>> dshuf.repeats

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('repeats')
        return self._inputs[index]

    @property
    def sequence(self):
        r'''Gets `sequence` input of Dshuf.

        ::

            >>> dshuf = ugentools.Dshuf.ar(
            ...     repeats=1,
            ...     sequence=None,
            ...     )
            >>> dshuf.sequence

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('sequence')
        return self._inputs[index]