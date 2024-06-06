import csv
import re
import requests

from bs4 import BeautifulSoup


def get_view(script):
    search = re.search(r'xhr\.open\("GET", "(.*?)", true\);', script).group(1)
    soup = BeautifulSoup(
        requests.get('https://informburo.kz'+search).text,
        'html.parser'
    )
    view = soup.text.strip()
    return view


def get_link(link, page):
    list1 = []
    for i in range(1, page+1):
        soup = BeautifulSoup(
            requests.get(f'{link}?page={i}').text,
            'html.parser'
        )
        lin = soup.find_all(
            'a',
            href=re.compile(r'^https://informburo\.kz/novosti/')
        )
        for a in lin:
            href = a['href']
            if href not in list1:
                list1.append(href)
            else:
                continue
    return list1


def parsing(links):
    headers = [
        'title', 'text', 'post_date',
        'tags', 'views', 'image_url', 'url'
    ]
    with open('result.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        writer.writerow(headers)
        for url in links:
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            title = soup.find('h1').get_text().replace('\n', '')
            post_date = soup.find('time').text
            try:
                image_url = [
                    'https://informburo.kz' + image.img['src']
                    for image in soup.find_all('figure', class_='image')
                ]
            except Exception:
                image_url = []
            script = soup.find(
                'small',
                class_='arrilot-widget-container uk-text-muted').find(
                    'script'
                    ).string
            views = get_view(script)
            tags = []
            for li in soup.find_all('ul', class_='article-tags'):
                all_tag = li.find_all('li')
                for tag in all_tag:
                    tags.append(tag.text)
            text = []
            for i in soup.find_all('div', class_='article'):
                get_text = i.get_text(strip=True)
                if 'Читайте также:' in get_text:
                    text.append(get_text.split('Читайте также:')[0])
                    break
                else:
                    text.append(get_text)
            writer.writerow([
                   title, text, post_date,
                   tags, views, image_url, url
            ])
    return 'Парсинг завершен!'


links = get_link('https://informburo.kz/novosti', 100)
print(parsing(links))
