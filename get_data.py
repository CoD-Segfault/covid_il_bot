import requests
from datetime import datetime, date, timedelta

import time


# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

# takes date from IDPH source and strips time value
def import_date(date, add_day=False):
    imported_date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
    if add_day:
        imported_date = imported_date + timedelta(1)
    formatted_date = format_date(imported_date)
    return formatted_date

# Pulls all data from IDPH and combines them to a single dictionary using the date as the key
def get_idph_data():

    # Get today's date and format it how needed
    today = date.today() - timedelta(3)
    today_formatted = format_date(today)
    
    # data source for tests and deaths
    test_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetIllinoisCases"

    # data source for hospital, ICU, and ventilator utilization
    hospital_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetHospitalUtilizationResults"

    # data source for vaccination info
    vaccine_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetVaccineAdministration?countyname="

    # grab all the data sources
    test_data = requests.get(test_url)
    hospital_data = requests.get(hospital_url)
    vaccine_data = requests.get(vaccine_url)

    # create a dictionary to combine all data by date
    combined_data = dict()

    # get relevant info for tests and deaths
    for day in test_data.json():
        day_date = day['testDate']
        day_cases = day['cases_change']
        day_deaths = day['deaths_change']
        day_tested = day['tested_change']

        normalized_date = import_date(day_date)

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['cases'] = day_cases
        combined_data[normalized_date]['deaths'] = day_deaths
        combined_data[normalized_date]['tested'] = day_tested

    # get relevant info for hospitalizations, etc.
    for day in hospital_data.json():
        day_date = day['ReportDate']
        day_covid_vent = day['VentilatorInUseCOVID']
        day_covid_icu = day['ICUInUseBedsCOVID']
        day_covid_beds = day['TotalInUseBedsCOVID']
        
        # data delayed by one day, adjusting to match official reports
        normalized_date = import_date(day_date, add_day=True)

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['covid_vent'] = day_covid_vent
        combined_data[normalized_date]['covid_icu'] = day_covid_icu
        combined_data[normalized_date]['covid_beds'] = day_covid_beds

    # get relevant info for vaccinations.
    for day in vaccine_data.json():
        day_date = day['Report_Date']
        day_vaccines_administered = day['AdministeredCountChange']
        day_vaccines_rolling_avg = day['AdministeredCountRollAvg']
        day_percent_vaccinated = day['PctVaccinatedPopulation']

        # percent vaccinated is provided as a ratio, converting to actual percent to 2 decimal places
        day_percent_vaccinated = round(day_percent_vaccinated * 100, 2)

        # data delayed by one day, adjusting to match official reports
        normalized_date = import_date(day_date, add_day=True)

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['vaccine_doses'] = day_vaccines_administered
        combined_data[normalized_date]['vaccine_rolling_average'] = day_vaccines_rolling_avg
        combined_data[normalized_date]['total_population_percent_vaccinated'] = day_percent_vaccinated
    
    # Check to make sure that the data for today is available, otherwise try again in 30 seconds.
    if today_formatted not in combined_data:
        print("Data not abailable yet, pausing 30 seconds.")
        time.sleep(30)
        combined_data = get_idph_data()

    return combined_data
