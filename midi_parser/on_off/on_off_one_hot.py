from ..one_hot_encoder import OneHotEncodeGen


#Only difference between OnOff and OnOnly one hot encoder is even ind
class OneHotEncoderOnOff(OneHotEncodeGen):
    def __init__(self, lookback=30, nClasses=200, startThresh = 20):
        super().__init__(lookback=lookback, nClasses=nClasses, startThresh=startThresh, evenInds=False)



