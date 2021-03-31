from midi_parser.multi_net import OneHotEncoderMultiNet, MidiToDecimalMultiNet




import unittest



encoderMultiNet = MidiToDecimalMultiNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderMultiNet.encode()
encodedOTs = encoderMultiNet.encoded



class TestOneHotEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        ohe = OneHotEncoderMultiNet()
        (x,yNotes, yTimes) = ohe.encode(encodedOTs, 500)
        print(len(x))
        print(len(yNotes))
        print(len(yTimes))




    
        
    




