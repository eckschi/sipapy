# author <me@eckschi.net>
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
import uvloop

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Timer:
    def __init__(self, timeout, callback):
        """
        Initialize the timer with a timeout (in seconds) and a callback method.
        :param timeout: Time in seconds after which the callback is called.
        :param callback: The method to be executed after the timeout.
        """
        self.timeout = timeout
        self.callback = callback
        self._task = None

    def start(self):
        """Start the timer."""
        # Create and start the timer task
        self._task = asyncio.create_task(self._run_timer())

    async def _run_timer(self):
        """Wait for the specified time and then call the callback."""
        try:
            print(f"Timer started for {self.timeout} seconds.")
            await asyncio.sleep(self.timeout)  # Wait for the timeout
            print(f"Timeout reached, executing callback.")
            self.callback()  # Call the callback method
        except asyncio.CancelledError:
            print("Timer was canceled.")

    def cancel(self):
        """Cancel the timer before it finishes."""
        if self._task:
            self._task.cancel()  # Cancel the task

# Example callback method to be called when the timer expires
def on_timeout():
    print("Timer expired, callback executed!")

async def main():
    # Create a timer that will trigger after 5 seconds
    timer = Timer(5, on_timeout)
    timer.start()

    # You can cancel the timer before it expires (e.g., after 2 seconds)
    await asyncio.sleep(2)  # Let the timer run for 2 seconds
    timer.cancel()  # Cancel the timer

    # Wait to ensure all tasks finish
    await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
