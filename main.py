import requests


url = "https://api.hh.ru/vacancies/"

vacancies_names = ["Программист Python", "Программист Ruby", "Программист Java",
                   "Программист Swift", "Программист Javascript", "Программист Go",
                   "Программист C++", "Программист PHP", "Программист C#"]


def predict_rub_average_salary_hh(vacancy_json):
    all_salaries = []
    for item in vacancy_json['items']:
        if item is not None and item['salary'] is not None and item['salary']['currency'] == 'RUR':
            salary = item['salary']
            if salary['from'] is not None and salary['to'] is not None:
                predicted_salary = (salary['from'] + salary['to']) / 2
            elif salary['from'] is not None and salary['to'] is None:
                predicted_salary = salary['from'] * 1.2
            elif salary['from'] is None and salary['to'] is not None:
                predicted_salary = salary['to'] * 0.8

            all_salaries.append(predicted_salary)
    processed_salaries = len(all_salaries)
    average_salary = sum(all_salaries) // len(all_salaries)
    return (processed_salaries, int(average_salary))


def get_vacancy_json(name):
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
        print(f'Loading  {name} page : {page}....')
        params["page"] = page
        response = requests.get(url, params=params)
        for item in response.json()['items']:
            response_json['items'].append(item)
        print(f'Loaded!')
    return response_json


def pretty_output(search_name):
    vacancy_json = get_vacancy_json(search_name)
    founded_vacancies = vacancy_json['found']
    vacancies_proceed, average_salary = predict_rub_average_salary_hh(vacancy_json)
    out_dict = {
        search_name: {
            "vacancies_found": founded_vacancies,
            "vacancies_processed": vacancies_proceed,
            "average_salary": average_salary
        }
    }
    print(out_dict)


top_langs_list = ["Программист Python", "Программист Ruby", "Программист Java",
                   "Программист Swift", "Программист Javascript", "Программист Go",
                   "Программист C++", "Программист PHP", "Программист C#"]

# pretty_output("Программист Python")
# for lang in top_langs_list:
#     pretty_output(lang)

def average_salary_from_superjob(vacancy_dict):
    all_salaries = []
    for item in vacancy_dict.keys():
        if vacancy_dict[item]['payment_from'] != 0 and vacancy_dict[item]['payment_to'] != 0:
            predicted_salary = (vacancy_dict[item]['payment_from'] + vacancy_dict[item]['payment_to']) / 2
        elif vacancy_dict[item]['payment_from'] != 0 and vacancy_dict[item]['payment_to'] == 0:
            predicted_salary = vacancy_dict[item]['payment_from'] * 1.2
        elif vacancy_dict[item]['payment_from'] == 0 and vacancy_dict[item]['payment_to'] != 0:
            predicted_salary = vacancy_dict[item]['payment_to'] * 0.8
        else:
            continue

        all_salaries.append(predicted_salary)
    processed_salaries = len(all_salaries)
    average_salary = sum(all_salaries) // len(all_salaries)
    return (processed_salaries, int(average_salary))


def fetch_vacancies_from_superjob(name):
    secret_key = "v3.r.128977974.a1abb3a24d8881daebd4b8268c0bb09839c95ca9.6c1f43473acc583d623876c00b4f6f535ede39dd"
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": secret_key
    }
    params = {
        "keyword": name,
        "town": 4
    }

    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    print(response_json)

    vacancies_json = {}
    for item in response_json['objects']:
        if item['currency'] == 'rub':
            vacancies_json[item['profession']] = {"payment_from": item['payment_from'], "payment_to": item['payment_to'], "town": "Москва"}
    return vacancies_json

# print(fetch_vacancies_from_superjob("Программист Python"))

vacancy_dict = fetch_vacancies_from_superjob("Программист Python")
print(average_salary_from_superjob(vacancy_dict))