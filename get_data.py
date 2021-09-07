import requests
from datetime import datetime, date, timedelta

import time


# formats date to ISO 8601
def format_date(date):
    return date.strftime("%Y-%m-%d")

# takes date from IDPH source and strips time value
def import_date(date, add_day=False, cdc=False):
    if cdc:
        imported_date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%f")
    else:
        imported_date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
    if add_day:
        imported_date = imported_date + timedelta(1)
    formatted_date = format_date(imported_date)
    return formatted_date

# Pulls all data from IDPH and combines them to a single dictionary using the date as the key
def get_idph_data():

    # Get today's date and format it how needed
    today = date.today()
    today_formatted = format_date(today)
    
    # data source for tests and deaths
    test_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetIllinoisCases"

    # data source for hospital, ICU, and ventilator utilization
    hospital_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetHospitalUtilizationResults"

    # data source for vaccination info
    #vaccine_url = "https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetVaccineAdministration?countyname="

    # CDC vaccination data source
    cdc_vaccine_url = "https://data.cdc.gov/resource/unsk-b7fc.json?location=IL"

    # grab all the data sources
    test_data = requests.get(test_url)
    hospital_data = requests.get(hospital_url)
    #vaccine_data = requests.get(vaccine_url)
    cdc_vaccine_data = requests.get(cdc_vaccine_url)

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

    # get relevant info for vaccinations. switching to CDC data
    """ for day in vaccine_data.json():
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
    """

    # Check to make sure that the data for today is available, otherwise try again in 5 minutes.
    if today_formatted not in combined_data:
        print("Data not available yet, pausing 30 seconds.")
        time.sleep(300)
        combined_data = get_idph_data()

    # Ingest CDC data
    for day in cdc_vaccine_data.json():
        day_date = day['date']
        day_vaccines_administered_total = day['administered']
        day_vaccines_administered_12plus = day['administered_12plus']
        day_vaccines_administered_18plus = day['administered_18plus']
        day_vaccines_administered_65plus = day['administered_65plus']
        first_dose_percent_total = day['administered_dose1_pop_pct']
        first_dose_percent_12plus = day['administered_dose1_recip_2']
        first_dose_percent_18plus = day['administered_dose1_recip_4']
        first_dose_percent_65plus = day['administered_dose1_recip_6']
        fully_vaccinated_total = day['series_complete_pop_pct']
        fully_vaccinated_12plus = day['series_complete_12pluspop']
        fully_vaccinated_18plus = day['series_complete_18pluspop']
        fully_vaccinated_65plus = day['series_complete_65pluspop']

        normalized_date = import_date(day_date, add_day=True, cdc=True)

        # add day if it doesn't exist
        if normalized_date not in combined_data:
            combined_data[normalized_date] = dict()

        combined_data[normalized_date]['vaccines_administered_total'] = day_vaccines_administered_total
        combined_data[normalized_date]['vaccines_administered_12plus'] = day_vaccines_administered_12plus
        combined_data[normalized_date]['vaccines_administered_18plus'] = day_vaccines_administered_18plus
        combined_data[normalized_date]['vaccines_administered_65plus'] = day_vaccines_administered_65plus
        combined_data[normalized_date]['vaccines_first_dose_percent_total'] = first_dose_percent_total
        combined_data[normalized_date]['vaccines_first_dose_percent_12plus'] = first_dose_percent_12plus
        combined_data[normalized_date]['vaccines_first_dose_percent_18plus'] = first_dose_percent_18plus
        combined_data[normalized_date]['vaccines_first_dose_percent_65plus'] = first_dose_percent_65plus
        combined_data[normalized_date]['fully_vaccinated_percent_total'] = fully_vaccinated_total
        combined_data[normalized_date]['fully_vaccinated_percent_12plus'] = fully_vaccinated_12plus
        combined_data[normalized_date]['fully_vaccinated_percent_18plus'] = fully_vaccinated_18plus
        combined_data[normalized_date]['fully_vaccinated_percent_65plus'] = fully_vaccinated_65plus
        
        
    # Check to make sure each data source had data.  Saw conditions where we retrieve data as it's being updated and crash.
    if "cases" not in combined_data[today_formatted]:
        print("IDPH case/test data not available yet, pausing 30 seconds.")
        time.sleep(300)
        combined_data = get_idph_data()
        
    if "covid_vent" not in combined_data[today_formatted]:
        print("IDPH hospitalization data not available yet, pausing 30 seconds.")
        time.sleep(300)
        combined_data = get_idph_data()
        
    if "vaccines_administered_total" not in combined_data[today_formatted]:
        print("CDC vaccine data not available yet, pausing 30 seconds.")
        time.sleep(300)
        combined_data = get_idph_data()

    return combined_data
    
