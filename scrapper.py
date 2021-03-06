# -*- coding: utf-8 -*-
"""Practica 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S6qP2qpjWGqMTjfWoKGv1PLa9nyZj4Xe

# **Càrrega de llibreries i definició de funcions**
"""

import re
import csv
import time
import random
import requests
from collections import UserList
from bs4 import BeautifulSoup as bs

# Declaració de variables
headers = {
  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
  "accept-encoding": "gzip, deflate, br",
  "accept-language": "en-US,en;q=0.9",
  "cache-control": "max-age=0",
  "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
  "sec-ch-ua-mobile": "?0",
  "sec-fetch-dest": "document",
  "sec-fetch-mode": "navigate",
  "sec-fetch-site": "same-origin",
  "sec-fetch-user": "?1",
  "upgrade-insecure-requests": "1",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
}

# Funcions i classes
def scrape(url,subQuery=""):
  """
  Funció per executar un request a una web

  :param url: URL base per fer el request
  :param subQuery: extensio de la url base per fer la request
  :return: HTTPS request de la crida a la url
  """
  res = requests.get(url+subQuery, headers = headers)
  delay = random.randint(40,80)
  time.sleep(delay)
  print('Request to :'+url+subQuery+' done in :',delay,' seconds.')

  return(res)

def get_pages_for_location(url, web1):
  """
  Funció per trobar la URL de totes les pàgines per una localitat determinada

  :param url: URL arrel per fer el request e.g. https://www.idealista.com
  :param url2: URL extensió per fer el request e.g. /venta-viviendas/igualada-barcelona
  :return: Llista amb totes les pàgines de pisos per la localitat indicada en base_url
  """
  x=1 #num pagina
  tmp_pages = []
  base_url = url+web1

  while True:
    int_url = ""
    int_url = f"{base_url}pagina-{x}.htm"

    r = scrape(int_url)
    soup = bs(r.text, "lxml")

    current_page = int(soup.find("div", {"class": "pagination"}).find("li", {"class":"selected"}).text)
    
    latest_page = [int(elem.text) for elem in soup.find("div", {"class": "pagination"}).find_all("a", {"class":""})][-1]
    
    if x==1:
        tmp_pages = [[int_url] + [url+elem["href"] for elem in soup.find("div", {"class": "pagination"}).find_all("a", {"class":""})]]
    elif current_page >= latest_page:
        tmp_pages.append([int_url])
        break
    elif x > current_page:
        break
    elif x == current_page:
        tmp_list = [url+elem["href"] for elem in soup.find("div", {"class": "pagination"}).find_all("a", {"class":""})]
        tmp_list = tmp_list[1:]
        tmp_pages.append(tmp_list)
    
    x = x + ((latest_page-current_page))
    
    time.sleep(random.randint(20,30)*random.random())

    agg_pages = sum(tmp_pages, [])
    return_value = list(dict.fromkeys(agg_pages))
  return(return_value)
  
def scrape_houses(web_html):
  """
  Funció per treure les extensions de tots els pisos d'una pàgina concreta

  :param web_html: contingut parsejat en html d'una pàgina concreta d'idealista
  :return: llista amb totes les extensions dels pisos d'una pàgina concreta
  """
  res_pags = list(web_html.find_all("article", {"class": "item"}))
  
  res_pags = res_pags[1]
  all_pags = list(web_html.find_all("a",{"class": "item-link"}))
  subweb = [('https://www.idealista.com'+elem['href']) for elem in all_pags]

  return subweb

def parse_house(url):
  """
  Funció per parsejar les dades d'un pis concret

  :param url: URL base d'un pis concret per fer el request
  :return: llista amb els resultats del scraping del pis
  """
  #request de la pàgina del pis
  r = scrape(url)

  #Parse de la resposta HTTPs
  soup = bs(r.text, 'lxml')

  #Capturar títol del anunci
  title = soup.find("span", {"class": "main-info__title-main"}).text.strip()

  #capturar localització del anunci
  location = soup.find("span", {"class": "main-info__title-minor"}).text.strip().split(",")
  area = location[0].strip()
  try:
    city = location[1].strip()
  except:
    city = location[0].strip()

  #capturar preu
  price = int(soup.find("span", {"class": "info-data-price"}).find("span").text.replace(".", "").strip())

  #capturar preu anterior abans del descompte si existeix
  try:
    previous_price = int(soup.find("span", {"class": "pricedown"}).find("span").text.replace(".", "").replace("€", "").strip())
  except:
    previous_price = price

  #capturar característiques generals
  property_feature_one = soup.find("section", {"id": "details"}).find("div", {"class":"details-property-feature-one"})
  property_feature_two = soup.find("section", {"id": "details"}).find("div", {"class":"details-property-feature-two"})
  property_feature_three = soup.find("section", {"id": "details"}).find("div", {"class":"details-property-feature-three"})

  basic_features = [feat.text.strip() for feat in property_feature_one.find_all("li")]
  extra_features = [feat.text.strip().replace("\n","") for feat in property_feature_two.find_all("li")]

  #capturar etiqueta energètica si existeix
  try: 
    energy_label = [title["title"] for title in [label.find_all("span")[1] for label in [feat for feat in property_feature_two.find_all("li")] if label.find_all("span") != []]]
  except:
    energy_label = "No etiqueta energética"

  #Crear output
  output = {
    "titol": title,
    "zona": area,
    "ciutat": city,
    "preu": price,
    "preu_anterior": previous_price,
    "c_basiques": basic_features,
    "c_extres": extra_features,
    "etiqueta_energetica": energy_label
    }
  
  return(output)
