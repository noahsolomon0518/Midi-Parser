from midi_parser.one_hot import OneHotEncodeAll, OneHotEncodeGen,  OneHotInfo 
from midi_parser.encoders import MidiToDecimal
import unittest

p = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/AMERICANA_FOLK_www.pdmusic.org_MIDIRip/1800s")
data = p.encode()
print(data)

oneHotEnc = OneHotEncodeAll()
encodeGen = OneHotEncodeGen()

class TestOTEncoder(unittest.TestCase):
    

    def test_one_hot_info(self):
        occurences = OneHotInfo.occurences(data)
        nSamples =OneHotInfo.nSamples(data, 20, 3)
        assert nSamples > 0
        assert occurences != []
        print("data folder can generate: " + str(nSamples) + " samples")
        print("occurences of each decimal encoded number are the following: ")
        print(occurences)




