from ..decimal_encoder import MidiToDecimal, OneTrack, OTEncoder
import math


class OneTrackVanilla(OneTrack):
    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4, smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(mido, convertToC = True, scales = "both", maxOctaves = maxOctaves)
    
    #Converts ticks to number of <smallestTimeUnit>nd notes. 
    def _timeConversion(self, _time):
        return int(math.ceil(_time*(1/self.tpb)/4/self.smallestTimeUnit))

class OTEncoderOnOff(OTEncoder):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)


    def _encodeOneMido(self, oneTrack):

        encodedOT = []

        for note in oneTrack.notesRel:
            encodedOT.extend(self._encodeOneNote(note))
        if(len(encodedOT) != 0):
            return encodedOT

    def _encodeOneNote(self, note):
        waitTime = []
        waitTime = [175+note.time] if note.time > 0 else []
        if(note.type == "note_on"):
        
            if(note.velocity == 0):
                waitTime.append(note.note)
                return waitTime
            else:
                waitTime.append(note.note+88)
                return waitTime
        else:
            waitTime.append(note.note)
            return waitTime





class MidiToDecimalOnOff(MidiToDecimal):
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(folder, maxOctaves = maxOctaves, debug=debug, r=r, convertToC = convertToC,  scales = scales)
    

    #Uses vanilla OneTrack to encode
    def _initOneTrack(self, mido):
        return OneTrackVanilla(mido, self.convertToC, self.scales, self.maxOctaves, self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderOnOff(oneTracks)


    