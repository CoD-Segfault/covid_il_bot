import json
import praw
from praw.util.token_manager import FileTokenManager
from format_data import week_comparison, weekly_reference, weekly_average, past_days
from datetime import datetime, date, timedelta
from get_data import get_idph_data

# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

# Get today's date and format it how needed
today = date.today()
today_formatted = format_date(today)

combined_data = get_idph_data()

# Get the info from today.
todays_data = combined_data[today_formatted]
new_cases = todays_data['cases']
deaths = todays_data['deaths']
tests = todays_data['tested']
positivity = round((new_cases / tests * 100), 2)

hospitalizations = todays_data['covid_beds']
icu_usage = todays_data['covid_icu']
ventilator_usage = todays_data['covid_vent']

vaccine_doses = todays_data['vaccine_doses']
vaccine_average = round(todays_data['vaccine_rolling_average'])
percent_vaccinated = todays_data['total_population_percent_vaccinated']

# Generate the title and text based on current data.
title = f"Unofficial Daily Update for {today_formatted}. {new_cases} New Cases."

selftext = (f"There were {new_cases:,} reported today.  With {tests:,} tests administered, we have a positivity rate of {positivity}%.\n\n"
        f"There were {deaths:,} reported deaths.\n\n"
        f"There are {hospitalizations:,} hospitalizations, with {icu_usage:,} in the ICU, and {ventilator_usage:,} ventilators in use.\n\n"
        f"{vaccine_doses:,} vaccine doses were administered yesterday, bringing the 7 day rolling average to {vaccine_average:,}.\n\n"
        f"{percent_vaccinated}% of the total Illinois population are fully vaccinated.\n\n\n"
        f"{weekly_reference(combined_data, reference_date=today)}\n\n"
        f"{week_comparison(combined_data, reference_date=today)}\n\n"
        "This post was automatically generated based on the latest data from the IDPH website.  \n"
        "Source code is available at https://github.com/CoD-Segfault/covid_il_bot")


credentials_file = open("credentials.json")
credentials = json.load(credentials_file)

refresh_token_filename = "refresh_token.txt"

refresh_token_manager = FileTokenManager(refresh_token_filename)
reddit = praw.Reddit(
    token_manager = refresh_token_manager,
    user_agent = "linux:com.committeeofdoom.covidilbot:v0.1 (by /u/CoD_Segfault)",
    client_id = credentials["praw_client_id"],
    client_secret = credentials["praw_client_secret"]
)

reddit.subreddit("coronavirusillinois").submit(title, selftext=selftext)
