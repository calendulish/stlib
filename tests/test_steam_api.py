import signal

from stlib import steam_api


# noinspection PyProtectedMember

class TestSteamAPI():
    steam_api = steam_api.SteamAPI()

    def test__init(self):
        assert isinstance(self.steam_api._init(), bool)

    def test_is_steam_running(self):
        assert isinstance(self.steam_api.is_steam_running(), bool)

    def test_shutdown(self):
        assert isinstance(self.steam_api.shutdown(), int)


class TestOverlay():
    overlay = steam_api.Overlay()

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
