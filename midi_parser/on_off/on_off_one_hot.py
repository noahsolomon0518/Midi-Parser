from ..one_hot_encoder import OneHotEncodeGen


#Only difference between OnOff and OnOnly one hot encoder is even ind
class OneHotEncoderOnOff(OneHotEncodeGen):
    def __init__(self, lookback=30, nClasses=200, startThresh = 20):
        super().__init__(lookback=lookback, nClasses=nClasses, startThresh=startThresh, evenInds=False)



class DataGenOnOff(keras.utils.Sequence):

    # samplersPerEpoch is multiplied against nNotes. Smaller fractions will result in less samplers per epoch
    def __init__(self, encoded, batchSize=32, lookback=20, nClasses=100, gap = 5):
        self.gap = gap
        self.encoded = encoded
        self.batchSize = batchSize
        self.nClasses = nClasses
        self.lookback = lookback
        self.indices = np.array([(pieceInd,noteInd) for pieceInd in range(len(self.encoded)) for noteInd in range(len(self.encoded[pieceInd]))  if noteInd%gap == 0 and (noteInd+1)< len(self.encoded[pieceInd])-self.lookback])
        self._shuffleInds()


    #Calculates how many batches to cycle through all data
    def __len__(self):
        distinctSamples = len(self.indices)
        return distinctSamples//self.batchSize

    def __getitem__(self, index):
        xIndices = self.indices[index*self.batchSize:(index+1)*self.batchSize]
        yIndices = np.array(list(map(lambda x: (x[0], x[1]+self.lookback),xIndices)))
        xEncoded = list(map(lambda x: self.encoded[x[0]][x[1]:x[1]+self.lookback], xIndices))
        yEncoded = list(map(lambda y: self.encoded[y[0]][y[1]], yIndices))
        X, y = self.__data_generation(xEncoded, yEncoded)

        return X, y



    def __data_generation(self, xEncoded, yEncoded):
        # one hot encode sequences
        x = self.oneHotEncodeX(xEncoded)
        y = self.oneHotEncodeY(yEncoded)

        

        return (x, y)

    def oneHotEncodeX(self, sequences):
        nSamples = len(sequences)
        oneHot = np.zeros((nSamples, self.lookback, self.nClasses), dtype = 'int8')        #dtype = 'int8 will reduce memory by alot'
        oneHot = np.array([list(map(self._mapOneHot,sample, [self.nClasses for i in range(nSamples)])) for sample in sequences], dtype = 'int8')
        return oneHot

    def oneHotEncodeY(self, sequences):
        nSamples = len(sequences)
        oneHot = np.zeros((nSamples, self.nClasses), dtype = 'int8') 
        oneHot = np.array(list(map(self._mapOneHot,sequences, [self.nClasses for i in range(nSamples)])) , dtype = 'int8')
        return oneHot



    def _mapOneHot(self, sample, nClasses):
        oneHot = np.zeros((nClasses), dtype = 'int8')
        oneHot[np.min([sample, nClasses-1])] = 1
        return oneHot


    def _shuffleInds(self):
        np.random.shuffle(self.indices)


    def on_epoch_end(self):
        self._shuffleInds()