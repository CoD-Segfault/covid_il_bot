import json
import praw
from praw.util.token_manager import FileTokenManager
from format_data import *
from datetime import datetime, date, timedelta
from get_data import get_idph_data
import os, sys

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

day_vaccines_administered_total = doses_administered(combined_data, 'vaccines_administered_total')
day_vaccines_administered_12plus = doses_administered(combined_data, 'vaccines_administered_12plus')
day_vaccines_administered_18plus = doses_administered(combined_data, 'vaccines_administered_18plus')
day_vaccines_administered_65plus = doses_administered(combined_data, 'vaccines_administered_65plus')
first_dose_percent_total = todays_data['vaccines_first_dose_percent_total']
first_dose_percent_12plus = todays_data['vaccines_first_dose_percent_12plus']
first_dose_percent_18plus = todays_data['vaccines_first_dose_percent_18plus']
first_dose_percent_65plus = todays_data['vaccines_first_dose_percent_65plus']
fully_vaccinated_total = todays_data['fully_vaccinated_percent_total']
fully_vaccinated_12plus = todays_data['fully_vaccinated_percent_12plus']
fully_vaccinated_18plus = todays_data['fully_vaccinated_percent_18plus']
fully_vaccinated_65plus = todays_data['fully_vaccinated_percent_65plus']
vaccine_average_total = vaccine_average(combined_data, 'vaccines_administered_total')

# Check if it's Monday and add weekend stats 
if today.isoweekday() == 1:
    sunday = today - timedelta(1)
    sunday_formatted = format_date(sunday)
    sunday_data = combined_data[sunday_formatted]

    saturday = today - timedelta(2)
    saturday_formatted = format_date(saturday)
    saturday_data = combined_data[saturday_formatted]

    weekend_cases = sunday_data['cases'] + saturday_data['cases']
    weekend_deaths = sunday_data['deaths'] + saturday_data['deaths']
    weekend_doses = doses_administered(combined_data, 'vaccines_administered_total', reference_date=sunday) + doses_administered(combined_data, 'vaccines_administered_total', reference_date=saturday)


# Generate the title and text based on current data.
title = f"Unofficial Daily Update for {today_formatted}. {new_cases} New Cases."

selftext = (f"There were {new_cases:,} reported today.  With {tests:,} tests administered, we have a positivity rate of {positivity}%.\n\n"
        f"There were {deaths:,} reported deaths.\n\n"
        f"There are {hospitalizations:,} hospitalizations, with {icu_usage:,} in the ICU, and {ventilator_usage:,} ventilators in use.\n\n"
        f"**Please note that the vaccine data source has changed from the IDPH to the CDC.**  \n"
        f"{day_vaccines_administered_total:,} vaccine doses were administered yesterday, bringing the 7 day rolling average to {vaccine_average_total:,}.\n\n"
        f"{fully_vaccinated_total}% of the total Illinois population are fully vaccinated, with {first_dose_percent_total}% having recieved their first dose.  \n"
        f"{fully_vaccinated_65plus}% of population age 65+ are fully vaccinated, with {first_dose_percent_65plus}% having recieved their first dose.  \n"
        f"{fully_vaccinated_18plus}% of population age 18+ are fully vaccinated, with {first_dose_percent_18plus}% having recieved their first dose.  \n"
        f"{fully_vaccinated_12plus}% of population age 12+ are fully vaccinated, with {first_dose_percent_12plus}% having recieved their first dose.  \n\n"
        )

if today.isoweekday() == 1:
    selftext += f"In addition to today's numbers, there have been {weekend_cases:,} new cases, {weekend_deaths:,} deaths, and {weekend_doses:,} vaccine doses administered since Friday's post.\n\n"
        
selftext += (f"{weekly_reference(combined_data, reference_date=today)}\n\n"
        f"{week_comparison(combined_data, reference_date=today)}\n\n"
        "This post was automatically generated based on the latest data from the IDPH and CDC websites.  \n"
        "Source code is available at https://github.com/CoD-Segfault/covid_il_bot")

credentials_file = open(os.path.join(sys.path[0], "credentials.json"))
credentials = json.load(credentials_file)

refresh_token_filename = os.path.join(sys.path[0], "refresh_token.txt")

refresh_token_manager = FileTokenManager(refresh_token_filename)
reddit = praw.Reddit(
    token_manager = refresh_token_manager,
    user_agent = "linux:com.committeeofdoom.covidilbot:v0.1 (by /u/CoD_Segfault)",
    client_id = credentials["praw_client_id"],
    client_secret = credentials["praw_client_secret"]
)

reddit.subreddit("coronavirusillinois").submit(title, selftext=selftext)
