"""
scrap_features: program that scraps several features of european car buyer Autoreflex
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


#On considère 2 lots d'information sur les annonces : le lot 1 composé de marque, modele, segment, prix 
#(scrappés dans la même balise), le lot 2 composé de kilometrage, annee, lieu, carburant, boite, puissance.
#On recuperera aussi le nom du vendeur et les équipements

def trouve_1(s):
    
    """Traite le texte pour trouver les caractéristiques du lot 1"""
    
    for i in range(len(s)-7):
        
        m = s[i:i+6]
        se = s[i:i+7]
        p = s[i:i+4]

        if m == "marque":
            marque = ""
            
            j = i + 7
            
            while s[j] != ";":
                marque+=s[j]
                j+=1
                
        elif m == "modele":
            modele = ""
            
            j = i + 7
            
            while s[j] != ";":
                modele+=s[j]
                j+=1
                
        if se == "segment":
            segment = ""
            
            j = i + 8
            
            while s[j] != ";":
                segment+=s[j]
                j+=1
            
        if p == "prix":
            prix = ""
            
            j = i + 5
            
            while s[j] != "'":
                prix+=s[j]
                j+=1
                  
    return [marque, modele, segment, prix]
            
            
def trouve_variables_lot_1(page):
    
    a = page.findAll("script", {"type" : "text/javascript"})
    s = str(a[4])
    
    return trouve_1(s)

def trouve_2(s):
    
    """Traite le texte pour trouver les caractéristiques du lot 2"""
    
    for i in range(len(s)-15):
            
            km = s[i:i+9]
            an = s[i:i+12]
            li = s[i:i+15]
            en = s[i:i+13]
            ge = s[i:i+11]
            po = s[i:i+12]

            if km == "search-km":
                kilometrage = ""
            
                j = i + 15
            
                while s[j+1] != "K":
                    kilometrage+=s[j]
                    j+=1
                    
            if an == "search-annee":
                annee = ""
            
                j = i + 18
            
                while s[j] != "<":
                    annee+=s[j]
                    j+=1
                
            if li == "search-location":
                lieu = ""

                j = i + 21

                while s[j] != "<":
                    lieu+=s[j]
                    j+=1
                
            if en == "search-engine":
                carburant = ""

                j = i + 19

                while s[j] != "<":
                    carburant+=s[j]
                    j+=1

                
            if ge == "search-gear":
                boite = ""

                j = i + 17

                while s[j] != "<":
                    boite+=s[j]
                    j+=1
            
            if po == "search-power":
                puissance = ""

                j = i + 18

                while s[j] != "<":
                    puissance+=s[j]
                    j+=1
                    
    return [kilometrage, annee, lieu, carburant, boite, puissance]
                
    
                
def trouve_variables_lot_2(page):
    
    a = page.findAll("div", {"class" : "specs"})[0]
    
    return trouve_2(str(a.findAll("li", {"style" : "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"})))

def trouve_equipements(page):
    
    """Recupere la liste des équipements de la voiture"""
    
    try:
        s = str(page.findAll("ul", {"class" : "small-block-grid-1 large-block-grid-2"})[0])
    except:
        return []
    equipements = []
    
    for i in range(len(s)-5):
        eq = s[i:i+6]
        
        if eq == "title=":
            item = ""
            j = i + 7

            while s[j+1] != ">":
                item+=s[j]
                j+=1
                
            equipements.append(item)
            
    return equipements

def trouve_variables(URL):
    
    """Recupère toutes les caractéristiques de la voiture (lots 1 et 2, vendeur et equipements)"""
    
    request_text = request.urlopen(URL).read()
    page = bs4.BeautifulSoup(request_text, "lxml")
    
    lot_1 = trouve_variables_lot_1(page)
    lot_2 = trouve_variables_lot_2(page)
    
    s = page.findAll("div", {"class" : "small-12 large-5 columns mg-bottom"})[0].findAll("h3")[0]
    vendeur = str(s)
    
    equipements = trouve_equipements(page)
    
    return lot_1 + lot_2 + [vendeur[4:len(vendeur)-5]] + [equipements]

#Lecture du fichier des url obtenu précedemment
with open('/Users/lilianmarey/Desktop/Python/Reezocar/liste_url0.txt', 'r') as f:
    liste_url = f.readlines()

#Creation d'un timer pour éviter de passer du temps sur des annonces qui n'existent plus

def handler(signum, frame):
    
    """Ce timer déclenche une erreur si un programme s'exécute pendant trop longtemps"""
    
    raise Exception("end of time")
    
signal.signal(signal.SIGALRM, handler)

def consruit_fichier(liste_url):
    
    """Construit un fichier csv contenant les différentes variables pour toutes les annonces récupérées"""
    
    with open('/Users/lilianmarey/Desktop/Python/Reezocar/data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Marque", "Modèle", "Segment", "Prix", "Kilometrage", "Date de production", "Lieu", 
                     "Type de carburant", "Type de boîte de vitesse", "Puissance", "Vendeur", "Equipements", "url"])
    
        for i in range(len(liste_url)):
            print("Numéro de l'annonce traitée : ",i)
            
            try:
                signal.alarm(10)
                writer.writerow(trouve_variables(liste_url[i][:-1])+[liste_url[i]])
                signal.alarm(0)
            except:
                print(i,"except")

consruit_fichier(liste_url)