class Pisos:
  def __init__(self):
    self.pisos = []
    self.numPisos = 0

  def afegeixPis(self, pis):
    if pis not in self.pisos:
      if pis.getId() == -1:
        pis.setId(self.numPisos)
      self.numPisos += 1
      self.pisos.append(pis)

class Pis:
  def __init__(self, url):
    self.html = parse_house(url)
    self.props = {'id': -1,'Construidos(m)':-1,'Útiles(m)':-1,'Habitaciones':-1,'Baños':-1,'Terraza':'NA','Balcón':'NA','Estado':'NA',
                  'Orientación':'NA', 'Garaje': 'NA', 'Construido':-2022,'Calefacción':'NA','Planta':-1,'Ascensor':'NA',
                  'Aire acondicionado':'NA','Zones verdes o Jardí':'NA','ciutat': 'NA', 'zona':'NA', 'etiqueta_energetica': 'NA','preu': -1,'preu_anterior': -1,'titol': 'NA'} #penso que falta també la zona juntament amb la ciutat
  def setId(self, num):
    self.props['id'] = num
  def getId(self):
    return self.props['id']

#Parser general amb crida a les variables
def parsePis(pis):
  #característiques bàsiques
  parseConst(pis)
  parseHab(pis)
  parseBany(pis)
  parseTerrassa(pis)
  parseBalco(pis)
  parseEstat(pis)
  parseOrientacio(pis)
  parseGaraje(pis)
  parseAnyCons(pis) #new
  parseCalef(pis) #new
  parsePlanta(pis) #new
  parseAscensor(pis)

  #preu, títol i ciutat
  parseCiutat(pis) #new
  parsePreu(pis) #new
  parseTitol(pis) #new

  #característiques extres
  parseAireCond(pis)#new
  parseJardi(pis)#new
  parseEtiqueta(pis)#new

#parsers diccionari
def parseConst(pis_prop):
  const = re.compile('[0-9]+ m² construidos+')
  util = re.compile('[0-9]+ m² construidos,\s[0-9]+ m² útiles')
  for query in pis_prop.html['c_basiques']:
    if util.match(query):
      const, util = query.split(",")
      c_val, c_name = const.split(" m²")
      u_val, u_name = util.split(" m²")
      pis_prop.props['Construidos(m)'] = int(c_val)
      pis_prop.props['Útiles(m)'] = int(u_val)
      return
    elif const.match(query):
      parsed = query.split(" m²")
      pis_prop.props['Construidos(m)'] = int(parsed[0])
      pis_prop.props['Útiles(m)'] = int(parsed[0])
      return
  
def parseHab(pis_prop):
  pattern = re.compile('[0-9]+ habitaciones')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      parsed = query.split(" ")
      pis_prop.props['Habitaciones'] = int(parsed[0])

def parseBany(pis_prop):
  pattern = re.compile('[0-9]+ baño') #busquem baño i no baños per capturar el número encara que tingui 1 bany
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      parsed = query.split(" ")
      pis_prop.props['Baños'] = int(parsed[0])

def parseBalco(pis_prop):
  pattern = re.compile('(?i)balc.*') 
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      pis_prop.props['Balcón'] = 'SI'
      break #afegir break si el troba perque no segueixi buscant
    else:
      pis_prop.props['Balcón'] = 'NO' #els NO són al no existir l'element. Podem assumir que si no es posa a les característiques no en té?

def parseTerrassa(pis_prop):
  pattern = re.compile('Terraza')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      pis_prop.props['Terraza'] = 'SI'
      break #afegir break si el troba perque no segueixi buscant
    else:
      pis_prop.props['Terraza'] = 'NO' #afegir NO en cas contrari

def parseOrientacio(pis_prop):
  pattern = re.compile('Orientación +')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      parsed = query.split(" ")
      pis_prop.props['Orientación'] = parsed[1]

def parseAscensor(pis_prop):
  pattern = re.compile('^Con [a-zA-Z]+$')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      pis_prop.props['Ascensor'] = 'SI'
      break #afegir break si el troba perque no segueixi buscant
    else:
      pis_prop.props['Ascensor'] = 'NO'

