from ..one_hot_encoder import OneHotEncoder
from ..decimal_encoder import OneTrack
import numpy as np


'''

This OneHotEncoder takes the set of pieces which each have a note list and time list. Notes can be encoded to a vector
of length up to 88, then the times are encoded on the same vector adding a length of choice to it. This one hot encoder
is used with a LSTM that uses previous notes/times to predict a note, then based on that predict a time. 

TODO: Combine functionality with OneHotEncodeEncapsulNet

'''

class OneHotEncoderContinueNet(OneHotEncoder):
    def __init__(self, lookback=30, startThresh = 20, octaves = 4, nClassesTimes = 100):
        self.minNote, self.maxNote = OneTrack.calcMinMaxNote(octaves)
        nClassesNotes = 12
        self.nClassesOctaves = int(5+octaves/2)
        self.startThresh = startThresh
        self.nClassesNotes = nClassesNotes + 1              #   +1 for waiting time signal
        self.nClassesTimes = nClassesTimes
        super().__init__(lookback=lookback, nClasses=nClassesTimes + nClassesNotes + self.nClassesOctaves)

    



    def encode(self, sequences, n):
        xNotes,yNotes, xTimes,yTimes, xOctaves, yOctaves = self._randInds(sequences, n)
        return self.oneHotEncode(xNotes,yNotes, xTimes,yTimes, xOctaves, yOctaves)

    def _randInds(self, sequences, n):
        xNotes = []
        yNotes = []
        xTimes = []
        yTimes = []
        xOctaves = []
        yOctaves = []
        for i in range(n):
            pieceInd = np.random.randint(len(sequences[0]))
            pieceNotes = sequences[pieceInd][0]
            pieceTimes = sequences[pieceInd][1]
            pieceOctaves = sequences[pieceInd][2]
            startRange = range(len(pieceNotes) - (self.lookback+1))
            if(len(startRange)>self.startThresh):
                start = np.random.choice(startRange)
                end = start+self.lookback
                xNotes.append(pieceNotes[start:end])
                yNotes.append(pieceNotes[end])
                xTimes.append(pieceTimes[start:end])
                yTimes.append(pieceTimes[end])
                xOctaves.append(pieceOctaves[start:end])
                yOctaves.append(pieceOctaves[end])
        return xNotes,yNotes, xTimes,yTimes, xOctaves, yOctaves
    

    def oneHotEncode(self, xNotes,yNotes, xTimes,yTimes, xOctaves, yOctaves):
        nSamples = len(xNotes)
        lookback = len(xNotes[0])
        nClasses = self.nClasses
        x = np.zeros((nSamples, lookback, nClasses))
        yNotesOH = np.zeros((nSamples, self.nClassesNotes))
        yTimesOH = np.zeros((nSamples, self.nClassesTimes))
        yOctavesOH = np.zeros((nSamples, self.nClassesOctaves))

        for i in range(nSamples):
            for j, note in enumerate(xNotes[i]):
                ind = 12 if note==88 else note
                x[i][j][ind] = 1
            ind = 12 if yNotes[i]==88 else yNotes[i]
            yNotesOH[i][ind] = 1
            for j, time in enumerate(xTimes[i]):
                ind = np.min([time+self.nClassesNotes, self.nClasses-1])
                x[i][j][ind] = 1
            ind = np.min([yTimes[i], self.nClassesTimes-1])
            yTimesOH[i][ind] = 1
            for j, octave in enumerate(xOctaves[i]):
                ind = np.min([octave+self.nClassesNotes+self.nClassesTimes, self.nClasses-1])
                x[i][j][ind] = 1
            ind = np.min([yOctaves[i], self.nClassesOctaves-1])
            yOctavesOH[i][ind] = 1
        return x,yNotesOH,yTimesOH, yOctavesOH
