from ..one_hot_encoder import OneHotEncodeGen



#EVEN INDS TRUE! Also use smaller value for nCLasses
class OneHotEncoderOnOnly(OneHotEncodeGen):
    def __init__(self, lookback=30, nClasses=100, startThresh = 20):
        super().__init__(lookback=lookback, nClasses=nClasses, startThresh=startThresh, evenInds=True)



