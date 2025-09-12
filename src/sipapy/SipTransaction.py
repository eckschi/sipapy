import asyncio
import time
from loguru import logger
from sipapy.SipTransactionStates import SipTransactionStates

class SipTransaction:
    def __init__(
        self,
        send_func,                     # async or sync send function
        timer_interval=0.5,            # base retransmit interval (T1)
        max_interval=4.0,              # max interval (T2)
        timeout=32.0,                  # overall transaction timeout (e.g. Timer F)
        retransmit=True,                # should retransmission occur
    ):
        self.send_func = send_func
        self.retransmit = retransmit
        self.initial_interval = timer_interval
        self.max_interval = max_interval
        self.timeout = timeout

        self._response_event = asyncio.Event()
        self._start_time = None
        self._active = False

        self.method : str = None
        self.tid = None
        self.connection = None

        self.need_ack = False
        self.ack_cb = None

    async def start(self):
        self._active = True
        self._start_time = time.monotonic()

        if self.retransmit:
            asyncio.create_task(self._retransmit_loop())

        try:
            await asyncio.wait_for(self._response_event.wait(), timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.warning("Transaction timed out after %.1f seconds", self.timeout)
        finally:
            self._active = False

    def receive_response(self, code: int):
        """Should be called externally when a response is received"""
        if self._active:
            logger.info("Response received: %s", code)
            self._response_event.set()

    async def _retransmit_loop(self):
        interval = self.initial_interval
        while self._active and not self._response_event.is_set():
            logger.debug("Transmitting request")
            result = self.send_func()
            if asyncio.iscoroutine(result):
                await result
            await asyncio.sleep(interval)
            interval = min(interval * 2, self.max_interval)

# async def dummy_send():
#     logger.info("Sending SIP request")

# async def main():
#     tx = AsyncSipTransaction(
#         send_func=dummy_send,
#         timer_interval=0.5,   # T1
#         max_interval=4.0,     # T2
#         timeout=64 * 0.5,     # Timer B/F
#     )
#     asyncio.create_task(tx.start())

#     await asyncio.sleep(1.5)
#     tx.receive_response(200)
