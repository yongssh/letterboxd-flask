
# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import math
import time 



def watchlist(friends):
### Getting Page Data ###
    def scraping_for_titles(url):  
        
        driver = webdriver.Chrome()
        page = driver.get(url)

        html = driver.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        #print(soup)
        
        ### Film Num ###
        raw_num_films = soup.find('h1', attrs={'class': 'section-heading'}).get_text()[:-6]
        num_of_films = int(''.join(i for i in raw_num_films if i.isdigit()))

        #print(num_of_films)

        films_per_page = 28
        page_count = math.ceil(num_of_films / films_per_page)
        #print(page_count)

        ### Titles on Page ###

        titles = []
        if page_count == 1:

            for film_name in soup.find_all('span', attrs={'class':'frame-title'}):
                titles.append(film_name.get_text())
                #print(titles)
                return titles
        
        if page_count > 1:
            for i in range(1, page_count + 1):
                new_url = url + '/page/' + str(i)
                driver.get(new_url)
                time.sleep(3)
                html = driver.execute_script("return document.body.innerHTML")
                soup = BeautifulSoup(html, "html.parser")
                for film_name in soup.find_all('span', attrs={'class':'frame-title'}):
                    titles.append(film_name.get_text())
            #print(titles)
            return titles
        else:
            #print(titles)
            return titles

    all_watchlists = []

    ### Replacing friends' usernames in URL ###
    # replace URL name with each friend's username in turn.

    def retrieve_friends(friends):
        for name in friends: 
            friend_url = "https://letterboxd.com/" + name + "/watchlist/"
            time.sleep(5)
            all_watchlists.append((scraping_for_titles(friend_url)))

        #print(all_watchlists)
        return all_watchlists

    title_freq = dict()

    # Add each movie in each playlist to a dictionary. For each repeat occurence, increment by 1. 
    # Initialize new movies with value of 1.
    def top_shared(all_watchlists):
        for watchlist in all_watchlists:
            for title in watchlist:
                if title not in title_freq: 
                    title_freq[title] = 1
                else: 
                    title_freq[title] += 1

        # Sort dictionary, return top 5 in an array.
        # How to resolve ties? 
        sorted_title_freq = dict(sorted(title_freq.items(), key=lambda x:x[1], reverse = True)[:5])
        # print(sorted_title_freq)
        title_array = []
        for i in sorted_title_freq.keys():
            title_array.append(i)
        return title_array
    def main():
        # Change according to friends' Letterboxd usernames.
        #friends = ["bravefish", "DiCee", "stayjohnson"]
        combined_watchlists = retrieve_friends(friends)
        should_watch = top_shared(combined_watchlists)

        # check for empty strings
        for i in should_watch:
            if i == '':
                should_watch.remove(i)
        if len(should_watch) == 0:
            return "They have no movies in common on their watchlists."
        if len(should_watch) == 1:
            return ', '.join(friends[:-1]) + ", and " + str(friends[-1]) + " should watch " + should_watch[0] + "based on their watchlists' similarities."
        return ', '.join(friends[:-1]) + ", and " + str(friends[-1]) + " should watch " +  ', '.join(should_watch[:-1]) + ", and " + should_watch[-1] + ", based on their watchlists' similarities."
 
    if __name__ == "__main__":
        main()
    return main()

def get_watchlist_results(friends):
    # Call the watchlist function and get the results
    watchlist_results = watchlist(friends)

    return watchlist_results

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
 
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/', methods=['GET', 'POST'])
# ‘/’ URL is bound with hello_world() function.
def index():
    if request.method == 'POST':
        new_friends = request.form.get('friends')
        friends = [friend.strip() for friend in new_friends.split(',')]

        watchlist_results = get_watchlist_results(friends)
        return render_template('index.html', results=watchlist_results, current_friends = new_friends)
    return render_template('index.html', results='', current_friends='')

# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)
