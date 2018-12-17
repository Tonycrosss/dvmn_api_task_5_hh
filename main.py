import requests


url = "https://api.hh.ru/vacancies/"

vacancies_names = ["Программист Python", "Программист Ruby", "Программист Java",
                   "Программист Swift", "Программист Javascript", "Программист Go",
                   "Программист C++", "Программист PHP", "Программист C#"]


def predict_rub_average_salary(vacancy_json):
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
    vacancies_proceed, average_salary = predict_rub_average_salary(vacancy_json)
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

pretty_output("Программист Python")