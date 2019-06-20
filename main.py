import requests
import logging
import argparse

MOSCOW_REGION = 113
MONTH_PERIOD = 30
MOSCOW_REGION_SJ = 4
VERBOSITY_TO_LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def get_predict_salary(sallaries):
    predicted_salary_list = []
    for salary in sallaries:
        if salary['from'] is not None and salary['to'] is not None:
            predicted_salary = (salary['from'] + salary['to']) / 2
        elif salary['from'] is not None and salary['to'] is None:
            predicted_salary = salary['from'] * 1.2
        elif salary['from'] is None and salary['to'] is not None:
            predicted_salary = salary['to'] * 0.8
        else:
            continue
        predicted_salary_list.append(predicted_salary)
    if predicted_salary_list:
        processed_salaries = len(predicted_salary_list)
        average_salary = sum(predicted_salary_list) // len(
            predicted_salary_list)
    else:
        processed_salaries, average_salary = (0, 0)
    return processed_salaries, average_salary


def get_vacancies_hh(language, region, period=None):
    url = "https://api.hh.ru/vacancies"
    params = {
        "area": 1261,
        "text": language,
        "period": period,
        "page": 0,
        # "areas": 1261
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    founded_vanacies = response_json['found']
    vacancies = response_json['items']
    pages = response_json['pages']
    for page in range(1, pages):
        logging.info(f'Loading  {language} page : {page}....')
        params["page"] = page
        sallaries = requests.get(url, params=params)
        vacancies.extend(sallaries.json()['items'])
    return founded_vanacies, vacancies


def get_vacancies_sj(language, region, period=None):
    secret_key = "v3.r.128977974.a1abb3a24d8881daebd4b8268c0bb09839c95ca9.6c1f43473acc583d623876c00b4f6f535ede39dd"
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": secret_key
    }
    params = {
        "keyword": language,
        "town": region,
    }
    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    founded_vacancies = response_json['total']
    vacancies = response_json['objects']
    return founded_vacancies, vacancies


def get_only_rub_av_salary_hh(vacancies):
    all_salaries = []
    for item in vacancies:
        if not item or not item['salary']:
            continue
        if item['salary']['currency'] != 'RUR':
            continue
        all_salaries.append(item['salary'])
    processed_salaries, average_salary = get_predict_salary(all_salaries)
    return processed_salaries, average_salary


def get_only_rub_av_salary_sj(vacancies):
    all_salaries = []
    for item in vacancies:
        # унифицируем ключи
        item["from"] = item.pop("payment_from")
        item["to"] = item.pop("payment_to")
        all_salaries.append(item)
    processed_salaries, average_salary = get_predict_salary(all_salaries)
    return processed_salaries, average_salary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count', default=1)
    args = parser.parse_args()
    logging_level = VERBOSITY_TO_LOGGING_LEVELS[args.verbose]
    logging.basicConfig(level=logging_level)
    # top_lang_list = ["Программист Python", "Программист Ruby",
    #                   "Программист Java",
    #                   "Программист Swift", "Программист Javascript",
    #                   "Программист Go",
    #                   "Программист C++", "Программист PHP", "Программист C#"]
    top_lang_list = ["Разработчик python"]

    for language in top_lang_list:
        hh_founded_vacancies_quantity, hh_vacancies = get_vacancies_hh(language, MOSCOW_REGION, MONTH_PERIOD)
        for vacancy in hh_vacancies:
            print(vacancy)
        hh_processed_salaries, hh_average_salary = get_only_rub_av_salary_hh(hh_vacancies)

if __name__ == '__main__':
    main()