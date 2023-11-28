# -*- coding: utf-8 -*-
from enum import auto
from lib2to3.pgen2 import driver
from tkinter import Button
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyautogui import hotkey
import pyautogui
import time
import os
import glob
import subprocess
import re
from selenium import webdriver
from time import sleep

import tkinter as tk
from tkinter import ttk 
from tkinter.filedialog import askdirectory
from tkinter import filedialog as fd
from time import sleep 
# from tqdm import tqdm

try :
    os.remove('path.txt')
except:
    print()

# create the root window
root = tk.Tk()
root.title('Unlock Zebra Device Tool')
root.resizable(False, False)
root.geometry('500x200')
var = tk.StringVar()

def select_dir():
    path = askdirectory(title ='Select your folder')
    # path = path.replace('/','\\')
    print("Path:"+path)
    var.set(path)
    with open('path.txt', 'w') as f:
        f.write(path)

def close_window():
    root.destroy()

devices=[]
adb_devices= subprocess.check_output(["adb", "devices"])
for i in adb_devices.split(b'\tdevices'):
    for ii in i.split(b'\n'):
        if ii !=b"" and ii not in b"List of devices attache":
            x=ii.decode("utf-8").split('\t')
            devices.append(x)
# print("devices:",devices)
devices_number=len(devices)-1

