import os
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk

from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from pymongo import MongoClient


client = MongoClient('localhost',27017)
db = client['bloknot']
c_news = db['news']
c_sentence = db['sentence']
c_objects = db['person']
c_tonality = db['tonality']

def show_frame(frame):
    frame.tkraise()

#Главное окно
win = tk.Tk()
win.title('Лингвистика')
win.attributes('-fullscreen', True)
win['bg'] = 'green'

#Левая и правая часть экрана
frame_left = LabelFrame(win, text="Навигатор")
frame_right = tk.Frame(win)
frame_left['bg'] = '#00CC33'

#Окна
frame_right_func = tk.Frame(frame_right)
frame_right_func['bg'] = '#00CC33'
frame_right_bd = tk.Frame(frame_right)
frame_right_syn = tk.Frame(frame_right)
frame_right_ton = tk.Frame(frame_right)



wrapper_bd = LabelFrame(frame_right_bd, text="Новости")
wrapper_elem_bd = LabelFrame(frame_right_bd, text="Выбранная новость")

wrapper_ton = LabelFrame(frame_right_ton, text="Тональность")
wrapper_ton.pack(fill="both", expand=0)

wrapper_syn = LabelFrame(frame_right_syn, text="Контекстные синонимы и слова окружения")
wrapper_syn.pack(fill="both", expand=1)

wrapper_func = LabelFrame(frame_right_func, text="Парсер и обработка")
#wrapper_sent = LabelFrame(frame_right_func, text="Предложения с личностями/местами")

frame_left.pack(fill="both", side = TOP, padx=20, pady=10)
frame_right.pack(fill="both", padx=20, pady=0)
wrapper_bd.pack(fill="both")
wrapper_elem_bd.pack(fill="both")
wrapper_func.pack(fill="both", expand = 0, padx=20, pady=10)
#wrapper_sent.pack(fill="both", padx=20, pady=10)

#my_list_sen = Listbox(wrapper_sent, height=28)
#my_list_sen.pack(fill="both", expand="yes", padx=20, pady=10)



my_list_per = Listbox(wrapper_syn)
my_list_per.pack(fill="both",side = RIGHT, padx=20, pady=10)

my_list_syn = Listbox(wrapper_syn)
my_list_syn.pack(fill="both", expand=1, side = LEFT)
my_list_slova = Listbox(wrapper_syn)
my_list_slova.pack(fill="both", expand=1, side = LEFT)

for frame in (frame_right_func, frame_right_bd, frame_right_syn, frame_right_ton):
  frame.grid(row=0,column=0,sticky='nsew')
  


def parser_site():
  os.system("python3 /home/vagrant/tomita-parser/build/bin/parser_site.py")
  
def tomita():
  os.system("python3 /home/vagrant/tomita-parser/build/bin/tomita.py")
  
def model_w2v():
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/w2v.py")
  
def analiz_tony():
  os.system("python3 /home/vagrant/tomita-parser/build/bin/analysis.py")

def natasha():
  a = my_list_per.get(ANCHOR)
  element={"name_object" : a}
  n = c_objects.find_one(element)
  element = n["num_object"]
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/natasha1.py"+ " " +str(element))
  
  my_list_slova.delete(0,'end')
  f = open('/home/vagrant/tomita-parser/build/bin/syn1.txt')
  for line in f:
    line = line.replace('\n', '')
    my_list_slova.insert(END,line)
  f.close()
  
def w2v():
  a = my_list_per.get(ANCHOR)
  element={"name_object" : a}
  n = c_objects.find_one(element)
  element = n["num_object"]
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/synonyms.py"+ " " +str(element))

  my_list_syn.delete(0,'end')
  f = open('/home/vagrant/tomita-parser/build/bin/syn.txt')
  for line in f:
    line = line.replace('\n', '')
    my_list_syn.insert(END,line)
  f.close()


parser_btn = tk.Button(wrapper_func, text='Парсер 10 новостей',command=parser_site, bg = 'yellow')
parser_btn.pack(fill='x', ipady=5, side = LEFT, expand=1)

