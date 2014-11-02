# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.BufInfoUGenBase import BufInfoUGenBase


class BufFrames(BufInfoUGenBase):
    r'''Buffer frame count info unit generator.

    ::

        >>> from supriya.tools import ugentools
        >>> ugentools.BufFrames.kr(buffer_id=0)
        BufFrames.kr()

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = 'Info UGens'

    __slots__ = ()

    ### INITIALIZER ###

    def __init__(
        self,
        buffer_id=None,
        rate=None,
        ):
        BufInfoUGenBase.__init__(
            self,
            buffer_id=buffer_id,
            rate=rate,
            )

    ### PUBLIC PROPERTIES ###

    @property
    def buffer_id(self):
        r'''Gets `buffer_id` input of BufFrames.

        ::

            >>> buffer_id = None
            >>> buf_frames = ugentools.BufFrames.ar(
            ...     buffer_id=buffer_id,
            ...     )
            >>> buf_frames.buffer_id

        Returns input.
        '''
        index = self._ordered_input_names.index('buffer_id')
        return self._inputs[index]