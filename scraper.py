from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import os
import time
from datetime import date
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy import create_engine
import schedule




def job():
    #options (weniger Errors)
    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--disable-logging")
    #needed for running on heroku
    chrome_options.add_argument('--headless') #activate if i dont want the chrome window to pop up
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    



    ###Setup für ChromeDriver Pfad und laden von ChromeDriver

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = chrome_options)

    MAX_PAGES = 10 ## Wieviele Seiten sollen gescrapet werden 


    #URLS
    url = "https://www.ebay.at/sch/i.html?_from=R40&_nkw=analoge+kamera"
    url_kleinanzeigen = "https://www.ebay-kleinanzeigen.de/s-analoge-kamera/k0"
    url_sold = "https://www.ebay.at/sch/i.html?_from=R40&_nkw=analoge+kamera&rt=nc&LH_Sold=1&LH_Complete=1"

    #Setup ebay---------------------------------
    #Laden der website (url)
    driver.get(url)

    #Cookies wegklicken
    time.sleep(3)
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="gdpr-banner-decline"]'))).click()

    ebay_listings = []

    soup = BeautifulSoup(driver.page_source, "html.parser")

    print("starting to scrape ebay")

    for current_page in range(1, MAX_PAGES + 1):

        print('Processing page {0} of ebay'.format(current_page))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        item_list = soup.find_all('li', 's-item__pl-on-bottom')
        
        for listing in item_list:
            product_detail = {}

            #Namen der Listings und Link zum Produkt
            product_detail['product_title'] = listing.find('div', 's-item__title').text
            product_detail['product_url'] = listing.a['href']
            
            #Subtitles der Listings
            listing_subtitles = listing.find_all('div', 's-item__subtitle')
            product_detail['subtitle1'] = None
            product_detail['subtitle2'] = None
            if len(listing_subtitles) >= 2:
                product_detail['subtitle1'] = listing_subtitles[0].text
                product_detail['subtitle2'] = listing_subtitles[1].text
            elif len(listing_subtitles) == 1:
                product_detail['subtitle1'] = listing_subtitles[0].text

            #Price
            product_detail['price'] = listing.find('span', 's-item__price').text
            
            #Datum -> Zeit bis Ende Auktion
            listing_datum = listing.find_all('span', 's-item__time')
            product_detail['time_left'] = None
            product_detail['time_end'] = None
            if len(listing_datum) >= 2:
                product_detail['time_left']= listing_datum[0].text
                product_detail['time_end'] = listing_datum[1].text
            elif len(listing_datum) == 1:
                product_detail['time_left'] = listing_datum[0].text

            #KaufOptionen
            listing_sofortkauf = listing.find_all('span', 's-item__purchase-options-with-icon')
            if len(listing_sofortkauf) == 1:
                listing_sofortkauf_1 = listing_sofortkauf[0].text
            else:
                listing_sofortkauf_1 = None

            product_detail['kaufoptionen'] = listing_sofortkauf_1

            #Shipping Details
            try:
                product_detail['shipping_detail'] = listing.find('span', 's-item__logisticsCost').text
            except AttributeError:
                product_detail['shipping_detail'] = 'Not Available'
            

            ebay_listings.append(product_detail)

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@type="next"]'))).click()
        except (NoSuchElementException, TimeoutException):
            break
    
    print("done scraping ebay")


    #Setup sold ebay---------------------------------
    #Laden der website (url)
    driver.get(url_sold)

    #Cookies wegklicken
    time.sleep(3)
    #WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="gdpr-banner-decline"]'))).click()

    sold_listings = []

    soup_sold = BeautifulSoup(driver.page_source, "html.parser")

    print("starting to scrape ebay sold ")

    for current_page_sold in range(1, MAX_PAGES + 1):

        print('Processing page {0} of sold ebay'.format(current_page_sold))

        soup_sold = BeautifulSoup(driver.page_source, 'html.parser')
        item_list_sold = soup_sold.find_all('li', 's-item__pl-on-bottom')
        
        for listing in item_list_sold:
            product_detail = {}

            #Namen der Listings und Link zum Produkt
            product_detail['product_title'] = listing.find('div', 's-item__title').text
            product_detail['product_url'] = listing.a['href']
            
            #Subtitles der Listings
            listing_subtitles = listing.find_all('div', 's-item__subtitle')
            product_detail['subtitle1'] = None
            product_detail['subtitle2'] = None
            if len(listing_subtitles) >= 2:
                product_detail['subtitle1'] = listing_subtitles[0].text
                product_detail['subtitle2'] = listing_subtitles[1].text
            elif len(listing_subtitles) == 1:
                product_detail['subtitle1'] = listing_subtitles[0].text

            #Price
            product_detail['price'] = listing.find('span', 's-item__price').text
            
            #Datum -> Zeit bis Ende Auktion
            listing_datum = listing.find_all('span', 's-item__time')
            product_detail['time_left'] = None
            product_detail['time_end'] = None
            if len(listing_datum) >= 2:
                product_detail['time_left']= listing_datum[0].text
                product_detail['time_end'] = listing_datum[1].text
            elif len(listing_datum) == 1:
                product_detail['time_left'] = listing_datum[0].text

            #KaufOptionen
            listing_sofortkauf = listing.find_all('span', 's-item__purchase-options-with-icon')
            if len(listing_sofortkauf) == 1:
                listing_sofortkauf_1 = listing_sofortkauf[0].text
            else:
                listing_sofortkauf_1 = None

            product_detail['kaufoptionen'] = listing_sofortkauf_1

            #Shipping Details
            try:
                product_detail['shipping_detail'] = listing.find('span', 's-item__logisticsCost').text
            except AttributeError:
                product_detail['shipping_detail'] = 'Not Available'
            

            sold_listings.append(product_detail)

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@type="next"]'))).click()
        except (NoSuchElementException, TimeoutException):
            break
    
    print("done scraping sold ebay")

    #setup kleinanzeigen
    #Laden der website (url)
    driver.get(url_kleinanzeigen)

    #Cookies wegklicken
    time.sleep(3)
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="gdpr-banner-accept"]'))).click()
    kleinanzeigen_listings = []
    soup_ka = BeautifulSoup(driver.page_source, "html.parser")

    print("starting to scrape kleinanzeigen")


    for current_page_ka in range(1, MAX_PAGES + 1):

        print('Processing page {0} of kleinanzeigen'.format(current_page_ka))

        soup_ka = BeautifulSoup(driver.page_source, 'html.parser')
        item_list_ka = soup_ka.find_all('li', 'lazyload-item')
        
        for listing in item_list_ka:
            product_detail = {}

            #Namen der Listings und Link zum Produkt
            product_detail['product_title'] = listing.find('a', 'ellipsis').text
            product_detail['product_url'] = listing.a['href']
            
            #Subtitles der Listings
            listing_subtitles = listing.find_all('p', 'aditem-main--middle--description')
            product_detail['subtitle1'] = None
            product_detail['subtitle2'] = None
            if len(listing_subtitles) >= 2:
                product_detail['subtitle1'] = listing_subtitles[0].text
                product_detail['subtitle2'] = listing_subtitles[1].text
            elif len(listing_subtitles) == 1:
                product_detail['subtitle1'] = listing_subtitles[0].text

            #Price
            product_detail['price'] = listing.find('p', 'aditem-main--middle--price-shipping--price').text
            
            #Datum -> Zeit bis Ende Auktion
            listing_datum = listing.find_all('div', 'aditem-main--top--right')
            product_detail['time_left'] = None
            if len(listing_datum) >= 2:
                product_detail['time_left']= listing_datum[0].text
            elif len(listing_datum) == 1:
                product_detail['time_left'] = listing_datum[0].text


            #Shipping Details
            try:
                product_detail['shipping_detail'] = listing.find('span', 'tag-small').text
            except AttributeError:
                product_detail['shipping_detail'] = 'Not Available'
            

            kleinanzeigen_listings.append(product_detail)

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//*[@title="Nächste"]'))).click()
        except (NoSuchElementException, TimeoutException):
            print('Last page {0}'.format(current_page_ka))
            break 

    driver.quit()
    print("done scraping kleinanzeigen")



    #Alles in ein DataFrame
    df = pd.DataFrame(ebay_listings)
    df_2 = pd.DataFrame(kleinanzeigen_listings)
    df_3 = pd.DataFrame(sold_listings)


    #datum für die Datei name
    heutiges_datum = date.today()
    gestern = date.today() - timedelta(days=1)

    #uhrzeit für datei name
    now = datetime.now()
    current_time = now.strftime("%H.%M")


    df['time_left'] = df['time_left'].str.replace('Heute', str(heutiges_datum))
    df['time_left'] = df['time_left'].str.replace('Gestern', str(gestern))
    
    df_2['time_left'] = df_2['time_left'].str.replace('Heute', str(heutiges_datum))
    df_2['time_left'] = df_2['time_left'].str.replace('Gestern', str(gestern)) 

    df_3['time_left'] = df_3['time_left'].str.replace('Heute', str(heutiges_datum))
    df_3['time_left'] = df_3['time_left'].str.replace('Gestern', str(gestern)) 
    
    #item id + platform + date
    #df['item_id']=df["product_url"].str.split('?').str[1].str.split("&").str[0]
    df["platform"]="ebay"
    df["date"] = now



    #df_2['item_id']=df_2["product_url"].str.split('/').str[3]
    df_2["platform"]="kleinanzeigen"
    df_2["date"] = now

    #df_3
    df_3["platform"]="ebay_sold"
    df_3["date"] = now

    #Filter dataframes
    df = df[~df["product_title"].str.contains("Shop on eBay")]
    df_3 = df_3[~df_3["product_title"].str.contains("Shop on eBay")]

    #df = df.drop_duplicates(subset=['item_id'], keep=False)
    #df_2 = df_2.drop_duplicates(subset=['item_id'], keep=False)


    #Write Output to excel file
    #df.to_excel("D:/Webscraping/daten/" + "ebay_analog_spiegelreflexkamera_" + str(heutiges_datum) + "_" + str(current_time) + ".xlsx")
    #df_2.to_excel("D:/Webscraping/daten/" + "kleinanzeigen_analog_spiegelreflexkamera_" + str(heutiges_datum) + "_" + str(current_time) + ".xlsx")
    #df_3.to_excel("D:/Webscraping/daten/" + "kleinanzeigen_analog_spiegelreflexkamera_" + str(heutiges_datum) + "_" + str(current_time) + ".xlsx")

    #postgres connection
    postgres_connection_url = "XXX"

    engine = sqlalchemy.create_engine(postgres_connection_url)

    df.to_sql("listings", engine, if_exists = "append", index = False)

    df_2.to_sql("listings", engine, if_exists = "append", index = False)

    df_3.to_sql("listings", engine, if_exists = "append", index = False)





schedule.every(2).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(200)
