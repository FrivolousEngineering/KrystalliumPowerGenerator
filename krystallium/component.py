import asyncio
import time
import logging
import signal


log = logging.getLogger(__name__)


class Component:
    """
    A base class that standardises some common patterns for running in an async loop.

    This adds async start/stop methods to deal with async initialization and deinitalization.
    It also adds an async update method that can be overridden to execute component-specific
    update logic. The update method will be called based on the interval specified.

    Components can also have children that are components. When start or stop of a component
    is called this will also start/stop the children. Furthermore the component will make sure
    to update children when needed.
    """

    def __init__(self, *args, name: str | None = None, interval: float | None = None, **kwargs) -> None:
        super().__init__()
        self.__name = name if name is not None else type(self).__name__
        self.__children: list[Component] = []
        self.__interval: float | None = interval
        self.__elapsed: float = 0
        self.__last_update: float = 0

    @property
    def name(self) -> str:
        return self.__name

    @property
    def children(self) -> list["Component"]:
        return self.__children

    async def start(self) -> None:
        for child in self.__children:
            log.debug(f"Starting {child.name}")
            await child.start()

    async def stop(self) -> None:
        for child in self.__children:
            log.debug(f"Stopping {child.name}")
            await child.stop()

    async def maybe_update(self) -> None:
        if self.__interval is None:
            return

        now = time.perf_counter()
        self.__elapsed += now - self.__last_update
        self.__last_update = now

        if self.__elapsed >= self.__interval:
            await self.update(self.__elapsed)
            self.__elapsed = 0

        for child in self.__children:
            await child.maybe_update()

    async def update(self, elapsed: float) -> None:
        raise NotImplementedError()


class MainLoop(Component):
    """
    A standardised "main loop" component that will run a loop as an async task. The loop will run
    at most update_rate times per second. It will ensure to call start() before starting the loop
    and stop() at the end.
    """

    def __init__(self, *, name: str | None = None, update_rate: int = 100, interval: float | None = None):
        super().__init__(name = name, interval = interval)
        self.__update_rate = update_rate
        self.__running = True

    async def run_loop(self):
        await self.start()

        interval = 1 / self.__update_rate

        try:
            while self.__running:
                start = time.perf_counter()

                await self.maybe_update()

                remain = interval - (time.perf_counter() - start)
                if remain > 0:
                    await asyncio.sleep(remain)
        finally:
            await self.stop()

    def run(self):
        loop = asyncio.new_event_loop()

        run_task = loop.create_task(self.run_loop())

        for s in signal.SIGINT, signal.SIGTERM:
            loop.add_signal_handler(s, run_task.cancel)

        loop.run_until_complete(run_task)

    def stop_loop(self):
        self.__running = False
