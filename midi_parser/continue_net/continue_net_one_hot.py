from ..one_hot_encoder import OneHotEncoder
from ..decimal_encoder import OneTrack
import numpy as np


'''

Lookback should be bigger for this implementation

'''


class OneHotEncoderContinueNet(OneHotEncoder):
    def __init__(self, lookback=60, startThresh=20, octaves=4):
        self.nClassesNotes = octaves*12
        self.nClassesContinues = self.nClassesNotes
        self.minNote, self.maxNote = OneTrack.calcMinMaxNote(octaves)
        self.startThresh = startThresh
        super().__init__(lookback=lookback, nClasses=2*self.nClassesNotes)

    def encode(self, sequences, n):
        xNotes, yNotes, xTimes, yTimes = self._randInds(sequences, n)
        return self.oneHotEncode(xNotes, yNotes, xTimes, yTimes)

    def _randInds(self, sequences, n):
        xNotes = []
        yNotes = []
        xContinues = []
        yContinues = []
        for i in range(n):
            pieceInd = np.random.randint(len(sequences))
            piece = np.array(sequences[pieceInd])
            startRange = range(len(piece) - (self.lookback+1))
            if(len(startRange) > self.startThresh):
                start = np.random.choice(startRange)
                end = start+self.lookback
                xNotes.append(list(piece[start:end, 0]))
                yNotes.append(list(piece[end, 0]))
                xContinues.append(list(piece[start:end, 1]))
                yContinues.append(list(piece[end, 1]))
            
        return xNotes, yNotes, xContinues, yContinues

    def oneHotEncode(self, xNotes, yNotes, xContinues, yContinues):
        nSamples=len(xNotes)
        lookback=self.lookback
        nClasses=self.nClasses
        x=np.zeros((nSamples, lookback, nClasses))
        yNotesOH=np.zeros((nSamples, self.nClassesNotes))
        yContinuesOH=np.zeros((nSamples, self.nClassesContinues))


        for i in range(nSamples):
            for j, timeUnit in enumerate(xNotes[i]):
                for note in timeUnit:
                    ind = note-self.minNote
                    x[i][j][ind]=1

            for note in yNotes[i]:
                ind = note-self.minNote
                yNotesOH[i][ind]=1

            for j, timeUnit in enumerate(xContinues[i]):
                for note in timeUnit:
                    ind = self.nClassesNotes + note - self.minNote
                    x[i][j][ind]=1

            for note in yContinues[i]:
                ind = note - self.minNote
                yContinuesOH[i][ind]=1


        return x, yNotesOH, yContinuesOH
