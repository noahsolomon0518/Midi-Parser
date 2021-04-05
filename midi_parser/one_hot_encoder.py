import numpy as np
import warnings
import keras



class OneHotInfo:

    @staticmethod
    def oneHotToDeci(sequence):
        encoded = []
        for note in sequence:
            encoded.append(np.argmax(note))
        return encoded

    
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
    def __init__(self, lookback, nClasses):
        self.lookback = lookback
        
    #These functions assume that all numbers will be one hot encoded to their raw value. 46 --> 46th index
    #                                                                                    2 -->2nd index ....
    def oneHotEncodeX(self, sequences, lookback, nClasses):
        nSamples = len(sequences)
        oneHot = np.zeros((nSamples, lookback, nClasses), dtype = 'int8')        #dtype = 'int8 will reduce memory by alot'
        oneHot = np.array([list(map(self._mapOneHot,sample, [nClasses for i in range(nSamples)])) for sample in sequences], dtype = 'int8')
        return oneHot

    def oneHotEncodeY(self, sequences, nClasses):
        nSamples = len(sequences)
        oneHot = np.zeros((nSamples, nClasses), dtype = 'int8') 
        oneHot = np.array(list(map(self._mapOneHot,sequences, [nClasses for i in range(nSamples)])) , dtype = 'int8')
        return oneHot



    def _mapOneHot(self, sample, nClasses):
        oneHot = np.zeros((nClasses), dtype = 'int8')
        oneHot[sample] = 1
        return oneHot
    
    def encode(self):
        raise NotImplementedError("Must implement encode function which return onehotencoded data")


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
    def __init__(self, lookback, nClasses, startThresh, evenInds):
        super().__init__(lookback=lookback, nClasses=nClasses)
        self.startThresh = startThresh
        self.evenInds = evenInds
        
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
            if(self.evenInds):
                startRange = [2*i for i in range((len(piece) - (self.lookback+1))//2)]
            else:
                startRange = range(len(piece) - (self.lookback+1))
            if(len(startRange)>self.startThresh):
                start = np.random.choice(startRange)
                
                end = start+self.lookback
                xSequences.append(piece[start:end])
                ySequences.append(piece[end])
        return (xSequences, ySequences)






