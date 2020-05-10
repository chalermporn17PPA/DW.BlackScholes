#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import json
import numpy as np
import math
import scipy.stats
def history(name):
    data = {'date' : [] , 'open' : [] , 'high' : [] , 'low' : [] , 'close' : [] , 'volume' : [] , 'adjclose' : []}
    if type('123') != type(name):
        return data , 'name is not string'
    url = 'https://finance.yahoo.com/quote/' + name + '/history?period1=0000000000&period2=1999999999&interval=1d&filter=history&frequency=1d'
    html = requests.get(url,stream=True)
    if html.text.find('{"prices":[') < 0:
        return data , 'no historical data'
    text = html.text.split('{"prices":[')[1]
    text = text.split('}],"isPending"')[0]
    spl = text.split('},{')
    spl[0] =spl[0][1:]
    for i in spl :
        if i.find('open') >= 0 and i.find('high') >= 0 and i.find('low') >= 0 and i.find('close') >= 0:
            spl2 = i.split(',')
            for pair in spl2:
                key = pair.split(':')[0].strip('"')
                value = pair.split(':')[1]
                data[key].append(value)
    if len(data['date']) <= 3:
        return {} , 'error'
    return data,'success'


def dw_list():
    data = {'name' : [] , 'sname' : [] , 'type' : [] , 'issuer' : [],'price' : [] , 'moneyness' : [] , 'percent' : [] , 'lastdate' : [] , 'dayleft' : []} 
    obg = { 'issuer_' : '' , 'selectedPage' : '1' , 'submit' : 'ค้นหา' , 'existing' : 'true'}
    url = 'https://www.thaiwarrant.com/th/dw/search.asp'
    npage = 2;
    j = 1
    print("Loading DW list")
    while(j < npage):
        obg['selectedPage'] = j
        html = requests.post(url,obg)
        text = html.text.split('<td onclick="javascript:window.open(\'../dw/')
        if j == 1 :
            x = html.text.split('<ul class="c-content-pagination c-theme"> ')[1].split('</ul>')[0].split('<li')
            npage = len(x)
        print("Loading : " , j / (npage-1) * 100 , "%")
        text = text[1:]
        text[-1] = text[-1].split('</tr>')[0]
        for i in range(0,len(text),10):
            data['name'].append(text[i].split('\'')[0])
            data['sname'].append(text[i+1].split('\r\n')[1].strip());
            data['type'].append(text[i+2].split('\r\n')[1].strip());
            data['issuer'].append(text[i+3].split('\r\n')[1].strip())
            data['price'].append(text[i+4].split('\r\n')[1].strip())
            data['moneyness'].append(text[i+7].split('\r\n')[1].strip().split('/')[0].strip())
            data['percent'].append(text[i+7].split('\r\n')[1].strip().split('/')[1].strip()[0:-1])
            data['lastdate'].append(text[i+8].split('\r\n')[1].strip())
            data['dayleft'].append(text[i+9].split('\r\n')[1].strip())
        j = j + 1
    print(len(data['name']) , 'has been loaded')
    return data


def dw_info():
    url = 'https://api.set.or.th/api/dw-info/list?symbol='
    data = requests.get(url)
    T = data.text.split('[')[1].strip('}').strip(']').split('}')
    data = {}
    for text in T:
        text = text.strip(',').strip('{')
        temp = text.split(',')
        mem = ''
        for t in temp:
            t = t.split(':')
            if(len(t) == 2):
                t[0] = t[0].strip('""')
                t[1] = t[1].strip('""')
                if t[0] == 'symbol':
                    data[t[1]] = {}
                    mem = t[1]
                else:
                    data[mem][t[0]] = t[1]
    return data


def log_return(x , sample = -1):
    df = pd.DataFrame.from_dict(x)
    df = df[df.close != 'null']
    res = []
    data = []
    if sample == -1 or sample > len(df) :
        sample = len(df)
    for i in df['close']:
        data.append(float(i))
    for i in range(0,sample-1):
        log_re = (data[i] - data[i+1])/data[i+1]
        if log_re < 1 :
            res.append(log_re)
    return res

def black_scholes(S,X,R,Sigma,T):
    d1 = ( math.log(S/X) + ( (R + (Sigma ** 2)/2) * T )) / (Sigma * math.sqrt(T))
    d2 = d1 - Sigma * math.sqrt(T)
    Nd1 = scipy.stats.norm(0, 1).cdf(d1)
    Nd2 = scipy.stats.norm(0, 1).cdf(d2)
    VCall = Nd1 * S - Nd2 * X * math.exp(-1*R*T)
    Nnd2 = scipy.stats.norm(0, 1).cdf(-1 * d2)
    Nnd1 = scipy.stats.norm(0, 1).cdf(-1 * d1)
    VPut = Nnd2 * X * math.exp(-1*R*T) - S * Nnd1
    return VCall , VPut






