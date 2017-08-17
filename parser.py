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

def parse_jahia(host_jahia, menu):
    result = {}
    for menu_item in menu.findAll('li', recursive=False):
        for link_div in menu_item.findAll('div', {'class', 'pageAction'}, recursive=False):
            link = link_div.find('a', recursive=False)
            if link and link.has_attr('href'):
                complete_link = host_jahia + link['href']
                if link['href'].startswith('http://'):
                    complete_link = link['href']
                if link.getText().strip() in result and complete_link not in result[link.getText().strip()]:
                    #links_jahia[link.getText().strip()].append(complete_link)
                    logging.warning('Un site a plusieurs fois un lien du même nom : ' + link.getText().strip() + ' : ' + complete_link)
                    result.pop(link.getText().strip(), None)
                else:
                    result[link.getText().strip()] = [complete_link]
                new_menu = menu_item.find('ul', recursive=False)
                if new_menu and link.getText().strip() in result:
                    result[link.getText().strip()].append(parse_jahia(host_jahia, new_menu))
    return result

def parse_wp(host_wp, menu):
    result = {}
    for menu_item in menu.findAll('li', recursive=False):
        link = menu_item.find('a', recursive=False)
        if link:
            complete_link = host_wp + link['href']
            if link['href'].startswith('http://'):
                complete_link = link['href']
            if link.getText().strip() in result and complete_link not in result[link.getText().strip()]:
                logging.warning('Un site a plusieurs fois un lien du même nom: ' + link.getText().strip() + ' : ' + complete_link)
                result.pop(link.getText().strip(), None)
            else:
                result[link.getText().strip()] = [complete_link]
            new_menu = menu_item.find('ul', recrusive=False)
            if new_menu and link.getText().strip() in result:
                result[link.getText().strip()].append(parse_wp(host_wp, new_menu))
    return result

i = 0
def add_to_output(url_jahia, url_wp, links_jahia, links_wp, level):
    global i
    result = []
    
    for key, value in links_jahia.items():
        if key in links_wp:
            result.append((i, level, value[0], links_wp[key][0]))
            i += 1
            if len(value) > 1 and len(links_wp[key]) > 1:
                result.extend(add_to_output(url_jahia, url_wp, value[1], links_wp[key][1], level + 1))
    return result

def write_output(result_file, result):
    for tup in result:
        line = ','.join([str(x) for x in tup])
        print(line, file=result_file)

def collect_links(url_jahia, url_wp, soup_jahia, soup_wp):
    links_jahia = {}
    links_wp = {}

    menu_jahia = soup_jahia.find('ul', {'id' : 'jquery_tree'})
    menu_wp = soup_wp.find('ul', {'class' : 'simple-sitemap-page'})
    #for c in sitemap_wp.findAll('li', recursive=False):
    #    if 'current_page_item' not in c['class']:
    #        menu_wp = c.find('ul')

    host_jahia = get_host(url_jahia)
    host_wp = get_host(url_wp)
    if menu_jahia:
        links_jahia.update(parse_jahia(host_jahia, menu_jahia))
    if menu_wp:
        links_wp.update(parse_wp(host_wp, menu_wp))

    return add_to_output(url_jahia, url_wp, links_jahia, links_wp, 1)

def find_languages_wp(soup_wp):
    languages = soup_wp.find('ul', {'class' : 'language-switcher'})
    wp_lang_curr = ""
    wp_other_link = ""
    wp_curr_link = ""
    if languages is not None:
        for language in languages.findAll('li'):
            if 'current-lang' in language['class']:
                wp_lang_curr = language.getText().strip().lower()
                wp_curr_link = language.find('a')['href']
            else:
                wp_other_link = language.find('a')['href']
    return (wp_lang_curr, wp_other_link, wp_curr_link)

def find_languages_jahia(soup_jahia, host_jahia):
    languages = soup_jahia.find('ul', {'id' : 'languages'})
    jahia_lang_curr = ""
    jahia_other_link = ""
    if languages is not None:
        for language in languages.findAll('li'):
            if language.has_attr('class'):
                jahia_lang_curr = language.getText().strip().lower()
            else:
                jahia_other_link = host_jahia + language.find('a')['href']
    return (jahia_lang_curr, jahia_other_link)

