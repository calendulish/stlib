import signal

from stlib import client


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
