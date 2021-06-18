from itertools import groupby

import pymorphy2
from bs4 import BeautifulSoup
from pymongo import MongoClient

morph = pymorphy2.MorphAnalyzer()

def replace_sen(sentence):
    objects = []
    #Чтение файла
    f = open('/home/vagrant/tomita-parser/build/bin/objects_lemm.txt', 'r')
    #Создание листа с объектом
    for line in f:
        objects.append(line.replace('\n', ''))
    f.close()
    counter = 1
    for object in objects:
        n = sentence.find(str(object))
        if (n > 0):
            d = "объект" + str(counter)
            sentence = sentence.replace(object, d)
        counter += 1
    return sentence

def mending_pretty():
    with open('/home/vagrant/tomita-parser/build/bin/pretty.html', 'r') as f:
        req_list = []
        for eachLine in f:
            req_list.append(eachLine)
        Text = '\n'.join(req_list).replace('</html>', '')
        Text = Text + '</html>'
    f = open('/home/vagrant/tomita-parser/build/bin/pretty.html', 'w+')
    f.seek(0)
    f.write(Text)
    f.close()

def parsing(collection_sentence):
    #Отрытие файла pretty и его чтение
    with open("/home/vagrant/tomita-parser/build/bin/pretty.html", "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        #Таблица с номерами
        tables = soup.find('table').find('tbody').find_all('tr')
        numbers = []
        for t in tables:
            a = t.find('a')
            if (a):
                a_link = a.get('href')
                a_link = a_link.replace('#', '')
                numbers.append(a_link)
        #Удаление повторов
        new_numbers = [el for el, _ in groupby(numbers)]
        #Номер предложения
        as_ = soup.find('body').find_all('a')
        numbers_sentence = []
        #Открытие временного файла
        temp_file = open('/home/vagrant/tomita-parser/build/bin/temp_text_news.txt', 'w+')
        for a in as_:
            a_name = a.get('name')
            #Если у a есть параметр name
            if (a_name):
                i = False
                for number in new_numbers:
                    #Если имя предложения равно номеру из таблицы
                    if (a_name == number):
                        i = True
                        numbers_sentence.append(a_name)
                        spans = a.find_all('span')
                        word = []
                        for span in spans:
                            span_text = span.get_text()
                            word.append(span_text)
                        sentence = ' '.join(word)
                        #Запись предложения с упоминанием в коллекцию с предложениями
                        data = {'sentence': sentence}
                        write_mongo(collection_sentence, data)

                        #Лемматизация
                        def lemmatize(sentence):
                            words = sentence.split()
                            res = list()
                            for word in words:
                                p = morph.parse(word)[0]
                                res.append(p.normal_form)
                            return res

                        change_sen_file = open('/home/vagrant/tomita-parser/build/bin/change_sentences.txt', 'a')
                        #Изменение предложений
                        sentence_change = ' '.join(lemmatize(sentence))
                        sentence = replace_sen(sentence_change)
                        #Запись предложения в файл
                        change_sen_file.write(sentence + '\n')
                        temp_file.write(sentence)
                        change_sen_file.close()
                #Если в предложении есть name, но нет персон
                if (i == False):
                    spans = a.find_all('span')
                    word = []
                    for span in spans:
                        span_text = span.get_text()
                        word.append(span_text)
                    sentence = ' '.join(word)
                    #Запись предложения в новый файл
                    temp_file.write(sentence)
        temp_file.close()
    f.close()

def write_mongo(collect, data):
    return collect.insert_one(data).inserted_id

def main():
    client = MongoClient('localhost', 27017)
    db = client['bloknot']
    collection_sentence = db['sentence']
    #Перезапись файла pretty
    mending_pretty()
    #Парсинг файла pretty
    parsing(collection_sentence)

if __name__ == '__main__':
    main()