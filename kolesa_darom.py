import csv
import json
import lxml
import os
import requests
import time
from bs4 import BeautifulSoup
from os import write
import datetime

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}

cur_time = datetime.datetime.now().strftime("%d.%m.%Y_%H:%M")
all_cards_link = []

def get_url(url):
    response = requests.get(url, headers)
    src = response.text

    with open('all.html', 'w', encoding='utf-8') as file:
        file.write(src)

def get_data():
    with open('all.html', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    search_page = soup.find('div', class_='main-section__footer').find('ul').find_all('a')[-2].get('href').find('page-')
    page_count = int(soup.find('div', class_='main-section__footer').find('ul').find_all('a')[-2].get('href')[
                     search_page + 5:search_page + 8])

    links = []
    for link in range(1, page_count + 1):
        links.append(f'https://saratov.kolesa-darom.ru/catalog/avto/shiny/nav/page-{link}/')

    with open(f'tyres_{cur_time}.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(
            (
                'Наименование',
                'Ширина',
                'Профиль',
                'Диаметр',
                'Индекс скорости',
                'Максимальная скорость',
                'Индекс нагрузки',
                'Максимальная нагрузка',
                'Цена',
                'Ссылка'
                # 'Изображение'
            )
        )

    count = 0
    count_2 = 0
    print('''Выберите режим работы парсера:
             1 - собрать данные о всех имеющихся шинах
             2 - отобрать шины по параметрам''')
    number = input('Введите число: ')
    while number != '1' and number != '2':
        print('Вы ввели неправиьное число!')
        time.sleep(2)
        os.system('cls')
        print('''Выберите режим работы парсера:
             1 - собрать данные о всех имеющихся шинах
             2 - отобрать шины по параметрам''')
        number = input('Введите число: ')

    if number == '2':
        tire_diameter = input('Введите диаметр шины: ')
        tire_profile = input('Введите профиль шины: ')
        tire_width = input('Введите ширина шины: ')

    print('Начинаю работать...')
    time.sleep(1)

    for link in links:
        head = {
            'path:': 'https://api.retailrocket.ru/api/2.0/recommendation/personal/compositeForCategory/60f810cc97a5251dd8f83160/?&categoryIds=5&algorithmType=personal&session=67cf40a1e65d8e09dbec3b34&pvid=578815607630520&isDebug=false&format=json',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        response = requests.get(link, head)
        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.find_all('div', class_='product-card__inner')

        for item in links:
            tyres_title = item.find('p').text
            price = item.find('div', class_='product-card__button').text.replace('₽', '').replace(' ', '')
            all_specifications = item.find('ul')

            properties = []
            for li in all_specifications():
                properties.append(li.text)
            if 'R' in properties[1]:
                properties.insert(1, '-')
            while len(properties) < 7:
                properties.append('None')

            tyres_link = 'https://saratov.kolesa-darom.ru' + item.find('a', class_='product-card__image-container').get(
                'href')

            tyres = {
                'Наименование': tyres_title,
                'Ширина': properties[0],
                'Профиль': properties[1],
                'Диаметр': properties[2],
                'Индекс скорости': properties[3],
                'Максимальная скорость': properties[4],
                'Индекс нагрузки': properties[5],
                'Максимальная нагрузка': properties[6],
                'Цена': price,
                'Ссылка': tyres_link
                # 'Изображение': image
            }
            count_2 += 1
            if number == '1':
                if tyres not in all_cards_link:
                    write_data(tyres)

            if number == '2':
                if tire_diameter == properties[2][1:] and tire_profile == properties[1] and tire_width == properties[0]:
                    if tyres not in all_cards_link:
                        write_data(tyres)

        count += 1
        os.system('cls')
        if number == '2':
            print(f'Диаметр шины: {tire_diameter}, Профиль шины: {tire_profile}, Ширина шины: {tire_width}\n')
        # print(time.time())
        print(f'Прогресс: {'{:.2f}'.format(count / page_count * 100).rjust(6)}% - {(int((count / page_count * 101) - 1) * '#') + ((100 - (int(count / page_count * 101))) * '_')}')
        print(f'Страниц обработано: {count}/{page_count}')
        # print('Количество проходов: ', count_2)

    with open(f'tyres_{cur_time}.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_cards_link, json_file, indent=4, ensure_ascii=False)

def main():
    start_time = time.time()
    get_url('https://saratov.kolesa-darom.ru/catalog/avto/shiny/')
    get_data()
    print(f'Затраченное время: {int((time.time() - start_time) // 60)} мин. {int((time.time() - start_time) % 60)} с.')

def write_data(tyres):
    with open(f'tyres_{cur_time}.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(
            (
                tyres['Наименование'],
                tyres['Ширина'],
                tyres['Профиль'],
                tyres['Диаметр'],
                tyres['Индекс скорости'],
                tyres['Максимальная скорость'],
                tyres['Индекс нагрузки'],
                tyres['Максимальная нагрузка'],
                tyres['Цена'],
                tyres['Ссылка']
                # 'Изображение': image
            )
        )
    return all_cards_link.append(tyres)

if __name__ == '__main__':
    main()

