from midi_parser.on_only import OneHotEncoderOnOnly, MidiToDecimalOnOnly




import unittest



encoderOnOnly = MidiToDecimalOnOnly("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderOnOnly.encode()
encodedOTs = encoderOnOnly.encoded



class TestOneHotEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        ohe = OneHotEncoderOnOnly()
        (x,y) = ohe.encode(encodedOTs, 500)
        self.assertEqual(len(x), 500)
        self.assertEqual(len(y), 500)
        print(len(x))
        print(len(y))




    
        
    




