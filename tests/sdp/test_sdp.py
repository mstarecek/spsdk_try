#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020 NXP
#
# SPDX-License-Identifier: BSD-3-Clause

from struct import pack

from spsdk.sdp.commands import ResponseValue, CmdResponse, CommandTag
from spsdk.sdp.error_codes import StatusCode
from spsdk.sdp.interfaces.base import Interface
from spsdk.sdp.sdp import SDP, CmdPacket


class VirtualDevice(Interface):

    def __init__(self, respond_sequence: list):
        self.respond_sequence = respond_sequence

    @property
    def is_opened(self):
        return True

    def open(self):
        pass

    def close(self):
        pass

    def read(self, timeout=1000):
        return self.respond_sequence.pop(0)

    def write(self, packet):
        pass

    def info(self):
        return 'VirtualDevice'


def test_sdp_hab_locked():
    """Test send data returns TRUE if HAB locked"""
    sdp = SDP(VirtualDevice(
        respond_sequence=[
            CmdResponse(True, pack('>I', ResponseValue.LOCKED)),
            CmdResponse(True, pack('>I', ResponseValue.HAB_SUCCESS))
        ]
    ))
    assert sdp.is_opened
    assert sdp._send_data(CmdPacket(0, 0, 0, 0), b'')
    assert sdp.status_code == StatusCode.HAB_IS_LOCKED
    assert sdp.response_value == ResponseValue.LOCKED


def test_sdp_read_hab_locked():
    """Test `read` returns None if HAB locked"""
    sdp = SDP(VirtualDevice(
        respond_sequence=[
            CmdResponse(True, pack('>I', ResponseValue.LOCKED)),
            CmdResponse(False, b"0000"),
            CmdResponse(True, pack('>I', ResponseValue.HAB_SUCCESS))
        ]
    ))
    assert sdp.is_opened
    assert sdp.read(0x20000000, 4)
    assert sdp.status_code == StatusCode.HAB_IS_LOCKED
    assert sdp.response_value == ResponseValue.LOCKED


def test_sdp_jump_and_run_hab_locked():
    """Test `jump_and_run` returns False if HAB locked (even the operation works)"""
    sdp = SDP(VirtualDevice(
        respond_sequence=[
            CmdResponse(True, pack('>I', ResponseValue.LOCKED))
        ]
    ))
    assert sdp.is_opened
    assert sdp.jump_and_run(0x20000000)
    assert sdp.status_code == StatusCode.HAB_IS_LOCKED
    assert sdp.response_value == ResponseValue.LOCKED


def test_sdp_send_data_errors():
    error_response = [
        CmdResponse(True, pack('>I', ResponseValue.UNLOCKED)),
        CmdResponse(True, pack('>I', 0x12345678))
    ]
    
    sdp = SDP(VirtualDevice(respond_sequence=error_response.copy()))
    
    sdp._device.respond_sequence=error_response.copy()
    assert not sdp._send_data(CmdPacket(CommandTag.WRITE_DCD, 0, 0, 0), b'')
    assert sdp.status_code == StatusCode.WRITE_DCD_FAILURE

    sdp._device.respond_sequence=error_response.copy()
    assert not sdp._send_data(CmdPacket(CommandTag.WRITE_CSF, 0, 0, 0), b'')
    assert sdp.status_code == StatusCode.WRITE_CSF_FAILURE

    sdp._device.respond_sequence=error_response.copy()
    assert not sdp._send_data(CmdPacket(CommandTag.WRITE_FILE, 0, 0, 0), b'')
    assert sdp.status_code == StatusCode.WRITE_IMAGE_FAILURE

    sdp._device.respond_sequence=error_response.copy()
    assert not sdp._send_data(CmdPacket(CommandTag.WRITE_DCD, 0, 0, 0), b'')
    assert sdp.status_code == StatusCode.WRITE_DCD_FAILURE
