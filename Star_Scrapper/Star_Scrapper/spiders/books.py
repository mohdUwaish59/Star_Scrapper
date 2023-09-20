import scrapy
from pathlib import Path
from pymongo import MongoClient
import datetime

client = MongoClient("mongodb+srv://USER:PASSWORD@cluster0.olcx7kr.mongodb.net/")
db = client.Star_Scrapper

def insertToDb(page, title, rating,image,price,inStock):
    collection = db[page]
    page_sliced = page.split("_")[0]
    doc = {
        "Type": page_sliced,
        "Title": title,
        "Rating": rating,
        "Image_Url": image,
        "Price": price,
        "inStock": inStock,
        "date":datetime.datetime.utcnow().strftime('%Y-%m-%d')
    }
    inserted = collection.insert_one(doc)
    return inserted.inserted_id
    

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://toscrape.com/"]

    def start_requests(self):
        urls = [
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
            "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page=response.url.split("/")[-2]
        filename = f"bookes-{page}.html"
        bookdetail = {}
        #Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
        cards = response.css(".product_pod")
        for card in cards:
            title = card.css("h3>a::text").get()

            rating = card.css(".star-rating").attrib["class"].split(" ")[1]

            image = card.css(".image_container img")
            image = image.attrib["src"].replace("../../../../media","https://books.toscrape.com/media/")

            price= card.css(".price_color::text").get()

            availability = card.css(".instock availability")
            if len(availability.css(".icon-ok"))>0:
                inStock=True
            else:
                inStock=False

            insertToDb(page, title, rating,image,price,inStock)
