import numpy_financial as npf

interestRate =.07
totalLoan = 1
payBackTime =20

annuity = npf.pmt(interestRate, payBackTime, totalLoan, fv=0, when='end')
print(annuity)


annuity_like_emlab = totalLoan * ((1 + interestRate) ** payBackTime * (interestRate)) / (
               (1 + interestRate) ** payBackTime - 1)

print(annuity_like_emlab)

annuity_like_book = totalLoan / ( (1 / interestRate) * (1-1/(1+interestRate) ** payBackTime ))
print(annuity_like_book)
