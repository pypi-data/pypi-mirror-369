
from logging import Logger
from logging import getLogger

from pathlib import Path
from typing import Callable

from wx import ID_ANY
from wx import ID_OK
from wx import DD_DEFAULT_STYLE
from wx import EVT_BUTTON

from wx import DirDialog
from wx import CommandEvent
from wx import Size
from wx import TextCtrl

from wx.lib.buttons import GenBitmapButton

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.resources.images import folder as ImgFolder

DirectoryPathChangedCallback = Callable[[Path], None]

CALLBACK_PARAMETER = 'pathChangedCallback'


class DirectorySelector(SizedPanel):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        We pass all keyword parameters to the sized panel except for 'callable'.  That
        is for us.

        Args:
            *args:
            **kwargs:
        """

        self.logger: Logger = getLogger(__name__)

        self._directorPathChangedCallback: DirectoryPathChangedCallback | None = kwargs.get(CALLBACK_PARAMETER, None)
        if self._directorPathChangedCallback is not None:
            kwargs.pop(CALLBACK_PARAMETER)

        super().__init__(*args, **kwargs)

        self.SetSizerType('horizontal')
        textCtrl: TextCtrl = TextCtrl(self, size=Size(300, -1))

        selectButton: GenBitmapButton = GenBitmapButton(self, ID_ANY, ImgFolder.embeddedImage.GetBitmap())

        textCtrl.SetValue('')
        textCtrl.SetEditable(False)

        self._textDiagramsDirectory = textCtrl
        self._directoryPath:       Path = Path('')

        self.Bind(EVT_BUTTON, self._onSelectDiagramsDirectory, selectButton)

    @property
    def directoryPath(self) -> Path:
        return self._directoryPath

    @directoryPath.setter
    def directoryPath(self, value: Path):

        self._directoryPath = value
        self._textDiagramsDirectory.SetValue(str(value))

    # noinspection PyUnusedLocal
    def _onSelectDiagramsDirectory(self, event: CommandEvent):

        with DirDialog(None, 'Choose the Diagrams Directory', defaultPath=str(self._directoryPath), style=DD_DEFAULT_STYLE) as dlg:

            if dlg.ShowModal() == ID_OK:
                self._directoryPath = Path(dlg.GetPath())
                self._textDiagramsDirectory.SetValue(str(self._directoryPath))
                if self._directorPathChangedCallback is not None:
                    self._directorPathChangedCallback(self._directoryPath)
