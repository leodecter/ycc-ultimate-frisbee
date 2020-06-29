import requests
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import csv
import ast

user_agent = {'User-Agent': 'Mozilla/5.0'}

def write_html(url, filename):
    r = requests.get(url, headers=user_agent)
    r.raise_for_status()
    with open(filename, 'w') as f:
        f.write(r.text)

def extract_team_information(url, team_info_dic):
    # clicks through and stores information
    driver = webdriver.Chrome('/Users/LeoDecter/Downloads/chromedriver')
    driver.get(url)
    for num in range(1,20):
        if num != 1:
            link = driver.find_element_by_link_text(str(num))
            link.click()
        driver.implicitly_wait(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        teams = soup.find_all('a', {'id' : re.compile(r'^CT_Main_0_gvList_ct')})
        for team in teams:
            base_url = "https://play.usaultimate.org" + team['href']
            ranking = team.previous_element.previous_element.previous_element.strip()
            power_rating = team.next_element.next_element.next_element.get_text().strip()
            division = team.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element
            region = division.next_element.next_element
            section = region.next_element.next_element
            team_info_dic[ranking] = [power_rating, division.strip(), region.strip(), section.strip()]            
            base_filename = "college_team_pages/" + ranking + ".html"
            write_html(base_url, base_filename)

    driver.quit()
    w = csv.writer(open("power_ratings.csv", "w"))
    for key, val in team_info_dic.items():
        w.writerow([key, val])

def scrape_rosters():
    team_name = []
    team_state = []
    rank = []
    power_rating = []
    division = []
    region = []
    section = []
    num_ycc_players = []
    num_total_players = []
    ycc_percentage = []
    ycc_years = []
    player_names = []
    ycc_location = []

    f = open('names_2014_to_2019.csv', 'r')
    reader = csv.reader(f)
    player_names_dic = {}
    for row in reader:
        name = clean_name(row[0])
        player_names_dic[name] = ast.literal_eval(row[1])

    g = open('power_ratings.csv', 'r')
    reader = csv.reader(g)
    team_info_dic = {}
    for row in reader:
        team_info_dic[int(row[0])] = ast.literal_eval(row[1]) 
    
    for x in range(1,390):
        try:
            f = open('college_team_pages/' + str(x) + '.html', 'r').read()
            soup = BeautifulSoup(f, 'html.parser')
            # get team name
            div = soup.find('div', class_='profile_info')
            name = div.find('h4').text
            team_name.append(name.strip())
            # get team location
            p = soup.find('p', class_ = 'team_city').text.strip()
            city_state = p.split(',')
            team_state.append(city_state[1].strip())
            # get team rank
            rank.append(x)
            # get team power rating
            power_rating.append(int(team_info_dic[x][0]))
            # division
            division.append(team_info_dic[x][1])
            # region
            region.append(team_info_dic[x][2])
            # section
            section.append(team_info_dic[x][3])

            # find player names, update num_ycc_players, num_total_players,
            # and ycc_years (total number of individual ycc seasons played by players)
            num_ycc_players.append(0)
            num_total_players.append(0)
            ycc_years.append(0)
            spans = soup.find_all('span', {'id' : re.compile(r'^CT_Right_1_gvListGoals')})
            player_names_list = []
            ycc_location_list = []
            for span in spans:
                num_total_players[x-1] += 1
                name = clean_name(span.get_text())
                if name in player_names_dic.keys():
                    num_ycc_players[x-1] += 1
                    player_names_list.append(name)
                    ycc_location_list.append(player_names_dic[name][1])
                    ycc_years[x-1] += player_names_dic[name][2]
            # record names of players who played YCC
            player_names.append(player_names_list)
            # record locations of where they played
            ycc_location.append(ycc_location_list)
            # record percentage that played ycc
            ycc_percentage.append(num_ycc_players[x-1]/num_total_players[x-1])

        # some ranks are missing for reasons I do not know.
        except OSError:
            print('No team with rank', x)
            team_name.append('N/A')
            team_state.append('N/A')
            rank.append('N/A')
            power_rating.append('N/A')
            division.append('N/A')
            region.append('N/A')
            section.append('N/A')
            num_ycc_players.append(0)
            num_total_players.append(0)
            ycc_percentage.append(0)
            ycc_years.append(0)
            player_names.append([])
            ycc_location.append([])

    # check to make sure nothing was incorrectly accumulated
    print(len(team_name))
    print(len(team_name))
    print(len(rank))
    print(len(power_rating))
    print(len(division))
    print(len(region))
    print(len(section))
    print(len(num_ycc_players))
    print(len(num_total_players))
    print(len(ycc_percentage))
    print(len(ycc_years))
    print(len(player_names ))
    print(len(ycc_location ))

    the_project = {
        'team' : team_name,
        'state' : team_state,
        'rank' : rank,
        'rating' : power_rating,
        'division' : division,
        'region' : region,
        'section' : section,
        'num_ycc' : num_ycc_players,
        'num_total' : num_total_players,
        'ycc_percentage' : ycc_percentage,
        'ycc_years' : ycc_years,
        'ycc_names' : player_names,
        'ycc_locations' : ycc_location
    }

    df = pd.DataFrame(the_project)
    df.to_csv('newest_college_ycc.csv')

def clean_name(name):
    # makes each string lowercase and removes any extra spaces
    lower_name = name.lower()
    strip_name = lower_name.strip()
    spaces_gone = ''
    previous_was_space = False
    for char in strip_name:
        if char != ' ':
            spaces_gone += char
            previous_was_space = False
        else:
            if previous_was_space == False:
                spaces_gone += char
                previous_was_space = True
    return spaces_gone

def test_names(names):
    # takes in list of test strings. 
    for x in range(len(names)):
        print(x)
        print(names[x])
        print(clean_name(names[x]))

# tests = [' Leo Decter', 'Leo  Decter', 'Leo Decter ', ' Leo  Decter ', 'Leo Decter-decter']
# test_names(tests)

def lower_ycc_names():
    # cleans irregularities in the ycc data (mainly names with extra spaces or capitlization)
    g = open('names_2014_to_2019.csv', 'r')
    reader = csv.reader(g)
    ycc_dic = {}
    for row in reader:
        loc = ast.literal_eval(row[1])[1]
        state = loc.split(',')[1].strip()
        if state == "IL":
            state = 'Illinois'
        ycc_dic[clean_name(row[0])] = state.strip()
    w = csv.writer(open("cleaned_ycc_names.csv", "w"))
    for key, val in ycc_dic.items():
        w.writerow([key, val])


url = 'https://play.usaultimate.org/teams/events/team_rankings/?RankSet=College-Men'
power_rating_dic = {}
extract_team_information(url, power_rating_dic)
scrape_rosters()
lower_ycc_names()