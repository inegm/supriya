import collections

from supriya import CalculationRate
from supriya.synthdefs import UGen


class LFDNoise1(UGen):
    """
    A dynamic ramp noise generator.

    ::

        >>> supriya.ugens.LFDNoise1.ar()
        LFDNoise1.ar()

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = "Noise UGens"

    _ordered_input_names = collections.OrderedDict([("frequency", 500.0)])

    _valid_calculation_rates = (CalculationRate.AUDIO, CalculationRate.CONTROL)
