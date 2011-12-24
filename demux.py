#!/usr/bin/env python2
# coding: utf-8

import struct
import sys
from bitstring import BitStream

VERSION = [
    "MPEG 2.5",
    "reserved",
    "MPEG 2",
    "MPEG 1"
]

LAYER = [
    "reserved",
    "Layer III",
    "Layer II",
    "Layer I"
]

BITRATE = [
    [ 0,  32000,  64000,  96000, 128000, 160000, 192000, 224000,
        256000, 288000, 320000, 352000, 384000, 416000, 448000 ],
    [ 0,  32000,  48000,  56000,  64000,  80000,  96000, 112000,
      128000, 160000, 192000, 224000, 256000, 320000, 384000 ],
    [ 0,  32000,  40000,  48000,  56000,  64000,  80000,  96000,
      112000, 128000, 160000, 192000, 224000, 256000, 320000 ]
]

SAMPLERATE = [44100, 48000, 32000]



def is_sync_word(bs):
    first = bs.read(8).uint == 0xff 
    second = bs.read(3).uint == 0x7
    return first and second
    
def test_for_sync_word():
    valid_sync1 = BitStream("0xfffb")
    valid_sync2 = BitStream("0xffff")
    invalid_sync1 = BitStream("0xff00")
    invalid_sync2 = BitStream("0x1107")
    assert is_sync_word(valid_sync1)
    assert is_sync_word(valid_sync2)
    assert not is_sync_word(invalid_sync1)
    assert not is_sync_word(invalid_sync2)

def parse_header(stream):
    header = {}

    header["version"] = stream.read(2).uint
    header["layer"] = stream.read(2).uint

    header["protection"] = stream.read(1).uint

    index = stream.read(4).uint
    if index == 15:
        print "bad bitrate"
        return -1
    header["bitrate"] = BITRATE[header["layer"] - 1][index]
    index = stream.read(2).uint
    if index == 3:
        print "bad sample rate"
        return -1
    header["samplerate"] = SAMPLERATE[index]
    header["padding"] = stream.read(1).uint
    header["private"] = stream.read(1).uint
    header["mode"] = stream.read(2).uint
    header["mode_extension"] = stream.read(2).uint
    header["copyright"] = stream.read(1).uint
    header["original"] = stream.read(1).uint
    header["emphasis"] = stream.read(2).uint

    print "Position: %s" % stream.pos
    return header

def create_sample_sync_frame():

    stream = BitStream(bin="0" * 32)
    stream.set(True, range(0,12)) # frame sync 
    stream.set(True, 14) # Layer III
    stream.set(True, 15) # protection bit
    stream.set(True, 17) # bitrate, 128k
          

    return stream

def main():

    test_for_sync_word()    
    stream = create_sample_sync_frame()
    if is_sync_word(stream):
        header = parse_header(stream)
        for key in header:
            print "%s: %s" % (key, header[key])


main()
