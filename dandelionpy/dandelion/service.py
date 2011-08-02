"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of Dandelion Messaging System.

Dandelion is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dandelion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Dandelion.  If not, see <http://www.gnu.org/licenses/>.
"""
import threading
import time

class Service:
    """Interface for an asynchronous background daemon."""

    def start(self):
        """Start the service. Block until the service is running."""

    def stop(self):
        """Stop the service. Block until the service is running."""

    def restart(self):
        """Stop then start the service. Blocking call"""
        self.stop()
        self.start()

    @property
    def running(self):
        """Returns True if the service is running, False otherwise"""


class RepetitiveWorker(Service):
    """Helper for a service implementation of a service that 
    repeatedly runs one and the same function."""

    def __init__(self, work_func, min_wait_time_sec=10):

        if not hasattr(work_func, '__call__'):
            raise TypeError

        if float(min_wait_time_sec) < 0:
            raise ValueError

        self._running = False
        self._stop_requested = True
        self._thread = None

        self._work_func = work_func
        self._min_wait_time_sec = min_wait_time_sec

    def start(self):
        """Start the service. Block until the service is running."""

        if self._running:
            return # Starting twice is a nop

        self._stop_requested = False
        self._thread = threading.Thread(target=self._work_loop)
        self._thread.start()
        self._running = True

    def stop(self):
        """Stop the service. Block until the service is stopped."""

        if not self._running:
            return # Stopping twice is a nop

        self._stop_requested = True
        if self._thread is not None:
            self._thread.join(1)
            if self._thread.is_alive():
                raise Exception # Timeout

        self._running = False

    @property
    def running(self):
        """Returns True if the service is running, False otherwise"""
        return self._running

    def _work_loop(self):
        """The sisyphosian work loop. Repeat the work function until it is stopped.
        
        No matter how fast the work function returns, wait at least min_wait_time_sec before running again.
        """

        t1 = time.time()
        while not self._stop_requested:
            t2 = time.time()

            """Should we run discovery yet or just keep checking the stop condition?"""
            if t2 - t1 < self._min_wait_time_sec:
                time.sleep(0.01) # Don't busy wait
                continue

            self._work_func()

            t1 = time.time()
