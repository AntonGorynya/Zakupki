#!/usr/bin/python3

import requests
import pprint
from lxml import etree
from lxml.html import fromstring
from bs4 import BeautifulSoup
from datetime import date, timedelta
import xlwt
import argparse
import time
import logging

VERBOSITY_TO_LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}
SITE = "http://www.zakupki.gov.ru"
SEARCH_URL = "http://www.zakupki.gov.ru/epz/order/extendedsearch/results.html"
DEAL_URL = "http://www.zakupki.gov.ru/epz/order/" \
           "notice/ea44/view/supplier-results.html"
KEY_WORDS = ["видеонаблюдение",
             "видеостена", "СКУД",
             "Домофония", "тепловизоры"]
DELAY = 10


def create_url(searchString, updateDateFrom, params, pageNumber = 1):
    if params == 'n':
        payload = {"searchString": searchString,
                   "pageNumber": pageNumber,
                   "fz44": "on", "fz223": "on",
                   "ppRf615": "on", "af": "on", "ca": "on",
                   "priceFromGeneral": "500000", "recordsPerPage": "_50",
                   "updateDateFrom": updateDateFrom,
                   "updateDateTo": date.today().strftime('%d.%m.%Y'),
                   "districts": "5277336"}
    if params == 'o':
        payload = {"searchString": searchString,
                   "pageNumber": pageNumber,
                   "fz44": "on", "fz223": "on",
                   "ppRf615": "on", "pc": "on",
                   "priceFromGeneral": "500000", "recordsPerPage": "_50",
                   "updateDateFrom": updateDateFrom,
                   "updateDateTo": date.today().strftime('%d.%m.%Y'),
                   "districts": "5277336"}
    logging.debug('payload is \n{}'.format(payload))
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
    all_records = html.find('p', class_='allRecords')
    if all_records is None:
        logging.debug("noting found")
        return None, None
    else:
        #all_records = fromstring(str(all_records)).xpath('//strong/text()')[0]
        all_records = int(all_records.strong.text)
        logging.debug(
            "total numbers of all_records {}".format(all_records))
    info = [{"Deal": ["Price", "FZ", "Status",
                      "Customer", "Create", "Update", "Link"]}]
    for deal in deals:
        zakupka_str = fromstring(str(deal))
        number = zakupka_str.xpath(
            '//td[contains(@class, "descriptTenderTd")]'
            '/dl/dt/a/text()')[0].strip()
        number = ''.join(c for c in number if c.isdigit())
        href = zakupka_str.xpath(
            '//td[contains(@class, "descriptTenderTd")]/dl/dt/a/@href')[0]
        if  href[0] == '/':
            href = SITE + href
        try:
            # price = zakupka_str.xpath('table/tr/td[1]/'
            #                          'dl/dd[2]/strong/text()')[0].strip()
            price = zakupka_str.xpath(
                '//td[contains(@class, "tenderTd")]'
                '/dl/dd[2]/strong/text()')[0].strip()
            price = ''.join(c for c in price if c.isdigit())
            price = int(price)
        except IndexError:
            price = None
        fz = zakupka_str.xpath(
            '//span[contains(@class, "orange")]/text()')[0].strip()
        status = zakupka_str.xpath('//span[contains(@class, "fzNews") '
                                   'or contains(@class, "timeNews") '
                                   'or contains(@class, "checked")'
                                   'and contains(@class, "noWrap")]'
                                   '/text()')[0].strip()[:-2]
        customer = zakupka_str.xpath(
            '//dd[contains(@class, "nameOrganization")]'
            '/ul/li/a/text()')[0].strip()
        create = zakupka_str.xpath('//td[contains(@class, "amountTenderTd")]'
                                   '/ul/li[1]/text()')[0].strip()
        update = zakupka_str.xpath('//td[contains(@class, "amountTenderTd")]'
                                   '/ul/li[2]/text()')[0].strip()
        info.append({number: [price, fz, status,
                              customer, create, update, href]})
    return info, all_records


