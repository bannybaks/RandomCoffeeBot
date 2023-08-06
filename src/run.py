import structlog

from bot.bot import init_bot
from depends import Container
from src.core import init_logging


def main():
    container = Container()
    container.wire(packages=("src",))
    init_logging()
    bot = init_bot(container.settings())
    log = structlog.get_logger()
    log.info("Application started")
    bot.run()


if __name__ == "__main__":
    main()
