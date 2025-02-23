import streamlit as st
import pandas as pd
import math


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
def page_auto_calculator():
    st.title("Калькулятор авто")

    # Ваш код для другого калькулятора
    st.write("Калькулятор ещё в процессе доработки...")

    # Словарь с ценами на материалы
    price = {
        'pvh_630': 250,
         'pvh_650': 385,
         'pvh_750': 450,
         'pvh_900': 500,
         'fanera_21_2': 5500,
         'fanera_21_3': 9400,
         'fanera_18': 4700,
         'petlya_gaz': 270,
         'petlya_kamaz': 530,
         'zamki_gaz': 2500,
         'zamki_kamaz': 2900,
         'uplotnitel_18': 290,
         'uplotnitel_21': 400,
         'work': 550,
         'truba_30_30_2': 874,
         'truba_60_40_3': 1752,
         'kronshtein': 212.4,
         'shveler': 1075.3,
         'podship_big': 60,
         'podship_small': 60,
         'amortizator': 1300,
         'fiksator': 250,
         'profil': 1300,
         'plastina_650': 350,
         'plastina_black': 70,
         'gaika_m14': 6.57,
         'bolt_10_20': 3.98,
         'bolt_12_30': 7.3,
         'du_15': 700,
         'shnur_8': 70,
         'remeshok': 80,
         'tros': 150,
         'shtorn_profil': 1200,
         'babochka': 100,
         'reklama': 750,
         'truba_40_40_3': 1374,
         'truba_40_40_2': 960,
         'truba_40_20_2': 702,
         'doska': 205,
         'truba_60_40_2': 1200
    }

    # Ввод данных
    length = st.number_input("Введите длину (м)", value=1.0, min_value=0.01)
    width = st.number_input("Введите ширину (м)", value=1.0, min_value=0.01)
    height_g = st.number_input("Введите высоту готовой стенки (м)", value=1.0, min_value=0.01)

    # Чекбоксы для ворот и щита
    col1, col2 = st.columns(2)  # Разделяем на две колонки
    with col1:
        is_vorota = st.checkbox("Наличие ворот")
        is_schit = st.checkbox("Наличие щита")
    with col2:
        is_legal_entity = st.checkbox("Юридическое лицо")
        apply_discount = st.checkbox("Предоставить скидку")

    # Поле для ввода скидки (появляется, если чекбокс выбран)
    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

    # Функция для расчёта площади изделия
    def calculate_area(length, width, height_g, is_vorota, is_schit):
        # Площадь ткани
        if is_vorota and is_schit:
            sq = (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            sq = (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            sq = (length * height_g * 2) + (width * height_g * 2) + (length * width)
        return sq

    # Функция для расчёта стоимости ткани
    def calculate_cost(material_price, area, is_legal_entity, discount_percent):
        # Стоимость ткани
        if length < 5:
            cost = material_price * 2.8
        elif length > 10:
            cost = material_price * 2.4
        else:
            cost = material_price * 2.6
        cost -= cost % -10
        cost = cost * area

        # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
        if is_legal_entity:
            cost *= 1.25

        # Применяем скидку, если она указана
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        # Округляем до сотых в большую сторону
        cost -= cost % -100
        return cost

    # Функция для расчёта стоимости "Тент (чулок)"
    def calculate_chulok_cost(material_price, area, length, is_legal_entity, discount_percent):
        # Стоимость ткани
        fabric_cost = material_price * area
        fabric_cost -= fabric_cost % -100

        # Количество бабочек
        babochka_count = ((round(length / 0.65)) - 6) * 3 + 6 * 5

        # Стоимость бабочек
        babochka_cost = babochka_count * price['babochka']

        # Стоимость работы
        work_cost = price['work'] * (length / 0.4)

        # Итоговая стоимость
        total_cost = (fabric_cost + babochka_cost + work_cost) * 2

        # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
        if is_legal_entity:
            total_cost *= 1.25

        # Применяем скидку, если она указана
        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        # Округляем до сотых в большую сторону
        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости "Тент сдвижной крыши"
    def calculate_sdvizhnoy_krysha_cost(material_price, length, width, is_legal_entity, discount_percent):
        # Площадь крыши
        s_krysha = (length + 0.6) * (width + 0.6)

        # Длина шнура
        p_shnur = length * 2 + 2

        # Количество пластин 650
        if math.ceil((length - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2) + 1

        # Количество ремешков
        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20

        # Длина усилителя
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width * 0.1) + ((length * 2 + width * 2) * 0.15)

        # Количество работы
        count_work = length * 1.5

        # Итоговая стоимость
        total_cost = (
            s_krysha * material_price +  # Стоимость ткани
            p_shnur * price['shnur_8'] +   # Стоимость шнура
            count_remeshki * price['remeshok'] +  # Стоимость ремешков
            p_usilitel * material_price +  # Стоимость усилителя
            count_work * price['work']  # Стоимость работы
        )

        # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
        if is_legal_entity:
            total_cost *= 1.25

        # Применяем скидку, если она указана
        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        # Округляем до сотых в большую сторону
        total_cost = total_cost * 1.7
        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости тента с рекламой
    def calculate_reklama_cost(reklama_area, total_area, material_price, length, is_legal_entity, discount_percent):
        # Стоимость рекламы
        reklama_cost = reklama_area * price['reklama']

        # Стоимость ткани
        fabric_cost = (total_area - reklama_area) * material_price

        # Стоимость работы
        work_cost = (length / 0.27) * price['work']

        # Итоговая стоимость
        total_cost = (reklama_cost + fabric_cost + work_cost) * 2

        # Увеличиваем стоимость на 25%, если выбрано юридическое лицо
        if is_legal_entity:
            total_cost *= 1.25

        # Применяем скидку, если она указана
        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        # Округляем до сотых в большую сторону
        total_cost -= total_cost % -100
        return total_cost

    # Рассчитываем площадь
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

    # Площади для рекламы
    reklama_2_stenki = length * height_g * 2
    reklama_2_stenki_and_klapan = (length * height_g * 2) + (width * height_g)
    reklama_2_stenki_and_krysha = (length * height_g * 2) + (length * width)
    reklama_2_stenki_and_klapan_and_krysha = (length * height_g * 2) + (width * height_g) + (length * width)

    # Создаём список для хранения результатов
    results_typical = []  # Для типового тента
    results_chulok = []   # Для тента (чулок)
    results_sdvizhnoy = []  # Для тента сдвижной крыши
    results_reklama_2_stenki = []  # Для тента с рекламой (2 стенки)
    results_reklama_2_stenki_and_klapan = []  # Для тента с рекламой (2 стенки + клапан)
    results_reklama_2_stenki_and_krysha = []  # Для тента с рекламой (2 стенки + крыша)
    results_reklama_2_stenki_and_klapan_and_krysha = []  # Для тента с рекламой (2 стенки + клапан + крыша)

    # Расчёт для каждого материала
    for material, material_price in price.items():
        if material not in ['babochka', 'work', 'shnur_8', 'remeshok', 'reklama']:  # Исключаем бабочки, работу, шнур, ремешки и рекламу
            # Стоимость для типового тента
            cost_typical = calculate_cost(material_price, area, is_legal_entity, discount_percent)
            results_typical.append(cost_typical)

            # Стоимость для тента (чулок)
            cost_chulok = calculate_chulok_cost(material_price, area, length, is_legal_entity, discount_percent)
            results_chulok.append(cost_chulok)

            # Стоимость для тента сдвижной крыши
            cost_sdvizhnoy = calculate_sdvizhnoy_krysha_cost(material_price, length, width, is_legal_entity, discount_percent)
            results_sdvizhnoy.append(cost_sdvizhnoy)

            # Стоимость для тента с рекламой (2 стенки)
            cost_reklama_2_stenki = calculate_reklama_cost(reklama_2_stenki, area, material_price, length, is_legal_entity, discount_percent)
            results_reklama_2_stenki.append(cost_reklama_2_stenki)

            # Стоимость для тента с рекламой (2 стенки + клапан)
            if not is_vorota:
                cost_reklama_2_stenki_and_klapan = calculate_reklama_cost(reklama_2_stenki_and_klapan, area, material_price, length, is_legal_entity, discount_percent)
                results_reklama_2_stenki_and_klapan.append(cost_reklama_2_stenki_and_klapan)
            else:
                results_reklama_2_stenki_and_klapan.append("НЕВЕРНО!")

            # Стоимость для тента с рекламой (2 стенки + крыша)
            cost_reklama_2_stenki_and_krysha = calculate_reklama_cost(reklama_2_stenki_and_krysha, area, material_price, length, is_legal_entity, discount_percent)
            results_reklama_2_stenki_and_krysha.append(cost_reklama_2_stenki_and_krysha)

            # Стоимость для тента с рекламой (2 стенки + клапан + крыша)
            if not is_vorota:
                cost_reklama_2_stenki_and_klapan_and_krysha = calculate_reklama_cost(reklama_2_stenki_and_klapan_and_krysha, area, material_price, length, is_legal_entity, discount_percent)
                results_reklama_2_stenki_and_klapan_and_krysha.append(cost_reklama_2_stenki_and_klapan_and_krysha)
            else:
                results_reklama_2_stenki_and_klapan_and_krysha.append("НЕВЕРНО!")

    # Создаём DataFrame для основной таблицы
    results_df = pd.DataFrame({
        "Тент": [
            "Тент типовой",
            "Тент сдвижной крыши",
            "Тент (чулок)",
        ],
        "ПВХ630": [
            results_typical[0],
            results_sdvizhnoy[0],
            results_chulok[0],
        ],
        "ПВХ650": [
            results_typical[1],
            results_sdvizhnoy[1],
            results_chulok[1],
        ],
        "ПВХ750": [
            results_typical[2],
            results_sdvizhnoy[2],
            results_chulok[2],
        ],
        "ПВХ900": [
            results_typical[3],
            results_sdvizhnoy[3],
            results_chulok[3],
        ],
    })

    # Создаём DataFrame для таблицы с рекламой
    reklama_df = pd.DataFrame({
        "Тент с рекламой": [
            "Реклама на 2-х стенках",
            "Реклама на 2-х стенках и клапане",
            "Реклама на 2-х стенках и крыше",
            "Реклама на 2-х стенках, клапане и крыше"
        ],
        "ПВХ650": [
            results_reklama_2_stenki[1],
            results_reklama_2_stenki_and_klapan[1],
            results_reklama_2_stenki_and_krysha[1],
            results_reklama_2_stenki_and_klapan_and_krysha[1]
        ],
    })

    # Функция для форматирования стоимости с разделением на разряды
    def format_cost(cost):
        if cost == "НЕВЕРНО!":
            return cost
        return "{:,.2f} руб".format(cost).replace(",", " ")

    # Применяем форматирование к столбцам с ценами
    for col in ["ПВХ630", "ПВХ650", "ПВХ750", "ПВХ900"]:
        results_df[col] = results_df[col].apply(format_cost)

    for col in ["ПВХ650"]:
        reklama_df[col] = reklama_df[col].apply(format_cost)

    # Выводим основную таблицу
    st.dataframe(
        results_df,
        hide_index=True,  # Скрываем индексы
        use_container_width=True  # Растягиваем таблицу на всю ширину контейнера
    )

    # Выводим таблицу с рекламой
    st.dataframe(
        reklama_df,
        hide_index=True,  # Скрываем индексы
        use_container_width=True  # Растягиваем таблицу на всю ширину контейнера
    )


# Функция для третьей страницы (информация)
def page_info():
    st.title("Ещё калькулятор")

    # Ваш код для страницы с информацией
    st.write("Место для ещё какого-нибудь калькулятора...")


# Боковое меню для навигации
st.sidebar.title("Меню")
page = st.sidebar.radio("Выберите страницу", ["Калькулятор пологов", "Калькулятор авто", "Ещё калькулятор"])

# Отображение выбранной страницы
if page == "Калькулятор пологов":
    page_polog_calculator()
elif page == "Калькулятор авто":
    page_auto_calculator()
elif page == "Ещё калькулятор":
    page_info()