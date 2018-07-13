#!/usr/bin/python3

import requests
import pprint
from lxml import etree
from lxml.html import fromstring
from bs4 import BeautifulSoup
from datetime import date, timedelta
import xlwt
import argparse

SITE = "http://www.zakupki.gov.ru"
SEARCH_URL = "http://www.zakupki.gov.ru/epz/order/extendedsearch/results.html"
DEAL_URL = "http://www.zakupki.gov.ru/epz/order/" \
           "notice/ea44/view/supplier-results.html"


def create_url(searchString, updateDateFrom):
    # week_ago = date.today() - timedelta(weeks=1)
    #"updateDateFrom": week_ago.strftime('%d.%m.%Y')
    payload = {"searchString": searchString, "fz44": "on",
               "fz223": "on", "af": "on", "ca": "on",
               "priceFromGeneral": "500000", "recordsPerPage": "_50",
               "updateDateFrom": updateDateFrom,
               "updateDateTo": date.today().strftime('%d.%m.%Y')}
    url = requests.get(SEARCH_URL, params=payload)
    url.encoding = 'UTF-8'
    return url.url


def get_page(search_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url=search_url, headers=headers)
    response.encoding = 'UTF-8'
    return response


def save(text):
    with open('test.html', 'w') as f:
        f.write(text)


def get_info(response):
    response = response.text
    html = BeautifulSoup(response, 'html.parser')
    deals = html.find_all('div',
                          class_='registerBox registerBoxBank margBtm20')
    info = [{"Deal": ["Price", "FZ", "Status",
                      "Customer", "Create", "Update", "Link"]}]
    for deal in deals:
        zakupka_str = fromstring(str(deal))
        number = zakupka_str.xpath('table/tr/td[2]/dl/dt/a/text()')[0].strip()
        number = ''.join(c for c in number if c.isdigit())
        number_href = SITE + zakupka_str.xpath('table/tr/td[2]'
                                               '/dl/dt/a/@href')[0]
        try:
            price = zakupka_str.xpath('table/tr/td[1]/'
                                      'dl/dd[2]/strong/text()')[0].strip()
            price = ''.join(c for c in price if c.isdigit())
        except:
            price = None
        fz = zakupka_str.xpath('table/tr/td[1]/dl/dt[2]'
                               '/span/span/text()')[0].strip()
        status = zakupka_str.xpath('table/tr/td[1]/dl/'
                                   'dt[2]/span/text()')[0].strip()
        customer = zakupka_str.xpath('table/tr/td[2]/dl/'
                                     'dd[1]/ul/li/a/text()')[0].strip()
        create = zakupka_str.xpath('table/tr/td[3]/ul/'
                                   'li[1]/text()')[0].strip()
        update = zakupka_str.xpath('table/tr/td[3]/ul/'
                                   'li[2]/text()')[0].strip()
        info.append({number: [price, fz, status,
                              customer, create, update, number_href]})
    return info


def extract_distributor(deals_info):
    for deal in deals_info[1::]:
        deal_number = list(deal.keys())[0]
        url = requests.Request('GET',
                               DEAL_URL,
                               params={"regNumber": deal_number}).prepare()
        deal_page = get_page(url.url)
        players = fromstring(str(deal_page.text)).xpath(
            '/html/body/div/div/div/div[5]'
            '/div/div/div/table/tr[2]/td[3]/text()')
        [0].strip()
        deal[deal_number].append(players)
    return deals_info


def create_report(deals_info, searchString):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Report')
    # deals_info[0]["Deal"].append("Winners")
    for (j, deal_info) in enumerate(deals_info):
        deal_number = list(deal_info.keys())[0]
        ws.write(j, 0, deal_number)
        print()
        for (k, info) in enumerate(deal_info[deal_number]):
            ws.write(j, 1 + k, info)
    wb.save('./Report {}.xls'.format(searchString))


def create_parser():
    week_ago = date.today() - timedelta(weeks=1)
    parser = argparse.ArgumentParser(description='zakupki')
    parser.add_argument('-s', default="видеонаблюдение",
                        type=str, help="searchString")
    parser.add_argument('-df', default=week_ago.strftime('%d.%m.%Y'),
                        type=str, help="%d.%m.%Y")
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    print(create_url(args.s, args.df))
    response = get_page(create_url(args.s, args.df))
    deals_info = get_info(response)
    # deals_info = extract_distributor(deals_info)
    pprint.pprint(deals_info)
    create_report(deals_info, args.s)
