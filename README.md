# ycc-ultimate-frisbee
A project that analyzes how participation in the Youth Club Championships for ultimate frisbee goes on to affect the performance of college ultimate frisbee teams.
The main goal was to find what percentage of each college team played in the Youth Club Championships, the highest-level youth tournament in the United States, and if
that had a strong correlation with a college team's end-of-season ranking.

The methods within ycc_data_fetch.py fetch and scrape information (mainly names) from YCC team roster pages from 2019 all the way back to 2014 (no records exist before then).
The methods within college_team_scraper.py fetch and scrape information about men's college ultimate teams from the 2020 season. I then combine it with information about ycc players to create a large pandas dataframe.
In ycc_analysis.ipynb, I use a pandas dataframe to analyze various relationships between youth club ultimate involvement and college team performance
