import requests
from terminaltables import AsciiTable
import logging
import argparse

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
    if predicted_salary_list != []:
        processed_salaries = len(predicted_salary_list)
        average_salary = sum(predicted_salary_list) // len(
            predicted_salary_list)
    else:
        processed_salaries, average_salary = (0, 0)
    return processed_salaries, average_salary


def get_predict_rub_salary_hh(vacancy):
    all_salaries = []
    for item in vacancy['items']:
        if item is not None and item['salary'] is not None and \
                item['salary']['currency'] == 'RUR':
            salary = item['salary']
            all_salaries.append(salary)
    return all_salaries


def get_predict_rub_salary_sj(vacancy):
    all_salaries = []
    for item in vacancy['objects']:
        # унифицируем ключи
        item["from"] = item.pop("payment_from")
        item["to"] = item.pop("payment_to")
        all_salaries.append(item)
    return all_salaries


def get_salaries_hh(language, region, period):
    url = "https://api.hh.ru/vacancies"
    params = {
        "area": 1,
        "text": language,
        "period": period,
        "page": 1,
        "areas": region
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    pages = response_json['pages']
    for page in range(2, pages):
        logging.info(f'Loading  {language} page : {page}....')
        params["page"] = page
        response = requests.get(url, params=params)
        for item in response.json()['items']:
            response_json['items'].append(item)
    return response_json


def get_salaries_sj(language, region, period=None):
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
    return response_json


def collect_hh_stat(json):
    founded_vacancies = len(json)
    processed_salaries_hh, hh_av_salary = get_predict_salary(json)
    return founded_vacancies, processed_salaries_hh, hh_av_salary


def collect_superjob_stat(json):
    founded_vacancies = len(json)
    processed_salaries_superjob, superjob_av_salary = get_predict_salary(json)
    return founded_vacancies, processed_salaries_superjob, superjob_av_salary


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
    table_data_hh = table_data_superjob = (('Наименование вакансии',
                                            'Всего найдено вакансий',
                                            'Обработано вакансий',
                                            'Средняя зарплата'),)
    for lang in top_langs_list:
        hh_json = get_salaries_hh(lang, 113, 30)
        hh_sallaries_list = get_predict_rub_salary_hh(hh_json)
        sj_json = get_salaries_sj(lang, 4)
        sj_sallaries_list = get_predict_rub_salary_sj(sj_json)
        table_data_hh = table_data_hh + \
                        ((lang, *collect_hh_stat(hh_sallaries_list)),)
        table_data_superjob = table_data_superjob + ((lang, *collect_superjob_stat(sj_sallaries_list)),)

    hh_title = 'HH Moscow'
    superjob_title = 'SJ Moscow'
    table_instance_hh = AsciiTable(table_data_hh, hh_title)
    table_instance_superjob = AsciiTable(table_data_superjob, superjob_title)
    print(table_instance_hh.table)
    print(table_instance_superjob.table)


if __name__ == '__main__':
    main()




