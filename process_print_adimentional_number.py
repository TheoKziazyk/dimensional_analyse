#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
Created on Fri May 22 12:04:53 2020

@author: kz
"""

import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd

OUTPUT_CSV = '1-2.csv'
OUTPUT_TEX = '1-2.tex'

def open_data(file_path):
    """ read a csv file, return a dataframe """
    print(file_path)
    dataframe = pd.read_csv(file_path[0], sep=',')
    try:
        dataframe = pd.read_csv(file_path[0], sep=',',
                                index_col='dim_numb', encoding='utf-8')
 #       dataframe = pd.read_csv(file_path, sep=',')
    except Exception as error:
        print(error)
        print("error while reading csv file")
        return None
    else:
        return dataframe

def define_filename():
    """ open file dialog to choose files, return list of files path """
    root = tk.Tk()
    root.withdraw()
    file_name = filedialog.askopenfilename()
    return file_name

def transform_column(df, index, index_row, list):
    """ Transform the column in order to reach the id matrice
    input : dataframe, index of column, index of row, the target column as list
    return datafram"""
    for i in range(len(list)):
        if list[i] != 0 and i != index:
            a = list[i] / list[index]
            df.loc[index_row[i]] -= a*df.loc[index_row[index]]
    df.loc[index_row[index]] = df.loc[index_row[index]]/df.loc[index_row[index]][index]
    return df

def preambule(*packages):
    """ input : packages: strings of package to add in a latex file
    return a string to add in the latex file """
    p = ""
    for i in packages:
        p = ''.join((p, "\\usepackage{", i, "}\n"))
    return p

def start_doc():
    """ return a string to start a latex document """
    s = "\\documentclass[12pt,a4paper,french,twocolumn]{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n"
    s = ''.join((s,
                 preambule('amsmath', 'lmodern', 'babel', 'booktabs',
                           'geometry', 'adjustbox', 'multicol',),
                 "\geometry{hmargin=1cm,vmargin=1cm}\n\\begin{document}\n"))
    return s

def end_doc():
    """ return a string to end a latex document """
    s = "\n\\end{document}"
    return s

def get_adi_number(df, body, i):
    """ Create an adimentional number with a matrice of variables transformed Buckingham theorem
    return a string of the adimentional number writing in latex"""
    res_var = df.columns[df.shape[0]+i]
    s = ''.join(('\[\pi_{', str(i), '}= '))
    den, num = "", res_var
    print(res_var)
    list = df[res_var]
    cnt = 0
    for i in list:
        reap_var = df.columns[cnt]
        power = str(abs(round(i, 2)))
        if i > 0:
            if power == 1.0:
                den = ''.join((den, reap_var))
            else:
                den = ''.join((den, reap_var, '^{', power, '}'))
        elif i < 0:
            if power == 1.0:
                num = ''.join((num, reap_var))
            else:
                num = ''.join((num, reap_var, '^{', power, '}'))
        cnt += 1
    frac = ''.join(('\\frac{', num, '}{', den, '}'))
    s = ''.join((s, frac, '\]\n'))
    return s

def save_file(df, name):
    """ save a dataframe with at the name set"""
    df.to_csv(name)

file_name = define_filename(),
df = open_data(file_name)
print(df)
for i in range(df.shape[0]):
    df = transform_column(df, i, df.index, df[df.columns[i]])
df = df.round(2)
print(df)
save_file(df, OUTPUT_CSV)
START = start_doc()
END = end_doc()
BODY = ''.join(('\n\\begin{table}\n\\begin{adjustbox}{angle=90}\n',
                df.to_latex(index=True, bold_rows=True,),
                '\\end{adjustbox}\n\\end{table}\n'))
for i in range(df.shape[1]-df.shape[0]):
    BODY = ''.join((BODY, get_adi_number(df, BODY, i)))
if os.path.exists(OUTPUT_TEX):
    os.remove(OUTPUT_TEX)
file = open(OUTPUT_TEX, "x") # "x" pour la création et l'écriture
file.write(''.join((START, BODY, END)))
file.close()
os.system(''.join(("pdflatex ", OUTPUT_TEX)))
os.system(''.join(("xdg-open ", OUTPUT_TEX[:-4], ".pdf")))
