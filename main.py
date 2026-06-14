import streamlit as st
import pandas as pd
import math


class PriceManager:
    """Класс для управления ценами из secrets"""

    def __init__(self):
        self.polog_prices = st.secrets.get("prices", {}).get("polog", {})
        self.auto_prices = st.secrets.get("prices", {}).get("auto", {})

    def get_polog_price(self, material: str) -> float:
        return self.polog_prices.get(material, 0)

    def get_auto_price(self, material: str) -> float:
        return self.auto_prices.get(material, 0)


class AuthManager:
    """Класс для управления авторизацией"""

    def __init__(self):
        self.username = st.secrets.get("auth", {}).get("username", "")
        self.password = st.secrets.get("auth", {}).get("password", "")

    def check_password(self) -> bool:
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

        if st.session_state.authenticated:
            return True

        with st.form("login_form"):
            st.title("Авторизация")
            username = st.text_input("Логин")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти")

            if submitted:
                if username == self.username and password == self.password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")

        return False

    def logout(self):
        if st.sidebar.button("Выйти"):
            st.session_state.authenticated = False
            st.rerun()


def page_polog_calculator(price_manager: PriceManager):
    st.title("Калькулятор пологов")

    material_names = {
        'pp': 'ПП', 'brezent': 'Брезент', 'pvh_300': 'ПВХ300',
        'pvh_500': 'ПВХ500', 'pvh_630': 'ПВХ630', 'pvh_650': 'ПВХ650',
        'pvh_900': 'ПВХ900', 'setka_green': 'Сетка зелёная',
        'setka_not_green': 'Сетка не зелёная', 'tafeta_and_brezent': 'Тафета+брезент',
        'plenka': 'Плёнка', 'tafeta_and_oksford': 'Тафета+оксфорд', 'oksford': 'Оксфорд'
    }

    length = st.number_input("Введите длину изделия (м)", value=1.0, min_value=0.01, step=0.1)
    width = st.number_input("Введите ширину изделия (м)", value=1.0, min_value=0.01, step=0.1)
    count = st.number_input("Введите количество изделий", value=1, min_value=1, step=1)

    is_legal_entity = st.checkbox("Юридическое лицо")
    apply_discount = st.checkbox("Предоставить скидку")

    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100, step=1)

    def calculate_cost(material_price, length, width):
        sq_pol = (length + 0.2) * (width + 0.2)
        luvers_pol = (length * 2 + width * 2) / 0.3
        luvers_pol -= luvers_pol % -1
        cost = ((sq_pol * material_price) + (luvers_pol * price_manager.get_polog_price('luver')) +
                (sq_pol * 0.2 * price_manager.get_polog_price('work'))) * 2.5
        cost -= cost % -100

        if is_legal_entity:
            cost = cost * 0.25 + cost

        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)
            cost = int(cost // 100 * 100)

        return int(cost)

    results = []

    for material, price in price_manager.polog_prices.items():
        if material not in ['luver', 'work']:
            cost_per_item = calculate_cost(price, length, width)
            total_cost = cost_per_item * count
            results.append({
                'Материал': material_names.get(material, material),
                'Стоимость за 1 изделие': cost_per_item,
                'Стоимость за все изделия': total_cost
            })

    results_df = pd.DataFrame(results)

    def format_cost(cost):
        return "{:,.2f} руб".format(cost).replace(",", " ")

    results_df['Стоимость за 1 изделие'] = results_df['Стоимость за 1 изделие'].apply(format_cost)
    results_df['Стоимость за все изделия'] = results_df['Стоимость за все изделия'].apply(format_cost)

    st.dataframe(results_df, hide_index=True, use_container_width=True)


def page_auto_calculator(price_manager: PriceManager):
    st.title("Калькулятор продукции на авто")
    st.write("Цены актуальны на 11.06.2025")

    # Ввод данных
    length = st.number_input("Введите длину (м)", value=1.0, min_value=0.01, step=0.1)
    width = st.number_input("Введите ширину (м)", value=1.0, min_value=0.01, step=0.1)
    height_p = st.number_input("Введите полезную высоту (м)", value=1.0, min_value=0.01, step=0.1)
    height_g = st.number_input("Введите высоту готовой стенки (м)", value=1.0, min_value=0.01, step=0.1)
    height_b = st.number_input("Введите высоту борта (м)", value=1.0, min_value=0.01, step=0.1)
    count_s = st.number_input("Введите количество стоек (шт)", value=1, min_value=1, step=1)
    marka = st.selectbox("Выберите марку авто", ("Газель", "Иное"), index=None, placeholder="Выбрать вариант")

    col1, col2 = st.columns(2)
    with col1:
        is_vorota = st.checkbox("Наличие ворот")
        is_schit = st.checkbox("Наличие щита")
    with col2:
        is_legal_entity = st.checkbox("Юридическое лицо")
        apply_discount = st.checkbox("Предоставить скидку")

    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100, step=1)

    # Функция для расчёта площади изделия
    def calculate_area(length, width, height_g, is_vorota, is_schit):
        if is_vorota and is_schit:
            sq = (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            sq = (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            sq = (length * height_g * 2) + (width * height_g * 2) + (length * width)
        return sq

    # Функция для расчёта стоимости ткани
    def calculate_cost(material_price, area, length_val, is_legal_entity, discount_percent):
        if length_val < 5:
            cost = material_price * 2.8
        elif length_val > 10:
            cost = material_price * 2.4
        else:
            cost = material_price * 2.6
        cost -= cost % -10
        cost = cost * area

        if is_legal_entity:
            cost *= 1.25

        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        cost -= cost % -100
        return cost

    # Функция для расчёта стоимости "Тент (чулок)"
    def calculate_chulok_cost(material_price, area, length_val, is_legal_entity, discount_percent):
        fabric_cost = material_price * area
        fabric_cost -= fabric_cost % -100

        babochka_count = ((round(length_val / 0.65)) - 6) * 3 + 6 * 5
        babochka_cost = babochka_count * price_manager.get_auto_price('babochka')
        work_cost = price_manager.get_auto_price('work') * (length_val / 0.4)

        total_cost = (fabric_cost + babochka_cost + work_cost) * 2

        if is_legal_entity:
            total_cost *= 1.25

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости "Тент сдвижной крыши"
    def calculate_sdvizhnoy_krysha_cost(material_price, length_val, width_val, is_legal_entity, discount_percent):
        s_krysha = (length_val + 0.6) * (width_val + 0.6)
        p_shnur = length_val * 2 + 2

        if math.ceil((length_val - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / 0.65 * 2) + 1

        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width_val * 0.1) + ((length_val * 2 + width_val * 2) * 0.15)
        count_work = length_val * 1.5

        total_cost = (s_krysha * material_price + p_shnur * price_manager.get_auto_price('shnur_8') +
                      count_remeshki * price_manager.get_auto_price('remeshok') + p_usilitel * material_price +
                      count_work * price_manager.get_auto_price('work'))

        if is_legal_entity:
            total_cost *= 1.25

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost = total_cost * 1.7
        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости тента с рекламой
    def calculate_reklama_cost(reklama_area, total_area, material_price, length_val, is_legal_entity, discount_percent):
        reklama_cost = reklama_area * price_manager.get_auto_price('reklama')
        fabric_cost = (total_area - reklama_area) * material_price
        work_cost = (length_val / 0.27) * price_manager.get_auto_price('work')

        total_cost = (reklama_cost + fabric_cost + work_cost) * 2

        if is_legal_entity:
            total_cost *= 1.25

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости МСК (пластины), Шторного механизма, Троса и Демонтажа тента
    def calculate_additional_costs(length_val, width_val, height_p_val, is_vorota, is_schit):
        perimetr_total = length_val * 2 + width_val * 2 + height_p_val * 4
        perimetr_half = length_val * 2 + width_val * 2 + height_p_val * 2
        perimetr_min = length_val * 2 + width_val * 2

        if math.ceil(length_val / 0.65 * 2) % 2 == 0:
            kronshtein_count = math.ceil(length_val / 0.65 * 2)
        else:
            kronshtein_count = math.ceil(length_val / 0.65 * 2) + 1

        truba_30_30_count = (kronshtein_count / 2 * 2.55) / 6
        truba_30_30_count -= truba_30_30_count % -1
        truba_60_40_count = length_val / 6 * 2
        truba_60_40_count -= truba_60_40_count % -1
        shveler_count = length_val / 2.48 * 2
        shveler_count -= shveler_count % -1

        if math.ceil((length_val - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / 0.65 * 2) + 1
        count_plastin_black = count_plastin_650 + 2

        msk_cost = int((kronshtein_count * price_manager.get_auto_price('kronshtein') +
                        truba_30_30_count * price_manager.get_auto_price('truba_30_30_2') +
                        truba_60_40_count * price_manager.get_auto_price('truba_60_40_3') +
                        shveler_count * price_manager.get_auto_price('shveler') +
                        kronshtein_count * price_manager.get_auto_price('podship_big') +
                        kronshtein_count * 2 * price_manager.get_auto_price('podship_small') +
                        kronshtein_count * 2 * price_manager.get_auto_price('gaika_m14') +
                        kronshtein_count * price_manager.get_auto_price('bolt_10_20') +
                        kronshtein_count * 2 * price_manager.get_auto_price('bolt_12_30') +
                        count_plastin_650 * price_manager.get_auto_price('plastina_650') +
                        count_plastin_black * price_manager.get_auto_price('plastina_black') +
                        2 * price_manager.get_auto_price('fiksator') +
                        2 * price_manager.get_auto_price('amortizator') +
                        48 * price_manager.get_auto_price('work') +
                        length_val * 6 * price_manager.get_auto_price('work')) * 2)

        if is_legal_entity:
            msk_cost *= 1.2

        if discount_percent > 0:
            msk_cost *= (1 - discount_percent / 100)

        msk_cost -= msk_cost % -100

        shtorn_profile_count = length_val / 6 * 2
        shtorn_profile_count -= shtorn_profile_count % -1
        shtorn_work_count = length_val * 0.73
        shtorn_work_count -= shtorn_work_count % -1
        shtornik_cost = int((shtorn_profile_count * price_manager.get_auto_price('shtorn_profil') +
                             shtorn_work_count * price_manager.get_auto_price('work')) * 2)

        if is_legal_entity:
            shtornik_cost *= 1.2

        if discount_percent > 0:
            shtornik_cost *= (1 - discount_percent / 100)

        shtornik_cost -= shtornik_cost % -100

        if is_vorota and is_schit:
            tros_cost = int(perimetr_total * price_manager.get_auto_price('tros') * 1.5)
        elif not is_vorota and not is_schit:
            tros_cost = int(perimetr_min * price_manager.get_auto_price('tros') * 1.5)
        else:
            tros_cost = int(perimetr_half * price_manager.get_auto_price('tros') * 1.5)

        if is_legal_entity:
            tros_cost *= 1.2

        if discount_percent > 0:
            tros_cost *= (1 - discount_percent / 100)

        tros_cost -= tros_cost % -100

        demontazh_tenta_cost = int(length_val * 0.6 * price_manager.get_auto_price('work'))

        if is_legal_entity:
            demontazh_tenta_cost *= 1.2

        if discount_percent > 0:
            demontazh_tenta_cost *= (1 - discount_percent / 100)

        demontazh_tenta_cost -= demontazh_tenta_cost % -100

        return msk_cost, shtornik_cost, tros_cost, demontazh_tenta_cost

    # Функция для расчёта стоимости ворот
    def calculate_vorota_cost(width_val, height_g_val, marka_val):
        ramka_vorot = (width_val * 2 + height_g_val * 2) / 6
        ramka_vorot -= ramka_vorot % -1
        zapory_count = width_val * 2 / 6
        zapory_count -= zapory_count % -1

        vorota_gazel = int((price_manager.get_auto_price('fanera_18') * 2 +
                            price_manager.get_auto_price('petlya_gaz') * 6 +
                            price_manager.get_auto_price('zamki_gaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_18') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_gazel -= vorota_gazel % -100

        vorota_kamaz = int((price_manager.get_auto_price('fanera_21_2') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_kamaz -= vorota_kamaz % -100

        vorota_other = int((price_manager.get_auto_price('fanera_21_3') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_other -= vorota_other % -100

        if marka_val == "Газель":
            vorota_cost = vorota_gazel
        elif marka_val == "Иное" and height_g_val > 2.4:
            vorota_cost = vorota_other
        elif marka_val == "Иное" and height_g_val <= 2.4:
            vorota_cost = vorota_kamaz
        else:
            vorota_cost = 0

        if is_legal_entity:
            vorota_cost *= 1.2

        if discount_percent > 0:
            vorota_cost *= (1 - discount_percent / 100)

        vorota_cost -= vorota_cost % -100
        return vorota_cost

    # Функция для расчёта сдвижных стенок
    def calculate_sdvig_stenki_cost(length_val, height_g_val):
        square_sdvig_stenok = (length_val + 0.9) * height_g_val + (length_val + 0.9)
        rolik_sd = round(length_val / 0.55)
        zamok = round(length_val / 0.55)
        lenta = (rolik_sd * (height_g_val + 0.2)) + length_val
        mehanizm = 2
        profil = 2
        perehodnik = 4
        luver_40 = math.ceil(length_val / 0.2)
        luver_40 -= luver_40 % -10
        espander = math.ceil(length_val * 1.25)
        kruchok = math.ceil(luver_40 / 2)
        luver_12 = math.ceil(length_val / 0.2)
        luver_12 -= luver_12 % -10
        rabota = length_val * 1.1

        sdvig_stenki_cost = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                             rolik_sd * price_manager.get_auto_price('rolik_sdvig') +
                             zamok * price_manager.get_auto_price('zamok_so_stropoi') +
                             lenta * price_manager.get_auto_price('lenta_F1300') +
                             luver_40 * price_manager.get_auto_price('luvers_40') +
                             espander * price_manager.get_auto_price('espander') +
                             kruchok * price_manager.get_auto_price('kruchok_s') +
                             luver_12 * price_manager.get_auto_price('luvers_12') +
                             rabota * price_manager.get_auto_price('work') +
                             profil * price_manager.get_auto_price('profil_allum') +
                             perehodnik * price_manager.get_auto_price('perehodnik_profilya') +
                             mehanizm * price_manager.get_auto_price('mehanizm_natyascheniya'))

        sdvig_stenki_cost = sdvig_stenki_cost * 2
        sdvig_stenki_cost = sdvig_stenki_cost * 1.8
        sdvig_stenki_cost -= sdvig_stenki_cost % 100

        sdvig_stenki_furnitura_cost = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                                       lenta * price_manager.get_auto_price('lenta_F1300') +
                                       rabota * price_manager.get_auto_price('work'))

        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * 2
        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * 1.8
        sdvig_stenki_furnitura_cost -= sdvig_stenki_furnitura_cost % 100

        sdvig_stenki_luvers_cost = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                                    luver_40 * price_manager.get_auto_price('luvers_40') +
                                    luver_12 * price_manager.get_auto_price('luvers_12') +
                                    kruchok * price_manager.get_auto_price('kruchok_s') +
                                    espander * price_manager.get_auto_price('espander') +
                                    rabota * price_manager.get_auto_price('work'))

        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * 2
        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * 1.8
        sdvig_stenki_luvers_cost -= sdvig_stenki_luvers_cost % 100

        if is_legal_entity:
            sdvig_stenki_cost *= 1.2
            sdvig_stenki_furnitura_cost *= 1.2
            sdvig_stenki_luvers_cost *= 1.2

        if discount_percent > 0:
            sdvig_stenki_cost *= (1 - discount_percent / 100)
            sdvig_stenki_furnitura_cost *= (1 - discount_percent / 100)
            sdvig_stenki_luvers_cost *= (1 - discount_percent / 100)

        sdvig_stenki_cost -= sdvig_stenki_cost % -100
        sdvig_stenki_furnitura_cost -= sdvig_stenki_furnitura_cost % -100
        sdvig_stenki_luvers_cost -= sdvig_stenki_luvers_cost % -100

        return sdvig_stenki_cost, sdvig_stenki_furnitura_cost, sdvig_stenki_luvers_cost

    # Функция для расчёта стоимости каркаса
    def calculate_karkas_cost(length_val, width_val, height_p_val, height_b_val, count_s_val, marka_val):
        s_borta_niz = (length_val * 2 + width_val) / 6
        s_borta_niz -= s_borta_niz % -1
        stoiki = count_s_val * (height_p_val - height_b_val) / 6
        stoiki -= stoiki % -1
        verh = (length_val * 2 + width_val * 3) / 6
        verh -= verh % -1
        usil_verh = length_val * 3 / 6
        usil_verh -= usil_verh % -1
        usil_bok_2 = (height_p_val - height_b_val) / 0.45
        usil_bok_2 -= usil_bok_2 % -1
        usil_bok = (length_val * 2 + width_val) * usil_bok_2 / 6
        usil_bok -= usil_bok % -1
        naborn_bort = (length_val * 2 + width_val) / 6
        naborn_bort -= naborn_bort % -1
        naborn_bort = naborn_bort * 4

        karkas_s_borta_gaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                              stoiki * price_manager.get_auto_price('truba_40_40_3') +
                              verh * price_manager.get_auto_price('truba_40_40_2') +
                              usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                              usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                              length_val / 0.1585 * price_manager.get_auto_price('work'))

        karkas_s_borta_kamaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                                stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                verh * price_manager.get_auto_price('truba_60_40_2') +
                                usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                length_val / 0.151 * price_manager.get_auto_price('work'))

        karkas_s_platform_gaz = (stoiki * price_manager.get_auto_price('truba_40_40_3') +
                                 verh * price_manager.get_auto_price('truba_40_40_2') +
                                 usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                                 usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                                 naborn_bort * price_manager.get_auto_price('doska') +
                                 length_val / 0.132 * price_manager.get_auto_price('work'))

        karkas_s_platform_kamaz = (stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                   verh * price_manager.get_auto_price('truba_60_40_2') +
                                   usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                   usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                   naborn_bort * price_manager.get_auto_price('doska') +
                                   length_val / 0.1417 * price_manager.get_auto_price('work'))

        if marka_val == "Газель":
            karkas_razborn = (karkas_s_platform_gaz * 2 + 6 * price_manager.get_auto_price('work') * 2)
        else:
            karkas_razborn = (karkas_s_platform_kamaz * 2 + 6 * price_manager.get_auto_price('work') * 2)

        if is_legal_entity:
            karkas_s_borta_gaz *= 1.2
            karkas_s_borta_kamaz *= 1.2
            karkas_s_platform_gaz *= 1.2
            karkas_s_platform_kamaz *= 1.2
            karkas_razborn *= 1.2

        if discount_percent > 0:
            karkas_s_borta_gaz *= (1 - discount_percent / 100)
            karkas_s_borta_kamaz *= (1 - discount_percent / 100)
            karkas_s_platform_gaz *= (1 - discount_percent / 100)
            karkas_s_platform_kamaz *= (1 - discount_percent / 100)
            karkas_razborn *= (1 - discount_percent / 100)

        karkas_s_borta_gaz = karkas_s_borta_gaz * 2
        karkas_s_borta_gaz -= karkas_s_borta_gaz % -100
        karkas_s_borta_kamaz = karkas_s_borta_kamaz * 2
        karkas_s_borta_kamaz -= karkas_s_borta_kamaz % -100
        karkas_s_platform_gaz = karkas_s_platform_gaz * 2
        karkas_s_platform_gaz -= karkas_s_platform_gaz % -100
        karkas_s_platform_kamaz = karkas_s_platform_kamaz * 2
        karkas_s_platform_kamaz -= karkas_s_platform_kamaz % -100
        karkas_razborn -= karkas_razborn % -100

        if marka_val == "Газель":
            karkas_s_borta = karkas_s_borta_gaz
            karkas_s_platform = karkas_s_platform_gaz
        else:
            karkas_s_borta = karkas_s_borta_kamaz
            karkas_s_platform = karkas_s_platform_kamaz

        return karkas_s_borta, karkas_s_platform, karkas_razborn

    # Рассчитываем площадь
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

    st.write(f"**Рассчитанная площадь: {area:.2f} м²**")

    # Расчет дополнительных затрат
    msk_cost, shtornik_cost, tros_cost, demontazh_tenta_cost = calculate_additional_costs(length, width, height_p,
                                                                                          is_vorota, is_schit)
    sdvig_stenki_cost, sdvig_stenki_furnitura_cost, sdvig_stenki_luvers_cost = calculate_sdvig_stenki_cost(length,
                                                                                                           height_g)
    karkas_s_borta, karkas_s_platform, karkas_razborn = calculate_karkas_cost(length, width, height_p, height_b,
                                                                              count_s, marka)
    vorota_cost = calculate_vorota_cost(width, height_g, marka) if marka else 0

    # Площади для рекламы
    reklama_2_stenki = length * height_g * 2
    reklama_2_stenki_and_klapan = (length * height_g * 2) + (width * height_g)
    reklama_2_stenki_and_krysha = (length * height_g * 2) + (length * width)
    reklama_2_stenki_and_klapan_and_krysha = (length * height_g * 2) + (width * height_g) + (length * width)

    # Список материалов для расчета
    material_prices = [
        ('ПВХ630', price_manager.get_auto_price('pvh_630')),
        ('ПВХ650', price_manager.get_auto_price('pvh_650')),
        ('ПВХ750', price_manager.get_auto_price('pvh_750')),
        ('ПВХ900', price_manager.get_auto_price('pvh_900'))
    ]

    # Функция для форматирования
    def format_cost(cost):
        if cost == "НЕВЕРНО!" or cost == 0:
            return "Не выбрано" if cost == 0 else cost
        return "{:,.2f} руб".format(cost).replace(",", " ")

    # Расчет для каждого материала
    results_typical = []
    results_chulok = []
    results_sdvizhnoy = []
    results_reklama_2_stenki = []
    results_reklama_2_stenki_and_klapan = []
    results_reklama_2_stenki_and_krysha = []
    results_reklama_2_stenki_and_klapan_and_krysha = []

    for material_name, material_price in material_prices:
        if material_price:
            results_typical.append(calculate_cost(material_price, area, length, is_legal_entity, discount_percent))
            results_chulok.append(
                calculate_chulok_cost(material_price, area, length, is_legal_entity, discount_percent))
            results_sdvizhnoy.append(
                calculate_sdvizhnoy_krysha_cost(material_price, length, width, is_legal_entity, discount_percent))
            results_reklama_2_stenki.append(
                calculate_reklama_cost(reklama_2_stenki, area, material_price, length, is_legal_entity,
                                       discount_percent))

            if not is_vorota:
                results_reklama_2_stenki_and_klapan.append(
                    calculate_reklama_cost(reklama_2_stenki_and_klapan, area, material_price, length, is_legal_entity,
                                           discount_percent))
            else:
                results_reklama_2_stenki_and_klapan.append("НЕВЕРНО!")

            results_reklama_2_stenki_and_krysha.append(
                calculate_reklama_cost(reklama_2_stenki_and_krysha, area, material_price, length, is_legal_entity,
                                       discount_percent))

            if not is_vorota:
                results_reklama_2_stenki_and_klapan_and_krysha.append(
                    calculate_reklama_cost(reklama_2_stenki_and_klapan_and_krysha, area, material_price, length,
                                           is_legal_entity, discount_percent))
            else:
                results_reklama_2_stenki_and_klapan_and_krysha.append("НЕВЕРНО!")

    # 1. Основная таблица
    st.subheader("📊 Основные типы тентов")
    if len(results_typical) >= 4:
        results_df = pd.DataFrame({
            "Тент": ["Тент типовой", "Тент сдвижной крыши", "Тент (чулок)"],
            "ПВХ630": [format_cost(results_typical[0]), format_cost(results_sdvizhnoy[0]),
                       format_cost(results_chulok[0])],
            "ПВХ650": [format_cost(results_typical[1]), format_cost(results_sdvizhnoy[1]),
                       format_cost(results_chulok[1])],
            "ПВХ750": [format_cost(results_typical[2]), format_cost(results_sdvizhnoy[2]),
                       format_cost(results_chulok[2])],
            "ПВХ900": [format_cost(results_typical[3]), format_cost(results_sdvizhnoy[3]),
                       format_cost(results_chulok[3])],
        })
        st.dataframe(results_df, hide_index=True, use_container_width=True)

    # 2. Таблица с рекламой
    st.subheader("🎯 Тенты с рекламой")
    if len(results_reklama_2_stenki) >= 4:
        reklama_df = pd.DataFrame({
            "Тент с рекламой": ["Реклама на 2-х стенках", "Реклама на 2-х стенках и клапане",
                                "Реклама на 2-х стенках и крыше", "Реклама на 2-х стенках, клапане и крыше"],
            "ПВХ650": [format_cost(results_reklama_2_stenki[1]),
                       format_cost(results_reklama_2_stenki_and_klapan[1]) if len(
                           results_reklama_2_stenki_and_klapan) > 1 else "Нет данных",
                       format_cost(results_reklama_2_stenki_and_krysha[1]) if len(
                           results_reklama_2_stenki_and_krysha) > 1 else "Нет данных",
                       format_cost(results_reklama_2_stenki_and_klapan_and_krysha[1]) if len(
                           results_reklama_2_stenki_and_klapan_and_krysha) > 1 else "Нет данных"],
        })
        st.dataframe(reklama_df, hide_index=True, use_container_width=True)

    # 3. Дополнительные компоненты
    st.subheader("🔧 Дополнительные компоненты")
    additional_costs_df = pd.DataFrame({
        "Наименование": ["МСК (пластины)", "Шторный механизм", "Трос", "Демонтаж тента"],
        "Стоимость": [format_cost(msk_cost), format_cost(shtornik_cost), format_cost(tros_cost),
                      format_cost(demontazh_tenta_cost)]
    })
    st.dataframe(additional_costs_df, hide_index=True, use_container_width=True)

    # 4. Сдвижные стенки
    st.subheader("🚪 Сдвижные стенки")
    sdvig_stenki_df = pd.DataFrame({
        "Наименование": ["Сдвижные стенки новые", "Сдвижные стенки с фурнитурой клиента",
                         "Сдвижные стенки с люверсами"],
        "Стоимость": [format_cost(sdvig_stenki_cost), format_cost(sdvig_stenki_furnitura_cost),
                      format_cost(sdvig_stenki_luvers_cost)]
    })
    st.dataframe(sdvig_stenki_df, hide_index=True, use_container_width=True)

    # 5. Каркас
    st.subheader("🏗️ Каркас")
    karkas_df = pd.DataFrame({
        "Наименование": ["Каркас с борта (цельносварной)", "Каркас с платформы (цельносварной)",
                         "Каркас под съёмную крышу", "Ворота"],
        "Стоимость": [format_cost(karkas_s_borta), format_cost(karkas_s_platform), format_cost(karkas_razborn),
                      format_cost(vorota_cost)]
    })
    st.dataframe(karkas_df, hide_index=True, use_container_width=True)


def page_info():
    st.title("Ещё калькулятор")
    st.write("Место для ещё какого-нибудь калькулятора...")


def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    auth_manager = AuthManager()

    if not auth_manager.check_password():
        return

    st.sidebar.title("Меню")
    page = st.sidebar.radio("Выберите страницу", ["Калькулятор пологов", "Калькулятор авто", "Ещё калькулятор"])

    auth_manager.logout()

    price_manager = PriceManager()

    if page == "Калькулятор пологов":
        page_polog_calculator(price_manager)
    elif page == "Калькулятор авто":
        page_auto_calculator(price_manager)
    elif page == "Ещё калькулятор":
        page_info()


if __name__ == "__main__":
    main()