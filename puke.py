#!/usr/bin/env python2
# coding: utf-8

import struct


FNAME = "test.flv"
ANAME = "input.mp3"

HEADER = {
    "hasAudio" : 4,
    "hasVideo" : 1
}

AMF = {
    "Number" : 0,
    "Bool" : 1,
    "String" : 2,
    "MixedArray" : 8,
    "EndOfObject" : 9
}

Tag = {
    "Audio" : 0x08,
    "Video" : 0x09,
    "Meta" : 0x12
}

class BinaryBuffer(bytearray):
    
    
    """
    Simple buffer settling upon bytearray.
    struct is neccessary because bytearray only takes strings.
    """

    def __init__(self):
        bytearray.__init__(self)
        self.offset = -1


    def append(self, v, fmt=">B"):
        hexstring = struct.pack(fmt, v)
        if len(self) == 0:
            self.extend(hexstring)
        else:
            # insert, Y U NO take multiple items???
            for x in hexstring:
                self.insert(self.offset, x)
                self.offset += 1
        self.offset += len(hexstring)

    def w8(self, v):
        self.append(v, ">B")

    def wb16(self, v):
        self.append(v, ">H")

    def wb24(self, v):
        """
        struct doesn't support ints of byte length 3.
        This is why we need to cut the first byte off.
        (Big endian, remember?)
        example:
        0xbf ->
        \x00\x00\x00\xbf
        => \x00\x00\xbf # first byte cut off
        """
        tmp = struct.pack(">i", v)
        self.extend(tmp[1:4])

    def wb32(self, v):
        self.append(v, ">i")

    def wS(self, v):
        self.append(v, "%ss" % len(v))

    def tell(self):
        return self.offset

    def seek(self, off):
        self.offset = off

    def skip(self, by):
        self.offset += by

    def amfString(self, v):
        self.append(len(v), ">H")
        self.append(v, "%ss" % len(v))

    def amfDouble(self, v):
        self.append(AMF["Number"])
        self.append(v, ">d")

    def amfBool(self, v):
        self.append(AMF["Bool"])
        self.append(int(bool(v))) # yay, type conversion \0/

class Encoder(object):

    def __init__(self, audio_name):
        self.audio_name = audio_name
        self.avio = BinaryBuffer() 

        self.bit_rate = 320000
        self.sample_rate = 44100
        self.channels = 2

    def write_header(self):
        avio = self.avio # lazy boy is lazy
        avio.wS("FLV") # magic 'number' 
        avio.w8(1) # flv version
        avio.w8(HEADER["hasAudio"]) # we only got audio

        avio.wb32(9) # header size
        avio.wb32(0) # ?

        # Meta tag time
        avio.w8(18) # metadata tag type
        metadataSizePos = avio.tell()
        avio.wb24(0) # size of data part, yet unkown, will have to change later
        avio.wb24(0) # time stamp
        avio.wb32(0) # reserved

        avio.w8(AMF["String"]) # Why the heck not always? ffmpeg source makes no sense!
        avio.amfString("onMetaData")

        avio.w8(AMF["MixedArray"])
        metadataCountPos = avio.tell()
        metadataCount = 5 + 2 # 5 fields for audio, 2 more for duration+filesize
        avio.wb32(metadataCount)

        avio.amfString("duration")
        avio.amfDouble(0.0) # dummy, will be filled later

        # Audio specific tags
        avio.amfString("audiodatarate")
        avio.amfDouble(self.bit_rate / 1024.0)

        avio.amfString("audiosamplerate")
        avio.amfDouble(self.sample_rate)

        avio.amfString("audiosamplesize")
        avio.amfDouble(16.0)
        
        avio.amfString("stereo")
        avio.amfBool(self.channels == 2)

        avio.amfString("audiocodecid")
        avio.amfDouble(2.0)
        
        # </Audio specific tags>

        avio.amfString("filesize")
        avio.amfDouble(0.0) # dummy, to be filled

        avio.amfString("")
        avio.w8(AMF["EndOfObject"])

        datasize = avio.tell()
        print "datasize=%s" % datasize
        print "metadatacount=%s" % metadataCount
        print "metadataCountPos=%s" % metadataCountPos
        print "metadataSizePos=%s" % metadataSizePos

        avio.seek(metadataCountPos)
        avio.wb32(metadataCount)

        avio.seek(metadataSizePos)
        avio.wb24(datasize)
        avio.skip(datasize + 10 - 3) # magic ffmpeg numbers

        avio.wb32(datasize + 11) # even moar magic!

        
    def writePacket(self, packet):
        avio = self.avio # we're laaazy 

        size = packet.size

        flagSize = 1
        flags = 0
        avio.w8(Tag["Audio"])

        ts = packet.dts
        avio.wb24(size + flagsSize)
        avio.wb24(ts)
        avio.w8((ts >> 24) & 0x7F) # stamps are 32bits signed
        avio.wb24(0) # actually flv reserved

        avio.w8(flags)
        avio.wS(packet.data)

        avio.wb32(size + flagsSize + 11)
        
        
    def save(self, output_file):
        with open(output_file, "wb") as f:
            f.write(self.avio)

def main():
    enc = Encoder(ANAME)
    enc.write_header()
    enc.save(FNAME)

if __name__ == '__main__':
    main()
         
