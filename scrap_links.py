"""
scrap_links: program that scraps all the links of car offers from the website Autoreflex
=============================================
.. moduleauthor:: Lilian MAREY <lilian.marey@ensae.fr>
"""
import numpy as np
import matplotlib.pyplot as plt

from time import asctime, localtime

import urllib
from urllib import request
import bs4

##########################################
# Usefull functions

def links_by_region_page(region_number, page_number):
    """Scraps all the offer links present in a singular page recognized by its region and its number

    Parameters:
    -----------
    region_number : int (from 1 to 29)
        number associated with the wanted region

    page_number : int
        number associated with the wanted page
       
    Return:
    --------
        url_list : str list
            the list of all the found links
    """

    region_number, page_number
    url_list = []

    # Building the URL from the two parameters
    URL = "http://www.autoreflex.com/0.0.-1.-1.-1.0.999999.1900.999999.-1." + str(region_number) + ".0." + str(page_number) + '?fulltext=&amp'
    
    page = request.urlopen(URL).read()
    soup = bs4.BeautifulSoup(page, 'lxml')
    digger_0 = soup.findAll('table', {'class' : 'listing line'})

    if len(digger_0) == 0:
        pass
        
    else:
        digger_1 = [i.findAll('tr') for i in digger_0][0]
    
        for k in range(1,len(digger_1)):
            href = (digger_1[k].findAll('td', {'valign' : 'top'}))[0].findAll('a')[0].get('href')
            
            url_list.append('http://www.autoreflex.com/' + href)
            
    return url_list
    
def links_by_region(region_number):
    """Scraps all the offer links present pages of a specific region

    Parameters:
    -----------
    region_number : int (from 1 to 29)
        number associated with the wanted region
       
    Return:
    --------
        url_list : str list
            the list of all the found links
    """
    page_number = 1
    url_list = []
    
    #Here is the main issue : offers order is shook when refreshing pages, 
    # so I tried to cover as many offers that I can in reasonable time
    while  page_number < 500 :
        L1 = links_by_region_page(region_number,page_number)
        L2 = links_by_region_page(region_number,page_number)

        if L1 == []: #If any offer is scraped, it means that last page has been reached
            break
        
        else:
            L = list(set(L1 + L2))
            url_list += L #Some offers might be in both lists

            print(str(len(L))+' new links added')

            page_number += 1

    url_list = list(set(url_list)) #Last check-up
        
    return url_list

        
def links():
    """Scraps all the offer links of all the regions
       
    Return:
    --------
        url_list : str list
            the list of all the found links
    """
    url_list = []
    
    for region_number in range(1,30):

        print('Region number : ' + str(region_number) + '/29')

        links = links_by_region(region_number)
        url_list.append(links)

    return url_list

##########################################
# Building text file containing all the links

url_list = links()  

with open('/Links/url_list.txt', 'w') as f:

    for item in list(set(url_list)):
        f.write('%s\n' % item)