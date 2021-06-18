import glob
import os

import pymorphy2
from pymongo import MongoClient
from razdel import sentenize

morph = pymorphy2.MorphAnalyzer()

def tomita_text_news(PATH, collection):
    #Цикл по всем записям в коллекции
    cursor = collection.find({})
    counter = 0
    for file in cursor:
        #Создать файл с порядковым номером записи
        name = PATH + "sentences_news_" + str(counter)
        
        sentence_file_w = open(name + ".txt", "w")
        sentence_file_w.seek(0)

        # запись в файл текст новости по предложениям из документа
        for it in list(sentenize(file["text_news"])):
            sentence_file_w.write(it.text + '\n')
        
        sentence_file_w.close()
        old_text = []
        new_text = []

        #Чтение текста новости
        sentence_file_r = open(name + ".txt", "r")
        for line in sentence_file_r:
            old_text.append(line.replace('\n', ''))

        sentence_file_r.close()

        #Запись в файл tomita текста текущей новости
        file_input = open('/home/vagrant/tomita-parser/build/bin/input.txt', 'w+')
        for line in old_text:
            file_input.write(line + '\n')

        file_input.close()

        #Запуск tomita
        os.system("./tomita-parser config.proto")

        #Запуск tomita-parser
        os.system("python3 /home/vagrant/tomita-parser/build/bin/tomita_parser.py")

        #Чтение нового текста новости
        temp_file = open('/home/vagrant/tomita-parser/build/bin/temp_text_news.txt', 'r')
        for line in temp_file:
            new_text.append(line.replace('\n', ''))

        temp_file.close()

        #Запись нового текста новости
        sentence_file = open(name + ".txt", "w+")
        for line in new_text:
            sentence_file.write(line + ' ')

        sentence_file.close()
        counter += 1

def main():
    open('/home/vagrant/tomita-parser/build/bin/change_sentences.txt', 'w').close()
    #Подключение к базе данных
    client = MongoClient('localhost', 27017)
    db = client['bloknot']
    collection = db['news']
    collection_sentence = db['sentence']

    #Удаление всех предложений
    collection_sentence.delete_many({})

    PATH = "/home/vagrant/tomita-parser/build/bin/packs_text_news/"
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    #Удаление всех файлов в папке
    files = glob.glob('/home/vagrant/tomita-parser/build/bin/packs_text_news/*.txt')
    for f in files:
        os.remove(f)

    #Запуск tomita
    tomita_text_news(PATH, collection)

if __name__ == '__main__':
    main()