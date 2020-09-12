"""
scrap_features: program that scraps several features from european car buyer Autoreflex
=============================================
.. moduleauthor:: Lilian MAREY <lilian.marey@ensae.fr>
"""
import csv
import numpy as np

from time import asctime, localtime, time, sleep
import signal

import urllib
from urllib import request
import bs4

##########################################
#Creation of a timer which will raises Exception Error if 
# a step of the program is too long

def handler(signum, frame):
    """Defines the overtime message
    """
    raise Exception("Too long execution time")
    
signal.signal(signal.SIGALRM, handler)

##########################################
#Scraping part :
# We consider 2 batches of information on a offer web page : 
# batch 1 composed of brand, model, segment, price (scraped in the same HTML tag).
# batch 2 is composed of mileage, year, location, fuel, gearbox, power.
# We will also scrap the name of the seller and the equipment

def text_processing_batch_1(scraped_text):
    """Extract from text features of batch 1

    Parameters:
    -----------
    scraped_text : str
        text scraped thanks to find_batch_1 function
       
    Return:
    --------
        batch : str list
            the list of all the features (brand, model, segment, price)
    """
    for i in range(len(scraped_text) - 7):
        brand_model_tag = scraped_text[i: i + 6]
        segment_tag = scraped_text[i: i + 7]
        price_tag = scraped_text[i: i + 4]

        if brand_model_tag == "marque":
            brand = ""
            
            j = i + 7

            while scraped_text[j] != ";":
                brand += scraped_text[j]

                j += 1
                
        elif brand_model_tag == "modele":
            model = ""
            
            j = i + 7
            
            while scraped_text[j] != ";":
                model += scraped_text[j]

                j += 1 
                
        if segment_tag == "segment":
            segment = ""
            
            j = i + 8
            
            while scraped_text[j] != ";":
                segment += scraped_text[j]

                j += 1
            
        if price_tag == "prix":
            price = ""
            
            j = i + 5
            
            while scraped_text[j] != "'":
                price += scraped_text[j]

                j += 1
    
    batch = [brand, model, segment, price]
                  
    return batch
            
def find_batch_1(page):
    """Scrapes and process brute web page text for finding batch 1 features

    Parameters:
    -----------
    page : web page (got by bs4.BeautifulSoup function)
        page on which I look for batch 1 information
    Return:
    --------
        batch_1 : str list
            the list of the found features (brand, model, segment, price)
    """
    digger_1 = page.findAll("script", {"type" : "text/javascript"})
    digger_2 = str(digger_1[4])
    batch_1 = text_processing_batch_1(digger_2)

    return batch_1

def text_processing_batch_2(scraped_text):
    """Extract from text features of batch 2 

    Parameters:
    -----------
    scraped_text : str
        text scraped thanks to find_batch_2 function
       
    Return:
    --------
        batch : str list
            the list of all the features (mileage, year, location, fuel, gearbox, power)
    """
    for i in range(len(scraped_text)-15):
            mileage_tag = scraped_text[i:i+9]
            year_tag = scraped_text[i:i+12]
            location_tag = scraped_text[i:i+15]
            fuel_tag = scraped_text[i:i+13]
            gearbox_tag = scraped_text[i:i+11]
            power_tag = scraped_text[i:i+12]

            if mileage_tag == "search-km":
                mileage = ""
            
                j = i + 15
            
                while scraped_text[j+1] != "K":
                    mileage += scraped_text[j]

                    j += 1
                    
            if year_tag == "search-annee":
                year = ""
            
                j = i + 18
            
                while scraped_text[j] != "<":
                    year += scraped_text[j]
                    j += 1  
                
            if location_tag == "search-location":
                location = ""

                j = i + 21

                while scraped_text[j] != "<":
                    location += scraped_text[j]

                    j += 1
                
            if fuel_tag == "search-engine":
                fuel = ""

                j = i + 19

                while scraped_text[j] != "<":
                    fuel += scraped_text[j]

                    j += 1
                
            if gearbox_tag == "search-gear":
                gearbox = ""

                j = i + 17

                while scraped_text[j] != "<":
                    gearbox += scraped_text[j]
                    
                    j += 1
            
            if power_tag == "search-power":
                power = ""

                j = i + 18

                while scraped_text[j] != "<":
                    power+=scraped_text[j]

                    j+=1
                    
    return [mileage, year, location, fuel, gearbox, power]
                
def find_batch_2(page):
    """Scrapes and process brute web page text for finding batch 2 features

    Parameters:
    -----------
    page : web page (got by bs4.BeautifulSoup function)
        page on which I look for batch 1 information

    Return:
    --------
        batch_2 : str list
            the list of the found features (brand, model, segment, price)
    """
    digger_1 = page.findAll("div", {"class" : "specs"})[0]
    digger_2 = digger_1.findAll("li", {"style" : "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"})
    batch_2 = text_processing_batch_2(str(digger_2))

    return batch_2

def find_equipments_feature(page):
    """Scrapes and process brute web page text for finding equipments feature

    Parameters:
    -----------
    page : web page (got by bs4.BeautifulSoup function)
        page on which I look for equipments information

    Return:
    --------
        equipments : str list
            the list of the equipments
    """
    try:
        page = str(page.findAll("ul", {"class" : "small-block-grid-1 large-block-grid-2"})[0])

    except:
        return []

    equipments = []
    
    for i in range(len(page) - 5):
        equipments_tag = page[i: i + 6]
        
        if equipments_tag == "title=":
            item = ""

            j = i + 7

            while page[j+1] != ">":
                item += page[j]
                
                j += 1
                
            equipments.append(item)
            
    return equipments

def find_all_features(URL):
    """Scrapes all the wanted feature from an offer web page

    Parameters:
    -----------
    URL : str
        the URL of the offer web page
    Return:
    --------
        features_list : str list
            the list of all the found features
    """    

    request_text = request.urlopen(URL).read()
    page = bs4.BeautifulSoup(request_text, "lxml")
    
    batch_1 = find_batch_1(page)
    batch_2 = find_batch_2(page)
    
    digger_1 = page.findAll("div", {"class" : "small-12 large-5 columns mg-bottom"})[0].findAll("h3")[0]
    digger_2 = str(digger_1)
    seller = digger_2[4: len(digger_2) - 5]
    
    equipments = find_equipments_feature(page)
    
    features_list = batch_1 + batch_2 + [seller] + [equipments]

    return features_list

def build_csv(url_list):
    """Build a csv file containing the different features for all the scraped ads 

    Parameters:
    -----------
    url_list : str list
        list of url of offer web pages
    """
    with open('Features/data.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(["Brand", "Model", "Segment", "Price", "Mileage", "Year", "Location", 
                     "Fuel", "Gearbox", "Power", "Seller", "Equipments", "url"])
    
        for i in range(len(url_list)):
            print("Offer processed number : ", i)
            
            try:
                signal.alarm(10)
                writer.writerow(find_all_features(url_list[i][:-1]) + [url_list[i]])
                signal.alarm(0)

            except:
                print(i, "Error, this Offer has been skipped")

##########################################
# Importing links and
# building csv file containing all the features

with open('Links/url_list_v0.txt', 'r') as f:
    url_list = f.readlines()

build_csv(url_list)