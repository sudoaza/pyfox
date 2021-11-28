#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
author: @thewhitetulip

A small python script to extract browsing history and bookmarks from  various
browsers, currently supports firefox and chromium (partially)

'''

import sqlite3
import os
from datetime import datetime
import sys
import argparse
import webbrowser


def execute_query(cursor, query):
    ''' Takes the cursor object and the query, executes it '''
    try:
        cursor.execute(query)
    except Exception as error:
        print(str(error) + "\n " + query)

def open_browser(url):
    '''Opens the default browswer'''
    webbrowser.open(url, autoraise=True)


def read_template():
    """ Reads the html content from the template which will be returned
    as a string to write in another file """
    file = open("template.html", 'r')
    lines = file.readlines()

    tmp = u""
    lines = [line.strip() for line in lines]
    for line in lines:
        tmp += str(line)
        tmp += "\n"
    return tmp

def history(cursor, pattern=None, src=""):
    ''' Function which extracts history from the sqlite file '''
    html = u""
    html = read_template()
    if src == 'firefox':
        sql = """SELECT url, title, last_visit_date, rev_host 
                FROM moz_historyvisits
                JOIN moz_places ON (moz_historyvisits.place_id = moz_places.id)"""

        if pattern is not None:
            sql += " WHERE url like '%"+pattern+"%' "
        sql += " order by last_visit_date desc;"


        execute_query(cursor, sql)

        for row in cursor:
            last_visit = datetime.fromtimestamp(row[2]/1000000).strftime('%Y-%m-%d %H:%M:%S')
            link = row[0]
            title = row[1]

            html += "<tr><td><a href='" + str(link) + "'>" + str(title)[:100] +\
            "</a></td>" + "<td>" + str(last_visit) + "</td>" + "<td>" + \
            str(link[:100]) + "</td>" + "</tr>\n"
            #print(a)

    if src == 'chrome':
        sql = "SELECT urls.url, urls.title, urls.visit_count, \
        urls.typed_count, datetime(urls.last_visit_time/1000000-11644473600,'unixepoch','localtime'), urls.hidden,\
        visits.visit_time, visits.from_visit, visits.transition FROM urls, visits\
         WHERE  urls.id = visits.url and urls.title is not null order by last_visit_time desc "

        execute_query(cursor, sql)
        for row in cursor:
            print("%s %s"%(row[0], row[4]))

    html += "</tbody>\n</table>\n</body>\n</html>"
    html_file = open("history.html", 'w')

    html_file.write(html)
    html_file.close()
    open_browser("history.html")

def bookmarks(cursor, pattern=None):
    ''' Function to extract bookmark related information '''

    the_query = """select url, moz_places.title, rev_host, frecency,
    last_visit_date from moz_places  join  \
    moz_bookmarks on moz_bookmarks.fk=moz_places.id where visit_count>0
    and moz_places.url  like 'http%'
    order by dateAdded desc;"""

    execute_query(cursor, the_query)

    html = u""
    html = read_template()
    html_file = open("bookmarks.html", 'w')
    for row in cursor:
        link = row[0]
        title = row[1]
        date = str(datetime.fromtimestamp(row[4]/1000000).strftime('%Y-%m-%d %H:%M:%S'))

        html += "<tr><td><a href='"+link+"'>"+title+"</a></td>"+"<td>"+link+\
        "</td>"+"<td>"+date+"</td></tr>\n"
        print("%s %s"%(row[0], row[1]))
    html += "</tbody>\n</table>\n</body>\n</html>"

    try:
        html_file.write(html.encode('utf8'))
    except:
        html_file.write(html)
    html_file.close()
    open_browser("bookmarks.html")

def get_path(browser):
    '''Gets the path where the sqlite3 database file is present'''
    if browser == 'firefox':
        if sys.platform.startswith('win') == True:
            path = '\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\'
        elif sys.platform.startswith('linux') == True:
            path = "/.mozilla/firefox/"
        elif sys.platform.startswith('darwin') == True:
            path = '/Library/Application Support/Firefox/Profiles/'

    #elif browser == 'chrome':
    #    if sys.platform.startswith('win') == True:
    #        path = ''
    #    elif sys.platform.startswith('linux') == True:
    #        path =  "/.config/chromium/Default/History"
    #    elif sys.platform.startswith('darwin') == True:
    #        path = ''

    return path

def get_default_profile():
    firefox_path = get_path('firefox')
    home_dir = os.environ['HOME']
    firefox_path = home_dir + firefox_path; print(firefox_path)
    profiles = [i for i in os.listdir(firefox_path) if i.endswith('.default')]
    return firefox_path+profiles[0]

if __name__ == "__main__":
    DESC_PYFOX = "Extract information from firefox's internal database"
    parser = argparse.ArgumentParser(description=DESC_PYFOX)
    parser.add_argument('--bm', '-b', default="")
    parser.add_argument('--hist', '-y', default="")
    parser.add_argument('--profile', '-p', default=get_default_profile())
    args = parser.parse_args()

    try:
        sqlite_path = args.profile+'/places.sqlite'
        print(sqlite_path)
        if os.path.exists(sqlite_path):
            firefox_connection = sqlite3.connect(sqlite_path)

        #chrome_sqlite_path = '/home/thewhitetulip/.config/chromium/Default/History'
        #chrome_sqlite_path = get_path('chrome')
        #if os.path.exists(chrome_sqlite_path):
        #    chrome_connection = sqlite3.connect(chrome_sqlite_path)
    except Exception as error:
        print("_main_")
        print(str(error))
        exit(1)

    cursor = firefox_connection.cursor()
    #CHROME_CURSOR = chrome_connection.cursor()

    if args.bm is not '':
        bookmarks(cursor, pattern=args.bm)
    if args.hist is not '':
        print("From firefox")
        history(cursor, pattern=args.hist, src="firefox")
        #print("From chrome")
        #history(CHROME_CURSOR, src="chrome")

    cursor.close()
    #CHROME_CURSOR.close()
