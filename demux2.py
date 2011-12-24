#!/usr/bin/env python2
# coding: utf-8

from bitstring import BitStream

FRAME_SYNC = "0b" + "1" * 11 # 11 bits set
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

def main():
    test_syncing()

main()
