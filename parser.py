#!/usr/bin/python3

import os
import sys

from bs4 import BeautifulSoup
from collections import OrderedDict

def parse_jahia(url_jahia, soup):
    # Parser la page jahia
    links_jahia = {}
    if soup.body is not None:
        menu_div = soup.find('div', {'id' : 'main-navigation'})
        if menu_div is not None:
            for menu_item in menu_div.findAll('li', {'id' : lambda x : x and x.startswith('dropdown')}):
                for link in menu_item.findAll('a'):
                    complete_link = url_jahia + link['href']
                    if link['href'].startswith('http://'):
                        complete_link = link['href']
                    if link.getText() in links_jahia and complete_link not in links_jahia[link.getText()]:
                        links_jahia[link.getText()].append(complete_link)
                    else:
                        links_jahia[link.getText()] = [complete_link]
    return links_jahia

def parse_wp(url_wp, soup):
    # Parser la page wordpress
    links_wp = {}
    if soup.body is not None:
        menu_div = soup.find('ul', {'id' : 'top-menu'})
        if menu_div is not None:
            for menu_item in menu_div.findAll('li', {'id' : lambda x : x and x.startswith('menu-item')}):
                for link in menu_item.findAll('a'):
                    complete_link = url_wp + link['href']
                    if link['href'].startswith('http://'):
                        complete_link = link['href']
                    if link.getText() in links_wp and complete_link not in links_wp[link.getText()]:
                        links_wp[link.getText()].append(complete_link)
                    else:
                        links_wp[link.getText()] = [complete_link]
    return links_wp

def add_to_output(url_jahia, url_wp, links_jahia, links_wp):
    result = []
    i = 0
    result.append((i, 1, url_jahia, url_wp))
    i += 1
    
    for key in links_jahia:
        if key in links_wp:
            for j in range(0, len(links_jahia[key])):
                result.append((i, 2, links_jahia[key][j], links_wp[key][j]))
            i += 1
    return result

def write_output(output_filename, result):
    result_file = open(output_filename, 'w')
    for tup in result:
        line = ','.join([str(x) for x in tup])
        print(line, file=result_file)
    result_file.close()


def make_mapping():
    proxy = sys.argv[2]
    port = sys.argv[3]

    credentials = open(sys.argv[1], 'r')
    # Sauter la premiere ligne
    next(credentials)

    for line in credentials:
        parts = line.split(',')
        server = parts[1]
        url_jahia = parts[2]
        url_wp = server + parts[4]
        user = parts[6]
        pwd = parts[7]
    
        new_jahia = os.popen("curl -s -I " + url_jahia + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        new_wp = os.popen("curl -s -I " + url_wp + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        if new_jahia != '':
            url_jahia = new_jahia
        if new_wp != '':
            url_wp = new_wp
    
        html_jahia = os.popen('wget -qO- ' + url_jahia).read()
        html_wp = os.popen('./aspi.sh ' + proxy + ' ' + str(port) + ' ' + url_wp + ' ' + user + ' ' + pwd).read()
    
        soup_jahia = BeautifulSoup(html_jahia, 'html.parser')
        soup_wp = BeautifulSoup(html_wp, 'html.parser')
    
        links_jahia = {}
        links_wp = {}
    
        links_jahia.update(parse_jahia(url_jahia, soup_jahia))
        links_wp.update(parse_wp(url_wp, soup_wp))

        result = add_to_output(url_jahia, url_wp, links_jahia, links_wp)

        write_output('result.csv', result)

if __name__ == "__main__":
    print("parser.py vers 1.0.1")

    if len(sys.argv) < 4:
        print("Pas assez d'arguments.")
        print("Syntaxe: ./parser.py fichier_des_sites addresse_du_proxy port_du_proxy")
        exit(1)

    make_mapping()

