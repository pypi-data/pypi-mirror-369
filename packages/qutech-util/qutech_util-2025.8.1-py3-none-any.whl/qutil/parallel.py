import threading
import time


class ThreadedPeriodicCallback:
    """Periodically call the given function. Dont forget to call start. You can change the period while it runs.
    Be aware that your callback needs to be thread safe. This means you need to make sure that the state there is always
    consistent.

    Example:
        >>> pcb = ThreadedPeriodicCallback(1., lambda: print('my function'))  # doctest: +SKIP
        >>> pcb.start()  # doctest: +SKIP

        >>> pcb.stop()  # doctest: +SKIP
        Stop the parallel thread
    """
    def __init__(self, period: float, callback: callable):
        self._stop = None
        self.period = period
        self.callback = callback
        self.thread = None

    def _run(self):
        while not self._stop:
            self.callback()
            time.sleep(self.period)

    def stop(self):
        if self.thread is not None:
            self._stop = True
            print('Stop the parallel thread')
            self.thread.join()
            self.thread = None

    def start(self):
        if self.thread is not None:
            raise RuntimeError("Thread is still running")

        self._stop = False
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def __del__(self):
        self.stop()
