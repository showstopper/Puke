#!/usr/bin/env python2
# coding: utf-8

from bitstring import BitStream

FRAME_SYNC = "0b" + "1" * 11 # 11 bits set

BITRATE = [
    # MPEG-1
    [ 0,  32000,  64000,  96000, 128000, 160000, 192000, 224000,  # Layer I   
      256000, 288000, 320000, 352000, 384000, 416000, 448000 ],
    [ 0,  32000,  48000,  56000,  64000,  80000,  96000, 112000,  # Layer II
      128000, 160000, 192000, 224000, 256000, 320000, 384000 ],
    [ 0,  32000,  40000,  48000,  56000,  64000,  80000,  96000,  # Layer III
      112000, 128000, 160000, 192000, 224000, 256000, 320000 ],
    # MPEG-2 LSF
    [ 0,  32000,  48000,  56000,  64000,  80000,  96000, 112000,  # Layer I
      128000, 144000, 160000, 176000, 192000, 224000, 256000 ],
    [ 0,   8000,  16000,  24000,  32000,  40000,  48000,  56000,  # Layers 
      64000,  80000,  96000, 112000, 128000, 144000, 160000 ]     # II & III  
]

VERSION = [
    2.5,
    -1, # reserved
    2,
    1
]

LAYER = [
    -1, # reserved
    3,
    2,
    1
]

SAMPLERATE = [ 44100, 48000, 32000 ]
def do_sync(stream):
    pos = stream.find(FRAME_SYNC, stream.pos) # adjusts position to occurence implicitly
    if pos:
        print "Found sync at offset=%s" % pos
        return True
    print "Did not succeed in finding a sync-frame."
    return False

def test_syncing():
    valid_sync = BitStream("0b0"+'1'*11)
    valid_sync2 = BitStream("0xff00fffb")
    invalid_sync = BitStream("0x0000")
    invalid_sync2 = BitStream("0xff00")
    # Remember: skip the 11 bits
    assert do_sync(valid_sync)
    assert do_sync(valid_sync2)
    assert not do_sync(invalid_sync)
    assert not do_sync(invalid_sync2)

def parse_header(stream):
    header = {}
    # we're already at the offset of a frame-sync, so let's skip it
    print stream.pos
    stream.pos += 11
    header["version"] = VERSION[stream.read(2).uint] # We only support v1+v2
    header["layer"] = LAYER[stream.read(2).uint]
    header["protection"] = stream.read(1).uint

    index = stream.read(4).uint # bitrate
    if index == 15:
        print "bad bitrate"
        return {}
    header["bitrate"] = BITRATE[header["layer"] -1][index]

    # sample rate
    index = stream.read(2).uint
    if index == 3:
        print "bad samplerate"
        return {}
    header["samplerate"] = SAMPLERATE[index]

    # padding-bit
    header["padding"] = stream.read(1).uint
    # private-bit
    header["private"] = stream.read(1).uint
    # mode
    header["mode"] = stream.read(2).uint
    # mode extension
    header["mode_extension"] = stream.read(2).uint
    # copyright
    header["copyright"] = stream.read(1).uint
    # original/copy
    header["original"] = stream.read(1).uint
    # emphasis
    header["emphasis"] = stream.read(2).uint

    if header["protection"]:
        print "protection"
        #stream.pos += 16 # skip, crc checksum is 16bit
    return header

   

def main():
    stream = BitStream(filename="stream_kotzt.mp3")
    if do_sync(stream):
        header = parse_header(stream)
        if header:
            for field in header:
                print field, header[field]
            padslot = header["padding"]
            length = 144 * header["bitrate"] / header["samplerate"] + padslot
            print length


main()
