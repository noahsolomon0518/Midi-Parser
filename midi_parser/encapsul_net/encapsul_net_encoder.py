
from ..on_only.on_only_encoder import OTEncoderOnOnly
from ..on_only.on_only_encoder import OneTrackOnOnly
from ..decimal_encoder import Note
from ..decimal_encoder import MidiToDecimal


class NoteEncapsulNet(Note):

    

    def __init__(self, note, time, type, velocity, instrument):
        super().__init__(note%12, time, type, velocity, instrument)
        self.octave = note//12



class OneTrackEncapsulNet(OneTrackOnOnly):

    def __init__(self, mido, convertToC = True, scales = "both", maxOctaves = 4, smallestTimeUnit = 1/32):
        super().__init__(mido, convertToC = True, scales = "both", maxOctaves = maxOctaves, smallestTimeUnit = smallestTimeUnit)
        self.notesTimed = map(OneTrackEncapsulNet.encapsulateData, self.notesTimed)


    @staticmethod
    def encapsulateData(note):
        return NoteEncapsulNet(note.note,note.time, note.type, note.velocity, note.instrument)


    


    


class OTEncoderEncapsulNet(OTEncoderOnOnly):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)

  
    def _encodeOneMido(self, OT):
        encodedNotes = []
        encodedTimes = []
        encodedOctaves = []
        encodedVelocities = []
        for note in OT.notesTimed:
    
            encodedNote, encodedTime, encodedOctave, encodedVelocity = self._encodeOneNote(note)
            if(encodedNote!=None and encodedTime!=None):

                if(len(encodedNotes)>0 and encodedTimes[-1]==encodedTime):          #Collaspes sequential time units
                    encodedTimes[-1]+=encodedTime
                else:
                    encodedNotes.append(encodedNote)
                    encodedTimes.append(encodedTime)
                    encodedOctaves.append(encodedOctave)
                    encodedVelocities.append(encodedVelocity)
            
        if(len(encodedNotes) != 0):
            return [encodedNotes, encodedTimes, encodedOctaves, encodedVelocities]


    def _encodeOneNote(self, note):
        if(note.time == 0):
            return [note.note, None, None, None]
        elif(note.type == "note_on"):
            return [note.note, note.time, note.octave, note.velocity]
        else:
            return [88, note.time, 0, 0]




class MidiToDecimalEncapsulNet(MidiToDecimal):
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(folder, maxOctaves = maxOctaves, debug=debug, r=r, convertToC = convertToC,  scales = scales)
    

    def _initOneTrack(self, mido):
        return OneTrackEncapsulNet(mido, self.convertToC, self.scales, self.maxOctaves, self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderEncapsulNet(oneTracks)
    