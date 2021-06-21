from datetime import datetime, date, timedelta

today = date.today()
today_formatted = today.strftime("%Y-%m-%d")

def format_date(date):
    return date.strftime("%Y-%m-%d")

def past_days(num_days, reference_date = date.today()):
    old_date = reference_date - timedelta(num_days)
    return old_date

def weekly_reference(combined_data, reference_date = date.today()):
    today_formatted = format_date(reference_date)
    seven_days_ago = format_date(past_days(7, reference_date = date.today()))
    fourteen_days_ago = format_date(past_days(14, reference_date = date.today()))
    twentyone_days_ago = format_date(past_days(21, reference_date = date.today()))
    twentyeight_days_ago = format_date(past_days(28, reference_date = date.today()))

    cases_today = combined_data[today_formatted]['cases']
    cases_seven_days_ago = combined_data[seven_days_ago]['cases']
    cases_fourteen_days_ago = combined_data[fourteen_days_ago]['cases']
    cases_twentyone_days_ago = combined_data[twentyone_days_ago]['cases']
    cases_twentyeight_days_ago = combined_data[twentyeight_days_ago]['cases']

    return (f"Week over week reference:  \n"
            f"28 Days Ago: {cases_twentyeight_days_ago:,}  \n"
            f"21 Days Ago: {cases_twentyone_days_ago:,}  \n"
            f"14 Days Ago: {cases_fourteen_days_ago:,}  \n"
            f"7 Days Ago: {cases_seven_days_ago:,}  \n"
            f"Today: {cases_today:,}  \n")

def weekly_average(combined_data, metric, reference_date = date.today()):
    total = 0
    for n in range(7):
        total += combined_data[format_date(past_days(n, reference_date))][metric]
    average = total / 7
    return average

def compare_metric(today, last_week):
    return round((today / last_week - 1) * 100, 2)

def week_comparison(combined_data, reference_date = date.today()):
    last_week = past_days(7, reference_date)
    case_7_day_avg_today = weekly_average(combined_data, "cases", reference_date)
    case_7_day_avg_last_week = weekly_average(combined_data, "cases", last_week)
    deaths_7_day_avg_today = weekly_average(combined_data, "deaths", reference_date)
    deaths_7_day_avg_last_week = weekly_average(combined_data, "deaths", last_week)
    hospitalizations_7_day_avg_today = weekly_average(combined_data, "covid_beds", reference_date)
    hospitalizations_7_day_avg_last_week = weekly_average(combined_data, "covid_beds", last_week)
    icu_7_day_avg_today = weekly_average(combined_data, "covid_icu", reference_date)
    icu_7_day_avg_last_week = weekly_average(combined_data, "covid_icu", last_week)
    vent_7_day_avg_today = weekly_average(combined_data, "covid_vent", reference_date)
    vent_7_day_avg_last_week = weekly_average(combined_data, "covid_vent", last_week)

    case_change = compare_metric(case_7_day_avg_today, case_7_day_avg_last_week)
    death_change = compare_metric(deaths_7_day_avg_today, deaths_7_day_avg_last_week)
    hospitalizations_change = compare_metric(hospitalizations_7_day_avg_today, hospitalizations_7_day_avg_last_week)
    icu_change = compare_metric(icu_7_day_avg_today, icu_7_day_avg_last_week)
    vent_change = compare_metric(vent_7_day_avg_today, vent_7_day_avg_last_week)

    text = "Week over week change in 7-day rolling average:  \n"

    if case_change > 0:
        text += f"New cases up {case_change}%  \n"
    else:
        text += f"New cases down {abs(case_change)}%  \n"
    if death_change > 0:
        text += f"Deaths up {death_change}%  \n"
    else:
        text += f"Deaths down {abs(death_change)}%  \n"
    if hospitalizations_change > 0:
        text += f"Hospitalizations up {hospitalizations_change}%  \n"
    else:
        text += f"Hospitalizations down {abs(hospitalizations_change)}%  \n"
    if icu_change > 0:
        text += f"ICU usage up {icu_change}%  \n"
    else:
        text += f"ICU usage down {abs(icu_change)}%  \n"
    if vent_change > 0:
        text += f"Ventilator usage up {vent_change}%  \n"
    else:
        text += f"Ventilator usage down {abs(vent_change)}%  \n"

    return text

