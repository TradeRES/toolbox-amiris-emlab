"""
This is a mock to test Npv calculations
"""
import numpy_financial as npf
import numpy as np

def npvexcel(rate, values):
    values = np.asarray(values)
    return (values / (1+rate)**np.arange(1, len(values)+1)).sum(axis=0)

def __npv(netCashFlow, wacc):
    npv = 0
    for k,v in enumerate(netCashFlow):
        npv += v / (  1 + wacc)  ** int(k)
    return npv

invest_MW = 380000
capacity = 150
totalInvest = invest_MW*150
equity = 0.3
downpayment = totalInvest*equity
lifetime = 20
debt = totalInvest*0.7
interestRate = 0.1
restPayment = debt/lifetime
operating_profit = 832316.88*capacity
print(operating_profit)
wacc = 0.1
buildingTime = 1
depreciationTime = 20
fixed_costs =	7250* capacity

investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
print('restPayment', restPayment)
for i in range(0, buildingTime):
    investmentCashFlow[i] = - downpayment
for i in range(buildingTime, depreciationTime + buildingTime):
    investmentCashFlow[i] = operating_profit - restPayment - fixed_costs

npv_withrestpayment = npf.npv(wacc, investmentCashFlow)
npv_excel = npvexcel(wacc, investmentCashFlow)
npv_emlab = __npv( investmentCashFlow, wacc)

print("npv_numpy", npv_withrestpayment)

print("npv_excel ", npv_excel)
print("npv_emlab ", npv_emlab)
# ----------------------------------------------------------------------------------------------------------------------
"""
Testing  that annuity is same calculated in original emlab as with numpy
"""
def annuity_emlab(debt,  depreciationTime,  q):
    annuity = debt * (q ** depreciationTime * (q - 1))/ (q ** depreciationTime - 1)
    return annuity

annuity = - npf.pmt(0.1, depreciationTime, debt, fv=1, when='end')
print ("annuity numpy", annuity)
q = interestRate +1
emlab_annuity = annuity_emlab(debt,  depreciationTime,  q)

print("annuity emlab ",emlab_annuity )
# ---------------------------------------------------------------------------------------------
investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
print('loan', annuity)
for i in range(0, buildingTime):
    investmentCashFlow[i] = - downpayment
for i in range(buildingTime, depreciationTime + buildingTime):
    investmentCashFlow[i] = operating_profit - annuity

npv_with_loan = npf.npv(wacc, investmentCashFlow)

#
# print("restPayment / loan")
# print(restPayment / loan)
# print("npvwith restpayment / npv_with_loan ")
# print(npv_withrestpayment / npv_with_loan)
