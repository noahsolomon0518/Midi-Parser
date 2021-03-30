from midi_parser.encapsul_net import MidiToDecimalEncapsulNet, OneHotEncoderEncapsulNet




import unittest



encoderEncapsulNet = MidiToDecimalEncapsulNet("C:/Users/noahs/Data Science/Music Generation AI/data/testing",  debug = True, maxOctaves=4, smallestTimeUnit=  1/32)
encoderEncapsulNet.encode()
encodedOTs = encoderEncapsulNet.encoded



class TestOneHotEncoderOnOff(unittest.TestCase):
    

    def test_encoding(self):
        print(encodedOTs)
        ohe = OneHotEncoderEncapsulNet()
        (x,yNotes, yTimes, yOctaves) = ohe.encode(encodedOTs, 500)
        print(x)
        print(yNotes)
        print(yTimes)
        print(yOctaves)




    
        
    