def parseGaraje(pis_prop):
  pattern = re.compile('^.*garaje.*$')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      pis_prop.props['Garaje'] = 'SI'
      break #afegir break si el troba perque no segueixi buscant
    else:
      pis_prop.props['Garaje'] = 'NO'

def parseEstat(pis_prop):
  sm_be = re.compile('.*mano/buen estado$') #no que comenci amb sino que tingui mano/buen estado al final (abans amb ^)
  sm_re = re.compile('.*mano/para reformar$')
  nou = re.compile('Promoción de obra nueva')
  for query in pis_prop.html['c_basiques']:
    if sm_be.match(query):
      pis_prop.props['Estado'] = 'Buen estado'
      return
    if sm_re.match(query):
      pis_prop.props['Estado'] = 'Por reformar'
      return
    if nou.match(query):
      pis_prop.props['Estado'] = 'Nuevo'
      return

def parseAnyCons(pis_prop):
  pattern = re.compile('Construido en')
  year_pattern = re.compile("(?<=Construido en ).*")
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      year_found = year_pattern.search(query)
      pis_prop.props['Construido'] = int(year_found.group(0))

def parsePlanta(pis_prop):
  pattern = re.compile('^Planta')
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      parsed = query.split(" ")[1].replace("ª", "")
      pis_prop.props['Planta'] = int(parsed[0])

def parseCalef(pis_prop): #versió simplificada de calefacció: nomes mira si en té o no i no de quin tipus
  pattern = re.compile("^Calef")
  for query in pis_prop.html['c_basiques']:
    if pattern.match(query):
      pis_prop.props['Calefacción'] = "SI"
      break
    else:
      pis_prop.props['Calefacción'] = "NO"

def parseCiutat(pis_prop):
  pis_prop.props['ciutat'] = pis_prop.html["ciutat"]
  pis_prop.props['zona'] = pis_prop.html["zona"]
    
def parseTitol(pis_prop):
  pis_prop.props['titol'] = pis_prop.html["titol"]
    
def parsePreu(pis_prop):
  pis_prop.props['preu'] = pis_prop.html["preu"]
  pis_prop.props['preu_anterior'] = pis_prop.html["preu_anterior"]

def parseAireCond(pis_prop):
  pattern = re.compile("^Aire")
  for query in pis_prop.html['c_extres']:
    if pattern.match(query):
      pis_prop.props['Aire acondicionado'] = "SI"
      break
    else:
      pis_prop.props['Aire acondicionado'] = "NO"
            
def parseJardi(pis_prop):
  p_jardi = re.compile("(?i)jard.*") #ignorar mayus i accent
  p_verdes = re.compile("(?i).*verdes")
  for query in pis_prop.html['c_extres']:
    if p_jardi.match(query):
      parsed = query.split()
      pis_prop.props['Zones verdes o Jardí'] = parsed[0]
      break
    elif p_verdes.match(query):
      pis_prop.props['Zones verdes o Jardí'] = query
      break
    else:
      pis_prop.props['Zones verdes o Jardí'] = "NO"

def parseEtiqueta(pis_prop):
  if pis_prop.html["etiqueta_energetica"][0].lower() == '':
    pis_prop.props['etiqueta_energetica'] = "NO"
  elif len(pis_prop.html["etiqueta_energetica"]) > 1:
    if (pis_prop.html["etiqueta_energetica"][0].lower()) >= (pis_prop.html["etiqueta_energetica"][1].lower()):
      pis_prop.props['etiqueta_energetica'] = pis_prop.html["etiqueta_energetica"][0].lower()
    else:
      pis_prop.props['etiqueta_energetica'] = pis_prop.html["etiqueta_energetica"][1].lower()    
  else:
    pis_prop.props['etiqueta_energetica'] = pis_prop.html["etiqueta_energetica"][0].lower()

url = "https://www.idealista.com"
web1 = "/venta-viviendas/igualada-barcelona/"
pisos = Pisos()

total_pages = get_pages_for_location(url=url, web1=web1)


for page_url in total_pages:
    
    print('Doing ' + page_url)
    
    r = scrape(page_url)

    web_html = bs(r.text, 'lxml')

    #Captura de totes les url dels pisos de la pàgina actual
    house_list = scrape_houses(web_html)
    
    #Per cada pis de la pàgina actual
    for pis_url in house_list:
        
        print('Doing ' + pis_url)
        
        #Captura les dades del pis
        pis_tmp = Pis(pis_url)
        
        #Mapeja els valors en brut del pis amb la taula pre-definida
        parsePis(pis_tmp)
        
        #afegeix pis a la llista
        pisos.afegeixPis(pis_tmp)
        
pisos_data_list = [pis.props for pis in pisos.pisos]


keys = pisos_data_list[0].keys()

#with open('C:/Users/i0386388/@Documents/caracteristiques_pisos_igualada.csv', 'w', newline='') as output_file:
#    dict_writer = csv.DictWriter(output_file, keys)
#    dict_writer.writeheader()
#    dict_writer.writerows(pisos_data_list)