tomita_btn = tk.Button(wrapper_func, text='Tomita',command=tomita, bg = 'yellow')
tomita_btn.pack(fill='x', ipady=5, side = LEFT, expand=1)

w2v_btn = tk.Button(wrapper_func, text='Word2vec',command=model_w2v, bg = 'yellow')
w2v_btn.pack(fill='x', ipady=5, side = LEFT, expand=1)

w2v_btn = tk.Button(wrapper_syn, text='Контекстные синонимы',command=w2v, bg = 'purple', fg = 'white')
w2v_btn.pack(fill='x', ipady=0, expand=1, side = BOTTOM)

natasha_btn = tk.Button(wrapper_syn, text='Слова окружения',command=natasha, bg = 'orange')
natasha_btn.pack(fill='x', ipady=0, expand=1, side = BOTTOM)

frame_func_btn = tk.Button(frame_left, text='Главное меню',command=lambda:show_frame(frame_right_func), bg = 'blue', fg = 'white')
frame_func_btn.pack(fill='y', ipadx=107, side = LEFT)

frame_bd_btn = tk.Button(frame_left, text='Новости',command=lambda:show_frame(frame_right_bd), bg = 'blue', fg = 'white')
frame_bd_btn.pack(fill='y', ipadx=107, side = LEFT)

frame_syn_btn = tk.Button(frame_left, text='Синонимы и слова',command=lambda:show_frame(frame_right_syn), bg = 'blue', fg = 'white')
frame_syn_btn.pack(fill='y',ipadx=107, side = LEFT)

frame_ton_btn = tk.Button(frame_left, text='Тональность',command=lambda:show_frame(frame_right_ton), bg = 'blue', fg = 'white')
frame_ton_btn.pack(fill='y',ipadx=107, side = LEFT)

my_tree_bd = ttk.Treeview(wrapper_bd, height="13")
my_tree_bd.pack(expand="yes")

my_tree_ton = ttk.Treeview(wrapper_ton, height="30")
my_tree_ton.pack(side = TOP, expand=0)

my_tree_bd['columns'] = ("ID", "NAME", "TEXT_NEWS", "DATE", "LINK", "LINK_VIDEO", "COMMENTS_COUNT")
my_tree_ton['columns'] = ("Sentence", "Tonality")
  
my_tree_bd.column("#0", width=0, stretch=NO)  
my_tree_bd.column("ID", anchor=CENTER, width=50)  
my_tree_bd.column("NAME", anchor=W , width=150)  
my_tree_bd.column("DATE", anchor=W, width=125)  
my_tree_bd.column("LINK", anchor=W, width=110)  
my_tree_bd.column("TEXT_NEWS", anchor=W, width=500) 
my_tree_bd.column("LINK_VIDEO",anchor=W, width=150)
my_tree_bd.column("COMMENTS_COUNT",anchor=W, width=110)

my_tree_bd.heading("#0", text="", anchor=CENTER) 
my_tree_bd.heading("ID", text="ID",anchor=CENTER)  
my_tree_bd.heading("NAME", text="Заголовок",anchor=CENTER)  
my_tree_bd.heading("DATE", text="Дата",anchor=CENTER)  
my_tree_bd.heading("LINK", text="Ссылка",anchor=CENTER) 
my_tree_bd.heading("TEXT_NEWS", text="Текст новости",anchor=CENTER)  
my_tree_bd.heading("LINK_VIDEO", text="Ссылка на видео", anchor=CENTER) 
my_tree_bd.heading("COMMENTS_COUNT", text="Комментарии", anchor=CENTER)

my_tree_ton.column("#0", width=0, stretch=NO)  
my_tree_ton.column("Sentence", anchor=W, width=1200)  
my_tree_ton.column("Tonality", anchor=W , width=100)  

my_tree_ton.heading("#0", text="", anchor=W) 
my_tree_ton.heading("Sentence", text="Предложение",anchor=CENTER)  
my_tree_ton.heading("Tonality", text="Тональность",anchor=CENTER)  

