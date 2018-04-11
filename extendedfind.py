#!/usr/bin/python
# Python file to monitor pastebin for pastes containing the passed regex

import sys
import time
from urllib.request import urlopen
import re

# User-defined variables
time_between = 65  # Seconds between iterations (not including time used to fetch pages - setting below 5s may cause a pastebin IP block, too high may miss pastes)
error_on_cl_args = "Please provide a single regex search via the command line"  # Error to display if improper command line arguments are provided

# Check for command line argument (a single regex)
search_term = "EXTINF"

iterater = 1
mypasteliset = []
while (1):
    counter = 0
    previousitems = mypasteliset[:]
    mypasteliset = []
    print("Scanning pastebin - iteration " + str(iterater) + "...")

    # Open the recently posted pastes page
    try:
        url = urlopen("http://pastebin.com/archive")
        html = url.read().decode("utf-8")
        url.close()
        html_lines = html.split("\n")
        for line in html_lines:
            if re.search(r'<td><img src=\"/i/t.gif\"  class=\"i_p0\" alt=\"\" /><a href=\"/[0-9a-zA-Z]{8}">.*</a></td>',line):
                link_id = line[61:69]
                mypasteliset.append(link_id)

        for eachitem in mypasteliset:
            if eachitem in previousitems :
                print("Skipping " + eachitem)
            if eachitem not in previousitems:
                newurl = "http://pastebin.com/raw.php?i=" + eachitem
                url_2 = urlopen(newurl)
                try:
                    raw_text = url_2.read().decode("utf-8")
                except Exception as e:
                    print("Inner exception : while reading pastebin")
                    print(e)
                    print("Going for next")
                    continue
                url_2.close()
                print("Checking : " + newurl)
                # if search_term in raw_text:
                if re.search(r'' + search_term, raw_text):
                    try:
                        f = open("pastes/"+eachitem+".m3u", "w+")
                        f.write(raw_text)
                        f.close()
                    except Exception as e:
                        print("Inner exception : While file write")
                        print(e)
                        print("Going for next")
                        continue
                    print("---------------------------------------------------")
                    print("FOUND " + search_term + " in http://pastebin.com/raw.php?i=" + link_id)
                    print("---------------------------------------------------")

                counter += 1
    except(IOError):
        print("Network error - are you connected?")
    except Exception as e:
        print("Fatal error! Exiting.")
        print(e)
        exit()
    iterater += 1
    print("Sleeping " + str(time_between) + " sec(s)")
    time.sleep(time_between)
