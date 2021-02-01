import json
import os
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def write_to_file(username, text, b):
    """Запись текста в файл 'username.txt'
    :param username: username пользователя
    :param text: данные, необходимый записать в 'username.txt'
    :param b: переменная для определения, файл 'username.txt' создается(0) или измененяется(1)
    """
    file = open(f"{username}.txt", "w")
    file.write(text)
    if b:
        print(f"Изменена запись {username}.txt;")
    else:
        print(f"Создана запись {username}.txt;")


def new_file_to_task(user_to_file, new_text):
    """Запись файлов 'username.txt' и 'old_username_data_time.txt'
    :param user_to_file: словарь, хранящий информацию о юзере
    :param new_text: данные для 'username.txt'
    """
    # если 'username.txt' уже существует
    if os.path.isfile(f"{user_to_file['username']}.txt"):
        # старый файл username.txt
        old_file = open(f"{user_to_file['username']}.txt", "r")
        # хранит текст из "страрого" 'username.txt'
        old_text = old_file.read()
        # создаем 'old_username_data_time.txt' и записываем в него старые данные
        try:
            old_username_file = open(
                f"old_{user_to_file['username']}_{datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S:%f')}.txt", "w")
            for old_lines in old_text:
                old_username_file.write(old_lines)
            # записываем новые данные в 'username.txt'
            try:
                write_to_file(user_to_file['username'], new_text, 1)
            except:
                print(f"Не удалось изменить файл '{user_to_file['username']}.txt!!!'")
        except:
            print(f"Не удалось создать файл 'old_{user_to_file['username']}_{datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S:%f')}.txt'!!!")
    # если 'username.txt' еще не существует
    else:
        # записываем новые данные в 'username.txt'
        try:
            write_to_file(user_to_file['username'], new_text, 0)
        except:
            print(f"Не удалось создать новый файл '{user_to_file['username']}.txt!!!'")


def text_to_user_file(user_to_file):
    """формирование текста для файла 'username.txt'
    :param user_to_file: словарь, хранящий информацию о юзере
    :return: данные для файла 'username.txt'

    Пример файла:
        Отчёт для Deckow-Crist.
        Ervin Howell <Shanna@melissa.tv> 23.09.2020 15:25
        Всего задач: 4

        Завершённые задачи (2):
        distinctio vitae autem nihil ut molestias quo
        est ut voluptate quam dolor

        Оставшиеся задачи (2):
        suscipit repellat esse quibusdam voluptatem incu...
        laborum aut in quam
    """
    # переменная, хранящая текст для файла 'username.txt
    new_text = (f"Отчет для компании {user_to_file['company_name']}.\n"
                f"{user_to_file['name']} "
                f"<{user_to_file['email']}> "
                f"{datetime.strftime(datetime.now(), '%d.%m.%Y %H:%M:%S:%f')}\n"
                f"Всего задач: {user_to_file['complete_users_todo'][0] + user_to_file['false_users_todo'][0]}\n"
                )
    # кол-во заверешенных задач и их список
    new_text += f"\nЗавершённые задачи ({user_to_file['complete_users_todo'][0]}):\n"
    for i in range(user_to_file['complete_users_todo'][0]):
        if len(user_to_file['complete_users_todo'][1][i]) > 48:
            new_text += f"{user_to_file['complete_users_todo'][1][i][0:48]}...\n"
        else:
            new_text += f"{user_to_file['complete_users_todo'][1][i]}\n"
    # кол-во оставшихся задач и их список
    new_text += f"\nОставшиеся задачи задачи ({user_to_file['false_users_todo'][0]}):\n"
    for i in range(user_to_file['false_users_todo'][0]):
        if len(user_to_file['false_users_todo'][1][i]) > 48:
            # Если название задачи больше 48 символов, обрезаем до 48 символов и добавляем '...'
            new_text += f"{user_to_file['false_users_todo'][1][i][0:48]}...\n"
        else:
            new_text += f"{user_to_file['false_users_todo'][1][i]}\n"
    new_text += f"\n"
    return new_text  # возврат данных для файла 'username.txt'


def count_of_completed(todos, user):
    """Подсчет завершенных и оставшихся задач и их названия у юзера
    :param todos: список задач
    :param user: словарь, хранящий информацю о пользователе
    :return: кол-во завершенных и оставшихся задач
    """
    complete_users_todo = [0, []]  # список, который содержит кол-во завершенных задач[0] и их названия в виде списка[1]
    false_users_todo = [0, []]  # список, который содержит кол-во оставшихся задач[0] и их названия в виде списка[1]
    for todo in todos:
        if len(todo) > 1:
            # выполняется, если существует описание задачи(не только поле 'id')
            if user.get('id') == todo.get('userId'):
                # если нашлась задача user'ом,
                # узнается, завершенная или нет
                if todo.get('completed'):
                    complete_users_todo[0] += 1
                    complete_users_todo[1].append(todo.get('title'))
                else:
                    false_users_todo[0] += 1
                    false_users_todo[1].append(todo.get('title'))
    return complete_users_todo, false_users_todo
    # возвращение списков завершенных и оставшихся задач и их названия у юзера


def read_from_api(path):
    """Чтение из API типа 'json' и возвращение данных типа 'dict'
    :param path: путь до файла типа 'json'
    :return response_json: - json файл
    """
    headers = {'Accept': 'application/json;odata=verbose'}
    responce = requests.get(path, verify=False, headers=headers)
    response_json = responce.json()
    return response_json


def create(todos_path, users_path):
    """ Создание файлов 'username.txt'
    :param todos_path: путь к 'todos'
    :param users_path: путь к 'users'
    """
    todos = read_from_api(todos_path)  # список задач из 'todos' (элементы списка типа 'dict')
    users = read_from_api(users_path)  # список пользователей из 'users' (элементы списка типа 'dict')
    users_to_file = []  # для вывода в 'username.txt'
    # рассматриваем по одному user'у
    for user in users:
        # если у пользователся есть данные (существует не только id)
        if len(user) > 1:
            # получение списков завершенных и оставшихся задач и их названия у юзера
            complete_users_todo, false_users_todo = count_of_completed(todos, user)
            # словарь, хранящий необходиму информацию из users.json
            # и списков завершенных и оставшихся задач и их названия для username.txt
            user_to_file = {"name": user["name"],
                            "username": user["username"],
                            "email": user["email"],
                            "company_name": user["company"]["name"],
                            "complete_users_todo": complete_users_todo,
                            "false_users_todo": false_users_todo
                            }
            # добавление информации в список данных пользователей
            users_to_file.append(user_to_file)
    if not os.path.isdir("tasks"):
        # если нет каталога "tasks", создаем его
        os.mkdir("tasks")
        print("Создана дериктория 'tasks'!")
    # переходим в каталог "tasks"
    os.chdir("tasks")
    for user_to_file in users_to_file:
        # текст для файла 'username.txt
        new_text = text_to_user_file(user_to_file)
        # запись файлов 'username.txt' и 'old_username_data_time.txt'
        new_file_to_task(user_to_file, new_text)
    # переход в родительский каталог для 'tasks'
    os.chdir("..")


def _main():
    try:
        todos_path = "https://json.medrating.org/todos"  # путь к 'todos'
        users_path = "https://json.medrating.org/users"  # путь к 'users'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        create(todos_path, users_path)  # создаем или изменяем записи 'username.txt'
    except:
        print("Не удалось подключиться к API!!!")


if __name__ == '__main__':
    _main()
