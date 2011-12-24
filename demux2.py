#!/usr/bin/env python2
# coding: utf-8

from bitstring import BitStream

def do_sync(stream):
    while True:
        pos = stream.find("0xff") # adjusts position to occurence implicitly
        if not pos:
            print "Did not succeed in finding a sync-frame."
            return False
        elif stream.read(11) == "0b%s" % '1' * 11: # 11 bits set
            print "Found sync-frame at %s." % pos
            return True

def test_syncing():
    valid_sync = BitStream("0x00fffb")
    invalid_sync = BitStream("0x0000")
    assert do_sync(valid_sync)
    assert not do_sync(invalid_sync)

def main():
    test_syncing()

main()
