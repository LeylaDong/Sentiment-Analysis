from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import re
import time 
import random
import pprint
import csv


# In[2]:


#getting links of Robert Pattinson's movies from IMDB actor page -> movie link -> rating link -> MetaCritic link 

#set-up
headers = {'user-agent': 'Chrome/99.0.4840.0'}
wait_time = random.randrange(5,10)

#Robert Pattinson's IMDB actor page
URL = 'https://www.imdb.com/name/nm1500155/?nmdp=1&#actor'
page = requests.get(URL, headers=headers)
time.sleep(wait_time)

#extracting imdb metacritics page links for each movie 
baseurl = 'https://www.imdb.com'
soup = BeautifulSoup(page.content, 'lxml')
movielist = soup.find_all('div', id=re.compile('^actor-tt')) #only movies he's credited in as actor
movielinks = []
        
for item in movielist:
    for link in item.find_all('a', href=True):
        url = link['href'].split('?')
        movielinks.append(baseurl + url[0] + 'criticreviews')

time.sleep(wait_time)
        
print(len(movielinks))


# In[3]:


#extracting actual metacritics page links for each movie 
metalinks = []

for link in movielinks:
    pages = requests.get(link, headers=headers)
    salad = BeautifulSoup(pages.content, 'lxml')
    if salad.find('span', id='noContent'):
        pass
    else: 
        greens = salad.find('div', class_='article')
        topping = greens.find('div', class_='see-more')
        metalink = topping.find('a', class_='offsite-link', href=True)
        metaurl = metalink['href'].split('?')
        metalinks.append(metaurl[0] + '/critic-reviews')
    time.sleep(wait_time)
    
print(len(metalinks))


# **Noting here that only 27 of the 38 movies where Robert Pattison was credited as actor have metacritic page links.**

# In[33]:


#testing extraction of information through print
testmoviedata = []
testurl = 'https://www.metacritic.com/movie/the-batman/critic-reviews'
testpage = requests.get(testurl, headers=headers)
testsoup = BeautifulSoup(testpage.content, "html.parser")
testtitle = testsoup.find('h1').text
testyear = testsoup.find('span', class_='release_date').text[-5:].replace("\n", "")
testcritrev = testsoup.find('div', class_='critic_reviews')    
testrevs = testcritrev.find_all('div', class_='review pad_top1 pad_btm1')
for item in testrevs: 
    testmovie = {}
    testmovie['Title'] = testtitle
    testmovie['Year'] = testyear
    testmovie['Rating'] = item.find('div', class_=re.compile('^metascore')).text
    testmovie['Critic Author'] = item.find('span', class_='author').text
    testmovie['Review'] = item.find('a', class_='no_hover').text.replace("\n", "")[48:] #there's a weird 48-chr space here
    testmoviedata.append(testmovie)
pp = pprint.PrettyPrinter(indent=1)
pp.pprint(testmoviedata)


# In[45]:


#creating CSV files containing critic reviews for each movie with a metacritic link
for link in metalinks:
    url = link
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    movietitle = soup.find('h1').text.replace(":","-")
    movieyear = soup.find('span', class_='release_date').text[-5:].replace("\n","")
    critrev = soup.find('div', class_='critic_reviews')
    revs = critrev.find_all('div',class_='review pad_top1 pad_btm1')

    title_list = []
    year_list = []
    rating_list = []
    publication_list = []
    author_list = []
    review_list = []

    for item in revs:
        try:
            #Movie title
            Title = movietitle
            
            #Movie year
            Year = movieyear
            
            #Movie critic rating
            Rating = item.find('div', class_=re.compile('^metascore')).text
            
            #Critic's publication
            if item.find('img', class_='pub-img'):
                Publication = item.find('img', class_='pub-img').get('title')
            else: Publication = item.find('span', class_='source').text.split('\n')[0]
                
            #Critic's name
            if item.find('span', class_='author'):
                Author = item.find('span', class_='author').text
            else: Author = 'Unnamed Author'
                
            #Content of critic's review
            Review = item.find('a', class_='no_hover').text.replace("\n", "")[48:] #there's a 48-chr space to delete
        
            #Appending to lists
            title_list.append(Title)
            year_list.append(Year)
            rating_list.append(Rating)
            publication_list.append(Publication)
            author_list.append(Author)
            review_list.append(Review)

        except:
            continue

    moviedict = {'Movie':title_list,
                 'Year':year_list,
                 'Rating':rating_list,
                 'Publication':publication_list,
                 'Author':author_list,
                 'Review':review_list}  
    df = pd.DataFrame(moviedict) 
    df.to_csv(f'critic_{movietitle}.csv') 
