
from typing import Callable

from logging import Logger
from logging import getLogger

from codeallybasic.MinMax import MinMax
from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues


class MinMaxControl(DualSpinnerControl):
    def __init__(self, sizedPanel: SizedPanel, displayText: str,
                 valueChangedCallback: Callable,
                 minValue: int, maxValue: int,
                 setControlsSize: bool = True):

        self.logger: Logger = getLogger(__name__)

        self._valuesChangedCallback: Callable = valueChangedCallback
        self._minMax:                MinMax   = MinMax()

        super().__init__(sizedPanel, displayText, self._onSpinValueChangedCallback, minValue, maxValue, setControlsSize)

    def _setMinMax(self, newValue: MinMax):
        self._position = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.minValue, value1=newValue.maxValue)

    # noinspection PyTypeChecker
    minMax = property(fdel=None, fget=None, fset=_setMinMax, doc='Write only property to set values')

    def _onSpinValueChangedCallback(self, spinnerValues: SpinnerValues):

        self.logger.info(f'{spinnerValues}')
        self._minMax.minValue = spinnerValues.value0
        self._minMax.maxValue = spinnerValues.value1

        self._valuesChangedCallback(self._minMax)
