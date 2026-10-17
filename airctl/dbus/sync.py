import asyncio
import atexit
import threading


class DBusRunner:
    def __init__(self):
        self._loop = None
        self._thread = None
        self._lock = threading.Lock()
        self._shutdown_hooks = []

        atexit.register(self.stop)

    def _start(self):
        if self._loop is not None:
            return

        with self._lock:
            if self._loop is not None:
                return

            loop = asyncio.new_event_loop()
            thread = threading.Thread(
                target=self._run,
                args=(loop,),
                name="airctl-dbus",
                daemon=True,
            )

            self._loop = loop
            self._thread = thread

            thread.start()

    def _run(self, loop):
        asyncio.set_event_loop(loop)

        try:
            loop.run_forever()
        finally:
            pending = asyncio.all_tasks(loop)

            for task in pending:
                task.cancel()

            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    def add_shutdown_hook(self, hook):
        self._shutdown_hooks.append(hook)

    def call(self, coroutine):
        self._start()

        if self._loop.is_closed():
            raise RuntimeError("the D-Bus event loop is closed")

        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)

        return future.result()

    async def _close(self):
        for hook in self._shutdown_hooks:
            try:
                result = hook()

                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                pass

    def stop(self):
        loop = self._loop

        if loop is None or loop.is_closed() or not loop.is_running():
            return

        try:
            future = asyncio.run_coroutine_threadsafe(self._close(), loop)
            future.result(timeout=3)
        except Exception:
            pass

        try:
            loop.call_soon_threadsafe(loop.stop)
        except RuntimeError:
            pass

        self._thread.join(timeout=3)
