import time
from datetime import datetime
import os
import requests
import xml.etree.ElementTree as et
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('index.html')


@app.route('/currency_rate', methods=['GET'])
def CurrencyRate():
    localtime = time.asctime(time.localtime(time.time()))
    url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5'
    data = requests.post(url)
    file = open("currency.xml", "wb")
    file.write(data.content)
    file.close()
    tree = et.parse('currency.xml')
    root = tree.getroot()
    ccy_list = []
    buy_list = []
    sale_list = []
    for child in root:
        for subchild in child:
            values = subchild.attrib
            ccy = values.get('ccy')
            buy = values.get('buy')
            sale = values.get('sale')
            ccy_list.append(ccy)
            buy_list.append(buy)
            sale_list.append(sale)

    result = list(zip(ccy_list, buy_list, sale_list))
    os.remove('currency.xml')
    return render_template('currency_rate.html', localtime=localtime, result=result)



@app.route('/currency_history', methods=['GET', 'POST'])
def HistoryData():
    if request.method == 'POST':
        date = request.form['date']
        date2 = datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')

    history_url_base = 'https://api.privatbank.ua/p24api/exchange_rates?date={}'.format(date2)
    data = requests.post(history_url_base)
    file = open("currency_history.xml", "wb")
    file.write(data.content)
    file.close()
    tree = et.parse('currency_history.xml')
    root = tree.getroot()
    ccy_list = []
    sale_list = []
    buy_list = []
    for child in root:        
        values = child.attrib
        if 'currency' not in child.attrib:
            ccy_list.append('UAH')
        ccy = values.get('currency')        
        buy = values.get('purchaseRateNB')
        sale = values.get('saleRateNB') 
        ccy_list.append(ccy)
        sale_list.append(buy)
        buy_list.append(sale)

    if None in ccy_list:
        ccy_list.remove(None)

    result = list(zip(ccy_list,sale_list,buy_list))
    os.remove('currency_history.xml')
    return render_template('currency_history.html', date2=date2, result=result)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=False)