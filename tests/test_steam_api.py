import signal

import steam_api
from stlib import client


# noinspection PyProtectedMember

class TestSteamAPI():
    def test__init(self):
        assert isinstance(steam_api.init(), bool)

    def test_is_steam_running(self):
        assert isinstance(steam_api.is_steam_running(), bool)

    def test_shutdown(self):
        steam_api.shutdown()
        assert True # if shutdown doesn't throw an exception, it's ok


class TestOverlay():
    overlay = client.Overlay()

    def test_hook(self):
        assert self.overlay.process is None
        result = self.overlay.hook(269670)
        assert result
        assert isinstance(self.overlay.process.pid, int)
        assert self.overlay.process.exitcode is None
        assert self.overlay.process.is_alive

    def test_unhook(self):
        self.overlay.unhook()
        assert self.overlay.process.exitcode == -signal.SIGTERM
