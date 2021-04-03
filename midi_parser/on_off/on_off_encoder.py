from ..decimal_encoder import MidiToDecimal, OneTrack, OTEncoder
import math


class OneTrackVanilla(OneTrack):
    def __init__(self, mido, nOctaves, smallestTimeUnit, convertToC = True, scales = "both"):
        super().__init__(
            mido, 
            convertToC = True, 
            scales = "both", 
            nOctaves = nOctaves, 
            smallestTimeUnit = smallestTimeUnit)
    
    #Converts ticks to number of <smallestTimeUnit>nd notes. 





class OTEncoderOnOff(OTEncoder):
    def __init__(self, oneTracks, nClassesTimes):
        self.nOctaves = oneTracks[0].nOctaves
        self.minNote = oneTracks[0].minNote
        self.maxNote = oneTracks[0].maxNote
        self.totalNotes = self.maxNote - self.minNote
        super().__init__(oneTracks)      #Min note extracted from onetrack


    def _encodeOneMido(self, oneTrack):

        encodedOT = []

        for note in oneTrack.notesRel:
            encodedOT.extend(self._encodeOneNote(note))
        if(len(encodedOT) != 0):
            return encodedOT

    def _encodeOneNote(self, note):
        waitTime = []
        waitTime = [2*(self.totalNotes)-1+note.time] if note.time > 0 else []
        if(note.type == "note_on"):
        
            if(note.velocity == 0):
                waitTime.append(note.note-self.minNote)
                return waitTime
            else:
                waitTime.append(note.note-self.minNote+self.totalNotes)
                return waitTime
        else:
            waitTime.append(note.note-self.minNote)
            return waitTime





class MidiToDecimalOnOff(MidiToDecimal):
    def __init__(self, folder, smallestTimeUnit, nClassesTimes,  nOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both"):
        
        self.nClassesTimes = nClassesTimes
        super().__init__(
            folder, 
            smallestTimeUnit = smallestTimeUnit,
            nOctaves = nOctaves, 
            debug=debug, 
            r=r, 
            convertToC = convertToC,  
            scales = scales)
    

    #Uses vanilla OneTrack to encode
    def _initOneTrack(self, mido):
        return OneTrackVanilla(
            mido, 
            convertToC = self.convertToC, 
            scales = self.scales, 
            nOctaves = self.nOctaves, 
            smallestTimeUnit = self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderOnOff(oneTracks, self.nClassesTimes)


    