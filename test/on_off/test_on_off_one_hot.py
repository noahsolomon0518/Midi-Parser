from midi_parser.on_off import OneHotEncoderOnOff, MidiToDecimalOnOff




import unittest



encoderOnOff = MidiToDecimalOnOff("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderOnOff.encode()
encodedOTs = encoderOnOff.encoded



class TestOTEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        ohe = OneHotEncoderOnOff()
        (x,y) = ohe.encode(encodedOTs, 500)
        print(len(x))
        print(len(y))

        
    



