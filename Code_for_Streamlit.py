#!/usr/bin/env python
# coding: utf-8

from PIL import Image
import requests
from io import BytesIO
import streamlit as st
from scipy.stats import shapiro, f_oneway
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('_mpl-gallery')    # Настройка стиля гистограмм

st.title('Статистика болезней в компании')

action = st.radio("Загрузить файл или использовать тестовые данные?", ('Загрузить файл', 'Тестовые данные'))
if action == 'Загрузить файл':
    uploaded_file = st.file_uploader("Выберите файл с данными", type='csv')

if action == 'Тестовые данные':
    uploaded_file = 'https://raw.githubusercontent.com/vladimir-molotkov/m.video_test_task/main/test_data.csv'

if uploaded_file is None:
    image = Image.open(requests.get('https://drive.google.com/u/0/uc?id=1YfEK8WK4tkZasjYpFSIrqCQHCGg3LUxL&export=download', stream=True).raw)
    st.image(image, caption='Жду данные', width=300)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file);

    if data.shape[1] > 3:
        st.write('Проверьте файл. Слишком большое количество столбцов')

    st.subheader('Свойства данных')
    st.write(f'Размер данных - {data.shape[0]} строк.')

    st.subheader('Выберете значения для проверки гипотез')

    check_days = st.checkbox('Другое количество дней', value=False)
    if not check_days:
        work_days = st.slider('Количество дней (work_days)', min_value=0, max_value=10, value=2, step=1)
    else:
        work_days = st.number_input('Введите количество дней', min_value=0, max_value=366)

    check_age = st.checkbox('Другой возраст сотрудников', value=False)
    if not check_age:
        age = st.slider('Возраст (age)', min_value=18, max_value=60, value=35, step=1)
    else:
        age = st.number_input('Введите возраст', min_value=0, max_value=150)

    # Проверка гипотезы 1

    st.subheader('Проверка гипотезы 1.')
    st.write(f'Гипотеза 1: Мужчины пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще женщин.')
    data_male = data[data['Пол'] == "М"]['Количество больничных дней']
    data_female = data[data['Пол'] == "Ж"]['Количество больничных дней']

    check_chart_first = st.checkbox('Показать графики распределения величин в выборках для проверки гипотезы 1.', value=False)
    if check_chart_first:
        st.write('Распределение количества дней у мужчин.')
        st.bar_chart(data=data_male.value_counts())
        st.write('Распределение количества дней у женщин.')
        st.bar_chart(data=data_female.value_counts())
    
    data_male = data_male[data_male > work_days] \
        .reset_index() \
        .drop('index', axis=1)

    data_female = data_female[data_female > work_days] \
        .reset_index() \
        .drop('index', axis=1)

    st.write('Выборки имеют следующие характеристики.')
    st.write(pd.concat([
        data_male.rename({'Количество больничных дней': 'Количество больничных дней у мужчин'}, axis=1).describe(), 
        data_female.rename({'Количество больничных дней': 'Количество больничных дней у женщин'}, axis=1).describe()
    ], axis=1))


    stat, anova_p = f_oneway(data_male, data_female)
    st.write(f'ANOVA p-value = {round(anova_p[0], 4)}')

    if anova_p < 0.05:
        st.write(' Гипотеза 1 отклонена. Нет значимых различий между межчинами и женщинами.')
    elif data_male['Количество больничных дней'].mean() > data_female['Количество больничных дней'].mean():
        st.write(f'Гипотеза 1 подтверждена. Мужчины пропускают по болезни более {work_days} дней в течение года значимо чаще женщин.')
    else:
        st.write(f'Гипотеза 1 отклонена. Женщины пропускают по болезни более {work_days} дней в течение года значимо чаще мужчин.')

    # Проверка гипотезы 2

    st.subheader('Проверка гипотезы 2.')
    st.write(f'Гипотеза 2: Работники старше {age} лет пропускают в течение года более {work_days} рабочих дней по болезни значимо чаще своих более молодых коллег.')

    data_old = data[data['Возраст'] > age]['Количество больничных дней']
    data_young = data[data['Возраст'] <= age]['Количество больничных дней']


    check_chart_second = st.checkbox('Показать графики распределения величин в выборках для проверки гипотезы 2.', value=False)
    if check_chart_second:
        st.write(f'Распределение количества дней у работников старше {age} лет.')
        st.bar_chart(data=data_old.value_counts())
        st.write(f'Распределение количества дней у работников младше {age} лет.')
        st.bar_chart(data=data_young.value_counts())

    data_old = pd.DataFrame(data_old[data_old > work_days]) \
        .reset_index() \
        .drop('index', axis=1)

    data_young = pd.DataFrame(data_young[data_young > work_days]) \
    .reset_index() \
    .drop('index', axis=1)


    st.write('Выборки имеют следующие характеристики.')
    st.write(pd.concat([data_old.rename({'Количество больничных дней': 'Больничных дни у работников старше 35 лет'}, axis=1).describe(), 
               data_young.rename({'Количество больничных дней': 'Больничных дни у работников младше 35 лет'}, axis=1).describe()], axis=1))


    stat, anova_p = f_oneway(data_old, data_young)
    st.write(f'ANOVA p-value = {round(anova_p[0], 4)}')

    if anova_p < 0.05:
        st.write(f'Гипотеза 2 отклонена. Нет значимых различий между работниками старше и младше {age} лет.')
    elif data_old['Количество больничных дней'].mean() > data_young['Количество больничных дней'].mean():
        st.write(f'Гипотеза 2 подтверждена. Работники старше {age} лет пропускают более {work_days} дней в течение года значимо чаще молодых коллег.')
    else:
        st.write(f'Гипотеза 2 отклонена. Работники младше {age} лет пропускают более {work_days} дней в течение года значимо чаще страших коллег.')
