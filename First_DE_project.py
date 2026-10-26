import requests
import pandas as pd
import numpy as np
import sqlite3
from bs4 import BeautifulSoup as bs
links = []
for page in range(1, 4):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    r = requests.get(url)
    soup = bs(r.content, 'lxml')
    books = soup.select("h3 a")
    for book in books:
        link = book.get("href")
        link = "https://books.toscrape.com/catalogue/" + link.replace("../", "")
        links.append(link)
        if len(links) == 50:
            break
    if len(links) == 50:
        break
titles = []
prices = []
availabilities = []
product_categories = []
product_ids = []
for link in links:
    r = requests.get(link)
    soup = bs(r.content, 'lxml')
    title = soup.select("title")
    price = soup.select("p.price_color")
    Availability = soup.select("td")
    product_category = soup.select("li a")
    product_id = soup.select("td")
    product_ids.append(product_id[0].text)
    availabilities.append(Availability[5].text)
    titles.append(title[0].text)
    prices.append(price[0].text)
    product_categories.append(product_category[2].text)
df = pd.DataFrame({
    "title": titles,
    "price": prices,
    "Availability": availabilities,
    "product_id": product_ids,
    "product_category": product_categories
})
#Data Cleaning
df["title"]=df["title"].str.strip()
df=df.dropna(subset=["title"])
df=df.drop_duplicates()
df["price"]=df["price"].str.replace("£","")
df=df.dropna(subset=["price"])
df["price"]=df["price"].astype(float)
df["Availability"]=df["Availability"].str.replace("In stock (","")
df["Availability"]=df["Availability"].str.replace("available)","")
df["Availability"]=df["Availability"].astype(int)
df["product_id"]=df["product_id"].astype(str)
df["product_category"]=df["product_category"].astype(str)
df.to_csv("DE.csv",index=False)
conn=sqlite3.connect("DE.db")
cursor=conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS DE(title varchar(50),price float,Availability int,product_id varchar(50),
product_category varchar(50))""")
df.to_sql("DE", conn, if_exists="append", index=False)
result = pd.read_sql_query("SELECT * FROM DE LIMIT 5", conn)
conn.commit()
print(result)
conn.close()