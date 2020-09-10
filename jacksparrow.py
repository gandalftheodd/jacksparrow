import requests
import re
import glob
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import html as dc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process, Pipe



name = ''
log = open('log.txt','w')
running = 0
rn = 0


def getLink(sng, conn): #function to search youtube for string sng and return a link to a youtube video
    otp = dict();
    rn = 0
    global running
    global log
    running = 1
    print('-----------------------------------')
    conn.send('-----------------------------------\n')
    print('Song: '+sng)
    conn.send('Working on: '+sng+'\n')
    song = sng.replace(" ","+")
    URL = 'https://www.youtube.com/results?search_query='+song
    page = requests.get(URL)
    rep = 0
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all("script")
    script = results[26]

    empt = script.string
    k = empt.encode('utf-8')
    y = str(k)
    x = y.replace('{',' ')
    x = x.replace('}',' ')

    ind = x.find('videoId')

    print("id ind")
    print(ind)
    idc = []
    title= x.find('title": "runs":')

    tend = x.find('accessibility',title)

    print('title: ')
    print(title)
    print('acc: ')
    print(tend)

    tit = []

    print(range(title,tend))
    for n in range((title+17),tend):
        tit.append(x[n])
    titl = ''.join(tit)
    titl = titl.lower()
    print(titl)
    for rep in range(11):
        idc.append(x[ind+10])
        ind+=1

    id = ''.join(idc)
    while rn == 0:

        if titl.find('video') != -1 or titl.find('live') != -1:

            print(id)
            print("coom")
            temp = title
            title = x.find('title": "runs":', tend)
            tend = x.find('accessibility',title)
            tit = []
            ind = x.find('videoId',title)
            print("id ind")
            print(ind)
            idc = []
            for rep in range(11):

                idc.append(x[ind+10])
                ind+=1
            id = ''.join(idc)
            for n in range((title+17),tend):
                tit.append(x[n])
            titl = ''.join(tit)

        else:
            print("doom")
            print(titl)
            rn = 1


    print('Video Id: ' + id)
    link = 'https://www.youtube.com/watch?v='+id
    print('Link: ' + link)
    conn.send('Link aquisition successful \n')
    #log.close()
    return link

def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

def capps(thing):  # fuction that capitalizes the first letter in every word of a string, defining a 'word' as a group of any character seperated by the beggining/end of the string or a space
    test = thing.split(' ')
    #print(test)
    fin = []
    hi = 0;
    for l in range(len(test)):
        if test[hi] == '':
            test.pop(hi)
        else: hi += 1
    #print(test)
    for j in range(len(test)):
        ind = 0;
        temp = []
        if ind == 0:
                temp.append(test[j][ind].upper())
                ind+=1
        for k in range(len(test[j])-ind):
                temp.append(test[j][ind])
                ind+=1
        fin.append(''.join(temp))
    return(' '.join(fin))

def download(sng,download_dir, conn):  # function that takes the link gotten from the getLink function and passes it through the youtubeToMp3 website
    global log
    splt = sng.split('by')
    sname = splt[0]
    #print('title1: '+sname)
    song_title = capps(''.join(sname))
    #print('title2:'+capps(''.join(sname)))
    if len(splt) > 1:
        artist = splt[1]
    print("artist: "+artist)
    artist_name = capps(''.join(artist))
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    frm = download_dir.replace('/',chr(92))
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": frm,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    global running
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://ytmp3.cc/en13/')
        enable_download_headless(driver, frm)
        inputElement = driver.find_element_by_id("input")
        inputElement.send_keys(getLink(sng, conn))
        python_button = driver.find_element_by_id("submit")
        python_button.click()
    except Exception as fukkk:
        print('exc starts here v')
        print(fukkk)
        print('exc ends here ^')
        if str(fukkk).find('Unable to locate element') != -1:
                messagebox.showinfo("Error", "It looks like youre not connected to the internet, please reconnect and try again")
                conn.send('Download failed')
        good = 1
    good = 0
    timeout = 30
    try:
        element_present = EC.presence_of_element_located((By.ID, 'ad'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        messagebox.showinfo("Error", "There was a problem downloading "+song_title+' by '+artist_name+", please try again")
        conn.send('Timeout Error \n')
        good = 1
    if good == 0:
        try:
            elem = driver.find_elements_by_xpath('//div[@id="buttons"]/a')
            html = driver.execute_script("return document.body.outerHTML;")
            tit = driver.find_element_by_id("title")
            title = tit.get_attribute('innerHTML')
            tittle = dc.unescape(title)
            fil = glob.glob(download_dir)
        except:
            print("something fucked up, try again")
            conn.send('Downlod Failed \n')
            messagebox.showinfo("Error", "There was a problem downloading "+song_title+' by '+artist_name+", please try again")
        troi = 0
        for h in range(len(fil)):
                if fil[h] == (download_dir+chr(92)+artist_name+' - '+song_title+".mp3"):
                    messagebox.showinfo("Duplication Error", "It looks like you already have "+song_title+' by '+artist_name+", so it will not be downloaded")
                    print('oops! it looks like you already have this song, lets try the next one')
                    h = len(fil)
                    troi = 1
                else:
                    h+=1
        tittle = tittle.replace(' |', '')
        tittle = tittle.replace(' :', '')
        tittle = tittle.replace(' &', '')
        if troi == 0:
            att = [x.get_attribute("href") for x in elem]
            print("'"+tittle+"'"+' download started')

            driver.get(att[0])
            conn.send('Downloading.....\n')
            src = 0
            files = glob.glob(str(download_dir+'/*.mp3'))
            while src >= 0:
                files = glob.glob(str(download_dir)+'/*.mp3')
                tmp = ' '.join(files)

                if(len(files) > 0):
                    if tmp.find(download_dir+chr(92)+tittle+'.mp3') != -1:
                        src = -1
                        print("'"+tittle+"'"+' download finished')
                        conn.send('Download complete\n')
                    else:
                        src += 1
                        if src == len(files):
                            src = 0
            os.rename(download_dir+chr(92)+tittle+'.mp3', download_dir+chr(92)+capps(''.join(artist))+' - '+capps(''.join(sname))+'.mp3')
    else:
        print('something went wrong, please try again')
    print('-----------------------------------')
    conn.send('-----------------------------------\n')
    running = 0





