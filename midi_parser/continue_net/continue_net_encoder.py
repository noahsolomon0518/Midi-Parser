
from ..on_only.on_only_encoder import OTEncoderOnOnly
from ..on_only.on_only_encoder import OneTrackOnOnly
from ..decimal_encoder import Note
from ..decimal_encoder import MidiToDecimal
from functools import reduce
import numpy as np 


'''

OTEncoderContinueNet takes the timed notes and encodes them by time unit. The final array will be a 3-dimensional list
with each time unit being represented by the 1st axis. The second axis has 2 list: 
    1. The notes that will be played at that specific time unit
    2. Which notes are continued represented by 1s and which are not continued represented by 0s

Eventually this encoding will be passed to OneHotEncoderContinueNet which is another multi-output nueral network outputting
the notes that are played in a timeunit all encoded in one vector. It also outputs another vector predicting what notes
are continued and which are not. These predictions are made after the notes are predicted to simplify the process.

maxTimeUnit: This is the largest amount of time a note can be held for. For 1/32 smallest time unit 20-40 is a decent range
'''

class OTEncoderContinueNet(OTEncoderOnOnly):
    def __init__(self, oneTrack, maxTimeUnit = 20, **args):
        self.maxTimeUnit = maxTimeUnit
        super().__init__(oneTrack,**args)


    def _encodeOneMido(self, oneTrack):
        totalTimeUnits = self._calculateTotalTimeUnits(oneTrack)
        encodedOT = [[[],[]] for  timeUnit in range(totalTimeUnits)]
        curTimeUnit = 0
        for note in oneTrack.notesTimed:
            _time = np.min([self.maxTimeUnit, note.time])
            if(note.note == 88):
                curTimeUnit+=_time
            else:
                '''
                0=continue and 1=start note
                Append note to next <_time> note lists and 1 to current continue lists
                0 appended to next <_time> - 1 continue list
                '''
                encodedOT[curTimeUnit][0].append(note.note)
                encodedOT[curTimeUnit][1].append(1)
                for timeUnit in range(_time-1):
                    nextTimeUnits = curTimeUnit+timeUnit+1      #+1 to account for curTimeUnit already accounted for
                    encodedOT[nextTimeUnits][0].append(note.note)
                    encodedOT[nextTimeUnits][1].append(0)
        return encodedOT

            

    
    #Calculates the total number of time units of OneTrackOnOnly
    def _calculateTotalTimeUnits(self, oneTrack):
        return reduce(self.totalTimeUnitsCB, oneTrack.notesTimed)
       
    def totalTimeUnitsCB(self, total, note):
        if(type(total)!=int):
            total = min([total.time, self.maxTimeUnit])
        if(note.note == 88):
            return total + min([note.time, self.maxTimeUnit])  
        return total


    






class MidiToDecimalContinueNet(MidiToDecimal):
    def __init__(self, folder, maxOctaves = 4, debug=False, r=True, convertToC = True,  scales = "both", smallestTimeUnit = 1/32):
        self.smallestTimeUnit = smallestTimeUnit
        super().__init__(folder, maxOctaves = maxOctaves, debug=debug, r=r, convertToC = convertToC,  scales = scales)
    

    def _initOneTrack(self, mido):
        return OneTrackOnOnly(mido, self.convertToC, self.scales, self.maxOctaves, self.smallestTimeUnit)

    def _initOTEncoder(self, oneTracks):
        return OTEncoderContinueNet(oneTracks)
    