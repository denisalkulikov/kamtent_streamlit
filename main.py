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
    st.title("Калькулятор продукции на авто")

    # Ваш код для другого калькулятора
    st.write("Цены актуальны на 07.03.2025")

    # Словарь с ценами на материалы
    price = {
        'pvh_630': 250,
        'pvh_650': 385,
        'pvh_750': 450,
        'pvh_900': 500,
        'fanera_21_2': 3515,
        'fanera_21_3': 6900,
        'fanera_18': 2870,
        'petlya_gaz': 650,
        'petlya_kamaz': 850,
        'zamki_gaz': 3100,
        'zamki_kamaz': 4200,
        'uplotnitel_18': 290,
        'uplotnitel_21': 400,
        'work': 550,
        'truba_30_30_2': 762,
        'truba_60_40_3': 1854,
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
        'truba_40_40_3': 1440,
        'truba_40_40_2': 1014,
        'truba_40_20_2': 756,
        'doska': 205,
        'truba_60_40_2': 1374,
        'lenta_F1300': 60,
        'rolik_sdvig': 500,
        'zamok_so_stropoi': 450,
        'mehanizm_natyascheniya': 7600,
        'profil_allum': 2000,
        'perehodnik_profilya': 1200,
        'luvers_40': 25,
        'espander': 100,
        'kruchok_s': 30,
        'luvers_12': 10

    }

    # Ввод данных
    length = st.number_input("Введите длину (м)", value=1.0, min_value=0.01)
    width = st.number_input("Введите ширину (м)", value=1.0, min_value=0.01)
    height_p = st.number_input("Введите полезную высоту (м)", value=1.0, min_value=0.01)
    height_g = st.number_input("Введите высоту готовой стенки (м)", value=1.0, min_value=0.01)
    height_b = st.number_input("Введите высоту борта (м)", value=1.0, min_value=0.01)
    count_s = st.number_input("Введите количество стоек (шт)", value=1, min_value=1, step=1)
    marka = st.selectbox("Выберите марку авто", ("Газель", "Иное"), index=None, placeholder="Выбрать вариант")

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

    # Функция для расчёта стоимости МСК (пластины), Шторного механизма, Троса и Демонтажа тента
    def calculate_additional_costs(length, width, height_p, is_vorota, is_schit, price):
        # Расчёт периметров с использованием полезной высоты (height_p)
        perimetr_total = length * 2 + width * 2 + height_p * 4
        perimetr_half = length * 2 + width * 2 + height_p * 2
        perimetr_min = length * 2 + width * 2

        # Расчёт количества кронштейнов
        if math.ceil(length / 0.65 * 2) % 2 == 0:
            kronshtein_count = math.ceil(length / 0.65 * 2)
        else:
            kronshtein_count = math.ceil(length / 0.65 * 2) + 1

        # Расчёт количества труб и других компонентов
        truba_30_30_count = (kronshtein_count / 2 * 2.55) / 6
        truba_30_30_count -= truba_30_30_count % -1
        truba_60_40_count = length / 6 * 2
        truba_60_40_count -= truba_60_40_count % -1
        shveler_count = length / 2.48 * 2
        shveler_count -= shveler_count % -1
        podshipnig_b_count = kronshtein_count
        podshipnik_s_count = kronshtein_count * 2
        gaika_count = kronshtein_count * 2
        bolt_10_count = kronshtein_count
        bolt_12_count = kronshtein_count * 2

        # Расчёт количества пластин
        if math.ceil((length - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2) + 1
        count_plastin_black = count_plastin_650 + 2

        # Расчёт стоимости МСК (пластины)
        msk_cost = int((kronshtein_count * price['kronshtein'] +
                        truba_30_30_count * price['truba_30_30_2'] +
                        truba_60_40_count * price['truba_60_40_3'] +
                        shveler_count * price['shveler'] +
                        podshipnig_b_count * price['podship_big'] +
                        podshipnik_s_count * price['podship_small'] +
                        gaika_count * price['gaika_m14'] +
                        bolt_10_count * price['bolt_10_20'] +
                        bolt_12_count * price['bolt_12_30'] +
                        count_plastin_650 * price['plastina_650'] +
                        count_plastin_black * price['plastina_black'] +
                        2 * price['fiksator'] +
                        2 * price['amortizator'] +
                        48 * price['work'] +
                        length * 6 * price['work']) * 2)

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            msk_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            msk_cost *= (1 - discount_percent / 100)

        msk_cost -= msk_cost % -100

        # Расчёт стоимости Шторного механизма
        shtorn_profile_count = length / 6 * 2
        shtorn_profile_count -= shtorn_profile_count % -1
        shtorn_work_count = length * 0.73
        shtorn_work_count -= shtorn_work_count % -1
        shtornik_cost = int((shtorn_profile_count * price['shtorn_profil'] + shtorn_work_count * price['work']) * 2)

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            shtornik_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            shtornik_cost *= (1 - discount_percent / 100)

        shtornik_cost -= shtornik_cost % -100

        # Расчёт стоимости Троса с использованием полезной высоты (height_p)
        if is_vorota and is_schit:
            tros_cost = int(perimetr_total * price['tros'] * 1.5)
        elif not is_vorota and not is_schit:
            tros_cost = int(perimetr_min * price['tros'] * 1.5)
        else:
            tros_cost = int(perimetr_half * price['tros'] * 1.5)

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            tros_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            tros_cost *= (1 - discount_percent / 100)

        tros_cost -= tros_cost % -100

        # Расчёт стоимости Демонтажа тента
        demontazh_tenta_cost = int(length * 0.6 * price['work'])

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            demontazh_tenta_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            demontazh_tenta_cost *= (1 - discount_percent / 100)

        demontazh_tenta_cost -= demontazh_tenta_cost % -100

        return msk_cost, shtornik_cost, tros_cost, demontazh_tenta_cost

    # Функция для расчёта стоимости ворот
    def calculate_vorota_cost(width, height_g, marka, price, is_legal_entity, discount_percent):
        # Расчёт количества рамок и запоров
        ramka_vorot = (width * 2 + height_g * 2) / 6
        ramka_vorot -= ramka_vorot % -1
        zapory_count = width * 2 / 6
        zapory_count -= zapory_count % -1

        # Расчёт стоимости ворот для Газели
        vorota_gazel = int((price['fanera_18'] * 2 +
                            price['petlya_gaz'] * 6 +
                            price['zamki_gaz'] * 2 +
                            (width * 2 + height_g * 3) * price['uplotnitel_18']) +
                            ramka_vorot * price['truba_60_40_3'] +
                            zapory_count * price['du_15'] +
                            32 * price['work']) * 2
        vorota_gazel -= vorota_gazel % -100

        # Расчёт стоимости ворот для Камаза
        vorota_kamaz = int((price['fanera_21_2'] * 2 +
                            price['petlya_kamaz'] * 8 +
                            price['zamki_kamaz'] * 2 +
                            (width * 2 + height_g * 3) * price['uplotnitel_21']) +
                            ramka_vorot * price['truba_60_40_3'] +
                            zapory_count * price['du_15'] +
                            32 * price['work']) * 2
        vorota_kamaz -= vorota_kamaz % -100

        # Расчёт стоимости ворот для других марок
        vorota_other = int((price['fanera_21_3'] * 2 +
                            price['petlya_kamaz'] * 8 +
                            price['zamki_kamaz'] * 2 +
                            (width * 2 + height_g * 3) * price['uplotnitel_21']) +
                            ramka_vorot * price['truba_60_40_3'] +
                            zapory_count * price['du_15'] +
                            32 * price['work']) * 2
        vorota_other -= vorota_other % -100

        # Выбор стоимости ворот в зависимости от марки авто
        if marka == "Газель":
            vorota_cost = vorota_gazel
        elif marka == "Иное" and height_g > 2.4:
            vorota_cost = vorota_other
        elif marka == "Иное" and height_g <= 2.4:
            vorota_cost = vorota_kamaz
        else:
            vorota_cost = 0  # Если марка не выбрана

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            vorota_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            vorota_cost *= (1 - discount_percent / 100)

        vorota_cost -= vorota_cost % -100

        return vorota_cost

    # Функция для расчёта сдвижных стенок
    def calculate_sdvig_stenki_cost(length, height_g, price, is_legal_entity, discount_percent):
        # Расчёт составляющих частей
        square_sdvig_stenok = (length + 0.9) * height_g + (length + 0.9)
        rolik_sd = round(length / 0.55)
        zamok = round(length / 0.55)
        lenta = (rolik_sd * (height_g + 0.2)) + length
        mehanizm = 2
        profil = 2
        perehodnik = 4
        luver_40 = math.ceil(length / 0.2)
        luver_40 -= luver_40 % -10
        espander = math.ceil(length * 1.25)
        kruchok = math.ceil(luver_40 / 2)
        luver_12 = math.ceil(length / 0.2)
        luver_12 -= luver_12 % -10
        rabota = length * 1.1

        # Расчёт стоимости сдвижных стенок (базовый вариант)
        sdvig_stenki_cost = (square_sdvig_stenok * price['pvh_630'] + rolik_sd * price['rolik_sdvig'] +
                             zamok * price['zamok_so_stropoi'] + lenta * price['lenta_F1300'] + luver_40 * price[
                                 'luvers_40'] +
                             espander * price['espander'] + kruchok * price['kruchok_s'] + luver_12 * price[
                                 'luvers_12'] +
                             rabota * price['work'] + profil * price['profil_allum'] + perehodnik * price[
                                 'perehodnik_profilya'] +
                             mehanizm * price['mehanizm_natyascheniya'])

        sdvig_stenki_cost = sdvig_stenki_cost * 2  # добавляем вторую стенку
        sdvig_stenki_cost = sdvig_stenki_cost * 1.8  # добавляем коэффициент
        sdvig_stenki_cost -= sdvig_stenki_cost % 100

        # Расчёт стоимости сдвижных стенок с фурнитурой клиента
        sdvig_stenki_furnitura_cost = (square_sdvig_stenok * price['pvh_630'] +
                                       lenta * price['lenta_F1300'] +
                                       rabota * price['work'])

        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * 2  # добавляем вторую стенку
        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * 1.8  # добавляем коэффициент
        sdvig_stenki_furnitura_cost -= sdvig_stenki_furnitura_cost % 100

        # Расчёт стоимости сдвижных стенок с люверсами
        sdvig_stenki_luvers_cost = (square_sdvig_stenok * price['pvh_630'] +
                                    luver_40 * price['luvers_40'] +
                                    luver_12 * price['luvers_12'] +
                                    kruchok * price['kruchok_s'] +
                                    espander * price['espander'] +
                                    rabota * price['work'])

        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * 2  # добавляем вторую стенку
        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * 1.8  # добавляем коэффициент
        sdvig_stenki_luvers_cost -= sdvig_stenki_luvers_cost % 100

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            sdvig_stenki_cost *= 1.2
            sdvig_stenki_furnitura_cost *= 1.2
            sdvig_stenki_luvers_cost *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            sdvig_stenki_cost *= (1 - discount_percent / 100)
            sdvig_stenki_furnitura_cost *= (1 - discount_percent / 100)
            sdvig_stenki_luvers_cost *= (1 - discount_percent / 100)

        sdvig_stenki_cost -= sdvig_stenki_cost % -100
        sdvig_stenki_furnitura_cost -= sdvig_stenki_furnitura_cost % -100
        sdvig_stenki_luvers_cost -= sdvig_stenki_luvers_cost % -100

        return sdvig_stenki_cost, sdvig_stenki_furnitura_cost, sdvig_stenki_luvers_cost

    # Функция для расчёта стоимости каркаса
    def calculate_karkas_cost(length, width, height_p, height_b, count_s, marka, price, is_legal_entity,
                              discount_percent):
        # Расчёт составляющих частей
        s_borta_niz = (length * 2 + width) / 6
        s_borta_niz -= s_borta_niz % -1
        stoiki = count_s * (height_p - height_b) / 6
        stoiki -= stoiki % -1
        verh = (length * 2 + width * 3) / 6
        verh -= verh % -1
        usil_verh = length * 3 / 6
        usil_verh -= usil_verh % -1
        usil_bok_2 = (height_p - height_b) / 0.45
        usil_bok_2 -= usil_bok_2 % -1
        usil_bok = (length * 2 + width) * usil_bok_2 / 6
        usil_bok -= usil_bok % -1
        naborn_bort = (length * 2 + width) / 6
        naborn_bort -= naborn_bort % -1
        naborn_bort = naborn_bort * 4

        # Расчёт стоимости каркаса с борта для Газели
        karkas_s_borta_gaz = (s_borta_niz * price['truba_40_20_2'] +
                              stoiki * price['truba_40_40_3'] +
                              verh * price['truba_40_40_2'] +
                              usil_verh * price['truba_40_20_2'] +
                              usil_bok * price['truba_40_20_2'] +
                              length / 0.1585 * price['work'])

        # Расчёт стоимости каркаса с борта для Камаза
        karkas_s_borta_kamaz = (s_borta_niz * price['truba_40_20_2'] +
                                stoiki * price['truba_60_40_3'] +
                                verh * price['truba_60_40_2'] +
                                usil_verh * price['truba_40_40_2'] +
                                usil_bok * price['truba_40_40_2'] +
                                length / 0.151 * price['work'])

        # Расчёт стоимости каркаса с платформы для Газели
        karkas_s_platform_gaz = (stoiki * price['truba_40_40_3'] +
                                 verh * price['truba_40_40_2'] +
                                 usil_verh * price['truba_40_20_2'] +
                                 usil_bok * price['truba_40_20_2'] +
                                 naborn_bort * price['doska'] +
                                 length / 0.132 * price['work'])

        # Расчёт стоимости каркаса с платформы для Камаза
        karkas_s_platform_kamaz = (stoiki * price['truba_60_40_3'] +
                                   verh * price['truba_60_40_2'] +
                                   usil_verh * price['truba_40_40_2'] +
                                   usil_bok * price['truba_40_40_2'] +
                                   naborn_bort * price['doska'] +
                                   length / 0.1417 * price['work'])

        # Расчёт стоимости каркаса под съёмную крышу
        if marka == "Газель":
            karkas_razborn = (karkas_s_platform_gaz * 2 + 6 * price['work'] * 2)
        else:
            karkas_razborn = (karkas_s_platform_kamaz * 2 + 6 * price['work'] * 2)

        # Увеличиваем стоимость на 20%, если выбрано юридическое лицо
        if is_legal_entity:
            karkas_s_borta_gaz *= 1.2
            karkas_s_borta_kamaz *= 1.2
            karkas_s_platform_gaz *= 1.2
            karkas_s_platform_kamaz *= 1.2
            karkas_razborn *= 1.2

        # Применяем скидку, если она указана
        if discount_percent > 0:
            karkas_s_borta_gaz *= (1 - discount_percent / 100)
            karkas_s_borta_kamaz *= (1 - discount_percent / 100)
            karkas_s_platform_gaz *= (1 - discount_percent / 100)
            karkas_s_platform_kamaz *= (1 - discount_percent / 100)
            karkas_razborn *= (1 - discount_percent / 100)

        # Округляем до сотен
        karkas_s_borta_gaz = karkas_s_borta_gaz * 2
        karkas_s_borta_gaz -= karkas_s_borta_gaz % -100
        karkas_s_borta_kamaz = karkas_s_borta_kamaz * 2
        karkas_s_borta_kamaz -= karkas_s_borta_kamaz % -100
        karkas_s_platform_gaz = karkas_s_platform_gaz * 2
        karkas_s_platform_gaz -= karkas_s_platform_gaz % -100
        karkas_s_platform_kamaz = karkas_s_platform_kamaz * 2
        karkas_s_platform_kamaz -= karkas_s_platform_kamaz % -100
        karkas_razborn -= karkas_razborn % -100

        # Выбор стоимости в зависимости от марки авто
        if marka == "Газель":
            karkas_s_borta = karkas_s_borta_gaz
            karkas_s_platform = karkas_s_platform_gaz
        else:
            karkas_s_borta = karkas_s_borta_kamaz
            karkas_s_platform = karkas_s_platform_kamaz

        return karkas_s_borta, karkas_s_platform, karkas_razborn

    # Рассчитываем площадь
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

    msk_cost, shtornik_cost, tros_cost, demontazh_tenta_cost = calculate_additional_costs(length, width, height_p,
                                                                                          is_vorota, is_schit, price)

    sdvig_stenki_cost, sdvig_stenki_furnitura_cost, sdvig_stenki_luvers_cost = calculate_sdvig_stenki_cost(length, height_g, price, is_legal_entity, discount_percent)

    karkas_s_borta, karkas_s_platform, karkas_razborn = calculate_karkas_cost(length, width, height_p, height_b,
                                                                              count_s, marka, price, is_legal_entity,
                                                                              discount_percent)

    # Площади для рекламы
    reklama_2_stenki = length * height_g * 2
    reklama_2_stenki_and_klapan = (length * height_g * 2) + (width * height_g)
    reklama_2_stenki_and_krysha = (length * height_g * 2) + (length * width)
    reklama_2_stenki_and_klapan_and_krysha = (length * height_g * 2) + (width * height_g) + (length * width)

    # Внутри функции page_auto_calculator, после расчёта дополнительных затрат, добавим вызов новой функции
    vorota_cost = calculate_vorota_cost(width, height_g, marka, price, is_legal_entity, discount_percent)

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

    # Создаём таблицу с дополнительными расчётами
    additional_costs_df = pd.DataFrame({
        "Наименование": ["МСК (пластины)", "Шторный механизм", "Трос", "Демонтаж тента"],
        "Стоимость": [msk_cost, shtornik_cost, tros_cost, demontazh_tenta_cost]
    })

    # Создаём таблицу с расчётом стоимости сдвижных стенок
    sdvig_stenki_df = pd.DataFrame({
        "Наименование": ["Сдвижные стенки новые", "Сдвижные стенки с фурнитурой клиента",
                         "Сдвижные стенки с люверсами"],
        "Стоимость": [sdvig_stenki_cost, sdvig_stenki_furnitura_cost, sdvig_stenki_luvers_cost]
    })

    # Создаём таблицу с расчётом стоимости каркаса
    karkas_df = pd.DataFrame({
        "Наименование": ["Каркас с борта (цельносварной)", "Каркас с платформы (цельносварной)",
                         "Каркас под съёмную крышу", "Ворота"],
        "Стоимость": [karkas_s_borta, karkas_s_platform, karkas_razborn, vorota_cost]
    })

    # Форматируем стоимость
    additional_costs_df['Стоимость'] = additional_costs_df['Стоимость'].apply(
        lambda x: "{:,.2f} руб".format(x).replace(",", " "))

    # Форматируем стоимость
    sdvig_stenki_df['Стоимость'] = sdvig_stenki_df['Стоимость'].apply(
        lambda x: "{:,.2f} руб".format(x).replace(",", " "))

    # Форматируем стоимость
    karkas_df['Стоимость'] = karkas_df['Стоимость'].apply(
        lambda x: "{:,.2f} руб".format(x).replace(",", " "))

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

    # Выводим таблицу с дополнительными расчётами
    st.dataframe(
        additional_costs_df,
        hide_index=True,
        use_container_width=True
    )

    # Выводим таблицу с расчётом стоимости сдвижных стенок
    st.dataframe(
        sdvig_stenki_df,
        hide_index=True,
        use_container_width=True
    )

    # Выводим таблицу с расчётом стоимости каркаса
    st.dataframe(
        karkas_df,
        hide_index=True,
        use_container_width=True
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