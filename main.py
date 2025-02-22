import streamlit as st
import pandas as pd


# Функция для первой страницы (калькулятор пологов)
def page_polog_calculator():
    st.title("Калькулятор пологов")

    # Ваш код для калькулятора пологов
    #st.write("Здесь будет калькулятор пологов...")
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
    #st.title("Программа для расчёта пологов")

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

    # Функция для расчёта стоимости одного полога
    def calculate_cost(material_price, length, width, count):
        # Площадь полога с учётом припусков
        sq_pol = (length + 0.2) * (width + 0.2)
        # Количество люверсов
        luvers_pol = (length * 2 + width * 2) / 0.3
        luvers_pol -= luvers_pol % -1  # Округляем до целого числа
        # Расчёт стоимости
        cost = ((sq_pol * material_price) + (luvers_pol * price_polog['luver']) + (
                    sq_pol * 0.2 * price_polog['work'])) * 2.5
        cost -= cost % -100  # Округляем до сотен

        # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
        if is_legal_entity:
            cost = cost * 0.25 + cost
            # cost = int(cost // 100 * 100)  # Округляем до сотен

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
                'Стоимость за 1 изделие': cost_per_item,  # Числовое значение
                'Стоимость за все изделия': total_cost  # Числовое значение
            })

    # Преобразуем результаты в DataFrame
    results_df = pd.DataFrame(results)

    # Убираем индексы из DataFrame
    results_df.reset_index(drop=True, inplace=True)

    # Функция для форматирования стоимости с разделением на разряды
    def format_cost(cost):
        return "{:,.2f} руб".format(cost).replace(",", " ")

    # Применяем форматирование к столбцам с ценами
    results_df['Стоимость за 1 изделие'] = results_df['Стоимость за 1 изделие'].apply(format_cost)
    results_df['Стоимость за все изделия'] = results_df['Стоимость за все изделия'].apply(format_cost)

    # Выводим таблицу с помощью st.dataframe
    st.dataframe(
        results_df,
        hide_index=True,  # Скрываем индексы
        use_container_width=True  # Растягиваем таблицу на всю ширину контейнера
    )


# Функция для второй страницы (другой калькулятор)
def page_another_calculator():
    st.title("Другой калькулятор")

    # Ваш код для другого калькулятора
    st.write("Здесь будет другой калькулятор...")


# Функция для третьей страницы (информация)
def page_info():
    st.title("Информация")

    # Ваш код для страницы с информацией
    st.write("Здесь будет информация о приложении...")


# Боковое меню для навигации
st.sidebar.title("Меню")
page = st.sidebar.radio("Выберите страницу", ["Калькулятор пологов", "Другой калькулятор", "Информация"])

# Отображение выбранной страницы
if page == "Калькулятор пологов":
    page_polog_calculator()
elif page == "Другой калькулятор":
    page_another_calculator()
elif page == "Информация":
    page_info()