import stock
import pandas as pd
import numpy as np
import math
import scipy.stats
r = 1.75
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

dw_list = stock.dw_list()
dw_data = stock.dw_info()
sd = {}
dw = {} #  type , sname , issuer , Cprice , Eprice , moneyness , percent , time , date , volatility , multiplier , Price , BPrice
N = len(dw_list['name'])
for counter in range(0,N):
    i = dw_list['name'][counter]
    if i in dw_data.keys():
        sym = dw_data[i]['underlyingSymbol']
        check = True
        if sym not in sd.keys():
            print('loading history of ' , sym + '.BK' )
            data , status = stock.history(sym + '.BK')
            if status == 'success':
                print('successful')
                res = stock.log_return(data)
                sd[sym] = np.std(res) * math.sqrt(500)
            else:
                print('failed')
                check = False
                sd[sym] = -1
        try:
            dw[i] = {}
            dw[i]['name'] = i
            dw[i]['type'] = dw_data[i]['dwType']
            dw[i]['sname'] = dw_data[i]['underlyingSymbol']
            dw[i]['issuer'] = dw_data[i]['issuerSymbol']
            dw[i]['Cprice'] = dw_data[i]['underlyingPrice']
            dw[i]['Eprice'] = dw_data[i]['exercisePrice']
            dw[i]['Equality'] = 0
            dw[i]['moneyness'] = dw_list['moneyness'][counter]
            dw[i]['percent'] = dw_list['percent'][counter]
            dw[i]['time'] = dw_list['dayleft'][counter]
            dw[i]['date'] = dw_list['lastdate'][counter]
            dw[i]['multiplier'] = dw_data[i]['multiplier']
            dw[i]['volatility'] = sd[sym]
            dw[i]['Price'] = dw_list['price'][counter]
            dw[i]['BPrice'] = 0
            #dw[i]['BPrice2'] = 0
        except:
            print(i,"not ok")
            pass 


for i in dw.keys():
    if dw[i]['volatility'] > 0 and dw[i]['Cprice'] != 'null' and dw[i]['Eprice'] != 'null' and dw[i]['time'] != 'null':
        S = float(dw[i]['Cprice'])
        X = float(dw[i]['Eprice'])
        Sigma = dw[i]['volatility']
        T = float(dw[i]['time']) / 365
        VCall , VPut = stock.black_scholes(S,X,r/100,Sigma,T)
        if dw[i]['type'] == 'Call':
            #dw[i]['BPrice2'] = VCall
            try:
                dw[i]['Equality'] = float(dw[i]['Price'])/float(dw[i]['multiplier']) + X
            except:
                pass
            dw[i]['BPrice'] = VCall * float(dw[i]['multiplier'])
        else:
            #dw[i]['BPrice2'] = VPut
            try:
                dw[i]['Equality'] = -1 * (float(dw[i]['Price'])/float(dw[i]['multiplier']) - X)
            except:
                pass
            dw[i]['BPrice'] = VPut * float(dw[i]['multiplier'])
    else:
        dw[i]['BPrice'] = -1

df = pd.DataFrame.from_dict(dw).T
data = df.to_dict('records')
data




