import numpy as np
import warnings



class OneHotInfo:
    
    #Provides every decimal encoded value and its number of occurences in sequences
    @staticmethod
    def occurences(sequences):
        nOccur = {}
        for sequence in sequences:
            for val in sequence:
                if(not val in nOccur.keys()):
                    nOccur[val] = 0
                nOccur[val] = nOccur[val]+1
        return sorted(nOccur.items())

    #Provides number of samples when factoring in gap and lookback
    @staticmethod
    def nSamples(sequences, lookback, gap):
        nSamples = 0
        if(type(sequences[0])==int):
            sequences = [sequences]
        
        for sequence in sequences:
            nSamples+=np.max(((len(sequence)-lookback)//gap), 0)
        if(nSamples<1):
            warnings.warn("Lookback is too high for given sequence. No samples can be generated from it.")
        return nSamples


class OneHotEncoder:
    def __init__(self, lookback=30, nClasses=200):
        self.lookback = lookback
        self.nClasses = nClasses
    

    #After getting n xSequences and n ySequences use to onehotencode
    def oneHotEncode(self, xSequences, ySequences):
        nSamples = len(xSequences)
        assert len(xSequences)==len(ySequences)
        lookback = self.lookback
        nClasses = self.nClasses

        x = np.zeros((nSamples, lookback, nClasses))
        y = np.zeros((nSamples, nClasses))

        for n, xSequence in enumerate(xSequences):
            for i, note in enumerate(xSequence):
                xNote = np.min([note,nClasses-1])
                x[n][i][xNote] = 1
            yNote = np.min([ySequences[n], nClasses-1])
            y[n][yNote] = 1
        return (x, y)

    
    def encode(self):
        pass


# One hot encoder for recurrent neural networks
# Class takes up ALOT of ram when encoding over 20 midi tracks. USE WITH CAUTION!

class OneHotEncodeAll(OneHotEncoder):
    def __init__(self, lookback=30, nClasses=200, gap = 5):
        super().__init__(lookback, nClasses)
        self.gap = gap
    
    def encode(self, sequences):
        xSamples, ySamples = self._gatherSamples(sequences)
        return self.oneHotEncode(xSamples, ySamples)


    def _gatherSamples(self, sequences):
        
        for sequence in sequences:
            xSamples = []
            ySamples = []
            nSamples = OneHotInfo.nSamples(sequence, self.lookback, self.gap)
            for i in range(nSamples):
                xSamples.append(sequence[i*self.gap:(i)*self.gap + self.lookback])
                ySamples.append(sequence[(i)*self.gap + self.lookback])
            
        return (xSamples,ySamples)




#startThresh ---> There must be atleast startthresh starting points in a piece to sample from it. Only super necessary for small midis
class OneHotEncodeGen(OneHotEncoder):
    def __init__(self, lookback=30, nClasses=200, startThresh = 20):
        super().__init__(lookback=lookback, nClasses=nClasses)
        self.startThresh = startThresh
        
    #   1. randInds ----> grabs n random starting notes in encoded
    def encode(self, sequences, n):
        xSequences, ySequences = self._randInds(sequences, n)
        x, y = self.oneHotEncode(xSequences, ySequences)
        return (x, y)

    # Picks n random indices for starting points
    def _randInds(self, sequences, n):
        recNSamples = OneHotInfo.nSamples(sequences, self.lookback, 3)
        if(n > recNSamples):
            warnings.warn("n set very high. Risk of overfitting \nRecommended n: " + str(recNSamples))
        xSequences = []
        ySequences = []
        for i in range(n):
            pieceInd = np.random.randint(len(sequences))
            piece = sequences[pieceInd]
            startRange = (len(piece) - (self.lookback+1))
            if(startRange>self.startThresh):
                start = np.random.randint(startRange)
                end = start+self.lookback
                xSequences.append(piece[start:end])
                ySequences.append(piece[end])
        return (xSequences, ySequences)
