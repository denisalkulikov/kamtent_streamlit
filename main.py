import streamlit as st
import pandas as pd

# Словарь с ценами материалов
price_polog = {
    'pp': 100,
    'brezent': 200,
    'pvh_300': 140,
    'pvh_500': 145,
    'pvh_630': 190,
    'pvh_650': 330,
    'pvh_900': 400,
    'setka_green': 50,
    'setka_not_green': 500,
    'tafeta_and_brezent': 250,
    'plenka': 650,
    'tafeta_and_oksford': 280,
    'oksford': 190,
    'luver': 10,
    'work': 550
}

# Словарь с русскими названиями материалов
material_names = {
    'pp': 'ПП',
    'brezent': 'Брезент',
    'pvh_300': 'ПВХ300',
    'pvh_500': 'ПВХ500',
    'pvh_630': 'ПВХ630',
    'pvh_650': 'ПВХ650',
    'pvh_900': 'ПВХ900',
    'setka_green': 'Сетка зелёная',
    'setka_not_green': 'Сетка не зелёная',
    'tafeta_and_brezent': 'Тафета+брезент',
    'plenka': 'Плёнка',
    'tafeta_and_oksford': 'Тафета+оксфорд',
    'oksford': 'Оксфорд'
}

# Заголовок приложения
st.title("Программа для расчёта пологов")

# Ввод данных
length = st.number_input("Введите длину изделия (м)", value=1.0, min_value=0.01)
width = st.number_input("Введите ширину изделия (м)", value=1.0, min_value=0.01)
count = st.number_input("Введите количество изделий", value=1, min_value=1, step=1)

# Функция для форматирования стоимости с разделением на разряды
def format_cost(cost):
    return "{:,.2f} руб".format(cost).replace(",", " ")

# Функция для расчёта стоимости одного полога
def calculate_cost(material_price, length, width, count):
    # Площадь полога с учётом припусков
    sq_pol = (length + 0.2) * (width + 0.2)
    # Количество люверсов
    luvers_pol = (length * 2 + width * 2) / 0.3
    luvers_pol -= luvers_pol % -1  # Округляем до целого числа
    # Расчёт стоимости
    cost = ((sq_pol * material_price) + (luvers_pol * price_polog['luver']) + (sq_pol * 0.2 * price_polog['work'])) * 2.5
    cost -= cost % -100  # Округляем до сотен
    total_cost = cost * count
    return cost, total_cost

# Создаём список для хранения результатов
results = []

# Расчёт для каждого материала
for material, price in price_polog.items():
    if material not in ['luver', 'work']:  # Исключаем люверсы и работу из расчётов
        cost_per_item, total_cost = calculate_cost(price, length, width, count)
        results.append({
            'Материал': material_names[material],  # Используем русские названия
            'Стоимость за 1 изделие': format_cost(cost_per_item),
            'Стоимость за все изделия': format_cost(total_cost)
        })

# Преобразуем результаты в DataFrame
results_df = pd.DataFrame(results)

# Убираем индексы из DataFrame
results_df.reset_index(drop=True, inplace=True)

# Создаём HTML-таблицу без индексов
html_table = results_df.to_html(index=False)

# Добавляем CSS для скрытия индексов и улучшения отображения таблицы
html = f"""
<style>
    table {{
        width: 100%;
        border-collapse: collapse;
    }}
    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #f2f2f2;
    }}
</style>
{html_table}
"""

# Выводим таблицу с помощью st.markdown
st.markdown(html, unsafe_allow_html=True)