#!/usr/bin/env python3
import datetime
import json
import os
import requests

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.getcwd()), '.env'))

# Для работы приложения можно просто указать
# token = "your_api_token"
token = os.getenv("API_TOKEN")

while True:
    # Приветствие и ввод данных
    request = input(
        "Укажите идентификатор города или широту и долготу через пробел;"
        " для завершения работы введите \"exit\":\n"
    )

    if request == "exit":
        print("Завершение программы")
        break

    validate_data = request.split()

    # Проверка введенных данных
    if len(validate_data) == 1:
        try:
            city_id = int(validate_data[0])
        except ValueError:
            print(
                "Не могу распознать идентификатор города.\n"
                "Убедитесь, что вводите идентификатор цифрами.\n"
                "Попробуйте еще раз."
            )
            continue

        # Если введен идентификатор - делаем запрос для получения координат
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "id": city_id,
            "appid": token,
        }

        response = requests.get(url, params)

        if response.status_code == 200:
            coords = json.loads(response.text)
            coords = coords["coord"]
        else:
            print("Внутренняя ошибка сервера. Попробуйте позже.")
            break

    # Проводим валидацию введенных координат
    elif len(validate_data) == 2:
        try:
            coords = [round(float(x), 4) for x in validate_data]
        except ValueError:
            try:
                coords = [round(float(x.replace(",", ".")), 4) for x in validate_data]
            except ValueError:
                print("Не могу прочитать координаты. Попробуйте еще раз.")
                break

        coords = {
            "lat": coords[0],
            "lon": coords[1],
        }
    else:
        print("Не могу разобрать данные.\nПопробуйте еще раз.")
        continue

    # Делаем запрос погоды
    url = "https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "exclude": "current,minutely,hourly,alerts",
        "units": "metric",
        "lang": "en",
        "appid": token
    }
    params.update(coords)
    response = requests.get(url, params)

    if response.status_code == 200:
        data = json.loads(response.text)
        days = [
            [
                data["daily"][i]["dt"],
                data["daily"][i]["temp"]["night"],
                data["daily"][i]["temp"]["morn"],
                data["daily"][i]["pressure"],
            ] for i in range(5)
        ]
    else:
        print("Внутренняя ошибка сервера. Попробуйте позже.")
        break

    # Выводим максимальное давление
    max_pressure = max([round(x[3]/10, 1) for x in days])
    message = "Максимальное давление в течение следующих 5 дней: {0} кПа"
    print(message.format(max_pressure))

    # Выводим минимальную разность температур ночью и утром
    temp_diff = [round(abs(x[1] - x[2]), 2) for x in days]
    min_temp = min(temp_diff)
    index = temp_diff.index(min_temp)
    day = days[index][0]

    # Выводим минимальную разность температур и дату
    date = datetime.datetime.utcfromtimestamp(day).strftime("%d.%m.%Y")
    message = "Минимальная разница между ночной и утренней температурой будет {0}г. Она составит: {1} °C"
    print(message.format(date, min_temp))
    break
