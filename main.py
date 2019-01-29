import requests
from terminaltables import AsciiTable
import logging
import argparse


VERBOSITY_TO_LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def fetch_json_from_hh(name):
    url = "https://api.hh.ru/vacancies"
    params = {
        "area": 1,
        "text": name,
        "period": 30,
        "page": 1
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    pages = response_json['pages']
    for page in range(2, pages):
        logging.info(f'Loading  {name} page : {page}....')
        params["page"] = page
        response = requests.get(url, params=params)
        for item in response.json()['items']:
            response_json['items'].append(item)
    return response_json


def fetch_json_from_superjob(name):
    secret_key = "v3.r.128977974.a1abb3a24d8881daebd4b8268c0bb09839c95ca9.6c1f43473acc583d623876c00b4f6f535ede39dd"
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": secret_key
    }
    params = {
        "keyword": name,
        "town": 4,
    }
    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    return response_json


def average_salary_from_site(vacancy_data, site):
    if site == 'hh':
        all_salaries = []
        for item in vacancy_data['items']:
            if item is not None and item['salary'] is not None and item['salary']['currency'] == 'RUR':
                salary = item['salary']
                if salary['from'] is not None and salary['to'] is not None:
                    predicted_salary = (salary['from'] + salary['to']) / 2
                elif salary['from'] is not None and salary['to'] is None:
                    predicted_salary = salary['from'] * 1.2
                elif salary['from'] is None and salary['to'] is not None:
                    predicted_salary = salary['to'] * 0.8
                else:
                    continue
                all_salaries.append(predicted_salary)
        processed_salaries = len(all_salaries)
        average_salary = sum(all_salaries) // len(all_salaries)
        return (processed_salaries, int(average_salary))

    elif site == 'superjob':
        all_salaries = []
        for item in vacancy_data['objects']:
            if item['payment_from'] != 0 and item['payment_to'] != 0:
                predicted_salary = (item['payment_from'] + item[
                    'payment_to']) / 2
            elif item['payment_from'] != 0 and item['payment_to'] == 0:
                predicted_salary = item['payment_from'] * 1.2
            elif item['payment_from'] == 0 and item['payment_to'] != 0:
                predicted_salary = item['payment_to'] * 0.8
            else:
                continue
            all_salaries.append(predicted_salary)
        if all_salaries != []:
            processed_salaries = len(all_salaries)
            average_salary = sum(all_salaries) // len(all_salaries)
        else:
            processed_salaries, average_salary = (0, 0)
        return processed_salaries, int(average_salary)


def collect_hh_stat(json):
    founded_vacancies = json['found']
    processed_salaries_hh, hh_av_salary = average_salary_from_site(json, site='hh')
    return (founded_vacancies, processed_salaries_hh, hh_av_salary)


def collect_superjob_stat(json):
    founded_vacancies = json['total']
    processed_salaries_superjob, superjob_av_salary = average_salary_from_site(json, site='superjob')
    return (founded_vacancies, processed_salaries_superjob, superjob_av_salary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count', default=1)
    args = parser.parse_args()
    logging_level = VERBOSITY_TO_LOGGING_LEVELS[args.verbose]
    logging.basicConfig(level=logging_level)
    top_langs_list = ["Программист Python", "Программист Ruby",
                      "Программист Java",
                      "Программист Swift", "Программист Javascript",
                      "Программист Go",
                      "Программист C++", "Программист PHP", "Программист C#"]
    table_data_hh = table_data_superjob = (('Наименование вакансии', 'Всего найдено вакансий', 'Обработано вакансий', 'Средняя зарплата'),)
    for lang in top_langs_list:
        hh_json = fetch_json_from_hh(lang)
        superjob_json = fetch_json_from_superjob(lang)
        table_data_hh = table_data_hh + ((lang, *collect_hh_stat(hh_json)), )
        table_data_superjob = table_data_superjob + ((lang, *collect_superjob_stat(superjob_json)),)
    hh_title = 'HH Moscow'
    superjob_title = 'SJ Moscow'
    table_instance_hh = AsciiTable(table_data_hh, hh_title)
    table_instance_superjob = AsciiTable(table_data_superjob, superjob_title)
    print(table_instance_hh.table)
    print(table_instance_superjob.table)


if __name__ == '__main__':
    main()




