from ..one_hot_encoder import OneHotEncoder
from ..decimal_encoder import OneTrack
import numpy as np


'''

This OneHotEncoder takes the set of pieces which each have a note list and time list. Notes can be encoded to a vector
of length up to 88, then the times are encoded on the same vector adding a length of choice to it. This one hot encoder
is used with a LSTM that uses previous notes/times to predict a note, then based on that predict a time. 

TODO: Combine functionality with OneHotEncodeEncapsulNet

'''

class OneHotEncoderMultiNet(OneHotEncoder):
    def __init__(self, lookback=30, startThresh = 20, octaves = 4, nClassesTimes = 100):
        self.minNote, self.maxNote = OneTrack.calcMinMaxNote(octaves)
        nClassesNotes = self.maxNote - self.minNote
        self.startThresh = startThresh
        self.nClassesNotes = nClassesNotes + 1              #   +1 for waiting time signal
        self.nClassesTimes = nClassesTimes
        super().__init__(lookback=lookback, nClasses = nClassesTimes + nClassesNotes + 1)

    



    def encode(self, sequences, n):
        self.weightedPieces = self._getPiecesWeights(sequences)
        xNotes,yNotes, xTimes,yTimes = self._randInds(sequences, n)
        return self.oneHotEncode(xNotes,yNotes, xTimes,yTimes)

    def _randInds(self, sequences, n):
        xNotes = []
        yNotes = []
        xTimes = []
        yTimes = []
        for i in range(n):
            pieceInd = np.random.choice(range(len(sequences)), p = self.weightedPieces)
            pieceNotes = sequences[pieceInd][0]
            pieceTimes = sequences[pieceInd][1]
            assert len(pieceNotes)==len(pieceTimes)
            startRange = range(len(pieceNotes) - (self.lookback+1))
            if(len(startRange)>self.startThresh):
                start = np.random.choice(startRange)
                end = start+self.lookback
                xNotes.append(pieceNotes[start:end])
                yNotes.append(pieceNotes[end])
                xTimes.append(pieceTimes[start:end])
                yTimes.append(pieceTimes[end])
        return xNotes,yNotes, xTimes,yTimes

    def _getPiecesWeights(self, sequences):
        tot = sum([len(piece[0]) for piece in sequences])
        return list(map(lambda x: len(x[0])/tot, sequences))

    def oneHotEncode(self, xNotes,yNotes, xTimes,yTimes):
        nSamples = len(xNotes)
        lookback = len(xNotes[0])
        nClasses = self.nClasses
        x = np.zeros((nSamples, lookback, nClasses))
        yNotesOH = np.zeros((nSamples, self.nClassesNotes))
        yTimesOH = np.zeros((nSamples, self.nClassesTimes))
        for i in range(nSamples):
            for j, note in enumerate(xNotes[i]):
                ind = self.maxNote - self.minNote if note==88 else note - self.minNote 
                x[i][j][ind] = 1
            ind = self.maxNote - self.minNote if yNotes[i]==88 else yNotes[i] - self.minNote 
            yNotesOH[i][ind] = 1
            for j, time in enumerate(xTimes[i]):
                ind = np.min([time+self.nClassesNotes, self.nClasses-1])
                x[i][j][ind] = 1
            ind = np.min([yTimes[i], self.nClassesTimes-1])
            yTimesOH[i][ind] = 1
        return x,yNotesOH,yTimesOH