def extract_distributor(deals_info):
    for deal in deals_info[1::]:
        deal_number = list(deal.keys())[0]
        fz = deal[deal_number][1]
        if fz == "44-ФЗ":
            url = requests.Request('GET',
                                   DEAL_URL,
                                   params={"regNumber": deal_number}).prepare()
            deal_page = get_page(url.url)
            logging.debug("extract distributor from \n {} \n".format(url.url))
            time.sleep(DELAY)
            # players = fromstring(str(deal_page.text)).xpath(
            #    '/html/body/div/div/div/div[5]'
            #    '/div/div/div/table/tr[2]/td[3]/text()')[0].strip()
            try:
                player_1 = fromstring(str(deal_page.text)).xpath(
                    '//div[contains(@class, "noticeTabBox")'
                    ' and '
                    'contains(@class, "padBtm20")]'
                    '/div/div/table/tr[2]/td[3]/text()')[0].strip()
            except IndexError:
                player_1 = None
            try:
                player_2 = fromstring(str(deal_page.text)).xpath(
                    '//div[contains(@class, "noticeTabBox") '
                    'and contains(@class, "padBtm20")]'
                    '/div/div/table/tr[3]/td[1]/text()')[0].strip()
            except IndexError:
                player_2 = None

            players = "{} \n {}".format(player_1, player_2)
            print(players)
            logging.debug('winners {}'.format(players))
            deal[deal_number].append(players)
    return deals_info


def test(html):
    players = fromstring(html).xpath(
        '//div[contains(@class, "noticeTabBox")'
        ' and contains(@class, "padBtm20")]/div/div/table/tr[2]/td[3]/text()')[
        0].strip()
    table = fromstring(html).xpath(
        '//div[contains(@class, "noticeTabBox") '
        'and contains(@class, "padBtm20")]/div/div/table')

    for node in table:
        print(node.tag, node.keys(), node.values())
        print('name =', node.get('name'))
        print('text =', [node.text])


def create_report(wb, deals_info, searchString, type):
    ws = wb.add_sheet(searchString)
    ws.col(0).width = 256*20
    ws.col(3).width = 256 * 20
    ws.col(4).width = 256 * 60
    ws.col(5).width = 256 * 10
    ws.col(6).width = 256 * 10
    ws.col(7).width = 256 * 20
    ws.col(8).width = 256 * 60
    style = xlwt.XFStyle()
    style.alignment.wrap = 1
    if type == 'o':
        deals_info[0]["Deal"].append("Winners")
    for (j, deal_info) in enumerate(deals_info):
        deal_number = list(deal_info.keys())[0]
        ws.write(j, 0, deal_number, style)
        for (k, info) in enumerate(deal_info[deal_number]):
            ws.write(j, 1 + k, info, style)


def search(word, dateFrom, mode, pageNumber=1):
    url = create_url(word, dateFrom, mode, pageNumber)
    logging.info('send url \n {}'.format(url))
    response = get_page(url)
    logging.info("waiting {} sec..... \n".format(DELAY))
    return response


def create_parser():
    week_ago = date.today() - timedelta(weeks=2)
    parser = argparse.ArgumentParser(description='zakupki')
    parser.add_argument('-s', default=KEY_WORDS,
                        type=str, help="searchString")
    parser.add_argument('-df', default=week_ago.strftime('%d.%m.%Y'),
                        type=str, help="date in format d.m.Y")
    parser.add_argument('--mode', '-m', default='n', type=str,
                        help="n - find new deals \n o - find old deals")
    parser.add_argument('--verbose', '-v', type=int, default=0)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    logging_level = VERBOSITY_TO_LOGGING_LEVELS[args.verbose]
    logging.basicConfig(level=logging_level)
    wb = xlwt.Workbook()
    for word in KEY_WORDS:
        response = search(word, args.df, args.mode)
        time.sleep(DELAY)
        deals_info, number_of_records = get_info(response)
        logging.info(" Number of record is {}".format(number_of_records))
        if number_of_records is not None and number_of_records > 50:
            pageAmount = number_of_records // 50 + 1
            logging.info("pageAmount is {}".format(pageAmount))
            for pageNumber in range(1, pageAmount):
                print(pageNumber)
                logging.info("new search page  {}".format(pageNumber))
                response = search(word, args.df, args.mode, pageNumber)
                time.sleep(DELAY)
                deals_info += get_info(response)[0]
        if args.mode == 'o' and deals_info is not None:
            logging.info('start extracting distributors........')
            deals_info = extract_distributor(deals_info)
        if deals_info is not None:
            logging.info(deals_info)
            create_report(wb, deals_info, word, args.mode)
    logging.info('save as ./Report {}_{}.xls'.format(date.today(), args.mode))
    wb.save('./Report {}_{}.xls'.format(date.today(), args.mode))
