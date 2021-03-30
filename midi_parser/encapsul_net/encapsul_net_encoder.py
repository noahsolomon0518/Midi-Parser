
from ..on_only.on_only_encoder import OTEncoderOnOnly
from ..on_only.on_only_encoder import OneTrackOnOnly
from ..decimal_encoder import MidiToDecimal


"""
--Purpose--
For each midi returns two list. One for the notes/waiting time and one for the durations of each note. 

--Parameters--
oneTracks: List of oneTrack objects
normalizationFactor: Smallest unit of time is quarter note / <normalizationFactor>. Larger it is the smaller and more accurate
                     units of times are. But more dimensions
"""

class OTEncoderMultiNet(OTEncoderOnOnly):
    def __init__(self, oneTracks):
        super().__init__(oneTracks)

  
    def _encodeOneMido(self, OT):
        encodedNotes = []
        encodedTimes = []
        for note in OT.notesTimed:
    
            encodedNote, encodedTime = self._encodeOneNote(note)
            if(encodedNote!=None and encodedTime!=None):

                if(len(encodedNotes)>0 and encodedNotes[-1]==encodedNote):
                    encodedTimes[-1]+=encodedTime
                else:
                    encodedNotes.append(encodedNote)
                    encodedTimes.append(encodedTime)
            
        if(len(encodedNotes) != 0):
            return [encodedNotes, encodedTimes]




class MidiToDecimalMultiNet(MidiToDecimal):
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(folder, maxOctaves = maxOctaves, debug=debug, r=r, convertToC = convertToC,  scales = scales)
    

    def _initOneTrack(self, mido):
        return OneTrackOnOnly(mido, self.convertToC, self.scales, self.maxOctaves, self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderMultiNet(oneTracks)
    