# -*- coding: utf-8 -*-
"""
A useful web scraping tool. Used to scrape publication metadata
off the NovaScan website.
Created as researchware for Fiona 

Author: Matt Smith
"""
import os, sys
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def ctrlClick(driver, element):
    # hackish but must be done like this in python 3 apparently
    ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'Detail:scroller')))


def slash():
    if sys.platform == "win32": return '\\'
    elif sys.platform == "darwin": return '/'
    else: return '/'
    
    
# init    
curpath = os.path.abspath(os.path.dirname(sys.argv[0]))
chromedriverpath = curpath + slash() + "chromedriver.exe"    
subjQuery = input("What publications would you like to search for?\n" + 
                  "Multiple queries can be seperated with a ';'\n")
data = {}
queries = subjQuery.split(";")


for q in queries:
    # have browser load the page
    browser = webdriver.Chrome(executable_path=chromedriverpath)
    url = "https://gesner.novascotia.ca/novascan/DocumentQuery.faces"
    browser.get(url) #navigate to the page
    
    # enter search query into page
    subjBox = browser.find_element_by_id("DocQuery:subject")
    subjBox.send_keys(q)
    submitButton = browser.find_element_by_name("DocQuery:_id85")
    submitButton.click()
    
    # iterate through pages and page elements
    # for each publication, open in a new tab and store data
    pages = 0
    nextPage = True
    while nextPage:
        nextButton = browser.find_element_by_id("Summary:JSF_NEXT")
        nextPage = nextButton.is_enabled()
        for x in range(0, 20):  # 20 items per page
            elementName = ("Summary:DocInfoTbl:" + str(x+(pages*20)) + ":search")
            try:
                more = browser.find_element_by_name(elementName)
            except:
                break
            ctrlClick(browser, more)
            soup = BeautifulSoup(browser.execute_script("return document.body.innerHTML"),
                                 "html.parser")
            table = soup.find_all("tr")[4]
            isn = int(table.find_all("tr")[2].text.split("\n")[2])
            data[isn] = {}
            data[isn]["Downloadable"] = "No"
            records = table.find_all("tr")[3:]
            for record in records:
                key = record.text.split("\n")[1]
                val = record.text.split("\n")[2]
                if "download" in str(record):
                    key = "Downloadable"
                    val = "Yes"
                data[isn][key] = val
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        pages += 1
        nextButton.click()
    
    
    # close browser and export data to csv
    browser.close()
df = pd.DataFrame.from_dict(data, orient='index')
df.to_csv(curpath + slash() + 'publications.csv') # write dataframe to file

