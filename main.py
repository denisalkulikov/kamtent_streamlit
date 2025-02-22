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

# Чекбокс для юридического лица
is_legal_entity = st.checkbox("Юридическое лицо")

# Чекбокс для скидки
apply_discount = st.checkbox("Предоставить скидку")

# Поле для ввода скидки (появляется, если чекбокс выбран)
discount_percent = 0
if apply_discount:
    discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

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

    # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
    if is_legal_entity:
        cost = cost * 0.25 +cost
        #cost = int(cost // 100 * 100)  # Округляем до сотен

    # Применяем скидку, если она указана
    if discount_percent > 0:
        cost *= (1 - discount_percent / 100)
        cost = int(cost // 100 * 100)  # Округляем до сотен

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

# Добавляем CSS для адаптации таблицы под тёмную тему
html = f"""
<style>
    table {{
        width: 100%;
        border-collapse: collapse;
        color: white;  /* Цвет текста в таблице */
        background-color: #262730;  /* Цвет фона таблицы */
    }}
    th, td {{
        border: 1px solid #444;  /* Границы ячеек */
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #1c1c24;  /* Цвет фона заголовков */
        color: white;  /* Цвет текста в заголовках */
    }}
    td {{
        background-color: #262730;  /* Цвет фона ячеек */
        color: white;  /* Цвет текста в ячейках */
    }}
</style>
{html_table}
"""

# Выводим таблицу с помощью st.markdown
st.markdown(html, unsafe_allow_html=True)