# ycc-ultimate-frisbee
Uses data from the Youth Club Championships (2014-2019) and 2020 men's college end-of-season rankings to analyze how participation in the Youth Club Championships goes on to affect the performance of college ultimate frisbee teams.
These scripts scrape data to calculate the percentage of each college team that played in the Youth Club Championships, the highest-level youth tournament in the United States. 

The methods within ycc_data_fetch.py fetch and scrape information (mainly names) from YCC team roster pages from 2019 all the way back to 2014 (no records exist before then).
The methods within college_team_scraper.py fetch and scrape information about men's college ultimate teams from the 2020 season.
Pandas combines these two datasets into one dataframe.
Analysis reveals a strong correlation between a college team's end-of-season ranking and the percentage of players of its roster who played in the YCC. It also reveals large disparities in Youth Club Championship invovlement among college regions.
