from midi_parser.continue_net import OneHotEncoderContinueNet, MidiToDecimalContinueNet




import unittest



encoderContinueNet = MidiToDecimalContinueNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderContinueNet.encode()
encodedOTs = encoderContinueNet.encoded



class TestOneHotEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        ohe = OneHotEncoderContinueNet()
        (x,yNotes, yContinues) = ohe.encode(encodedOTs, 500)
        print(x.shape)
        print(yNotes.shape)
        print(yContinues.shape)




    
        
    




