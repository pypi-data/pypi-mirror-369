from typing import Any
from typing import Callable
from typing import List

from dataclasses import dataclass

from math import ceil

from logging import Logger
from logging import getLogger
from typing import cast

from wx import ALIGN_LEFT
from wx import ID_ANY
from wx import StaticText

from wx.lib.agw.knobctrl import EVT_KC_ANGLE_CHANGED
from wx.lib.agw.knobctrl import KnobCtrl
from wx.lib.agw.knobctrl import KnobCtrlEvent

from wx.lib.sized_controls import SizedStaticBox

FormatValueCallback = Callable[[Any], str]
ValueChangeCallback = Callable[[Any], None]

NO_FORMAT_CALLBACK:  FormatValueCallback = cast(FormatValueCallback, None)
NO_VALUE_CALLBACK:   ValueChangeCallback = cast(ValueChangeCallback, None)


@dataclass
class DialSelectorParameters:
    minValue:  int | float = 0
    maxValue:  int | float = 0
    dialLabel: str         = ''
    formatValueCallback:  FormatValueCallback = NO_FORMAT_CALLBACK
    valueChangedCallback: ValueChangeCallback = NO_VALUE_CALLBACK


OPINIONATED_TICK_FREQUENCY: int = 10
OPINIONATED_TICK_VALUE:     int = 10
KNOB_CTRL_GRANULARITY:      int = 100


class DialSelector(SizedStaticBox):
    """
    Using the Adapter pattern.  I don't care what PyBites says
    The wrapped knob control reports 100 positions; We will put
    tick marks (tags) every 10 positions and coerce the reported
    values to align on those marks
    """

    def __init__(self, parent, parameters: DialSelectorParameters):

        super().__init__(parent, label=parameters.dialLabel)
        self.logger: Logger = getLogger(__name__)

        self._parameters:    DialSelectorParameters = parameters

        self._tickFrequency: int         = OPINIONATED_TICK_FREQUENCY
        self._tickValue:     int | float = OPINIONATED_TICK_VALUE
        self._value:         int | float = parameters.minValue

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self._knobCtrl: KnobCtrl = KnobCtrl(self, size=(100, 100))

        self._knobCtrl.SetAngularRange(-45, 225)
        self._knobCtrl.SetKnobRadius(4)
        self._setTicksOnKnob()

        self._knobTracker: StaticText = StaticText(parent=self, id=ID_ANY, label=f'{parameters.dialLabel}: 0', style=ALIGN_LEFT)

        self._displayValue(value=parameters.minValue)

        self.Bind(EVT_KC_ANGLE_CHANGED, self._onKnobChanged, self._knobCtrl)

    @property
    def tickFrequency(self) -> int | float:
        return self._tickFrequency

    @tickFrequency.setter
    def tickFrequency(self, value: int):
        """
        The underlying control has a tick granularity of 100. Set a
        value between 1 and 100

        The underlying control computes the value of each tick

        Args:
            value: Indicates how to space out the tick marks
        """
        assert 1 <= value <= 100
        self._tickFrequency = value
        self._setTicksOnKnob()

    @property
    def tickValue(self) -> int | float:
        return self._tickValue

    @tickValue.setter
    def tickValue(self, value: int | float):
        self._tickValue = value
        self._displayValue(value=value)

    @property
    def value(self) -> int | float:
        """
        The returned value is between the min/max values specified in the
        dial range;  It is modulo the specified tick frequency.
        Returns:  The current control value
        """
        return self._value

    @value.setter
    def value(self, newValue: int | float):

        self._value = newValue

        tickNumber: int = self._valueToTick(value=newValue)

        self.logger.debug(f'{newValue=} {tickNumber=}')

        self._knobCtrl.SetValue(tickNumber)
        self._displayValue(newValue)

    def _onKnobChanged(self, event: KnobCtrlEvent):

        knobValue:        int = event.GetValue()
        roundedKnobValue: int = self._alignKnobToTick(knobValue=knobValue)
        self._knobCtrl.SetValue(roundedKnobValue)

        realValue = self._calculateRealValue(roundedKnobValue=roundedKnobValue,
                                             tickValue=self._tickValue,
                                             tickFrequency=self._tickFrequency)

        self.logger.debug(f'realValue={realValue:.2f}')
        self._displayValue(value=realValue)

        self._value = realValue

        self._parameters.valueChangedCallback(self._value)

        event.Skip(skip=True)

    def _alignKnobToTick(self, knobValue: int):

        # TODO: This will be moved to codeallybasic
        # Including the unit tests
        #
        def roundUpToNearestTick(valueToRound, boundaryValue: int) -> int:
            return int(ceil(valueToRound / boundaryValue)) * boundaryValue

        roundToIncrement: int = KNOB_CTRL_GRANULARITY // self._tickFrequency

        roundedKnobValue: int = roundUpToNearestTick(valueToRound=knobValue, boundaryValue=roundToIncrement)

        self.logger.info(f'{knobValue=} {roundedKnobValue=}')

        return roundedKnobValue

    def _setTicksOnKnob(self):
        assert self._parameters is not None, 'Developer Error'
        assert self._tickFrequency != 0,    'Developer Error'
        assert self._knobCtrl is not None,  'Developer Error'

        integerList:   List[int] = list(range(1, self._tickFrequency, 1))

        self.logger.debug(f'{integerList=}')
        self._knobCtrl.SetTags(integerList)

    def _displayValue(self, value: int | float):

        label: str = self._parameters.formatValueCallback(value)

        self._knobTracker.SetLabel(label)
        self._knobTracker.Refresh()

    def _calculateRealValue(self, roundedKnobValue: int, tickValue: int | float, tickFrequency: int):

        tickPosition: int = int((roundedKnobValue / KNOB_CTRL_GRANULARITY) * tickFrequency)
        self.logger.debug(f'{tickPosition=}')
        realValue    = tickValue * tickPosition

        return realValue

    def _valueToTick(self, value: int | float) -> int:

        tickNumber: int = int(value // self._tickValue)

        return tickNumber
