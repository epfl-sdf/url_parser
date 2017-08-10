#!/usr/bin/python3

import os
import sys
import logging

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime

from version import __version__

def get_host(url):
    parts = url.split('/')
    if url.startswith('http'):
        return parts[2]
    else:
        return parts[0]

def parse_jahia(host_jahia, soup):
    # Parser la page jahia
    links_jahia = {}
    if soup.body is not None:
        menu_div = soup.find('div', {'id' : 'main-navigation'})
        if menu_div is not None:
            for menu_item in menu_div.findAll('li', {'id' : lambda x : x and x.startswith('dropdown')}):
                for link in menu_item.findAll('a'):
                    complete_link = host_jahia + link['href']
                    if link['href'].startswith('http://'):
                        complete_link = link['href']
                    if link.getText().strip() in links_jahia and complete_link not in links_jahia[link.getText().strip()]:
                        #links_jahia[link.getText().strip()].append(complete_link)
                        logging.warning('Un site a plusieurs fois un lien du même nom : ' + link.getText().strip() + ' : ' + complete_link)
                        links_jahia.pop(link.getText().strip(), None)
                    else:
                        links_jahia[link.getText().strip()] = [complete_link]
    return links_jahia

def parse_wp(host_wp, soup):
    # Parser la page wordpress
    links_wp = {}
    if soup.body is not None:
        menu_div = soup.find('ul', {'id' : 'top-menu'})
        if menu_div is not None:
            for menu_item in menu_div.findAll('li', {'id' : lambda x : x and x.startswith('menu-item')}):
                for link in menu_item.findAll('a'):
                    complete_link = host_wp + link['href']
                    if link['href'].startswith('http://'):
                        complete_link = link['href']
                    if link.getText().strip() in links_wp and complete_link not in links_wp[link.getText().strip()]:
                        #links_wp[link.getText().strip()].append(complete_link)
                        logging.warning('Un site a plusieurs fois un lien du même nom: ' + link.getText().strip() + ' : ' + complete_link)
                        links_wp.pop(link.getText().strip(), None)
                    else:
                        links_wp[link.getText().strip()] = [complete_link]
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

def write_output(result_file, result):
    for tup in result:
        line = ','.join([str(x) for x in tup])
        print(line, file=result_file)

def collect_links(url_jahia, url_wp, soup_jahia, soup_wp):
    links_jahia = {}
    links_wp = {}

    host_jahia = get_host(url_jahia)
    host_wp = get_host(url_wp)
    links_jahia.update(parse_jahia(host_jahia, soup_jahia))
    links_wp.update(parse_wp(host_wp, soup_wp))

    return add_to_output(url_jahia, url_wp, links_jahia, links_wp)

def make_mapping():
    proxy = sys.argv[2]
    port = sys.argv[3]

    credentials = open(sys.argv[1], 'r')
    # Sauter la premiere ligne
    next(credentials)
    
    result_file = open('result.csv', 'w')

    for line in credentials:
        parts = line.strip().split(',')
        url_jahia = parts[1]
        url_wp = parts[2]
        user = parts[5]
        pwd = parts[6]
    
        new_jahia = os.popen("curl -s -I " + url_jahia + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        new_wp = os.popen("curl -s -I " + url_wp + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        if new_jahia != '':
            url_jahia = new_jahia
        if new_wp != '':
            url_wp = new_wp

        host_jahia = get_host(url_jahia)
        host_wp = get_host(url_wp)

        html_jahia = os.popen('wget -qO- ' + url_jahia).read()
        html_wp = os.popen('./aspi.sh ' + proxy + ' ' + str(port) + ' ' + url_wp + ' ' + user + ' ' + pwd + ' true').read()
    
        soup_jahia = BeautifulSoup(html_jahia, 'html.parser')
        soup_wp = BeautifulSoup(html_wp, 'html.parser')
        
        # Detection et verification de langues
        jahia_lang_other = ""
        jahia_other_link = ""
        wp_lang_other = ""
        wp_other_link = ""
        languages = soup_jahia.find('ul', {'id' : 'languages'})
        if languages is not None:
            for language in languages.findAll('li'):
                if language.has_attr('class'):
                    jahia_lang_curr = language.getText().strip().lower()
                else:
                    jahia_lang_other = language.getText().strip().lower()
                    jahia_other_link = host_jahia + language.find('a')['href']
        languages = soup_wp.find('ul', {'class' : 'language-switcher'})
        if languages is not None:
            for language in languages.findAll('li'):
                if 'current-lang' in language['class']:
                    wp_lang_curr = language.getText().strip().lower()
                else:
                    wp_lang_other = language.getText().strip().lower()
                    wp_other_link = language.find('a')['href']

        if jahia_lang_curr != wp_lang_curr and jahia_other_link != "":
            old_url_jahia = url_jahia
            old_soup_jahia = soup_jahia
            url_jahia = jahia_other_link
            html_jahia = os.popen('wget -qO- ' + url_jahia).read()
            soup_jahia = BeautifulSoup(html_jahia, 'html.parser')
        
        if jahia_lang_curr != wp_lang_curr:
            if jahia_other_link == "":
                logging.warning('Le site jahia' + url_jahia +' est en ' + jahia_lang_curr + ' mais le WP est en ' + wp_lang_curr + " et le site correspondant jahia n'existe pas")
            if wp_other_link == "":
                logging.warning('Le site wp ' + url_wp +' est en ' + wp_lang_curr + ' mais le jahia est en ' + jahia_lang_curr + " et le site correspondant WP n'existe pas")

        result = collect_links(url_jahia, url_wp, soup_jahia, soup_wp)

        if jahia_lang_curr != wp_lang_curr and jahia_other_link != "":
            url_jahia = old_url_jahia
            soup_jahia = old_soup_jahia
        else:
            url_jahia = jahia_other_link
            if url_jahia != '':
                html_jahia = os.popen('wget -qO- ' + url_jahia).read()
                soup_jahia = BeautifulSoup(html_jahia, 'html.parser')

        if wp_other_link != '':
            url_wp = wp_other_link
            html_wp = os.popen('./aspi.sh ' + proxy + ' ' + str(port) + ' ' + url_wp + ' ' + user + ' ' + pwd).read()
            soup_wp = BeautifulSoup(html_wp, 'html.parser')

        if wp_other_link != '' and jahia_other_link != '':
            result.extend(collect_links(url_jahia, url_wp, soup_jahia, soup_wp))

        write_output(result_file, result)
    result_file.close()

if __name__ == "__main__":
    print("parser.py vers " + __version__)
    logging.basicConfig(filename='warnings-' + str(datetime.now()) + '.log')

    if len(sys.argv) < 4:
        print("Pas assez d'arguments.")
        print("Syntaxe: ./parser.py fichier_des_sites addresse_du_proxy port_du_proxy")
        exit(1)

    make_mapping()

