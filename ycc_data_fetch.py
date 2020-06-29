import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv
import ast

user_agent = {'User-Agent': 'Mozilla/5.0'}

def write_html(url, filename):
    r = requests.get(url, headers=user_agent)
    r.raise_for_status()
    with open(filename, 'w') as f:
        f.write(r.text)

divisions = ['mixed/youth-club-u-20-mixed/', 'Boys/youth-club-u-17-boys/', 'Boys/youth-club-u-20-boys/']

def fetch_ycc_division(division, year, url):
    base_url = url + division
    file_division = division.replace('/', '_')
    base_filename = "YCC_team_list_"+ file_division + str(year) + ".html"
    time.sleep(1)
    write_html(base_url, base_filename)

def get_ycc_team_page(href, count, division, year):
    # writes html page for a team using href
    base_url = "https://play.usaultimate.org" + href
    base_filename = "team_rosters_" + str(year) + "/YCC_team_" + division + str(count) + ".html"
    write_html(base_url, base_filename)

def get_team_links(division, year):
    # returns the number of teams in that division
    in_filename = "YCC_team_list_"+ division + str(year) + ".html"
    f = open(in_filename, 'r').read()
    soup = BeautifulSoup(f, 'html.parser')

    hrefs = []
    pools = soup.find_all('div', class_="pool")
    for pool in pools:
        anchors = pool.find_all('a')
        for anchor in anchors:
            hrefs.append(anchor['href'])
    # count used to make unique filenames and record the number of teams in the division
    count = 0
    for href in hrefs:
        get_ycc_team_page(href, count, division, year)
        count += 1
    return count

def get_player_names(count, division, player_names_dic, processed_teams, year):
    # replace with correct year
    in_filename = "team_rosters_" + str(year) + "/YCC_team_" + division.replace('/', '_') + str(count) + ".html"

    f = open(in_filename, 'r').read()
    soup = BeautifulSoup(f, 'html.parser')
    
    team_name_list = soup.find_all('a', {'id' : re.compile(r'^CT_Main_0_ucTeamDetails_lnkTeamName')})
    team_name = team_name_list[0].get_text()

    if not team_name in processed_teams:
        processed_teams.append(team_name)

        spans = soup.find_all('span', {'id' : re.compile(r'^CT_Right_1_gvListGoals')})
        team_location = soup.find('p', id ='CT_Main_0_ucTeamDetails_dlCity').get_text()
        cleaned_location = team_location[4 : len(team_location)-3]
        for span in spans:
            name = span.get_text()
            if name in player_names_dic.keys():
                current_values = player_names_dic[name]
                if current_values[2] <= 2019 - year:
                    list_of_teams = current_values[0]
                    list_of_teams.append(team_name)
                    current_values[0] = list_of_teams
                    current_values[2] += 1
                    player_names_dic[name] = current_values
            else:
                # records new player name as key, with value holding teams played for, location of team, years of experience
                player_names_dic.update({name: [[team_name], cleaned_location, 1]})

def process(divisions, year, url):
    # returns updated dictionary of player names from 2019 back to the given year
    # if player name dictionary already made, use it
    if year != 2019:
        f = open('names_' + str(year + 1) + '_to_2019.csv', 'r')
        reader = csv.reader(f)
        player_names_dic = {}
        for row in reader:
            player_names_dic[row[0]] = ast.literal_eval(row[1])
    else:
        player_names_dic = {}

    for division in divisions:
        # update fetch_ycc_division method with correct base_url for the event page
        fetch_ycc_division(division, year, url)
        get_team_links(division.replace('/', '_'), year)
        # to record teams whose players' names have been extracted
        processed_teams = []
        # count used and incremented below to access filenames one by one
        count = 0
        # will continue to get player names from teams until no teams remain
        teams_left_to_extract = True
        while teams_left_to_extract:
            try:
                get_player_names(count, division, player_names_dic, processed_teams, year)
                count += 1
            except OSError:
                # count exceeds the number of team pages found, so opening the file generated an error
                teams_left_to_extract = False
    return player_names_dic

# set year to 2019 and move it back one (until 2014) after each successful scrape
year = 2019
# replace event_page_url with correct link for event page
event_page_url = "https://play.usaultimate.org/events/2019-US-Open-Club-Championship/"
base_url = event_page_url + "schedule/"

updated_player_dic = process(divisions, year, base_url)
w = csv.writer(open("names_" + str(year) + "_to_2019.csv", "w"))
for key, val in updated_player_dic.items():
    w.writerow([key, val])