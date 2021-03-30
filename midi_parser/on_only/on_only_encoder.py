from ..decimal_encoder import MidiToDecimal, OTEncoder, Note
from ..on_off.on_off_encoder import OneTrackVanilla
import math

#Inherits the timing
class OneTrackOnOnly(OneTrackVanilla):
    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4, smallestTimeUnit = 1/32):
        super().__init__(mido, convertToC = True, scales = "both", maxOctaves = maxOctaves, smallestTimeUnit = smallestTimeUnit)
        self.notesTimed = []
        self._calculateNoteOns()

    def _calculateNoteOns(self):
        for i, note in enumerate(self.notesRel):
            if(note.time>0):
                self.notesTimed.append(Note(88, note.time, "time_unit", 0, 0 ))
            if(note.type == "note_on"):
                noteNum = note.note
                dt = 0
                for nextNote in self.notesRel[i:]:
                    if(nextNote.type == "note_off" and nextNote.note == noteNum):
                        dt+=nextNote.time 
                        break
                    dt+=nextNote.time 
                self.notesTimed.append(Note(note.note, dt, "note_on", note.velocity, note.instrument))

class OTEncoderOnOnly(OTEncoder):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)


    def _encodeOneMido(self, OT):
        encodedOT = []
        for note in OT.notesTimed:
            encodedNote = self._encodeOneNote(note)
            if(None not in encodedNote):
                encodedOT.extend(encodedNote)
        if(len(encodedOT) != 0):
            return encodedOT
        
        
    def _encodeOneNote(self, note):
        if(note.time == 0):
            return [note.note, None]
        elif(note.type == "note_on"):
            return [note.note, note.time]
        else:
            return [88, note.time]





class MidiToDecimalOnOnly(MidiToDecimal):
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(folder, maxOctaves = maxOctaves, debug=debug, r=r, convertToC = convertToC,  scales = scales)
    

    def _initOneTrack(self, mido):
        return OneTrackOnOnly(mido, self.convertToC, self.scales, self.maxOctaves, self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderOnOnly(oneTracks)
    