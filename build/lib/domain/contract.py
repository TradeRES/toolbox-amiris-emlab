class Contract:

    def __init__(self):
        #instance fields found by Java to Python Converter:
        self.__from_keyword_conflict = None
        self.__to = None
        self.__pricePerUnit = 0
        self.__signed = False
        self.__start = 0
        self.__finish = 0


    #    @RelatedTo(type = "CONTRACT_FROM", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)

    #    @RelatedTo(type = "CONTRACT_TO", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)


    def getPricePerUnit(self):
        return self.__pricePerUnit

    def setPricePerUnit(self, pricePerUnit):
        self.__pricePerUnit = pricePerUnit

    def isSigned(self):
        return self.__signed

    def setSigned(self, signed):
        self.__signed = signed

    def getStart(self):
        return self.__start

    def setStart(self, start):
        self.__start = start

    def getFinish(self):
        return self.__finish

    def setFinish(self, finish):
        self.__finish = finish

    def getFrom(self):
        return self.__from_keyword_conflict

    def setFrom(self, from_keyword_conflict):
        self.__from_keyword_conflict = from_keyword_conflict

    def getTo(self):
        return self.__to

    def setTo(self, to):
        self.__to = to
