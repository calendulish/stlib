import asyncio
import os
import sys

# noinspection PyUnresolvedReferences
import pytest

from stlib import authenticator


def get_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()  # on windows IO needs this
    return asyncio.new_event_loop()  # default on UNIX is fine


@pytest.yield_fixture()
def event_loop():
    """pytest-asyncio customization"""
    if sys.platform != "win32":
        asyncio.set_event_loop(None)  # see https://github.com/pytest-dev/pytest-asyncio/issues/73
    loop = get_event_loop()
    if sys.platform != "win32":
        # on UNIX we also need to attach the loop to the child watcher for asyncio.subprocess
        policy = asyncio.get_event_loop_policy()
        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(loop)
        policy.set_child_watcher(watcher)
    try:
        yield loop
    finally:
        loop.close()


# noinspection PyProtectedMember
class TestAuthenticator:
    adb = authenticator.AndroidDebugBridge(os.path.join('C:\\', 'platform-tools', 'adb.exe'),
                                           '/data/data/com.valvesoftware.android.steam.community/')

    @pytest.mark.asyncio
    async def test__do_checks(self):
        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == False

        await self.adb._do_checks()

        for field in authenticator.Checks._fields:
            assert getattr(authenticator.CHECKS_RESULT, field) == True

    @pytest.mark.asyncio
    async def test__run(self):
        result = await self.adb._run(['shell', 'echo', 'hello'])
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test__get_data(self):
        result = await self.adb._get_data('shared_prefs/steam.uuid.xml')
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_secret(self):
        tasks = [
            asyncio.create_task(self.adb.get_secret('shared')),
            asyncio.create_task(self.adb.get_secret('identity')),
            asyncio.create_task(self.adb.get_secret('dummy')),
        ]

        tasks_done, _ = await asyncio.wait(tasks)
        assert isinstance(list(tasks_done)[0].result(), (str, bytes))
        assert isinstance(list(tasks_done)[1].result(), (str, bytes))

        try:
            result = list(tasks_done)[2].result()
        except KeyError:
            assert True
        else:
            assert False
