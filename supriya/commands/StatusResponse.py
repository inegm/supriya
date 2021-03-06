from supriya.commands.Response import Response


class StatusResponse(Response):

    ### INITIALIZER ###

    def __init__(
        self,
        actual_sample_rate=None,
        average_cpu_usage=None,
        group_count=None,
        peak_cpu_usage=None,
        synth_count=None,
        synthdef_count=None,
        target_sample_rate=None,
        ugen_count=None,
    ):
        self._actual_sample_rate = actual_sample_rate
        self._average_cpu_usage = average_cpu_usage
        self._group_count = group_count
        self._peak_cpu_usage = peak_cpu_usage
        self._synth_count = synth_count
        self._synthdef_count = synthdef_count
        self._target_sample_rate = target_sample_rate
        self._ugen_count = ugen_count

    ### PUBLIC METHODS ###

    @classmethod
    def from_osc_message(cls, osc_message):
        """
        Create response from OSC message.

        ::

            >>> message = supriya.osc.OscMessage(
            ...     '/status.reply', 1, 0, 0, 2, 4,
            ...     0.040679048746824265, 0.15118031203746796,
            ...     44100.0, 44100.00077873274,
            ...     )
            >>> supriya.commands.StatusResponse.from_osc_message(message)
            StatusResponse(
                actual_sample_rate=44100.00077873274,
                average_cpu_usage=0.040679048746824265,
                group_count=2,
                peak_cpu_usage=0.15118031203746796,
                synth_count=0,
                synthdef_count=4,
                target_sample_rate=44100.0,
                ugen_count=0,
                )

        """
        arguments = osc_message.contents[1:]
        (
            ugen_count,
            synth_count,
            group_count,
            synthdef_count,
            average_cpu_usage,
            peak_cpu_usage,
            target_sample_rate,
            actual_sample_rate,
        ) = arguments
        response = cls(
            actual_sample_rate=actual_sample_rate,
            average_cpu_usage=average_cpu_usage,
            group_count=group_count,
            peak_cpu_usage=peak_cpu_usage,
            synth_count=synth_count,
            synthdef_count=synthdef_count,
            target_sample_rate=target_sample_rate,
            ugen_count=ugen_count,
        )
        return response

    def to_dict(self):
        """
        Convert StatusResponse to JSON-serializable dictionay.

        ::

            >>> status_response = supriya.commands.StatusResponse(
            ...     actual_sample_rate=44100.05692801021,
            ...     average_cpu_usage=8.151924133300781,
            ...     group_count=6,
            ...     peak_cpu_usage=15.151398658752441,
            ...     synth_count=19,
            ...     synthdef_count=42,
            ...     target_sample_rate=44100.0,
            ...     ugen_count=685
            ...     )

        ::

            >>> import json
            >>> result = status_response.to_dict()
            >>> result = json.dumps(
            ...     result,
            ...     indent=4,
            ...     separators=(',', ': '),
            ...     sort_keys=True,
            ...     )
            >>> print(result)
            {
                "server_status": {
                    "actual_sample_rate": 44100.05692801021,
                    "average_cpu_usage": 8.151924133300781,
                    "group_count": 6,
                    "peak_cpu_usage": 15.151398658752441,
                    "synth_count": 19,
                    "synthdef_count": 42,
                    "target_sample_rate": 44100.0,
                    "ugen_count": 685
                }
            }

        """
        result = {
            "server_status": {
                "actual_sample_rate": self.actual_sample_rate,
                "average_cpu_usage": self.average_cpu_usage,
                "group_count": self.group_count,
                "peak_cpu_usage": self.peak_cpu_usage,
                "synth_count": self.synth_count,
                "synthdef_count": self.synthdef_count,
                "target_sample_rate": self.target_sample_rate,
                "ugen_count": self.ugen_count,
            }
        }
        return result

    ### PUBLIC PROPERTIES ###

    @property
    def actual_sample_rate(self):
        return self._actual_sample_rate

    @property
    def average_cpu_usage(self):
        return self._average_cpu_usage

    @property
    def group_count(self):
        return self._group_count

    @property
    def peak_cpu_usage(self):
        return self._peak_cpu_usage

    @property
    def synth_count(self):
        return self._synth_count

    @property
    def synthdef_count(self):
        return self._synthdef_count

    @property
    def target_sample_rate(self):
        return self._target_sample_rate

    @property
    def ugen_count(self):
        return self._ugen_count