def show():
    devices_id=[]
    devices_snt=[] #serialno
    devices_sn={}

    def chechmode():
        check =input('Please comfirm all devices have entered fastboot mode [y/n] ...')
        if check !='y':
            chechmode()
    
    # devicesid= subprocess.check_output(["adb", "devices"])
    # devicesid=str(devicesid.decode())
    # print("devicesid : ",devicesid)
    for i in range(1,devices_number+1):
        # print("devices : ",devices[i].split("\t")[0])
        devices_id.append(devices[i].split("\t")[0])
    print("id:"+devices_id[0])

    for i in devices_id:
        try:
            os.system(f'adb -s {i} reboot bootloader')
            serialno=subprocess.check_output(["fastboot","-s",f'{i}',"getvar","msmserialno"], stderr=subprocess.STDOUT)
            print(serialno)
            serialno=serialno.decode().replace(":","")
            print(serialno)
            devices_snt.append(serialno[43:52].replace('\n',''))
        except:
            devices_id.remove(i)
    print("devices serial number :",devices_snt)


        


    for i in range(len(devices_id)):
        temp = {f'{devices_id[i]}':f'{devices_snt[i]}'}
        devices_sn.update(temp)
    print("devices serial number :",devices_sn)

    for i in devices_id:
        lock=subprocess.check_output(["fastboot","-s",f'{i}',"getvar","unlocked"], stderr=subprocess.STDOUT)
        lock=lock.decode().replace(":","")
        if(lock[9:12]=="yes"):
            os.system(f'fastboot -s {i} oem lock_all')
            pyautogui.sleep(80)
            os.system(f'adb -s {i} reboot bootloader')
    chechmode()

        
           
    with open('path.txt', 'r') as f:
        path = f.read()        
    os.system(f'gnome-terminal -- google-chrome --remote-debugging-port=9222 --user-data-dir="{path}"')
    count = 0
    # WEBDRIVER_PATH = "/usr/bin/chromedriver"
    # options = Options()
    # driver = webdriver.Chrome() 
    options=webdriver.ChromeOptions()
    service = Service('/usr/bin/chromedriver')
    service.start()
    options.add_argument('--headless')
    # url = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
    # session_id = driver.session_id  
    # options.headless = True
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # browser = webdriver.Chrome(WEBDRIVER_PATH,options=options)
    browser=webdriver.Chrome(service=service, options=options)
    # browser = webdriver.Chrome()
    for i in devices_id:
        count = count+1

        # url = 'https://jira.zebra.com/secure/Dashboard.jspa'
        # browser.get(url)
        # print(browser.title)
        # pyautogui.sleep(3)

        url = 'https://jira.zebra.com/secure/CreateIssue!default.jspa'
        browser.get(url)
        print(browser.title)
        pyautogui.sleep(3)

        button = browser.find_element(By.ID, 'issue-create-submit')
        button.click()
        summary = browser.find_element(By.NAME, 'summary')
        summary.send_keys(f'fbkey {i} {devices_sn[i]} 100')

        pyautogui.sleep(10)

        create = browser.find_element(By.NAME, 'Create')
        create.click()

        pyautogui.sleep(5)

        if(devices_number>count):
            pyautogui.hotkey('ctrl','t',interval=0.1)
        print('count:',count)
        if count==devices_number:
            break
        else:
            browser.switch_to.window(browser.window_handles[count])
        # count = count+1

    #clear .bin file
    with open('path.txt', 'r') as f:
        path = f.read()
        # path.replace('\',\'/')
    # files = glob.glob('D:/adb2/image/**/*.bin', recursive=True)
    files = glob.glob(f'{path}/**/*.bin', recursive=True)
    print('path:',f'{path}/**/*.bin')
    print("file:",files)
    keyword = 'otp'
    for f in files:
        print('f:',f)
        # os.remove(f)
        if keyword in f:
            print("remove file : ",f)
            os.system(f'rm {f}')
    print("clear done")

    #download .bin file
    print('Number of devices :',count)
    for i in range(count):
        page=count-i-1
        if i>count:
            count==0
        browser.switch_to.window(browser.window_handles[page])
        pyautogui.sleep(30)
        while 1:
            try:
                download = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="attachment_thumbnails"]/li/div/a'))) # 顯性等待
                time.sleep(3)
                download.click() # 偵測到文件產出可以下載就點擊下載
                print ('可以下載!')
                time.sleep(5)
                browser.close()
                break 
            except:
                print("還不能下載! 重新整理!")
                browser.refresh() # 重整頁面
        print('OK')
        



    #unlock devices
    for i in devices_id:
        print('Start')
        print(f'fastboot -s {i} oem allow_unlock')
        os.system(f'fastboot -s {i} oem allow_unlock')
        pyautogui.sleep(10)
        # os.system('cd //d D:\\adb2\\image')
        os.chdir(path)
        pyautogui.sleep(5)

        file_list =  os.listdir(path)
        # output = subprocess.check_output(command, shell=True).decode('utf-8')
        # file_list = output.splitlines()
        for j in file_list:
            if devices_sn[i] in j:
                print(f'fastboot -s {i} flash otp {j}')
                os.system(f'fastboot -s {i} flash otp {j}')
        # print(f'fastboot -s {i} flash otp otp_{devices_sn[i]}_default.bin')
        # os.system(f'fastboot -s {i} flash otp otp_{devices_sn[i]}_default.bin')
        pyautogui.sleep(10)
        print(f'fastboot -s {i} oem unlock_all')
        os.system(f'fastboot -s {i} oem unlock_all')
        print('end')
        pyautogui.sleep(10)

    close_window()
    # print("browser.close")
    # browser.close()
    # browser.quit()
    # hotkey('Ctrl','w')
    # pyautogui.hotkey('ctrl','w',interval=0.1)
 
    


# open button
start_button = tk.Button(
    root,
    text = "Start",
    width=5,
    # font = ('Arial',9),
    command=show)

close_button = tk.Button(
    text = "Quit",
    width=5,
    # font = ('Arial',9),
    command = close_window)


e_path = tk.Entry(root,textvariable=var,width=24)
e_path.place(x=50,y=50)
b_select = tk.Button(root,text='select folder',command=select_dir,width=14,height=1)
b_select.place(x=280,y=48)
start_button.pack(expand=True)
start_button.place(x=165,y=150)
close_button.pack(expand=True)
close_button.place(x=235,y=150)
n =tk.Label(root,text=f'The number of connected devices : {devices_number}')
n.pack()
n.place(x=50,y=100)

root.mainloop()