def record():
  my_tree_bd.delete(*my_tree_bd.get_children())
  cursor = c_news.find({})
  count=0
  for document in cursor:
    my_tree_bd.insert(parent='', index='end', iid=count, text="",values=(count,document["name_news"],document["text_news"],document["date_news"],document["link_news"], document["link_video"], document["comments_count"]))
    count+=1

def update_list_sen():
  my_list_sen.delete(0,'end')
  cursor = c_sentence.find({})
  count=1
  for document in cursor:
    my_list_sen.insert(END,str(count)+") "+ document["sentence"])
    count+=1

#update_sen_btn = Button(wrapper_sent, text='Показать',command=update_list_sen, bg = 'red', fg = 'white')
#update_sen_btn.pack(fill='x', expand="yes")

f = open('/home/vagrant/tomita-parser/build/bin/list_w2v.txt')
for line in f:
  line = line.replace('\n', '')
  my_list_per.insert(END,line)
f.close()
 
def update_tony():
  cursor1 = c_tonality.find({})
  for document in cursor1:
    my_tree_ton.insert(parent='', index='end', text="",values=(document["sentence"], document["tonality"]))


btn3 = Button(wrapper_ton, text='Анализ',command=analiz_tony, bg = 'blue2', fg = 'white')
btn3.pack(fill="both", side = LEFT, expand=1)

btn2 = Button(wrapper_ton, text="Показать",command=update_tony, bg = 'red', fg = 'white')
btn2.pack(fill="both", side = LEFT,  expand=1)

btn1 = Button(wrapper_bd, text='Показать',command=record, bg = 'red', fg = 'white')
btn1.pack(fill='x')

def select_record():
  id_box.delete(0, END)
  name_box.delete(0, END)
  date_box.delete(0, END)
  link_box.delete(0, END)
  com_box.delete(0, END)
  text_box.delete('1.0', END)
  video_box.delete(0, END)
  selected = my_tree_bd.focus()
  
  values = my_tree_bd.item(selected, 'values')
  
  id_box.insert(0, values[0])
  name_box.insert(1, values[1])
  date_box.insert(2, values[3])
  link_box.insert(3, values[4])
  text_box.insert('4.0', values[2])
  video_box.insert(5, values[5])
  com_box.insert(6, values[6])

def clicker(e):
  select_record()

il = Label(wrapper_elem_bd, text = "ID")
il.grid(row=0, column=0)

nl = Label(wrapper_elem_bd, text = 'Заголовок')
nl.grid(row=1,column=0)

dl = Label(wrapper_elem_bd, text = 'Дата')
dl.grid(row=2,column=0)

ll = Label(wrapper_elem_bd, text = 'Комментарии')
ll.grid(row=3,column=0)

ll = Label(wrapper_elem_bd, text = 'Ссылка')
ll.grid(row=4,column=0)

tl = Label(wrapper_elem_bd, text = 'Ссылка на видео')
tl.grid(row=5,column=0)

vl = Label(wrapper_elem_bd, text = 'Текст новости')
vl.grid(row=6,column=0)

id_box=Entry(wrapper_elem_bd, width=130)
id_box.grid(row=0,column=1,columnspan=5)

name_box=Entry(wrapper_elem_bd, width=130)
name_box.grid(row=1,column=1,columnspan=5)

date_box=Entry(wrapper_elem_bd, width=130)
date_box.grid(row=2,column=1,columnspan=5)

com_box=Entry(wrapper_elem_bd, width=130)
com_box.grid(row=3,column=1,columnspan=5)

link_box=Entry(wrapper_elem_bd, width=130)
link_box.grid(row=4,column=1,columnspan=5)

video_box=Entry(wrapper_elem_bd, width=130)
video_box.grid(row=5,column=1,columnspan=5)

text_box=Text(wrapper_elem_bd, width=130, height=9, fg='black', wrap=WORD)
text_box.grid(row=6,column=1,columnspan=5)

my_tree_bd.bind("<Double-1>", clicker)

show_frame(frame_right_func)



win.mainloop()