import numpy as np



class SequenceToOneHot:
    def __init__(self, sampleLength, gap, oneHotDimension):
        self.sampleLength = sampleLength
        self.gap = gap
        self.oneHotDimension = oneHotDimension
        self.xEncoded = []
        self.yEncoded = []
        
    def fit(self, sequences):
        for sequence in sequences:
            self.oneHotEncodeSequence(sequence)
        self.xEncoded = np.array(self.xEncoded)
        self.yEncoded = np.array(self.yEncoded)   
    
    
    def oneHotEncodeSequence(self,sequence):
        nSamples = self.getNSamples(sequence)
        for i in range(nSamples):
            xSample = sequence[i*self.gap:(i)*self.gap + self.sampleLength]
            ySample = sequence[(i)*self.gap + self.sampleLength]
            self.oneHotEncodeSample(xSample, ySample)
            
    
    
    def oneHotEncodeSample(self,x,y):
        xOneHot = np.zeros((self.sampleLength,self.oneHotDimension))
        yOneHot = np.zeros((self.oneHotDimension))
        yOneHot[y] = 1
        for i,sample in enumerate(x):
            xOneHot[i][sample] = 1
        self.xEncoded.append(xOneHot)
        self.yEncoded.append(yOneHot)
            
            
    def getNSamples(self, sequence):
        return (len(sequence)-self.sampleLength)//self.gap
    
    
    def invertOneHot(self):
        pass
    
    
    
    
    
    
    
def test():
    toOneHot = SequenceToOneHot(4, 2, 4)
    data = [[0,2,1,3,2,3,2,2,2,2,2,2,2,2,2,2,2,1,2,3,1,2,2,2,2,2,2,2,2],
            [3,3,3,0,0,1,3],
            [1,2]]
    toOneHot.fit(data)
    print(toOneHot.xEncoded)
    print(toOneHot.yEncoded)
#test()    
    