def make_mapping():
    global i

    credentials = open(sys.argv[1], 'r')
    # Sauter la premiere ligne
    next(credentials)
    
    result_file = open('result.csv', 'w')

    index = 0
    for line in credentials:
        parts = line.strip().split(',')
        url_jahia = parts[1].strip('/') + '/sitemap'
        url_wp = parts[2].strip('/')
        user = parts[5]
        pwd = parts[6]
    
        new_jahia = os.popen("curl -s -I " + url_jahia + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        new_wp = os.popen("curl -s -I " + url_wp + "| awk '/Location: (.*)/ {print $2}' | tail -n 1").read().strip()
        if new_jahia != '':
            url_jahia = new_jahia
            if not url_jahia.endswith('/sitemap'):
                url_jahia += '/sitemap'
        if new_wp != '':
            url_wp = new_wp
        
        print(str(index) + ' : ' + url_jahia + ' ' + url_wp)
        index += 1

        host_jahia = get_host(url_jahia)
        host_wp = get_host(url_wp)

        html_jahia = os.popen('wget -qO- ' + url_jahia).read()
        if html_jahia == '':
            url_jahia = url_jahia[:-8] + '/plan-du-site'
            html_jahia = os.popen('wget -qO- ' + url_jahia).read()
        html_wp = os.popen('./aspi.sh ' + ' ' + url_wp + ' /sitemap ' + user + ' ' + pwd + ' true').read()
    
        soup_jahia = BeautifulSoup(html_jahia, 'html.parser')
        soup_wp = BeautifulSoup(html_wp, 'html.parser')
        
        # Detection et verification de langues
        (jahia_lang_curr, jahia_other_link) = find_languages_jahia(soup_jahia, host_jahia)
        (wp_lang_curr, wp_other_link, wp_curr_link) = find_languages_wp(soup_wp)
        url_wp = wp_curr_link

        if jahia_other_link != '':
            html_other_jahia = os.popen('wget -qO- ' + jahia_other_link).read()
            soup_other_jahia = BeautifulSoup(html_other_jahia, 'html.parser')
            url_jahia = find_languages_jahia(soup_other_jahia, host_jahia)[1]

        if jahia_lang_curr != wp_lang_curr and jahia_other_link != '':
            old_url_jahia = url_jahia
            old_soup_jahia = soup_jahia
            url_jahia = jahia_other_link
            html_jahia = html_other_jahia
            soup_jahia = soup_other_jahia
        
        '''
        if jahia_lang_curr != wp_lang_curr:
            if jahia_other_link == "":
                logging.warning('Le site jahia' + url_jahia +' est en ' + jahia_lang_curr + ' mais le WP est en ' + wp_lang_curr + " et le site correspondant jahia n'existe pas")
            if wp_other_link == "":
                logging.warning('Le site wp ' + url_wp +' est en ' + wp_lang_curr + ' mais le jahia est en ' + jahia_lang_curr + " et le site correspondant WP n'existe pas")
        '''
        result = collect_links(url_jahia, url_wp, soup_jahia, soup_wp)

        if jahia_lang_curr != wp_lang_curr and jahia_other_link != "":
            url_jahia = old_url_jahia
            soup_jahia = old_soup_jahia
        else:
            url_jahia = jahia_other_link
            if url_jahia != '':
                html_jahia = html_other_jahia
                soup_jahia = soup_other_jahia

        if wp_other_link != '':
            url_wp = wp_other_link
            html_wp = os.popen('./aspi.sh ' + ' ' + url_wp + ' / ' + user + ' ' + pwd).read()
            soup_wp = BeautifulSoup(html_wp, 'html.parser')

        if wp_other_link != '' and jahia_other_link != '':
            result.extend(collect_links(url_jahia, url_wp, soup_jahia, soup_wp))

        write_output(result_file, result)
        i = 0
    result_file.close()

if __name__ == "__main__":
    print("parser.py vers " + __version__)
    logging.basicConfig(filename='warnings-' + str(datetime.now()) + '.log')

    if len(sys.argv) < 2:
        print("Pas assez d'arguments.")
        print("Syntaxe: ./parser.py fichier_des_sites")
        exit(1)

    make_mapping()

