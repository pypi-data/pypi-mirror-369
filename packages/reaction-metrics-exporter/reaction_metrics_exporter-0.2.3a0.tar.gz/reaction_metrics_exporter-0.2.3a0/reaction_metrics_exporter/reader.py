from abc import ABC, abstractmethod
import asyncio
from collections.abc import AsyncGenerator
from contextlib import closing
from datetime import datetime
from typing import Any

import aiofiles
import aionotify
import structlog
from systemd import journal
from systemd.journal import Reader

from .models.config import Config
from .models.exception import UnsupportedLine
from .models.log import Log, LogLevel

logger = structlog.get_logger()
config = Config.get_config()


class LogReader(ABC):
    """
    Asynchonously yield reaction logs.

    path is "abstract" (e.g. it is the unit to be read specific to subclasses).
    """

    @abstractmethod
    def __init__(self, path: str) -> None:
        self._path = path

    @abstractmethod
    def logs(self) -> AsyncGenerator[Log]:
        pass


class FileReader(LogReader):
    def __init__(self, path: str) -> None:
        super().__init__(path)

    async def logs(self) -> AsyncGenerator[Log]:
        async with aiofiles.open(self._path, "a+") as file:
            # go to the end of the file
            with closing(aionotify.Watcher()) as watcher:
                # register inotify watcher
                watcher.watch(self._path, flags=aionotify.Flags.MODIFY)
                await watcher.setup()
                while True:
                    # watch for changes
                    print(await file.read())
                    await file.seek(0)
                    _ = await watcher.get_event()
                    # consume new lines
                    async for line in file:
                        yield self._to_log(line)

    def _to_log(self, line: str) -> Log:
        line = line.strip()
        try:
            # split only first space
            level, _ = line.split(" ", 1)
        except ValueError as e:
            raise UnsupportedLine(f"cannot parse loglevel in line {line}: {e}")
        try:
            loglevel: LogLevel = LogLevel[level]
            # note that loglevel is part of the message
            return Log(datetime.now(), loglevel, line)
        except (ValueError, KeyError) as e:
            raise UnsupportedLine(f"unrecognized loglevel {level} found in line {line}: {e}")


class JournalReader(LogReader):
    def __init__(self, path: str):
        super().__init__(path)
        # when mounting in Docker, without the path logs are not read because
        # they come from "another" computer. in that case the path points
        # mounted journal files, otherwise None will be transparent
        self._jd: Reader = journal.Reader(path=config.journal)
        self._jd.log_level(journal.LOG_INFO)
        # no nice way to check for existence, but no exception if it doesn't
        self._jd.add_match(_SYSTEMD_UNIT=path)

        try:
            next(self._jd)
        except StopIteration:
            logger.error(f"no journald entry can be read: check your permissions unless you just started reaction")

    async def logs(self) -> AsyncGenerator[Log]:
        self._jd.seek_realtime(datetime.now())
        while True:
            # evaluate to true when a new entry (at least) appears
            if await self._wait_entries() == journal.APPEND:
                print("a")
                for entry in self._jd:
                    print(entry)
                    yield self._to_log(entry)

    async def _wait_entries(self) -> int:
        # Reader.wait() is synchronous, execute in another thread
        loop = asyncio.get_running_loop()
        # back to polling with 1s non-blocking timeout
        res: int = await loop.run_in_executor(None, self._jd.wait, 1)
        return res

    def _to_log(self, entry: dict[str, Any]) -> Log:
        # timestamp is already a datetime object
        return Log(entry["__REALTIME_TIMESTAMP"], entry["PRIORITY"], entry["MESSAGE"].strip())
