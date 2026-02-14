import asyncio
import uvloop
import sys
import socket
import time

from loguru import logger

from sipapy.network.TcpServer import TcpServer
from sipapy.network.UdpServer import UdpServer
from sipapy.network.TransportType import TransportType

# Re-export TransportType for convenience
__all__ = ['SipCore', 'TransportType']
from sipapy.core.Exceptions import dump_exception
# from sipapy.time.MonoTime import MonoTime
# from sipapy.time.Timeout import Timeout
from sipapy.SipHeader import SipHeader
from sipapy.SipResponse import SipResponse
from sipapy.SipRequest import SipRequest
from sipapy.SipAddress import SipAddress
from sipapy.SipRoute import SipRoute
from sipapy.SipHeader import SipHeader
from sipapy.exceptions.SipParseError import SipParseError, SdpParseError
from datetime import datetime
from hashlib import md5
from traceback import print_exc
from functools import reduce


from sipapy.SipTransaction import SipTransaction
from sipapy.SipTransactionStates import SipTransactionStates
from sipapy.SipTimers import SipTimers

# Set uvloop as the default event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class SipCore:
    def __init__(self, receive_callback, transports=None):
        self.server = TcpServer()
        self.transports = []  # List of all transport servers
        self.server_task = None
        self.transport_tasks = {}  # Dict to store transport tasks
        self.recvRequest = receive_callback
        self.client_transactions = {}  # client transactions
        self.server_transactions = {}  # server transactions
        
        # Setup transports based on the transports parameter
        if transports is None:
            # Default: only TCP
            transports = [TransportType.TCP]
        
        # Add additional transport servers (excluding TCP which is handled separately)
        for transport_type in transports:
            if transport_type == TransportType.UDP:
                self.transports.append(UdpServer())
            elif transport_type == TransportType.TLS:
                # TODO: Implement TLS support
                pass
            # TCP is handled separately as self.server

    def start(self, host='192.168.56.104', port=5060):
        # Start the TCP server in the background
        self.server_task = asyncio.create_task(
            self.server.start_server(host, port, data_received_callback=self.data_received))
        
        # Start additional transport servers
        for transport in self.transports:
            transport_task = asyncio.create_task(
                transport.start_server(host, port, data_received_callback=self.data_received))
            self.transport_tasks[transport] = transport_task

    async def stop(self):
        # Stop additional transport servers first
        for transport in self.transports:
            if transport in self.transport_tasks:
                await transport.stop_server()
                del self.transport_tasks[transport]
        
        # Stop the TCP server (if it's not already stopped as a transport)
        if self.server not in self.transports:
            await self.server.stop_server()
        self.server_task = None

    # User code that interacts with the server and provides a data-received callback
    async def data_received(self, connection, data):
        address = connection.peername
        rtime = time.monotonic()

        if len(data) < 32:
            return
        if isinstance(data, bytes):
            message = data.decode('utf-8', 'backslashreplace')
        else:
            message = data

        logger.debug(
            f'RECEIVED message from {address[0]}:{address[1]}:\n{message}')
        checksum = md5(data).digest()
        # retrans = self.l1rcache.get(checksum, None)
        # if retrans == None:
        #    retrans = self.l2rcache.get(checksum, None)
        # if retrans is not None:
        #    if retrans.data == None:
        #        return
        #    self.transmitData(retrans.userv, retrans.data, retrans.address)
        #    return
        if message.startswith('SIP/2.0 '):
            try:
                resp = SipResponse(message)
                tid = resp.getTId(True, True)
            except Exception as exception:
                dump_exception('can\'t parse SIP response from %s:%d' %
                               (address[0], address[1]), extra=message)
                # self.l1rcache[checksum] = SipTMRetransmitO()
                return
            if resp.getSCode()[0] < 100 or resp.getSCode()[0] > 999:
                print(
                    (datetime.now(), 'invalid status code in SIP response from %s:%d:' % address))
                print(message)
                sys.stdout.flush()
                # self.l1rcache[checksum] = SipTMRetransmitO()
                return
            resp.rtime = rtime
            if not tid in self.client_transactions:
                print('no transaction with tid of %s in progress' % str(tid))
                # self.l1rcache[checksum] = SipTMRetransmitO()
                return
            # t = self.client_transactions[tid]
            # if self.nat_traversal and resp.countHFs('contact') > 0 and not check1918(t.address[0]):
            #    cbody = resp.getHFBody('contact')
            #    if not cbody.asterisk:
            #        curl = cbody.getUrl()
            #        if check1918(curl.host):
            #            curl.host, curl.port = address
            # resp.setSource(address)
            # self.incomingResponse(resp, t, checksum)
        else:
            try:
                req = SipRequest(message)
                tids = req.getTIds()
                logger.debug(f'parse request {req}')
            except Exception as exception:
                if isinstance(exception, SipParseError):
                    resp = exception.getResponse()
                    if resp is not None:
                        self.transmitMsg(server, resp, address, checksum)
                dump_exception('can\'t parse SIP request from %s:%d' %
                               (address[0], address[1]), extra=message)
                # self.l1rcache[checksum] = SipTMRetransmitO()
                return
            req.rtime = rtime
            via0 = req.getHFBody('via')
            ahost, aport = via0.getAddr()
            rhost, rport = address
            # if self.nat_traversal and rport != aport and (check1918(ahost) or check7118(ahost)):
            #     req.nated = True
            # if ahost != rhost:
            #     via0.params['received'] = rhost
            # if 'rport' in via0.params or req.nated:
            #     via0.params['rport'] = str(rport)
            # if self.nat_traversal and req.countHFs('contact') > 0 and req.countHFs('via') == 1:
            #     try:
            #         cbody = req.getHFBody('contact')
            #     except Exception as exception:
            #         dump_exception('can\'t parse SIP request from %s:%d: %s:' % (
            #             address[0], address[1]), extra=message)
            #         self.l1rcache[checksum] = SipTMRetransmitO()
            #         return
            #     if not cbody.asterisk:
            #         curl = cbody.getUrl()
            #         if check1918(curl.host) or curl.port == 0 or curl.host == '255.255.255.255':
            #             curl.host, curl.port = address
            #             req.nated = True
            req.setSource(address)
            try:
                await self.incomingRequest(req, checksum, tids, connection)
            # except RtpProxyError as ex:
            #     resp = ex.getResponse(req)
            #     self.sendResponse(resp)
            #     raise
            except SdpParseError as ex:
                resp = ex.getResponse(req)
                self.sendResponse(resp)
            except SipParseError as ex:
                resp = ex.getResponse(req)
                if resp is None:
                    raise ex
                self.sendResponse(resp)

    # Server transaction methods
    async def incomingRequest(self, msg, checksum, tids, connection):
        for tid in tids:
            if tid in self.client_transactions:
                logger.info('Loop Detected')
                t = self.client_transactions[tid]
                resp = msg.genResponse(482, 'Loop Detected')
                self.transmitMsg(connection, resp, resp.getHFBody('via').getTAddr())
                return
        if msg.getMethod() != 'ACK':
            tid = msg.getTId(wBRN=True)
        else:
            tid = msg.getTId(wTTG=True)

        # check for existing server transaction
        t = self.server_transactions.get(tid, None)
        if t != None:
            logger.debug('existing transaction')
            if msg.getMethod() == t.method:
                # Duplicate received, check that we have sent any response on this request already
                if t.data != None:
                    self.transmitData(t.userv, t.data, t.address, checksum)
                return
            elif msg.getMethod() == 'CANCEL':
                # RFC3261 says that we have to reply 200 OK in all cases if there is such transaction
                resp = msg.genResponse(200, 'OK')
                self.transmitMsg(t.connection, resp, resp.getHFBody('via').getTAddr())
                if t.state in (SipTransactionStates.TRYING, SipTransactionStates.PROCEEDING):
                    #self.doCancel(t, msg.rtime, msg)
                    pass # TODO implement doCancel
            elif msg.getMethod() == 'ACK' and t.state == COMPLETED:
                t.state = CONFIRMED
                if t.teA != None:
                    t.teA.cancel()
                    t.teA = None
                t.teD.cancel()
                # We have done with the transaction, no need to wait for timeout
                del self.server_transactions[t.tid]
                if t.ack_cb != None:
                    t.ack_cb(msg)
                t.cleanup()
                # self.l1rcache[checksum] = SipTMRetransmitO()
        elif msg.getMethod() == 'ACK':
            # Some ACK that doesn't match any existing transaction.
            # Drop and forget it - upper layer is unlikely to be interested
            # to seeing this anyway.
            logger.info('unmatched ACK transaction - ignoring')
            # self.l1rcache[checksum] = SipTMRetransmitO()
        elif msg.getMethod() == 'CANCEL':
            resp = msg.genResponse(481, 'Call Leg/Transaction Does Not Exist')
            self.transmitMsg(server, resp, resp.getHFBody(
                'via').getTAddr(), checksum)
        else:
            logger.debug(f'new incoming transaction {msg.getMethod()} tit {tid}')
            t = SipTransaction(self.sendResponse)
            t.tid = tid
            t.state = SipTransactionStates.TRYING
            t.connection = connection
            # t.teA = None
            # t.teD = None
            # t.teE = None
            # t.teF = None
            # t.teG = None
            t.method = msg.getMethod()
            # t.rtime = msg.rtime
            # t.data = None
            # t.address = None
            # t.noack_cb = None
            # t.ack_cb = None
            # t.cancel_cb = None
            # t.checksum = checksum
            # if not server.uopts.isWildCard():
            #     t.userv = server
            # else:
            #     # For messages received on the wildcard interface find
            #     # or create more specific server.
            #     t.userv = self.l4r.geserver_transactions(msg.getSource())
            # if msg.getMethod() == 'INVITE':
            #     t.r487 = msg.genResponse(487, 'Request Terminated')
            #     t.needack = True
            #     t.branch = msg.getHFBody('via').getBranch()
            #     try:
            #         e = msg.getHFBody('expires').getNum()
            #         if e <= 0:
            #             e = 300
            #     except IndexError:
            #         e = 300
            #     t.teE = Timeout(self.timerE, e, 1, t)
            # else:
            #     t.r487 = None
            #     t.needack = False
            #     t.branch = None
            self.server_transactions[t.tid] = t
            # for consumer in self.req_consumers.get(t.tid[0], ()):
            #     cobj = consumer.cobj.isYours(msg)
            #     if cobj != None:
            #         rval = cobj.recvRequest(msg, t)
            # Handle both async and sync callbacks
            callback_result = self.recvRequest(msg, t)
            if asyncio.iscoroutine(callback_result):
                rval = await callback_result
            else:
                rval = callback_result

            #         break
            # else:
            #     if self.req_cb == None:
            #         self.l1rcache[checksum] = SipTMRetransmitO()
            #         return
            #     rval = self.req_cb(msg, t)
            # if rval == None:
            #     if t.teA != None or t.teD != None or t.teE != None or t.teF != None:
            #         return
            #     if t.tid in self.server_transactions:
            #         del self.server_transactions[t.tid]
            #     t.cleanup()
            #     return
            # resp, t.cancel_cb, t.noack_cb = rval
            
            # Handle case where callback returns just a response vs tuple
            if isinstance(rval, tuple) and len(rval) >= 1:
                resp = rval[0]
            else:
                resp = rval
                
            if resp != None:
                self.sendResponse(resp, t)


    def sendResponse(self, resp, t=None, retrans=False, ack_cb=None):
        if t == None:
            tid = resp.getTId(wBRN=True)
            t = self.server_transactions[tid]
        if t.state not in (SipTransactionStates.TRYING, SipTransactionStates.PROCEEDING) and not retrans:
            raise ValueError('BUG: attempt to send reply on already finished transaction!')
        
        scode = resp.getSCode()[0]
        toHF = resp.getHFBody('to')
        if scode > 100 and toHF.getTag() == None:
            toHF.genTag()
        
        address = resp.getHFBody('via').getTAddr()
        self.transmitMsg(t.connection, resp, address)
        
        if scode < 200:
            t.state = SipTransactionStates.PROCEEDING
            # if self.provisional_retr > 0 and scode > 100:
            #     if t.teF is not None:
            #         t.teF.cancel()
            #     t.teF = Timeout(self.timerF, self.provisional_retr, 1, t)
        else:
            t.state = SipTransactionStates.COMPLETED
            # if t.teE is not None:
            #     t.teE.cancel()
            #     t.teE = None
            # if t.teF is not None:
            #     t.teF.cancel()
            #     t.teF = None
            if t.need_ack:
                # Schedule removal of the transaction
                t.ack_cb = ack_cb
                #t.teD = Timeout(self.timerD, 32.0, 1, t)
                
                
                # if scode >= 200:
                #     # Black magick to allow proxy send us another INVITE
                #     # same branch and From tag. Use To tag to match
                #     # ACK transaction after this point. Branch tag in ACK
                #     # could differ as well.
                #     del self.server_transactions[t.tid]
                #     t.tid = list(t.tid[:-1])
                #     t.tid.append(resp.getHFBody('to').getTag())
                #     t.tid = tuple(t.tid)
                #     self.server_transactions[t.tid] = t
                # Install retransmit timer if necessary
                
                #t.tout = 0.5
                #t.teA = Timeout(self.timerA, t.tout, 1, t)
            else:
                # We have done with the transaction
                del self.server_transactions[t.tid]
                #t.cleanup()


    def transmitMsg(self, connection, msg, address):
        data = msg.localStr('192.168.56.104')
        logger.debug(f'SENDING message to {address[0]}:{address[1]}\n{data}')
        
        # Check if this is a UDP connection (has send_to method)
        if hasattr(connection, 'send_to'):
            # UDP connection - use old method for backward compatibility
            connection.send_to(address, data)
        elif hasattr(connection, 'send_data'):
            # TCP connection or new-style connection
            if hasattr(connection, 'peername'):
                # TCP connection - use connection directly
                connection.send_data(data)
            else:
                # UDP-style connection - need to find the right transport
                # For now, send via UDP if available
                for transport in self.transports:
                    if transport.get_transport_type() == TransportType.UDP:
                        transport.send_data(data, address)
                        break

    # def transmitData(self, userv, data, address, cachesum=None):
    #     userv.send_to(data, address)
    #     logger.debug(f'SENDING message to {address[0]}:{address[1]}\n{data}')
        # if cachesum is not None:
        #     self.l1rcache[cachesum] = SipTMRetransmitO(userv, data, address, None)

    def sendACK(self, t):
        # print 'sendACK', t.state
        if t.teG is not None:
            t.teG.cancel()
            t.teG = None
        self.transmitMsg(t.userv, t.ack, t.ack_rAddr)
        if t.req_out_cb is not None:
            t.req_out_cb(t.ack)
        del self.tclient[t.tid]
        t.cleanup()
