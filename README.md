# Zakupki

Collect data from the site http://www.zakupki.gov.ru/ and after that create a exel report.

# How to Install

Python 3 should be already installed. Then use pip (or pip3 if there is a conflict with old Python 2 setup) to install dependencies:

```bash
pip install -r requirements.txt # alternatively try pip3
```

# Quickstart

You can download and run it directly through console

Example of script launch on Linux, Python 3.5:

```bash
./Zakupki_main.py -m o -v 1
dieul@ubuntu:~/PycharmProjects/Zakupki$ ./Zakupki_main.py -m o -v 1
INFO:root:payload is 
{'searchString': 'видеонаблюдение', 'fz44': 'on', 'fz223': 'on', 'ppRf615': 'on', 'pc': 'on', 'priceFromGeneral': '500000', 'recordsPerPage': '_50', 'updateDateFrom': '18.07.2018', 'updateDateTo': '01.08.2018', 'districts': '5277336'}
INFO:root:send url 
 http://www.zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5&fz44=on&fz223=on&ppRf615=on&pc=on&priceFromGeneral=500000&recordsPerPage=_50&updateDateFrom=18.07.2018&updateDateTo=01.08.2018&districts=5277336
INFO:root:waiting 10 sec..... 

```
