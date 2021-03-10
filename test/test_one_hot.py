from midi_parser.one_hot import OneHotEncodeAll, OneHotEncodeGen,  OneHotInfo, OneHotEncodeMultiNet
from midi_parser.encoders import MidiToDecimal
import unittest

p = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/AMERICANA_FOLK_www.pdmusic.org_MIDIRip/1800s/subset")
data = p.encode()
print(data)

oneHotEnc = OneHotEncodeAll()
encodeGen = OneHotEncodeGen(lookback=100, nClasses=100, evenInds=True)

class TestOTEncoder(unittest.TestCase):
    

    def test_one_hot_info(self):
        occurences = OneHotInfo.occurences(data)
        nSamples =OneHotInfo.nSamples(data, 20, 3)
        assert nSamples > 0
        assert occurences != []
        print("data folder can generate: " + str(nSamples) + " samples")
        print("occurences of each decimal encoded number are the following: ")
        print(occurences)

    def test_one_hot_gen(self):
        (x,y) = encodeGen.encode(data, 500)
        assert x.shape == (500,100,100)
        assert y.shape == (500,100)



    def test_one_hot_multi(self):
        p = MidiToDecimal("C:/Users/noahs/Data Science/Music Generation AI/data/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/AMERICANA_FOLK_www.pdmusic.org_MIDIRip/1800s/subset", method = "multi_network")
        data = p.encode()
        oneHot = OneHotEncodeMultiNet(lookback=100)
        x,yNotes, yTimes = oneHot.encode(data, 20)
        print("x shape", x.shape)
        print("yNotes shape", yNotes.shape)
        print("yTimes shape", yTimes.shape)

