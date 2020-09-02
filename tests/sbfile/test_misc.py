#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020 NXP
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from spsdk.sbfile.misc import BcdVersion3, SecBootBlckSize


def test_size_sbfile1x():
    """Test `SizeSB1` class"""
    assert SecBootBlckSize.BLOCK_SIZE == 16
    assert SecBootBlckSize.to_num_blocks(0) == 0
    assert SecBootBlckSize.to_num_blocks(16) == 1
    assert SecBootBlckSize.to_num_blocks(16 * 15) == 15
    assert SecBootBlckSize.to_num_blocks(16 * 65537) == 65537
    with pytest.raises(ValueError):
        SecBootBlckSize.to_num_blocks(1)
    assert len(SecBootBlckSize.align_block_fill_random(b'1')) == 16


def test_bcd_version3():
    """Test `BcdVersion3` class"""
    # default value
    version = BcdVersion3()
    assert str(version) == '1.0.0'
    assert version.nums == [1, 0, 0]
    # explicit value
    version = BcdVersion3(0x987, 0x654, 0x321)
    assert str(version) == '987.654.321'
    assert version.nums == [0x987, 0x654, 0x321]
    # invalid value
    with pytest.raises(ValueError):
        BcdVersion3(0x19999)
    with pytest.raises(ValueError):
        BcdVersion3(0xF)
    with pytest.raises(ValueError):
        BcdVersion3.to_version(0xF)
    with pytest.raises(ValueError):
        BcdVersion3(0xF1, 0, 0)
    # conversion from string
    fs_version = BcdVersion3.from_str('987.654.321')
    assert fs_version == version
    # conversion from string
    fs_version = BcdVersion3.to_version('987.654.321')
    assert fs_version == version
    # conversion from BcdVersion3
    fs_version = BcdVersion3.to_version(fs_version)
    assert fs_version == version
