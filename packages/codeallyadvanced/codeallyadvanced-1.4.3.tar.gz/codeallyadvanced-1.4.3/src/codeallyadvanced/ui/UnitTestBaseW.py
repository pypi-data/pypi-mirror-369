

from wx import App
from wx import Frame
from wx import ID_ANY
from wx import ScrolledWindow

from codeallybasic.UnitTestBase import UnitTestBase


class DummyApp(App):
    def OnInit(self):
        return True


class UnitTestBaseW(UnitTestBase):
    """
    This base class is meant to be used by unit tests that need a wx.App
    instance opened.
    """

    def setUp(self):
        super().setUp()

        self._app:   DummyApp = DummyApp()

        baseFrame: Frame = Frame(None, ID_ANY, "", size=(10, 10))

        umlFrame: ScrolledWindow = ScrolledWindow(baseFrame)
        umlFrame.Show(True)

        self._listeningWindow: ScrolledWindow = umlFrame    # For event handling
        self._topLevelWindow:  ScrolledWindow = umlFrame    # For use as a parent window

    def tearDown(self):
        self._app.OnExit()
