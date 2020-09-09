from proxies import proxies
from user_agent import user_agent
import requests as rq
import urllib.parse as parse
import re
import json
import time
import tkinter as tk
from tkinter import filedialog
import os
import datetime
from tkinter.ttk import *
import threading
import pandas as pd
# import pkg_resources.py2_warn
# import numpy 
# import dateutil
# import pytz
from sys import exit
import re


#global variables.
rate = 0
#base page number 
base_page = 2

#header 
header = {
"Content-Type": "text/html;charset=UTF-8",
"Accept-Language": "en-US,en;q=0.9",
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Accept-Encoding":"gzip, deflate, br",
"DNT":"1",
"cache-control": "no-cache",
"Upgrade-Insecure-Requests": "1",
"Referer": "https://www.google.com",
"User-Agent":'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}

#count number of error request
count = 0
load = 0
token_ = None


start_time = time.time()
#base url
base_url =  "https://www.aliexpress.com/wholesale?catid=0&SearchText="
# #next_page url
next_url = None
#proxy class
proxy = None
#agent class
agent = None
bar = None
window = None
display = None
# makefile(prod,path)
#thread lock
lock = None
file = None
f_path = None 
thread_list = []
comp_label = None



"""
do_sort function where the sorting part is done.
i use pandas and sort by sold,rating, reviews and likes field

"""
def sort():
    global f_path, file, comp_label
    comp_label.config(text = "start sorting")#use this line to print label on gui window
    #main sorting logic is going here
    regex = r"US \$([\d\S]*)"
    df = pd.read_csv(f_path)
    df['Score']=""
    sold_ = None
    review_ = None
    likes_ = None
    price = None
    Shipping = None
    feedback = None
    for n in range( df.shape[0] ):
    #get the nth line
        linea = df.iloc[n]
        try:
            price = float(re.findall(regex,linea.Price)[0])
        except:
            price = 0
        try:
            Shipping = float(re.findall(regex,linea.Shipping_Charges)[0])
        except:
            Shipping = 0
        try:
            feedback = float(linea.Positive_Feedback[:-1])
        except:
            feedback = 0
        try:
            sold_ = float(linea.Sold)
        except:
            sold_ = 0
        try:
            review_ = float(linea.Reviews)
        except:
            review_ = 0
        try:
            likes_ = float(linea.Likes)
        except:
            likes_ = 0


        df.at[n, "Score"]= ((price*0.05) + (sold_* 0.2) + (Shipping*0.05) + (likes_* 0.2) + (feedback*0.2) + (review_*0.1) )
    sort_data = df.sort_values(by=["Score"], ascending=False)
    sort_data.to_csv(f_path, index=False)
    # data = pd.read_csv(f_path)
    # sort_data = data.sort_values(["Sold", "Rating", "Reviews", "Likes"], ascending=False)
    # sort_data.to_csv(f_path, index=False)

    comp_label.config(text = "Scraping and Sorting Complete")#use this line to print label on gui window

def do_sort():
    global f_path, file, comp_label
    file.close()#dont change the line
    comp_label.config(text = "start sorting")#use this line to print label on gui window
    
    #main sorting logic is going here
    regex = r"US \$([\d\S]*)"
    df = pd.read_csv(f_path)
    df['Score']=""
    sold_ = None
    review_ = None
    likes_ = None
    price = None
    Shipping = None
    feedback = None
    
    for n in range( df.shape[0] ):
    #get the nth line
        linea = df.iloc[n]
        try:
        	price = float(re.findall(regex,linea.Price)[0])
        except:
        	price = 0
        try:
            Shipping = float(re.findall(regex,linea.Shipping_Charges)[0])
        except:
            Shipping = 0
        try:
        	feedback = float(linea.Positive_Feedback[:-1])
        except:
        	feedback = 0
        try:
        	sold_ = float(linea.Sold)
        except:
        	sold_ = 0
        try:
        	review_ = float(linea.Reviews)
        except:
        	review_ = 0
        try:
        	likes_ = float(linea.Likes)
        except:
        	likes_ = 0


        df.at[n, "Score"]= ((price*0.05) + (sold_* 0.2) + (Shipping*0.05) + (likes_* 0.2) + (feedback*0.2) + (review_*0.1) )
    sort_data = df.sort_values(by=["Score"], ascending=False)
    sort_data.to_csv(f_path, index=False)
    # data = pd.read_csv(f_path)
    # sort_data = data.sort_values(["Sold", "Rating", "Reviews", "Likes"], ascending=False)
    # sort_data.to_csv(f_path, index=False)

    comp_label.config(text = "Scraping and Sorting Complete")#use this line to print label on gui window


"""
makefile function where the file is created

file name format = filename_day_month_year_hour_min_sec.(of the current day)

"""
def makefile(prod,path):
    global file, f_path
    #file name
    date = datetime.datetime.now()
    d = date.strftime("%d_%m_%y_%H_%M_%S")#filename_day_month_year_hour_min_sec.(
    file_name = str(prod.replace(" ","_"))+"_"+d
    #file path
    file_path = os.path.join(path,file_name)
    #make dir
    os.mkdir(file_path)
    display.insert(tk.END,  "Output file des: "+file_path+"\n")
    window.update()
    #open file
    file_path = os.path.join(file_path, file_name+".csv")
    f_path = file_path
    file = open(file_path, "w")
    file.write("Product_Name,Product_Photo,Price,Sold,Rating,Shipping_Charges,Seller_Contact_Link,Store_Name,Product_Description,Product_Link,Specification,Likes,Positive_Feedback,Reviews\n")  



"""
output_result function where the data is stored into the file

"""
def output_result(Product_Name, Product_Photo, Price, Sold, Rating,Shipping_Charges, Seller_Contact_Link, Store_Name, Product_Description,Product_Link, Specification, Likes, Positive_Feedback, Reviews):
    global file, proxy, agent, bar, window, display, lock
    #"Product_Name, Product_Photo, Price, Sold, Rating,Shipping_Charge, Seller_Contact_Link, Store_Name, Product_Description,Product_Link, Specification, Likes, Positive_Feedback, Reviews"
    row = str(Product_Name)+","+str(Product_Photo)+","+str(Price)+","+str(Sold)+","+str(Rating)+","+str(Shipping_Charges)+","+str(Seller_Contact_Link)+","+str(Store_Name)+","+str(Product_Description)+","+str(Product_Link)+","+str(Specification)+","+str(Likes)+","+str(Positive_Feedback)+","+str(Reviews)+"\n"
    lock.acquire() #dont change the line here 
    file.write(row)
    display.insert(tk.END, row+"\n")
    window.update()
    lock.release()#dont change the line
    print("thread ", threading.current_thread(), row)


"""
after finish fuction the do_sort function is called. for sorting.

"""
def finish():
    global proxy, agent, bar, window, display, lock, start_time, thread_list
    lock.acquire()
    print("finished scrape ",threading.current_thread() )
    end = time.time()
    print(str(end - start_time)+"\n")
    thread_list.append(threading.current_thread().name)
    lock.release()
    if(len(thread_list) == 10):#count if all the thered finished there work.
        do_sort() ##call the do_sort function for sorting.



"""
product details extract function to scrape the required fields.

"""
def prod_extract(response, Product_Name, Price, Sold,Shipping_Charges):
    print("prod_extract thread", threading.current_thread())
    data = re.findall("window.runParams = (.+?);\n", response.text, re.S)
    data = re.findall("\n (.+?),\n", data[0], re.S)
    data = data[0].split("data:")
    json_data = json.loads(data[1])
    

    Product_Photo = json_data['imageModule']['imagePathList'][0]
    try:
        Rating = json_data['titleModule']['feedbackRating']['averageStar']
    except:
        Rating = None
    try:
        Seller_Contact_Link = "https:"+json_data['storeModule']['storeURL']
    except:
        Seller_Contact_Link = None
    try:
        Store_Name = json_data['storeModule']['storeName'].replace("\n ,", ' ').replace(",", "")
    except:
        Store_Name = None
    try:
        Product_Description = json_data['pageModule']['description'].replace("\n", " ").replace(",", "")
    except:
        Product_Description = None
    Product_Link = json_data['pageModule']['itemDetailUrl']
    spec = ""
    try:
        for i in json_data['specsModule']['props']:
            spec += i['attrName']+": "+i["attrValue"]+" "
        Specification = spec.replace("\n", " ").replace(",","")
    except:
        Specification = "None"
    try:
        Likes = json_data['actionModule'][ 'itemWishedCount']
    except:
        Likes = None
    try:
        Positive_Feedback = json_data[ 'storeModule']['positiveRate']
    except:
        Positive_Feedback = None
    try:
        Reviews = json_data['titleModule'][  'feedbackRating'][  'totalValidNum']
    except:
        Reviews = None
    output_result(Product_Name, Product_Photo, Price, Sold, Rating,Shipping_Charges, Seller_Contact_Link, Store_Name, Product_Description,Product_Link, Specification, Likes, Positive_Feedback, Reviews)


"""

product details page where i start scrape of the all the product link

"""
def product_details_scrape(prod_next,Product_Name, Price, Sold,Shipping_Charges, count):
    global header,proxy, agent, bar, window, display, lock
    lock.acquire()
    p = proxy.get_proxy()
    a = agent.get_agent()
    head = header
    lock.release()
    head["User-Agent"] = a
    try:
        print("prod_details thread, url", threading.current_thread(), prod_next)
        res = rq.get(prod_next, headers = head,  timeout=(1, 60), allow_redirects=False)
        prod_extract(res, Product_Name, Price, Sold,Shipping_Charges)
    except Exception as e:
        print(e)
        count += 1
        lock.acquire()
        time.sleep(2)
        lock.release()
        if count == 30:
            exit(0)
        product_details_scrape(prod_next, Product_Name, Price, Sold,Shipping_Charges,count)

"""
scrape_main_page main fuction where the base url is called and start the scraping.


"""
def scrape_main_page(response, start, end, load):
    global next_url, start_time, token_, rate
    data = re.findall("window.runParams = (.+?);\n", response.text, re.S)

    item = json.loads(data[1])
    for i in item["items"]:

        Product_Name = i["title"].replace("\n", ' ').replace(",", "")

        Price = i["price"].replace("\n", ' ').replace(",", "")

        try:
            Shipping_Charges = i["logisticsDesc"].replace("\n", ' ').replace(",", "")
        except:
            Shipping_Charges = None
        try:
            Sold = i['tradeDesc'].replace("\n", ' ').replace(",", "")
            Sold = Sold.split("Sold")
            Sold = Sold[0].replace("\n", ' ').replace(",", "")
            Sold = Sold.strip()
        except:
            Sold = 0
        prod_next = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+"https:"+i["productDetailUrl"]
        print("thread next_url", threading.current_thread(), prod_next)
        time.sleep(1)
        product_details_scrape(prod_next,Product_Name, Price, Sold,Shipping_Charges, 0)
        load += 1
        bar['value']=load
        rate += 1
        if rate == 20:
            print("i am rate")
            lock.acquire()
            time.sleep(10)
            lock.release()
            rate = 0


    lock.acquire()
    print("scrape process finished of page %d: %f\n" %(start,time.time()-start_time))
    start += 1
    url = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+ parse.quote(next_url + str(start))
    lock.release()
    if start<=end:
        print("thread next page", threading.current_thread(), url)
        time.sleep(1)
        start_scrape(url, start, end, 0, load)
    else:
        finish()

"""
initial fuction to start the scrape fuction.

"""
def start_scrape(url, start, end, count, load):
    global header, proxy, agent, bar, window, display, lock
    lock.acquire()
    p = proxy.get_proxy()
    a = agent.get_agent()
    head = header
    lock.release()
    head["User-Agent"] = a
    try:
        print("start_scrape url thread", url, threading.current_thread())
        res = rq.get(url, headers=head,  timeout=(1, 60), allow_redirects=False)
        scrape_main_page(res, start, end, load)
    except Exception as e:
        print(" start_scrape ",e)
        count += 1
        if count == 30:
            exit(0)
        lock.acquire()
        time.sleep(2)
        lock.release()
        start_scrape(url, start, end, count, load)



"""

thread class where i create threads and start the work.
every therad is handeling 6 pages

"""

class thread:

    set1 = (1, 6)
    set2 = (7, 12)
    set3 = (13, 18)
    set4 = (19, 24)
    set5 = (25, 30)
    set6 = (31, 36)
    set7 = (37, 42)
    set8 = (43, 48)
    set9 = (49, 54)
    set10 =(55, 60)

    def __init__(self,prod, path, barload, window_, text_):
        global base_url, proxy, agent, bar, window, display, lock, next_url, token_
        #base url
        url =  base_url+parse.quote(prod)
        #next_page url
        next_url = url+"&page="
        #proxy class
        proxy = proxies()
        #agent class
        agent = user_agent()
        bar = barload
        window = window_
        display = text_
        makefile(prod,path)
        print(base_url, proxy, agent, window, display, lock, next_url)
        
        #get token:

        token = open("token.txt", "r")
        token_ = token.readlines()
        token.close()
        token_ = token_[0].replace("\n", "")
        token_ = token_.replace(" ", "")


        #thread lock
        lock = threading.Lock()
        url1 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set1[0]))
        url2 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set2[0]))
        url3 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set3[0]))
        url4 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set4[0]))
        url5 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set5[0]))
        url6 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set6[0]))
        url7 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set7[0]))
        url8 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set8[0]))
        url9 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set9[0]))
        url10 = 'http://api.scrapestack.com/scrape?access_key='+token_+'&url='+parse.quote(next_url + str(self.set10[0]))
        print("url1: ", url1)
        print("url2: ", url2)
        print("url3: ", url3)
        print("url4: ", url4)
        print("url5: ", url5)
        print("url6: ", url6)
        print("url7: ", url7)
        print("url8: ", url8)
        print("url9: ", url9)
        print("url10: ", url10)
        t1 = threading.Thread(name="page1", target=start_scrape, args=(url1, self.set1[0], self.set1[1], 0, 0), daemon=True)
        t2 = threading.Thread(name="page2", target=start_scrape, args=(url2, self.set2[0], self.set2[1], 0, 0), daemon=True)
        t3 = threading.Thread(name="page3", target=start_scrape, args=(url3, self.set3[0], self.set3[1], 0, 0), daemon=True)
        t4 = threading.Thread(name="page4", target=start_scrape, args=(url4, self.set4[0], self.set4[1], 0, 0), daemon=True)
        t5 = threading.Thread(name="page5", target=start_scrape, args=(url5, self.set5[0], self.set5[1], 0, 0), daemon=True)
        t6 = threading.Thread(name="page6", target=start_scrape, args=(url6, self.set6[0], self.set6[1], 0, 0), daemon=True)
        t7 = threading.Thread(name="page7", target=start_scrape, args=(url7, self.set7[0], self.set7[1], 0, 0), daemon=True)
        t8 = threading.Thread(name="page8", target=start_scrape, args=(url8, self.set8[0], self.set8[1], 0, 0), daemon=True)
        t9 = threading.Thread(name="page9", target=start_scrape, args=(url9, self.set9[0], self.set9[1], 0, 0), daemon=True)
        t10 = threading.Thread(name="page10", target=start_scrape, args=(url10, self.set10[0], self.set10[1], 0, 0), daemon=True)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()
        t10.start()



