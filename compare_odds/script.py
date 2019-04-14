# %%
# import required libraries
from fuzzywuzzy import fuzz 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time


# %%
# Automated chromedriver and its path where its saved
driver = webdriver.Chrome(executable_path='chromedriver.exe')


# pinnacle sports URLs
soccerUrl = "https://www.pinnacle.com/en/odds/today/soccer"
tennisUrl = "https://www.pinnacle.com/en/odds/today/tennis"
basketbalUrl = "https://www.pinnacle.com/en/odds/today/basketball"
aussportsUrl = "http://odds.aussportsbetting.com/betting?function=next24hours"


# %%
# function takes pinnacle sport URL and return available matches in a python dictionary
def get_pinnacle_dict(url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    table = driver.find_elements_by_xpath(
        '//*[@id="left-content"]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]/div[1]')
    oddtip = []
    teams = []
    teams.append([i.text.split('\n')
                  for i in soup.find_all(class_='name game-name')])
    oddtip.append([i.text for i in soup.find_all(
        class_='oddTip game-moneyline')])
    pinnacle_dict = {
        1: {
            'team':  '',
            'oddtip': '',
        },
    }
    count = 0
    for i in range(len(teams[0])):
        count += 1
        pinnacle_dict[count] = {}
        pinnacle_dict[count]['team'] = teams[0][i][1]
        tip = oddtip[0][i].replace('\n', '')
        pinnacle_dict[count]['oddtip'] = tip
    return pinnacle_dict


# %%

soccer_dict = get_pinnacle_dict(soccerUrl)
time.sleep(10)
tennis_dict = get_pinnacle_dict(tennisUrl)
time.sleep(10)
basketbal_dict = get_pinnacle_dict(basketbalUrl)
time.sleep(10)


# %%
# function return all sports available matches of aussports in a python dictionary
def get_aussports_dict():
    driver.get(aussportsUrl)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    table = driver.find_element_by_xpath('//*[@id="sectionData"]/table[2]')
    table = table.text.split('\n')
    aussports_dict = {
        1: {
            'league': '',
            'team':  '',
            'time':  '',
            'sport':  '',
        },
    }
    count = 0
    for i in table:
        if 'Odds Overview' in i:
            val = i.split('-')
            sport = val[0]
            league = val[1].replace('Odds Overview', '')
        elif 'Compare Odds' in i:
            count += 1
            aussports_dict[count] = {}
            aussports_dict[count]['league'] = league
            aussports_dict[count]['time'] = i[:17]
            team = i.replace(aussports_dict[count]['time'], '')
            team = team.replace('Compare Odds Stats SportsTron', '')
            aussports_dict[count]['team'] = team
            aussports_dict[count]['sport'] = sport
    return aussports_dict


# %%
# function takes pinnacle sport dictionary ,sport name,and aussport dictionary and compare pinnacle sport dictionary with aussport dictionary
# return same matches in python dictionary
def compare_to_aussports_dict(pinnacle_dict, sport, aussports_dict):
    final_teams = {

    }
    pinnacleTeam = ''
    aussportTeam = ''
    team = ''
    matchCount = 0
    for i in pinnacle_dict:
        if(i+1) < len(pinnacle_dict):
            #             if pinnacle_dict[i]['team'] != '' and pinnacle_dict[i+1]['team'] != '':
            pinnacle = pinnacle_dict[i]['team']+'vs'+pinnacle_dict[i+1]['team']
            for letter in pinnacle:
                if letter.isalpha():
                    team += letter.lower()
            pinnacleTeam = team.replace('ll', '')
            team = ''
            for k in aussports_dict:
                flag = False
                if aussports_dict[k]['sport'] == sport:
                    for pre in final_teams:
                        if aussports_dict[k]['team'] == final_teams[pre]['team']:
                            flag = True
                    if(flag == False):
                        for letter in aussports_dict[k]['team']:
                            if letter.isalpha():
                                team += letter.lower()
                            aussportTeam = team.replace('ll', '')
                        if sport == 'Tennis ':
                            if fuzz.ratio(aussportTeam, pinnacleTeam) >= 65:
                                matchCount += 1
                                final_teams[matchCount] = {}
                                final_teams[matchCount]['league'] = aussports_dict[k]['league']
                                final_teams[matchCount]['team'] = aussports_dict[k]['team']
                                final_teams[matchCount]['time'] = aussports_dict[k]['time']
                                final_teams[matchCount]['pinnacleOdd1'] = pinnacle_dict[i]['oddtip']
                                final_teams[matchCount]['pinnacleOdd2'] = pinnacle_dict[i+1]['oddtip']
                                final_teams[matchCount]['sport'] = aussports_dict[k]['sport']
                                if(pinnacle_dict[i+2]['team'] == ''):
                                    final_teams[matchCount]['pinnacleDraw'] = pinnacle_dict[i+2]['oddtip']
                                else:
                                    final_teams[matchCount]['pinnacleDraw'] = 'NA'
                        else:
                            if aussportTeam == pinnacleTeam:
                                matchCount += 1
                                final_teams[matchCount] = {}
                                final_teams[matchCount]['league'] = aussports_dict[k]['league']
                                final_teams[matchCount]['team'] = aussports_dict[k]['team']
                                final_teams[matchCount]['time'] = aussports_dict[k]['time']
                                final_teams[matchCount]['pinnacleOdd1'] = pinnacle_dict[i]['oddtip']
                                final_teams[matchCount]['pinnacleOdd2'] = pinnacle_dict[i +1]['oddtip']
                                final_teams[matchCount]['sport'] = aussports_dict[k]['sport']
                                if(pinnacle_dict[i+2]['team'] == ''):
                                    final_teams[matchCount]['pinnacleDraw'] = pinnacle_dict[i+2]['oddtip']
                                else:
                                    final_teams[matchCount]['pinnacleDraw'] = 'NA'
                        team = ''
    return final_teams


# %%
aussports_dict = get_aussports_dict()
soccer = compare_to_aussports_dict(soccer_dict, 'Soccer ', aussports_dict)
basketball = compare_to_aussports_dict(
    basketbal_dict, 'Basketball ', aussports_dict)
tennis = compare_to_aussports_dict(tennis_dict, 'Tennis ', aussports_dict)

# %%
# save all same matches in sportUp.txt
file = open('sportUp.txt', 'w')
for k in soccer:
    if(len(soccer) == 0):
        file.write("No matches found for Soccer")
    file.write("Sport: "+soccer[k]['sport']+"   "+"Game: " +
               soccer[k]['league']+"   "+soccer[k]['time']+'\n')
    file.write("Aussp: "+soccer[k]['team']+" Pinna: "+soccer[k]['pinnacleOdd1'] +
               " "+soccer[k]['pinnacleDraw']+" "+soccer[k]['pinnacleOdd2']+'\n\n')
for k in basketball:
    if(len(basketball) == 0):
        file.write("No matches found for Basketball")
    file.write("Sport: "+basketball[k]['sport']+"   "+"Game: " +
               basketball[k]['league']+"   "+basketball[k]['time']+'\n')
    file.write("Aussp: "+basketball[k]['team']+" Pinna: "+basketball[k]['pinnacleOdd1'] +
               " "+basketball[k]['pinnacleDraw']+" "+basketball[k]['pinnacleOdd2']+'\n\n')
for k in tennis:
    if(len(tennis) == 0):
        file.write("No matches found for Tennis")
    file.write("Sport: "+tennis[k]['sport']+"   "+"Game: " +
               tennis[k]['league']+"   "+tennis[k]['time']+'\n')
    file.write("Aussp: "+tennis[k]['team']+" Pinna: "+tennis[k]['pinnacleOdd1'] +
               " "+tennis[k]['pinnacleDraw']+" "+tennis[k]['pinnacleOdd2']+'\n\n')

file.close()
driver.close()
