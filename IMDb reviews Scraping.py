## import the package needed
from bs4 import BeautifulSoup
import requests
import time
import codecs
import numpy as np
import re
from pymongo import MongoClient
from pprint import pprint
from random import randint


# In[2]:


# Downloading imdb movie's data
URL = 'https://www.imdb.com/name/nm1500155/?ref_=tt_ov_st'
AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'
response = requests.get(URL)

# create a BeautifulSoup object
SOUP = BeautifulSoup(response.text, 'lxml')


# In[3]:


# Movie URL
Movie_urls = [a.get('href') for a in SOUP.select('div.filmo-category-section > div > b > a')][0:38]


# In[4]:


# open a file in append mode to write into in the same directory where we ran this script from
csvfile = open('IMDB.csv', 'a')
csvwriter = csv.writer(csvfile)

# write header in the file
fields = ['Title', 'Rating', 'No.of Reviews','Genres', 'Star', 'Role', 'Review url'] 
csvwriter.writerow(fields)

deliminator = '======================================================================='

# movie information
for i in range(0,38,1):
    BASE_URL = "https://www.imdb.com"
    URL = BASE_URL + Movie_urls[i]
    response = requests.get(url=URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Title
    Title = soup.find("h1",{'data-testid':'hero-title-block__title'}).text
    print('Title:', Title)
    
    # Title
    Year = soup.find("span",{'class':'TitleBlockMetaData__ListItemText-sc-12ein40-2 jedhex'}).text
    print('Year:', Year)

    # Rating
    Rating = soup.find("div",{'data-testid':'hero-rating-bar__aggregate-rating__score'}).text
    print('Rating:', Rating)

    # No. of Reviews
    Reviews = soup.find("span",{'class':'score'}).text
    print('No. of Reviews:', Reviews)

    # Genre
    Genres = soup.find_all(name="a",attrs={"class":"GenresAndPlot__GenreChip-sc-cum89p-3 LKJMs ipc-chip ipc-chip--on-baseAlt"})
    Genres = [Genre.text for Genre in Genres]
    print('Genres:', Genres)

    # Role
    Stars = soup.find(name="li",attrs={"class":"ipc-metadata-list__item ipc-metadata-list-item--link"})
    Star = Stars.find_all(name="li",attrs={'class':'ipc-inline-list__item'})
    Star = [Stars.text for Stars in Star]
    if("Robert Pattinson" in Star) :
        Role = "Leading Role"
    else:
        Role = "Minor Role"
    print('Star:',Star)
    print('Role:', Role)
    
    # Review linked url
    review_url = BASE_URL + soup.find("a",{'class':'ipc-link ipc-link--baseAlt ipc-link--touch-target ReviewContent__StyledTextLink-sc-vlmc3o-2 dTjvFT isReview'}).get('href')
    print("Review URL:",review_url)
    
    print(deliminator)

    
    # write a row in the file
    csvwriter.writerow([Title, Year, Rating, Reviews, Genres, Star, Role, review_url])   
    


# In[112]:


# open a file in append mode to write into in the same directory where we ran this script from
#csvfile = open('Movie Reviews.csv', 'a')
#csvwriter = csv.writer(csvfile)

# write header in the file
#fields = ['Review Rating', 'Review Rating', 'Review Content'] 
#csvwriter.writerow(fields)

deliminator = '======================================================================='

for i in range(0,38,1):
    BASE_URL = "https://www.imdb.com"
    start_url = BASE_URL + Movie_urls[i] + "reviews?sort=totalVotes&dir=desc&ratingFilter=0"
    link = BASE_URL + Movie_urls[i] + "/_ajax"
    response = requests.get(url=URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # open a file in append mode to write into in the same directory where we ran this script from
    csvfile = open('Movie Reviews'+str(i+17)+'.csv', 'a')
    csvwriter = csv.writer(csvfile)

    # write header in the file
    fields = ['Review Rating', 'Review Rating', 'Review Content'] 
    csvwriter.writerow(fields)


    params = {
        'ref_': 'undefined',
        'paginationKey': ''
    }

    with requests.Session() as s:
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        res = s.get(start_url)

        while True:
            soup = BeautifulSoup(res.text,"lxml")
            for item in soup.select(".review-container")[:5]:
                if item.find("span.rating-other-user-rating > span"):
                    review_rating = item.select_one("span.rating-other-user-rating > span").get_text(strip=True)
                else:
                    review_rating = "NULL"
                review_title = item.select_one("a.title").get_text(strip=True)
                reviews = item.select_one("div.content").get_text(strip=True)
                #print(review_rating,"/10")
                #print(review_title)
                #print(reviews)
                #print(deliminator)

                # write a row in the file
                csvwriter.writerow([review_rating, review_title, reviews])        

            try:
                pagination_key = soup.select_one(".load-more-data[data-key]").get("data-key")
            except AttributeError:    
                break

            params['paginationKey'] = pagination_key
            res = s.get(link,params=params)
