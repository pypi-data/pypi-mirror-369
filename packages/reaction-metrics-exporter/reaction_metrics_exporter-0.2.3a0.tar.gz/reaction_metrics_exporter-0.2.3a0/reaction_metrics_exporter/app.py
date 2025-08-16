import argparse
import asyncio
import json
import logging
import sys
import textwrap

import asyncio_simple_http_server
from asyncio_simple_http_server import HttpServer
from ruamel.yaml import YAML
import structlog

from . import __version__
from .handler import MetricsHandler
from .models.config import Config
from .models.event import Start
from .models.exception import ReactionException, UnsupportedLine
from .models.metric import ReactionMetrics
from .reaction import Reaction
from .reader import FileReader, JournalReader
from .transformer import ActionIgnored, Transformer, UnsupportedLog

config = Config.get_config()
logger = structlog.get_logger()
# dirty hack so that we don't have ill-formatted debug messages
asyncio_simple_http_server.server.logger.setLevel(logging.WARNING)

parser = argparse.ArgumentParser(
    prog=f"python -m {__package__}",
    epilog=textwrap.dedent(
        """
    command:
        start: continuously read logs, compute metrics and serve HTTP endpoint
        defaults: print the default configuration in json and exit
        test-config: validate and output configuration in json and exit
        version: print the exporter's version and exit
        """
    ),
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument("command", help="mode of operation; see below", choices=["start", "defaults", "test-config", "version"])
parser.add_argument("-c", "--config", help="path to the configuration file (JSON or YAML)", required=False)
parser.add_argument(
    "-f", "--format", help="format for dumping default configuration (defautl yaml)", choices=("yaml", "json"), default="yaml", required=False
)


class ExporterApp:
    def __init__(self) -> None:
        self.metrics = ReactionMetrics()

        match config.type:
            case "file":
                reader_class = FileReader
            case "systemd":
                reader_class = JournalReader
            case _:
                raise TypeError(f"unknown log type: {config.type}")

        # path is either a filepath or a unit name
        self.reader: FileReader | JournalReader = reader_class(config.path)

    async def start(self):
        """
        command start: consume new metrics, serve them, etc.
        """
        # fetch reaction configuration
        Reaction.init()
        # executes in a background task
        await self._run_webserver()
        # ignore actions if needed
        asyncio.create_task(self._wait_ignore_actions())
        # executes until stream is closed
        await self._consume_logs()

    @staticmethod
    def defaults(format: str) -> None:
        """
        command defaults: dumps pretty-print default configuration.
        """
        conf = config._schema.validate({})
        match format:
            case "json":
                json.dump(conf, sort_keys=True, indent=4, fp=sys.stdout)
            case "yaml":
                with YAML(output=sys.stdout) as yaml:
                    yaml.dump(conf)
            case _:
                raise ValueError(f"unsupported format: {format}")
        sys.exit(0)

    @staticmethod
    def version() -> None:
        print(__version__)
        sys.exit(0)

    @staticmethod
    def test_config() -> None:
        """
        command test_config: validates and dumps configuration.
        """
        logger.info("valid config. dumping with added defaults...")
        print(json.dumps(config._conf, sort_keys=True, indent=4))
        sys.exit(0)

    @classmethod
    async def run(cls):
        args = parser.parse_args()
        logger.debug(f"running with command {args.command}")

        if args.command == "defaults":
            cls.defaults(args.format)
        elif args.command == "version":
            cls.version()

        # fetch exporter configuration
        if args.config is not None:
            config.from_file(args.config)
            if args.command == "test-config":
                cls.test_config()
        else:
            logger.warn(f"running without configuration file is not recommended: use your own")
            config.from_default()

        cls._configure_logger()
        inst = cls()

        # run command
        match args.command:
            case "start":
                await inst.start()
            case _:
                raise ValueError(f"unknown command: {args.command}")

    async def _consume_logs(self):
        # never stops while async generator does not stop
        try:
            async for log in self.reader.logs():
                try:
                    event = Transformer.to_event(log)
                    match event:
                        case Start():
                            # reset counter if multiple restarts
                            if config.ignore_actions < config.hold:
                                config.ignore_actions = config.hold
                                logger.info(f"start command detected, ignoring actions for {config.ignore_actions} seconds")
                        case _:
                            pass
                    self.metrics.add(event)

                except ActionIgnored:
                    logger.info(f"reaction is starting, ignoring action: {log}")
                # do not quit for a bad formatted log
                except ReactionException as e:
                    logger.warning(f"{e.__class__.__name__}: {e}; ignoring line")
        except (UnsupportedLog, UnsupportedLine) as e:
            logger.warning(f"cannot parse line: {e}")

    async def _run_webserver(self):
        http_server = HttpServer()
        http_server.add_handler(MetricsHandler(self.metrics))
        address, port = config.listen
        await http_server.start(address, port)
        logger.info(f"web server listens on http://{address}:{port}/metrics")
        asyncio.create_task(http_server.serve_forever())

    async def _wait_ignore_actions(self):
        """continuously decrease the ignore action counter if > 0"""
        while True:
            if config.ignore_actions > 0:
                config.ignore_actions -= 1
                if config.ignore_actions == 0:
                    logger.info("starting to take into account reaction commands, actions and so on.")
            await asyncio.sleep(1)

    @staticmethod
    def _configure_logger():
        colors = structlog.dev.ConsoleRenderer.get_default_level_styles()
        colors["info"] = structlog.dev.BLUE
        colors["warn"] = structlog.dev.YELLOW
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
                structlog.dev.ConsoleRenderer(level_styles=colors),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, config.log_level)),
        )
