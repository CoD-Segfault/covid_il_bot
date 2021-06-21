# covid_il_bot
 Pulls data from IDPH sources, formats it, then posts to /r/CoronavirusIllinois on Reddit.

Here is the Python 3.6+ app that is used for the unofficial daily updates on 
the /r/CoronavirusIllinois subreddit. PRAW is the only dependency outside of 
the standard Python3 libraries.  More info at https://praw.readthedocs.io

To access the Reddit API, you will need to create an application and authorize 
it on your account.  You create an app at https://www.reddit.com/prefs/apps/, 
then obtain a refresh token and save it in a file named 
refresh_token.txt.  I used the script located at 
https://praw.readthedocs.io/en/latest/tutorials/refresh_token.html
to get the token.  You will need to put the client id and secret into the 
credentials.json file.  A sample file is provided to show the format.

Operating the bot is as simple as running post_reddit.py with Python3.6 or 
higher.  All testing has been done on Python 3.9.2.