import numpy as np
import warnings
import keras


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




class DataGen(keras.utils.Sequence):

    # samplersPerEpoch is multiplied against nNotes. Smaller fractions will result in less samplers per epoch
    def __init__(self, xEncoded, batchSize=32, sequenceSize=20, nClasses=300, samplesPerEpoch=1/3):

        self.xEncoded = xEncoded
        self.batchSize = batchSize
        self.nClasses = nClasses
        self.sequenceSize = sequenceSize
        self.samplesPerEpoch = samplesPerEpoch
        self.length = int(
            np.sum([len(piece)-(self.sequenceSize+1) for piece in self.xEncoded]))

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        # If batchsize<nPieces => choose batchsize pieces and sample from them
        # If batchsize>nPieces => sample from each piece batchsize//nPieces times then choose remainder peices to sample from
        batchEncoded = []
        nPieces = len(self.xEncoded)
        for i in range(self.batchSize//nPieces):
            for piece in self.xEncoded:
                batchEncoded.append(self._randSequence(piece))

        r = self.batchSize % nPieces
        pieceInds = np.random.choice(range(nPieces), replace=False, size=r)
        for ind in pieceInds:
            batchEncoded.append(self._randSequence(self.xEncoded[ind]))

        batchEncoded = np.array(batchEncoded)
        X, y = self.__data_generation(batchEncoded)

        return X, y

    def _randSequence(self, piece):
        start = np.random.randint(len(piece)-(self.sequenceSize+1))

        return piece[start:start+self.sequenceSize]

    def __data_generation(self, xEncoded):
        # one hot encode sequences
        x = np.zeros((self.batchSize, self.sequenceSize, self.nClasses))
        y = np.zeros((self.batchSize, self.nClasses))
        for i, sequence in enumerate(xEncoded):
            for n, val in enumerate(sequence[:-1]):
                if(val > (self.nClasses-1)):
                    x[i][n][self.nClasses-1] = 1
                else:
                    x[i][n][val] = 1

            yVal = sequence[-1]
            if(yVal > (self.nClasses-1)):
                y[i][self.nClasses-1] = 1
            else:
                y[i][yVal] = 1

        return (x, y)
