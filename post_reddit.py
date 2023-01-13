from format_data import *
from datetime import date
from get_data import get_idph_data
import time


# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

# Get today's date and format it how needed
today = date.today()
today_formatted = format_date(today)

combined_data = get_idph_data(today)

while today_formatted not in combined_data:
    print("Data not available yet, pausing 300 seconds.")
    time.sleep(300)

    today = date.today()
    today_formatted = format_date(today)


# Get the info from today.
todays_data = combined_data[today_formatted]

infection_data_available = 'cases' in todays_data
hospitalization_data_available = 'covid_icu' in todays_data
vaccine_data_available = 'vaccines_administered_total' in todays_data
tests_data_available = 'tested' in todays_data

combined_data_keys_sorted = sorted(combined_data.keys(), reverse=True)

previous_infection_date = None
previous_infection_data = None
if infection_data_available:
    for date_key in combined_data_keys_sorted:
        if date_key != today_formatted and 'cases' in combined_data[date_key]:
            previous_infection_date = date_key
            previous_infection_data = combined_data[date_key]
            break

previous_hospitalization_date = None
previous_hospitalization_data = None
if hospitalization_data_available:
    for date_key in combined_data_keys_sorted:
        if date_key != today_formatted and 'covid_icu' in combined_data[date_key]:
            previous_hospitalization_date = date_key
            previous_hospitalization_data = combined_data[date_key]
            break

previous_vaccine_date = None
previous_vaccine_data = None
if vaccine_data_available:
    for date_key in combined_data_keys_sorted:
        if date_key != today_formatted and 'vaccines_administered_total' in combined_data[date_key]:
            previous_vaccine_date = date_key
            previous_vaccine_data = combined_data[date_key]
            break

tests_date = None
tests_data = None
if tests_data_available:
    for date_key in combined_data_keys_sorted:
        if date_key != today_formatted and 'vaccines_administered_total' in combined_data[date_key]:
            tests_date = date_key
            tests_data = combined_data[date_key]
            break

# positivity = round((new_cases / tests * 100), 2)
positivity = 0


if vaccine_data_available:
    day_vaccines_administered_total = doses_administered(combined_data, 'vaccines_administered_total', today, previous_vaccine_date)
    day_vaccines_administered_12plus = doses_administered(combined_data, 'vaccines_administered_12plus', today, previous_vaccine_date)
    day_vaccines_administered_18plus = doses_administered(combined_data, 'vaccines_administered_18plus', today, previous_vaccine_date)
    day_vaccines_administered_65plus = doses_administered(combined_data, 'vaccines_administered_65plus', today, previous_vaccine_date)

    first_dose_percent_total = todays_data['vaccines_first_dose_percent_total']
    first_dose_percent_5plus = todays_data['vaccines_first_dose_percent_5plus']
    first_dose_percent_12plus = todays_data['vaccines_first_dose_percent_12plus']
    first_dose_percent_18plus = todays_data['vaccines_first_dose_percent_18plus']
    first_dose_percent_65plus = todays_data['vaccines_first_dose_percent_65plus']
    fully_vaccinated_total = todays_data['fully_vaccinated_percent_total']
    fully_vaccinated_5plus = todays_data['fully_vaccinated_percent_5plus']
    fully_vaccinated_12plus = todays_data['fully_vaccinated_percent_12plus']
    fully_vaccinated_18plus = todays_data['fully_vaccinated_percent_18plus']
    fully_vaccinated_65plus = todays_data['fully_vaccinated_percent_65plus']
    booster_percent_total = todays_data['booster_percent_total']
    booster_percent_18plus = todays_data['booster_percent_18plus']
    booster_percent_65plus = todays_data['booster_percent_65plus']
    # vaccine_average_total = vaccine_average(combined_data, 'vaccines_administered_total')


# Generate the title and text based on current data.
title = f"Unofficial Daily Update for {today_formatted}. "
if infection_data_available:
    title += f"{todays_data['cases']:,} New Cases."

selftext = ""

if infection_data_available:
    selftext += f"There were {todays_data['cases']:,} positive cases reported since {previous_infection_date}. \n\n"
    selftext += f"There were {todays_data['deaths']:,} reported deaths since {previous_infection_date}.\n\n"

if tests_data_available:
    selftext += f"With {todays_data['tested']:,} tests administered, we have a positivity rate of {positivity}%.\n\n"


if hospitalization_data_available:
    selftext +=  f"Since {previous_hospitalization_date}, there are {todays_data['covid_beds']:,} hospitalizations, with {todays_data['covid_icu']:,} in the ICU, and {todays_data['covid_vent']:,} ventilators in use.\n\n"

if vaccine_data_available:
    selftext += f"**Please note that the vaccine data source has changed from the IDPH to the CDC.**  \n"
    # selftext += f"{day_vaccines_administered_total:,} vaccine doses were administered since {previous_vaccine_date}, bringing the 7 day rolling average to {vaccine_average_total:,}.\n\n"
    selftext += f"{day_vaccines_administered_total:,} vaccine doses were administered since {previous_vaccine_date}.\n\n"
    selftext += f"{fully_vaccinated_total}% of the total Illinois population are fully vaccinated, with {first_dose_percent_total}% having received their first dose.  {booster_percent_total}% have recieved a booster. {todays_data['bivalent_booster_5plus']}% have recceived a bivalent booster. \n"
    selftext += f"{fully_vaccinated_65plus}% of population age 65+ are fully vaccinated, with {first_dose_percent_65plus}% having received their first dose.  {booster_percent_65plus}% have recieved a booster.  \n"
    selftext += f"{fully_vaccinated_18plus}% of population age 18+ are fully vaccinated, with {first_dose_percent_18plus}% having received their first dose.  {booster_percent_18plus}% have recieved a booster.  \n"
    selftext += f"{fully_vaccinated_12plus}% of population age 12+ are fully vaccinated, with {first_dose_percent_12plus}% having received their first dose.  \n"
    selftext += f"{fully_vaccinated_5plus}% of population age 5+ are fully vaccinated, with {first_dose_percent_5plus}% having received their first dose.  \n\n"


if False:
    selftext += (f"{weekly_reference(combined_data, reference_date=today)}\n\n"
    f"{week_comparison(combined_data, reference_date=today)}\n\n")

selftext += (
        "This post was automatically generated based on the latest data from the IDPH and CDC websites.  \n"
        "Source code is available at https://github.com/jsheputis/covid_il_bot")


# print(title)
# print("---------------------------------------------------------------------------------------------------------------------------")
# print(selftext)

credentials_file = open(os.path.join(sys.path[0], "credentials.json"))
credentials = json.load(credentials_file)

refresh_token_filename = os.path.join(sys.path[0], "refresh_token.txt")

refresh_token_manager = FileTokenManager(refresh_token_filename)
reddit = praw.Reddit(
    token_manager = refresh_token_manager,
    user_agent = "linux:com.jsheputis.covidilbot:v0.2 (by /u/compg318)",
    client_id = credentials["praw_client_id"],
    client_secret = credentials["praw_client_secret"]
)

reddit.validate_on_submit = True
post = reddit.subreddit("coronavirusillinois").submit(title, selftext=selftext, flair_id="4be3f066-cf71-11eb-95ff-0e28526b1d53")

