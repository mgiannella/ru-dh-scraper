from utils import Logger, find_between
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from threading import Thread

log = Logger('log.txt')

locationNames = ["Brower+Commons", "Livingston+Dining+Commons", "Busch+Dining+Hall", "Neilson+Dining+Hall"]
locationNum = ['01','03','04','05']
mealNames = ["Breakfast", "Lunch", "Dinner"]

def getHTML(campusnum, mealnum):
    date = datetime.now()
    formattedDate = '{}/{}/{}'.format(date.month, date.day, date.year) 
    try:
        r = requests.get('http://menuportal.dining.rutgers.edu/FoodPro/pickmenu.asp?locationNum={}&locationName={}&dtdate={}&mealName={}&sName=Rutgers+University+Dining'.format(locationNum[campusnum], locationNames[campusnum], formattedDate, mealNames[mealnum]))
    except:
        log.error('Unable to scrape {} at {}'.format(mealNames[mealnum], locationNames[campusnum].replace('+', ' ')))
        return 'error'
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

def getNutritionInfo(itemID):
    try:
        r = requests.get('http://menuportal.dining.rutgers.edu/FoodPro/label.asp?RecNumAndPort={}'.format(itemID))
        soup = BeautifulSoup(r.text, 'lxml')
        itemJson = {}
        mainInfo= soup.find('div', id='facts')
        macros = soup.find('div', id='specs').find_all('tr')
        itemJson["Serving Size"] = mainInfo.find('p').string.replace("Serving Size ", "")
        itemJson["Calories"] = {}
        itemJson["Calories"]["Calories"] = mainInfo.find('p', attrs={'class': 'strong'}).string.replace('Calories\xa0', '')
        itemJson["Calories"]["Calories From Fat"] = mainInfo.find('p', attrs={'class': 'indent'}).string.replace('Calories from Fat\xa0', '')
        itemJson["Fat"] = {}
        itemJson["Fat"]["Total Fat"] = str(macros[1].find('td')).split('\xa0')[1].split('\n')[0]
        itemJson["Fat"]["Saturated Fat"] = str(macros[2].find('td')).split('\xa0')[1].split('\n')[0]
        itemJson["Fat"]["Trans Fat"] = str(macros[3].find('td')).split('\xa0')[1].split('\n')[0]
        itemJson["Cholesterol"] = str(macros[4].find('td')).split('\xa0')[1].split('\n')[0].replace('</b>', '')
        itemJson["Sodium"] = str(macros[5].find('td')).split('\xa0')[1].split('\n')[0].replace('</b>', '')
        itemJson["Carbohydrates"] = {}
        itemJson["Carbohydrates"]["Total Carbs"] = str(macros[1].find_all('td')[2]).split('\xa0')[1].split('\n')[0]
        itemJson["Carbohydrates"]["Dietary Fiber"] = str(macros[2].find_all('td')[2]).split('\xa0')[1].split('\n')[0]
        itemJson["Carbohydrates"]["Sugars"] = str(macros[3].find_all('td')[2]).split('\xa0')[1].split('\n')[0]
        itemJson["Protein"] = str(macros[4].find_all('td')[2]).split('\xa0')[1].split('\n')[0].replace('</b>', '')
        itemJson["Ingredients"] = str(soup.find_all('div', attrs={'class':'row'})[5].p).replace('<p><b>INGREDIENTS:\xa0\xa0</b>', '').replace('</p>','')
        return itemJson
    except:
        return 'No Information Available for this Item'
def getFoods(campusnum, mealnum):
    mealJson = {}
    soup = getHTML(campusnum, mealnum)
    if soup == 'error':
        return 'error'
    log.status('Scraping foods for meal: {}'.format(mealNames[mealnum]))
    categ = soup.find_all('p', attrs={'style': 'margin: 3px 0;'})
    categories = []
    for cat in categ:
        categories.append(cat.b.string.replace('--','').strip())
    
    for a in range(0, len(categ) - 1):
        souptext = find_between(str(soup), str(categ[a]), str(categ[a+1]))
        soup2 = BeautifulSoup(souptext, 'lxml')
        items = soup2.find_all('div', attrs={'class', 'col-1'})
        mealJson[categories[a]] = {}
        for item in items:
            itID = item.input['value'].replace('*','%2A')
            tag = item.find('input')
            tag.extract()
            mealJson[categories[a]][item.string] = getNutritionInfo(itID)
            if mealJson[categories[a]][item.string] == 'No Information Available for this Item':
                log.warn('No information available for item: {}'.format(item.string))

    
    if mealJson == {}:
        return 'No foods available for this meal today'
    
    return mealJson

def getCampusJson(campusnum):
    campusJson = {}
    date = datetime.now()
    campusJson["Date"] = '{}/{}/{}'.format(date.month, date.day, date.year)
    campusJson["Campus Name"] = locationNames[campusnum].replace('+', ' ')
    for i in range(0,3):
        campusJson[mealNames[i]] = getFoods(campusnum, i)
        if campusJson[mealNames[i]] == 'No foods available for this meal today':
            log.warn('No food available for meal: {} in location: {}'.format(mealNames[i], locationNames[campusnum].replace('+', ' ')))
        elif campusJson[mealNames[i]] == 'error':
            log.error('Problem grabbing food item, going on to next item')
        else:
            log.status('Scraped foods for meal: {} on campus: {}'.format(mealNames[i], locationNames[campusnum].replace('+', ' ')))
    log.success('Scraped Meals for Campus: {}'.format(locationNames[campusnum].replace('+', ' ')))
    with open('{}.json'.format(locationNames[campusnum].lower().replace('+','_')), 'w') as outfile:
        json.dump(campusJson, outfile)
    log.success('Dumped meals to {}'.format('{}.json'.format(locationNames[campusnum].lower().replace('+','_'))))
if __name__ == "__main__":
    print('=============================================')
    print('RU Dining Hall Info Scraper')
    print('Created by @mgiannella, Michael Giannella')
    print('=============================================')
    for i in range(4):
        t = Thread(target=getCampusJson, args=(i,))
        t.start()