"""

gui class here the main gui interface is written


"""
class gui:
    def __init__(self):
        global comp_label
        self.window = tk.Tk()
        self.window.geometry("1300x600")
        self.window.title("AliScraper")
        self.window['bg'] = "#ff7017"
        f1 = tk.Frame(self.window)
        f1.pack()
        f1['bg'] = "#ff7017"
        tk.Label(f1, text="AliScraper", bg="#ff7017", bd=0, fg="white",font=("Roboto Mono",30),width=700).pack()
        self.dir = filedialog.askdirectory()
        f2 = tk.Frame(self.window)
        f2.pack()
        f2['bg'] = "#ff7017"
        tk.Label(f2, text="Search Any Product", bg="#ff7017", bd=0, fg="white", font=("Roboto Mono",18), padx=1).grid(row=1,column=1, padx=2)
        self.prod = tk.Entry(f2,  bg="#ff7017", bd=0,font=("Roboto Mono",14), fg="white", state="normal", width="20" )
        self.prod.grid(row=1,column=2,padx=15)
        self.str_btn = tk.Button(f2, text="Start Scrape", command=self.start_process, relief=tk.RAISED, bg="white", fg="#ff7017",font=("Roboto Mono",14))
        self.str_btn.grid(row=1,column=3, padx=15)
        self.ref_btn = tk.Button(f2, text="Refresh", state="disabled" ,command=self.refresh, relief=tk.RAISED, bg="white", fg="#ff7017",font=("Roboto Mono",14))
        self.ref_btn.grid(row=1,column=4, padx=15)
        self.t = tk.Entry(f2,  bg="#ff7017", bd=0,font=("Roboto Mono",14), fg="white", state="normal", width="20" )
        self.t.grid(row=1,column=5,padx=15)
        self.t_btn = tk.Button(f2, text="Change Token" ,command=self.change_token, relief=tk.RAISED, bg="white", fg="#ff7017",font=("Roboto Mono",12))
        self.t_btn.grid(row=1,column=6, padx=15)
        self.sort_btn = tk.Button(f2, text="Sort" ,command=sort, relief=tk.RAISED, bg="white", fg="#ff7017",font=("Roboto Mono",12))
        self.sort_btn.grid(row=1,column=7, padx=15)
        f3 = tk.Frame(self.window)
        f3.pack()
        self.comp = tk.Label(f3, text="", bg="#ff7017", bd=0, fg="white", font=("Roboto Mono",18), padx=1)
        self.comp.pack()
        comp_label = self.comp
        self.bar = Progressbar(self.window, orient = tk.HORIZONTAL, length = 1100,maximum = 360, mode="determinate")
        self.bar.pack(padx=10,pady=30)
        self.text = tk.Text(self.window,  bg="#ff7017", fg="#072757",font=("Roboto Mono",12), bd=0)
        self.text.pack(expand=True,side=tk.LEFT, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(self.window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

    def start_process(self):
        self.bar['value']=0
        self.str_btn["state"] = tk.DISABLED
        self.ref_btn["state"] = tk.NORMAL
        self.text.delete('1.0', tk.END)
        self.window.update_idletasks()
        self.text.insert(tk.END, "product name: "+self.prod.get()+"\n")
        self.text.yview_pickplace("end")
        self.window.update_idletasks()
        self.text.insert(tk.END, "Start Process...\n")
        self.window.update_idletasks()
        self.text.insert(tk.END, "path: "+self.dir+"\n")
        self.window.update_idletasks()
        t = thread(self.prod.get(), self.dir, self.bar, self.window, self.text)

    def refresh(self):
        global thread_list
        thread_list = []
        self.bar['value']=0
        self.text.delete('1.0', tk.END)
        self.str_btn["state"] = tk.NORMAL
        self.ref_btn["state"] = tk.DISABLED
        self.prod.delete(0, 'end')
        self.comp.config(text="")

    def change_token(self):
        token = open("token.txt", "w")
        token.write(self.t.get())
        token.close()
        self.t.delete(0, 'end')





#never change this lines.

window = gui()
window.window.mainloop()
try:
    print("exit")
    file.close()
except:
    print("exit")
exit(0)
