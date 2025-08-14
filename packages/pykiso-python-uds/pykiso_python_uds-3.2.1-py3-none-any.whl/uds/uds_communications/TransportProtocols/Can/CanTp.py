#!/usr/bin/env python

from __future__ import annotations

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

import logging
import queue
from typing import List

from uds.config import Config
from uds.interfaces import TpInterface
from uds import ResettableTimer, fillArray
from uds.uds_communications.TransportProtocols.Can.CanTpTypes import (
    CANTP_MAX_PAYLOAD_LENGTH,
    CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX,
    CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX,
    FC_BS_INDEX,
    FC_STMIN_INDEX,
    FIRST_FRAME_DATA_START_INDEX,
    FIRST_FRAME_DL_INDEX_HIGH,
    FIRST_FRAME_DL_INDEX_LOW,
    MINIMUM_HEADER_SIZE,
    N_PCI_INDEX,
    SINGLE_FRAME_DATA_START_INDEX,
    CanTpAddressingTypes,
    CanTpFsTypes,
    CanTpMessageType,
    CanTpMTypes,
    CanTpState,
)

logger = logging.getLogger(__name__)


##
# @class CanTp
# @brief This is the main class to support CAN transport protocol
#
# Will spawn a CanTpListener class for incoming messages
# depends on a bus object for communication on CAN
class CanTp(TpInterface):

    configParams = ["reqId", "resId", "addressingType"]
    PADDING_PATTERN = 0x00
    CAN_FD_DATA_LENGTHS = (8, 12, 16, 20, 24, 32, 48, 64)

    ##
    # @brief constructor for the CanTp object
    def __init__(self, connector=None, is_fd: bool = True, **kwargs):

        self.__N_AE = Config.isotp.n_ae
        self.__N_TA = Config.isotp.n_ta
        self.__N_SA = Config.isotp.n_sa

        Mtype = Config.isotp.m_type
        if Mtype == "DIAGNOSTICS":
            self._M_type = CanTpMTypes.DIAGNOSTICS
        elif Mtype == "REMOTE_DIAGNOSTICS":
            self._M_type = CanTpMTypes.REMOTE_DIAGNOSTICS
        else:
            raise Exception("Do not understand the Mtype config")

        addressingType = Config.isotp.addressing_type
        if addressingType == "NORMAL":
            self._addressing_type = CanTpAddressingTypes.NORMAL
        elif addressingType == "NORMAL_FIXED":
            self._addressing_type = CanTpAddressingTypes.NORMAL_FIXED
        elif self._addressing_type == "EXTENDED":
            self._addressing_type = CanTpAddressingTypes.EXTENDED
        elif addressingType == "MIXED":
            self._addressing_type = CanTpAddressingTypes.MIXED
        else:
            raise Exception("Do not understand the addressing config")

        self.__reqId = Config.isotp.req_id
        self.__resId = Config.isotp.res_id

        self._connection = connector
        self._recv_buffer = queue.Queue()
        self._discard_negative_responses = Config.isotp.discard_neg_resp

        # default STmin for flow control when receiving consecutive frames
        self.st_min = 0.030

        # sets up the relevant parameters in the instance
        if self._addressing_type in (CanTpAddressingTypes.NORMAL, CanTpAddressingTypes.NORMAL_FIXED):
            self._pdu_start_index = 0
        elif self._addressing_type in (CanTpAddressingTypes.EXTENDED, CanTpAddressingTypes.MIXED):
            self._pdu_start_index = 1

        self._max_frame_length = 64 if is_fd else 8
        # 7 bytes PDU for normal addressing, 6 for extended and mixed
        self._max_pdu_length = self._max_frame_length - self._pdu_start_index - MINIMUM_HEADER_SIZE
        # maximum payload length of a 'classic' single frame with a message data length of 7 bytes at most (defined by ISO)
        self._single_frame_max_length_for_short_header = 0b111 - self._pdu_start_index

    @property
    def is_fd(self) -> bool:
        return self._max_frame_length == 64

    @is_fd.setter
    def is_fd(self, value: bool):
        self._max_frame_length = 64 if value is True else 8
        self._max_pdu_length = self._max_frame_length - self._pdu_start_index - MINIMUM_HEADER_SIZE

    @property
    def reqIdAddress(self):
        return self.__reqId

    @reqIdAddress.setter
    def reqIdAddress(self, value):
        self.__reqId = value

    @property
    def resIdAddress(self):
        return self.__resId

    @resIdAddress.setter
    def resIdAddress(self, value):
        self.__resId = value

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    ##
    # @brief send method
    # @param [in] payload the payload to be sent
    # @param [in] tpWaitTime time to wait inside loop
    def send(self, payload, functionalReq=False, tpWaitTime=0.01) -> None:
        result = self.encode_isotp(payload, functionalReq)
        return result

    def make_single_frame(self, payload: List[int]) -> List[int]:
        single_frame = [self.PADDING_PATTERN] * 8
        if not self.is_fd or len(payload) <= self._single_frame_max_length_for_short_header:
            # if we are not using CAN FD or the payload can be packed within 8 bytes, create a short frame
            # the MDL is then indicated on the low nibble of the 1st byte
            single_frame = [
                (CanTpMessageType.SINGLE_FRAME << 4) + len(payload),
                # pad the frame to send to have a total length of 8 bytes
                *fillArray(
                    payload, length=self._single_frame_max_length_for_short_header, fillValue=self.PADDING_PATTERN
                ),
            ]
        else:
            # otherwise the MDL is indicated in the entire 2nd byte
            single_frame = [CanTpMessageType.SINGLE_FRAME, len(payload), *payload]
            single_frame = self.add_padding(single_frame)
        return single_frame

    def make_first_frame(self, payload: List[int]) -> List[int]:
        mdl = len(payload)
        mdl_high_nibble = (mdl & 0xF00) >> 8
        mdl_low_nibble = mdl & 0x0FF
        first_frame = [
            (CanTpMessageType.FIRST_FRAME << 4) + mdl_high_nibble,
            mdl_low_nibble,
            *payload[: self._max_pdu_length - 1],
        ]
        first_frame = self.add_padding(first_frame)
        return first_frame

    def make_consecutive_frame(self, payload: List[int], sequence_number: int = 1) -> List[int]:
        consecutive_frame = [(CanTpMessageType.CONSECUTIVE_FRAME << 4) + sequence_number, *payload]
        consecutive_frame = self.add_padding(consecutive_frame)
        return consecutive_frame

    def make_flow_control_frame(self, blocksize: int = 0, st_min: float = 0) -> List[int]:
        flow_control_frame = [(CanTpMessageType.FLOW_CONTROL << 4), blocksize, self.encode_stMin(st_min)]
        flow_control_frame = self.add_padding(flow_control_frame)
        return flow_control_frame

    ##
    # @brief encoding method
    # @param payload the payload to be sent
    # @param use_external_snd_rcv_functions boolean to state if external sending and receiving functions shall be used
    # @param [in] tpWaitTime time to wait inside loop
    def encode_isotp(
        self,
        payload,
        functionalReq: bool = False,
        use_external_snd_rcv_functions: bool = False,
    ) -> List[int] | None:

        payloadLength = len(payload)
        payloadPtr = 0

        state = CanTpState.IDLE

        if payloadLength > CANTP_MAX_PAYLOAD_LENGTH:
            raise ValueError("Payload too large for CAN Transport Protocol")

        if payloadLength <= self._max_pdu_length:
            state = CanTpState.SEND_SINGLE_FRAME
        else:
            # we might need a check for functional request as we may not be able to service functional requests for
            # multi frame requests
            state = CanTpState.SEND_FIRST_FRAME

        sequenceNumber = 1
        endOfMessage_flag = False

        blockList = []
        current_block = []

        # TODO this needs fixing to get the timing from the config
        # general timeout when waiting for a flow control frame from the ECU
        timeoutTimer = ResettableTimer(1)
        stMinTimer = ResettableTimer()

        data = None

        while endOfMessage_flag is False:

            if state == CanTpState.WAIT_FLOW_CONTROL:
                rxPdu = self.getNextBufferedMessage(timeoutTimer.remainingTime)
                if rxPdu is None:
                    raise TimeoutError("Timed out while waiting for flow control message")

                N_PCI = (rxPdu[0] & 0xF0) >> 4
                if N_PCI == CanTpMessageType.FLOW_CONTROL:
                    fs = rxPdu[0] & 0x0F
                    if fs == CanTpFsTypes.CONTINUE_TO_SEND:
                        if state != CanTpState.WAIT_FLOW_CONTROL:
                            raise ValueError("Received unexpected Flow Control Continue to Send request")

                        block_size = rxPdu[FC_BS_INDEX]
                        if block_size == 0:
                            block_size = 585
                        blockList = self.create_blockList(payload[payloadPtr:], block_size)
                        current_block = blockList.pop(0)
                        stMin = self.decode_stMin(rxPdu[FC_STMIN_INDEX])
                        stMinTimer.timeoutTime = stMin
                        stMinTimer.start()
                        timeoutTimer.stop()
                        state = CanTpState.SEND_CONSECUTIVE_FRAME
                    elif fs == CanTpFsTypes.WAIT:
                        raise NotImplementedError("Wait not currently supported")
                    elif fs == CanTpFsTypes.OVERFLOW:
                        raise Exception("Overflow received from ECU")
                    else:
                        raise ValueError(f"Unexpected fs response from ECU. {rxPdu}")
                else:
                    logger.warning(
                        f"Unexpected response from ECU while waiting for flow control: 0x{bytes(rxPdu).hex()}"
                    )

            if state == CanTpState.SEND_SINGLE_FRAME:
                txPdu = self.make_single_frame(payload)
                data = self.transmit(txPdu, functionalReq, use_external_snd_rcv_functions)
                endOfMessage_flag = True
            elif state == CanTpState.SEND_FIRST_FRAME:
                txPdu = self.make_first_frame(payload)
                payloadPtr += self._max_pdu_length - 1
                data = self.transmit(txPdu, functionalReq, use_external_snd_rcv_functions)
                timeoutTimer.start()
                state = CanTpState.WAIT_FLOW_CONTROL
            elif state == CanTpState.SEND_CONSECUTIVE_FRAME and stMinTimer.isExpired():
                txPdu = self.make_consecutive_frame(current_block.pop(0), sequenceNumber)
                payloadPtr += self._max_pdu_length
                data = self.transmit(txPdu, functionalReq, use_external_snd_rcv_functions)
                sequenceNumber = (sequenceNumber + 1) % 16
                stMinTimer.restart()
                if len(current_block) == 0:
                    if len(blockList) == 0:
                        endOfMessage_flag = True
                    else:
                        timeoutTimer.start()
                        state = CanTpState.WAIT_FLOW_CONTROL

        if use_external_snd_rcv_functions:
            return data

    ##
    # @brief recv method
    # @param [in] timeout_ms The timeout to wait before exiting
    # @return a list
    def recv(self, timeout_s=1):
        return self.decode_isotp(timeout_s)

    ##
    # @brief decoding method
    # @param timeout_ms the timeout to wait before exiting
    # @param received_data the data that should be decoded in case of ITF Automation
    # @param use_external_snd_rcv_functions boolean to state if external sending and receiving functions shall be used
    # @return a list
    def decode_isotp(
        self,
        timeout_s=1,
        received_data=None,
        use_external_snd_rcv_functions: bool = False,
    ) -> list:

        payload = []
        payloadPtr = 0
        payloadLength = None

        sequenceNumberExpected = 1

        endOfMessage_flag = False

        state = CanTpState.IDLE

        timeoutTimer = ResettableTimer(timeout_s)
        timeoutTimer.start()

        while endOfMessage_flag is False:

            if use_external_snd_rcv_functions and state != CanTpState.RECEIVING_CONSECUTIVE_FRAME:
                rxPdu = received_data
            else:
                rxPdu = self.getNextBufferedMessage(timeout=timeoutTimer.remainingTime)
                if rxPdu is None:
                    raise TimeoutError(f"Timed out while waiting for message in state {state.name}")

            if rxPdu[N_PCI_INDEX] == 0x00:
                rxPdu = rxPdu[1:]
                N_PCI = CanTpMessageType.SINGLE_FRAME
            else:
                N_PCI = (rxPdu[N_PCI_INDEX] & 0xF0) >> 4

            if state == CanTpState.IDLE:
                if N_PCI == CanTpMessageType.SINGLE_FRAME:
                    payloadLength = rxPdu[N_PCI_INDEX & 0x0F]
                    payload = rxPdu[SINGLE_FRAME_DATA_START_INDEX : SINGLE_FRAME_DATA_START_INDEX + payloadLength]
                    endOfMessage_flag = True
                elif N_PCI == CanTpMessageType.FIRST_FRAME:
                    payload = rxPdu[FIRST_FRAME_DATA_START_INDEX:]
                    payloadLength = ((rxPdu[FIRST_FRAME_DL_INDEX_HIGH] & 0x0F) << 8) + rxPdu[FIRST_FRAME_DL_INDEX_LOW]
                    payloadPtr = self._max_pdu_length - 1
                    state = CanTpState.SEND_FLOW_CONTROL
                elif N_PCI == CanTpMessageType.CONSECUTIVE_FRAME:
                    # Consecutive frames are not expected in idle state else we are in an infinite loop
                    raise RuntimeError("Consecutive frames are not supported in idle state")
            elif state == CanTpState.RECEIVING_CONSECUTIVE_FRAME:
                if N_PCI == CanTpMessageType.CONSECUTIVE_FRAME:
                    sequenceNumber = rxPdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] & 0x0F
                    if sequenceNumber != sequenceNumberExpected:
                        raise ValueError(
                            f"Consecutive frame sequence out of order, expected {sequenceNumberExpected} got {sequenceNumber}"
                        )

                    sequenceNumberExpected = (sequenceNumberExpected + 1) % 16
                    payload += rxPdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:]
                    payloadPtr += self._max_pdu_length
                    timeoutTimer.restart()
                else:
                    logger.warning(
                        f"Unexpected PDU received while waiting for consecutive frame: 0x{bytes(rxPdu).hex()}"
                    )

            if state == CanTpState.SEND_FLOW_CONTROL:
                txPdu = self.make_flow_control_frame(blocksize=0, st_min=self.st_min)
                self.transmit(txPdu)
                state = CanTpState.RECEIVING_CONSECUTIVE_FRAME

            if payloadLength is not None and payloadPtr >= payloadLength:
                endOfMessage_flag = True

        return list(payload[:payloadLength])

    ##
    # @brief clear out the receive list
    def clearBufferedMessages(self):
        with self._recv_buffer.mutex:
            self._recv_buffer.queue.clear()

    ##
    # @brief retrieves the next message from the received message buffers
    # @return list, or None if nothing is on the receive list
    def getNextBufferedMessage(self, timeout: float = 0) -> List[int] | None:
        try:
            return self._recv_buffer.get(timeout=timeout)
        except queue.Empty:
            return None

    ##
    # @brief the listener callback used when a message is received
    def callback_onReceive(self, msg):
        if self._addressing_type == CanTpAddressingTypes.NORMAL:
            if msg.arbitration_id == self.__resId:
                self._recv_buffer.put(list(msg.data[self._pdu_start_index :]))
        elif self._addressing_type == CanTpAddressingTypes.NORMAL_FIXED:
            raise NotImplementedError("I do not know how to receive this addressing type yet")
        elif self._addressing_type == CanTpAddressingTypes.MIXED:
            raise NotImplementedError("I do not know how to receive this addressing type yet")
        else:
            raise NotImplementedError("I do not know how to receive this addressing type")

    ##
    # @brief function to decode the StMin parameter
    @staticmethod
    def decode_stMin(val: int) -> float:
        if val <= 0x7F:
            return val / 1000
        elif 0xF1 <= val <= 0xF9:
            return (val & 0x0F) / 10000
        else:
            raise ValueError(
                f"Invalid STMin value {hex(val)}, should be between 0x00 and 0x7F or between 0xF1 and 0xF9"
            )

    @staticmethod
    def encode_stMin(val: float) -> int:
        if (0x01 * 1e-3) <= val <= (0x7F * 1e-3):
            # 1ms - 127ms -> 0x01 - 0x7F
            return int(val * 1000)
        elif 1e-4 <= val <= 9e-4:
            # 100us - 900us -> 0xF1 - 0xF9
            return 0xF0 + int(val * 1e4)
        else:
            raise ValueError(f"Invalid STMin time {val}, should be between 0.1 and 0.9 ms or between 1 and 127 ms")

    ##
    # @brief creates the blocklist from the blocksize and payload
    def create_blockList(self, payload: List[int], blockSize: int) -> List[List[int]]:

        blockList = []
        current_block = []
        currPdu = []

        payloadPtr = 0
        blockPtr = 0

        payloadLength = len(payload)
        pduLength = self._max_pdu_length
        blockLength = blockSize * pduLength
        working = True
        while working:

            if (payloadPtr + pduLength) >= payloadLength:
                working = False
                last_pdu = payload[payloadPtr:]
                current_block.append(last_pdu)
                blockList.append(current_block)

            if working:
                currPdu = payload[payloadPtr : payloadPtr + pduLength]
                current_block.append(currPdu)
                payloadPtr += pduLength
                blockPtr += pduLength

                if blockPtr == blockLength:
                    blockList.append(current_block)
                    current_block = []
                    blockPtr = 0

        return blockList

    def add_padding(self, payload: List[int]) -> List[int]:
        """Add padding to the payload to be sent over CAN.

        :param payload: payload to be sent.
        :param header_size: size of the ISO TP header of the CAN frame's payload.
        :return: the padded payload.
        """
        if not self.is_fd:
            return fillArray(
                payload,
                length=self._max_frame_length,
                fillValue=self.PADDING_PATTERN,
            )
        else:
            padded_length = next(size for size in self.CAN_FD_DATA_LENGTHS if size >= len(payload))
            return fillArray(
                payload,
                length=padded_length,
                fillValue=self.PADDING_PATTERN,
            )

    ##
    # @brief transmits the data over can using can connection
    def transmit(self, data, functionalReq=False, use_external_snd_rcv_functions: bool = False):
        # check functional request
        if functionalReq:
            raise Exception("Functional requests are currently not supported")

        transmitData = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        if self._addressing_type in (CanTpAddressingTypes.NORMAL, CanTpAddressingTypes.NORMAL_FIXED):
            transmitData = data
        elif self._addressing_type == CanTpAddressingTypes.MIXED:
            transmitData[0] = self.__N_AE
            transmitData[1:] = data
        else:
            raise Exception(f"Addressing type {self._addressing_type} is not supported yet")
        self._connection.transmit(transmitData, self.__reqId)
