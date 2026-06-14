import streamlit as st
import pandas as pd
import math
from typing import Any


class PriceManager:
    """Класс для управления ценами и коэффициентами из secrets"""

    def __init__(self):
        self.polog_prices = st.secrets.get("prices", {}).get("polog", {})
        self.auto_prices = st.secrets.get("prices", {}).get("auto", {})
        self.polog_coeffs = st.secrets.get("polog_coefficients", {})
        self.auto_coeffs = st.secrets.get("auto_coefficients", {})

    def get_polog_price(self, material: str) -> float:
        return self.polog_prices.get(material, 0)

    def get_auto_price(self, material: str) -> float:
        return self.auto_prices.get(material, 0)

    def get_polog_coeff(self, name: str, default: Any = None) -> Any:
        return self.polog_coeffs.get(name, default)

    def get_auto_coeff(self, name: str, default: Any = None) -> Any:
        return self.auto_coeffs.get(name, default)


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
        luver_spacing = price_manager.get_polog_coeff("luver_spacing", 0.3)
        luvers_pol = (length * 2 + width * 2) / luver_spacing
        luvers_pol -= luvers_pol % -1

        multiplier = price_manager.get_polog_coeff("multiplier", 2.5)
        work_percentage = price_manager.get_polog_coeff("work_percentage", 0.2)

        cost = ((sq_pol * material_price) +
                (luvers_pol * price_manager.get_polog_price('luver')) +
                (sq_pol * work_percentage * price_manager.get_polog_price('work'))) * multiplier

        # Первое округление до сотен
        cost -= cost % -100

        if is_legal_entity:
            legal_multiplier = price_manager.get_polog_coeff("legal_entity_multiplier", 0.25)
            cost = cost * (1 + legal_multiplier)

        # Применяем скидку
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)
            # НЕ округляем после скидки, оставляем как есть

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

    # Получаем коэффициенты для юрлица из secrets
    legal_multiplier = price_manager.get_auto_coeff("legal_entity_multiplier", 1.25)
    chulok_legal_multiplier = price_manager.get_auto_coeff("chulok_legal_multiplier", 1.25)
    sdvizhnoy_legal_multiplier = price_manager.get_auto_coeff("sdvizhnoy_legal_multiplier", 1.25)
    reklama_legal_multiplier = price_manager.get_auto_coeff("reklama_legal_multiplier", 1.25)

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
        length_small = price_manager.get_auto_coeff("length_small", 5)
        length_large = price_manager.get_auto_coeff("length_large", 10)
        coeff_small = price_manager.get_auto_coeff("coefficient_small", 2.8)
        coeff_medium = price_manager.get_auto_coeff("coefficient_medium", 2.6)
        coeff_large = price_manager.get_auto_coeff("coefficient_large", 2.4)
        rounding_step = price_manager.get_auto_coeff("rounding_step", 10)
        rounding_final = price_manager.get_auto_coeff("rounding_final", 100)

        if length_val < length_small:
            cost = material_price * coeff_small
        elif length_val > length_large:
            cost = material_price * coeff_large
        else:
            cost = material_price * coeff_medium
        cost -= cost % -rounding_step
        cost = cost * area

        if is_legal_entity:
            cost *= legal_multiplier

        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        cost -= cost % -rounding_final
        return cost

    # Функция для расчёта стоимости "Тент (чулок)"
    def calculate_chulok_cost(material_price, area, length_val, is_legal_entity, discount_percent):
        fabric_cost = material_price * area
        fabric_cost -= fabric_cost % -100

        babochka_step = price_manager.get_auto_coeff("babochka_step", 0.65)
        babochka_base = price_manager.get_auto_coeff("babochka_base", 6)
        babochka_count = ((round(length_val / babochka_step)) - babochka_base) * 3 + 6 * 5
        babochka_cost = babochka_count * price_manager.get_auto_price('babochka')

        work_step = price_manager.get_auto_coeff("work_step", 0.4)
        work_cost = price_manager.get_auto_price('work') * (length_val / work_step)

        chulok_multiplier = price_manager.get_auto_coeff("chulok_multiplier", 2)
        total_cost = (fabric_cost + babochka_cost + work_cost) * chulok_multiplier

        if is_legal_entity:
            total_cost *= chulok_legal_multiplier

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости "Тент сдвижной крыши"
    def calculate_sdvizhnoy_krysha_cost(material_price, length_val, width_val, is_legal_entity, discount_percent):
        add_length = price_manager.get_auto_coeff("sdvizhnoy_add_length", 0.6)
        s_krysha = (length_val + add_length) * (width_val + 0.6)
        p_shnur = length_val * 2 + 2

        plastin_step = price_manager.get_auto_coeff("plastin_step", 0.65)
        if math.ceil((length_val - 1) / plastin_step * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / plastin_step * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / plastin_step * 2) + 1

        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width_val * 0.1) + ((length_val * 2 + width_val * 2) * 0.15)
        count_work = length_val * 1.5

        total_cost = (s_krysha * material_price + p_shnur * price_manager.get_auto_price('shnur_8') +
                      count_remeshki * price_manager.get_auto_price('remeshok') + p_usilitel * material_price +
                      count_work * price_manager.get_auto_price('work'))

        if is_legal_entity:
            total_cost *= sdvizhnoy_legal_multiplier

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        sdvizhnoy_multiplier = price_manager.get_auto_coeff("sdvizhnoy_multiplier", 1.7)
        total_cost = total_cost * sdvizhnoy_multiplier
        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости тента с рекламой
    def calculate_reklama_cost(reklama_area, total_area, material_price, length_val, is_legal_entity, discount_percent):
        reklama_cost = reklama_area * price_manager.get_auto_price('reklama')
        fabric_cost = (total_area - reklama_area) * material_price

        reklama_work_step = price_manager.get_auto_coeff("reklama_work_step", 0.27)
        work_cost = (length_val / reklama_work_step) * price_manager.get_auto_price('work')

        reklama_multiplier = price_manager.get_auto_coeff("reklama_multiplier", 2)
        total_cost = (reklama_cost + fabric_cost + work_cost) * reklama_multiplier

        if is_legal_entity:
            total_cost *= reklama_legal_multiplier

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost -= total_cost % -100
        return total_cost

    # Функция для расчёта стоимости МСК (пластины)
    def calculate_msk_cost(length_val, width_val, is_vorota, is_schit):
        kronshtein_step = price_manager.get_auto_coeff("msk_kronshtein_step", 0.65)
        if math.ceil(length_val / kronshtein_step * 2) % 2 == 0:
            kronshtein_count = math.ceil(length_val / kronshtein_step * 2)
        else:
            kronshtein_count = math.ceil(length_val / kronshtein_step * 2) + 1

        truba_coeff = price_manager.get_auto_coeff("msk_truba_coeff", 2.55)
        truba_divider = price_manager.get_auto_coeff("msk_truba_divider", 6)
        truba_30_30_count = (kronshtein_count / 2 * truba_coeff) / truba_divider
        truba_30_30_count -= truba_30_30_count % -1

        truba_60_40_count = length_val / 6 * 2
        truba_60_40_count -= truba_60_40_count % -1

        shveler_step = price_manager.get_auto_coeff("msk_shveler_step", 2.48)
        shveler_count = length_val / shveler_step * 2
        shveler_count -= shveler_count % -1

        plastin_step = price_manager.get_auto_coeff("msk_plastin_step", 0.65)
        if math.ceil((length_val - 1) / plastin_step * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / plastin_step * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / plastin_step * 2) + 1
        count_plastin_black = count_plastin_650 + 2

        msk_multiplier = price_manager.get_auto_coeff("msk_multiplier", 2)
        msk_work_hours = price_manager.get_auto_coeff("msk_work_hours", 48)
        msk_work_per_meter = price_manager.get_auto_coeff("msk_work_per_meter", 6)

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
                        msk_work_hours * price_manager.get_auto_price('work') +
                        length_val * msk_work_per_meter * price_manager.get_auto_price('work')) * msk_multiplier)

        legal_multiplier = price_manager.get_auto_coeff("msk_legal_multiplier", 1.2)
        if is_legal_entity:
            msk_cost *= legal_multiplier

        if discount_percent > 0:
            msk_cost *= (1 - discount_percent / 100)

        msk_cost -= msk_cost % -100
        return msk_cost

    # Функция для расчёта стоимости Шторного механизма
    def calculate_shtornik_cost(length_val):
        profile_divider = price_manager.get_auto_coeff("shtornik_profile_divider", 6)
        shtorn_profile_count = length_val / profile_divider * 2
        shtorn_profile_count -= shtorn_profile_count % -1

        work_coeff = price_manager.get_auto_coeff("shtornik_work_coeff", 0.73)
        shtorn_work_count = length_val * work_coeff
        shtorn_work_count -= shtorn_work_count % -1

        shtornik_multiplier = price_manager.get_auto_coeff("shtornik_multiplier", 2)
        shtornik_cost = int((shtorn_profile_count * price_manager.get_auto_price('shtorn_profil') +
                             shtorn_work_count * price_manager.get_auto_price('work')) * shtornik_multiplier)

        legal_multiplier = price_manager.get_auto_coeff("shtornik_legal_multiplier", 1.2)
        if is_legal_entity:
            shtornik_cost *= legal_multiplier

        if discount_percent > 0:
            shtornik_cost *= (1 - discount_percent / 100)

        shtornik_cost -= shtornik_cost % -100
        return shtornik_cost

    # Функция для расчёта стоимости Троса
    def calculate_tros_cost(length_val, width_val, height_p_val, is_vorota, is_schit):
        perimetr_total = length_val * 2 + width_val * 2 + height_p_val * 4
        perimetr_half = length_val * 2 + width_val * 2 + height_p_val * 2
        perimetr_min = length_val * 2 + width_val * 2

        tros_multiplier = price_manager.get_auto_coeff("tros_multiplier", 1.5)
        if is_vorota and is_schit:
            tros_cost = int(perimetr_total * price_manager.get_auto_price('tros') * tros_multiplier)
        elif not is_vorota and not is_schit:
            tros_cost = int(perimetr_min * price_manager.get_auto_price('tros') * tros_multiplier)
        else:
            tros_cost = int(perimetr_half * price_manager.get_auto_price('tros') * tros_multiplier)

        legal_multiplier = price_manager.get_auto_coeff("tros_legal_multiplier", 1.2)
        if is_legal_entity:
            tros_cost *= legal_multiplier

        if discount_percent > 0:
            tros_cost *= (1 - discount_percent / 100)

        tros_cost -= tros_cost % -100
        return tros_cost

    # Функция для расчёта стоимости Демонтажа тента
    def calculate_demontazh_cost(length_val):
        demontazh_multiplier = price_manager.get_auto_coeff("demontazh_multiplier", 0.6)
        demontazh_cost = int(length_val * demontazh_multiplier * price_manager.get_auto_price('work'))

        legal_multiplier = price_manager.get_auto_coeff("demontazh_legal_multiplier", 1.2)
        if is_legal_entity:
            demontazh_cost *= legal_multiplier

        if discount_percent > 0:
            demontazh_cost *= (1 - discount_percent / 100)

        demontazh_cost -= demontazh_cost % -100
        return demontazh_cost

    # Функция для расчёта стоимости ворот
    def calculate_vorota_cost(width_val, height_g_val, marka_val):
        ramka_divider = price_manager.get_auto_coeff("vorota_ramka_divider", 6)
        ramka_vorot = (width_val * 2 + height_g_val * 2) / ramka_divider
        ramka_vorot -= ramka_vorot % -1

        zapory_divider = price_manager.get_auto_coeff("vorota_zapory_divider", 6)
        zapory_count = width_val * 2 / zapory_divider
        zapory_count -= zapory_count % -1

        work_hours = price_manager.get_auto_coeff("vorota_work_hours", 32)
        height_threshold = price_manager.get_auto_coeff("vorota_height_threshold", 2.4)

        vorota_gazel = int((price_manager.get_auto_price('fanera_18') * 2 +
                            price_manager.get_auto_price('petlya_gaz') * 6 +
                            price_manager.get_auto_price('zamki_gaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_18') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            work_hours * price_manager.get_auto_price('work')) * 2)
        vorota_gazel -= vorota_gazel % -100

        vorota_kamaz = int((price_manager.get_auto_price('fanera_21_2') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            work_hours * price_manager.get_auto_price('work')) * 2)
        vorota_kamaz -= vorota_kamaz % -100

        vorota_other = int((price_manager.get_auto_price('fanera_21_3') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            work_hours * price_manager.get_auto_price('work')) * 2)
        vorota_other -= vorota_other % -100

        if marka_val == "Газель":
            vorota_cost = vorota_gazel
        elif marka_val == "Иное" and height_g_val > height_threshold:
            vorota_cost = vorota_other
        elif marka_val == "Иное" and height_g_val <= height_threshold:
            vorota_cost = vorota_kamaz
        else:
            vorota_cost = 0

        legal_multiplier = price_manager.get_auto_coeff("vorota_legal_multiplier", 1.2)
        if is_legal_entity:
            vorota_cost *= legal_multiplier

        if discount_percent > 0:
            vorota_cost *= (1 - discount_percent / 100)

        vorota_cost -= vorota_cost % -100
        return vorota_cost

    # Функция для расчёта сдвижных стенок
    def calculate_sdvig_stenki_cost(length_val, height_g_val):
        add_length = price_manager.get_auto_coeff("sdvig_add_length", 0.9)
        square_sdvig_stenok = (length_val + add_length) * height_g_val + (length_val + add_length)

        rolik_step = price_manager.get_auto_coeff("sdvig_rolik_step", 0.55)
        rolik_sd = round(length_val / rolik_step)
        zamok = round(length_val / rolik_step)

        lenta_add = price_manager.get_auto_coeff("sdvig_lenta_add", 0.2)
        lenta = (rolik_sd * (height_g_val + lenta_add)) + length_val

        mehanizm = 2
        profil = 2
        perehodnik = 4

        luver_step = price_manager.get_auto_coeff("sdvig_luver_step", 0.2)
        luver_40 = math.ceil(length_val / luver_step)
        luver_rounding = price_manager.get_auto_coeff("sdvig_luver_rounding", 10)
        luver_40 -= luver_40 % -luver_rounding

        espander_multiplier = price_manager.get_auto_coeff("sdvig_espander_multiplier", 1.25)
        espander = math.ceil(length_val * espander_multiplier)
        kruchok = math.ceil(luver_40 / 2)

        luver_12 = math.ceil(length_val / luver_step)
        luver_12 -= luver_12 % -luver_rounding

        work_multiplier = price_manager.get_auto_coeff("sdvig_work_multiplier", 1.1)
        rabota = length_val * work_multiplier

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

        walls_multiplier = price_manager.get_auto_coeff("sdvig_walls_multiplier", 2)
        sdvig_stenki_cost = sdvig_stenki_cost * walls_multiplier

        final_multiplier = price_manager.get_auto_coeff("sdvig_final_multiplier", 1.8)
        sdvig_stenki_cost = sdvig_stenki_cost * final_multiplier
        sdvig_stenki_cost -= sdvig_stenki_cost % 100

        sdvig_stenki_furnitura_cost = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                                       lenta * price_manager.get_auto_price('lenta_F1300') +
                                       rabota * price_manager.get_auto_price('work'))

        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * walls_multiplier
        sdvig_stenki_furnitura_cost = sdvig_stenki_furnitura_cost * final_multiplier
        sdvig_stenki_furnitura_cost -= sdvig_stenki_furnitura_cost % 100

        sdvig_stenki_luvers_cost = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                                    luver_40 * price_manager.get_auto_price('luvers_40') +
                                    luver_12 * price_manager.get_auto_price('luvers_12') +
                                    kruchok * price_manager.get_auto_price('kruchok_s') +
                                    espander * price_manager.get_auto_price('espander') +
                                    rabota * price_manager.get_auto_price('work'))

        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * walls_multiplier
        sdvig_stenki_luvers_cost = sdvig_stenki_luvers_cost * final_multiplier
        sdvig_stenki_luvers_cost -= sdvig_stenki_luvers_cost % 100

        legal_multiplier = price_manager.get_auto_coeff("sdvig_legal_multiplier", 1.2)
        if is_legal_entity:
            sdvig_stenki_cost *= legal_multiplier
            sdvig_stenki_furnitura_cost *= legal_multiplier
            sdvig_stenki_luvers_cost *= legal_multiplier

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
        borta_divider = price_manager.get_auto_coeff("karkas_borta_divider", 6)
        s_borta_niz = (length_val * 2 + width_val) / borta_divider
        s_borta_niz -= s_borta_niz % -1

        stoiki_divider = price_manager.get_auto_coeff("karkas_stoiki_divider", 6)
        stoiki = count_s_val * (height_p_val - height_b_val) / stoiki_divider
        stoiki -= stoiki % -1

        verh_divider = price_manager.get_auto_coeff("karkas_verh_divider", 6)
        verh = (length_val * 2 + width_val * 3) / verh_divider
        verh -= verh % -1

        usil_verh_divider = price_manager.get_auto_coeff("karkas_usil_verh_divider", 6)
        usil_verh = length_val * 3 / usil_verh_divider
        usil_verh -= usil_verh % -1

        usil_bok_step = price_manager.get_auto_coeff("karkas_usil_bok_step", 0.45)
        usil_bok_2 = (height_p_val - height_b_val) / usil_bok_step
        usil_bok_2 -= usil_bok_2 % -1
        usil_bok = (length_val * 2 + width_val) * usil_bok_2 / borta_divider
        usil_bok -= usil_bok % -1

        naborn_divider = price_manager.get_auto_coeff("karkas_naborn_bort_divider", 6)
        naborn_bort = (length_val * 2 + width_val) / naborn_divider
        naborn_bort -= naborn_bort % -1
        naborn_multiplier = price_manager.get_auto_coeff("karkas_naborn_bort_multiplier", 4)
        naborn_bort = naborn_bort * naborn_multiplier

        gaz_work_rate = price_manager.get_auto_coeff("karkas_gaz_work_rate", 0.1585)
        karkas_s_borta_gaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                              stoiki * price_manager.get_auto_price('truba_40_40_3') +
                              verh * price_manager.get_auto_price('truba_40_40_2') +
                              usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                              usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                              length_val / gaz_work_rate * price_manager.get_auto_price('work'))

        kamaz_work_rate = price_manager.get_auto_coeff("karkas_kamaz_work_rate", 0.151)
        karkas_s_borta_kamaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                                stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                verh * price_manager.get_auto_price('truba_60_40_2') +
                                usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                length_val / kamaz_work_rate * price_manager.get_auto_price('work'))

        platform_gaz_rate = price_manager.get_auto_coeff("karkas_platform_gaz_rate", 0.132)
        karkas_s_platform_gaz = (stoiki * price_manager.get_auto_price('truba_40_40_3') +
                                 verh * price_manager.get_auto_price('truba_40_40_2') +
                                 usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                                 usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                                 naborn_bort * price_manager.get_auto_price('doska') +
                                 length_val / platform_gaz_rate * price_manager.get_auto_price('work'))

        platform_kamaz_rate = price_manager.get_auto_coeff("karkas_platform_kamaz_rate", 0.1417)
        karkas_s_platform_kamaz = (stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                   verh * price_manager.get_auto_price('truba_60_40_2') +
                                   usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                   usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                   naborn_bort * price_manager.get_auto_price('doska') +
                                   length_val / platform_kamaz_rate * price_manager.get_auto_price('work'))

        razborn_work = price_manager.get_auto_coeff("karkas_razborn_work", 6)
        if marka_val == "Газель":
            karkas_razborn = (karkas_s_platform_gaz * 2 + razborn_work * price_manager.get_auto_price('work') * 2)
        else:
            karkas_razborn = (karkas_s_platform_kamaz * 2 + razborn_work * price_manager.get_auto_price('work') * 2)

        legal_multiplier = price_manager.get_auto_coeff("karkas_legal_multiplier", 1.2)
        if is_legal_entity:
            karkas_s_borta_gaz *= legal_multiplier
            karkas_s_borta_kamaz *= legal_multiplier
            karkas_s_platform_gaz *= legal_multiplier
            karkas_s_platform_kamaz *= legal_multiplier
            karkas_razborn *= legal_multiplier

        if discount_percent > 0:
            karkas_s_borta_gaz *= (1 - discount_percent / 100)
            karkas_s_borta_kamaz *= (1 - discount_percent / 100)
            karkas_s_platform_gaz *= (1 - discount_percent / 100)
            karkas_s_platform_kamaz *= (1 - discount_percent / 100)
            karkas_razborn *= (1 - discount_percent / 100)

        final_multiplier = price_manager.get_auto_coeff("karkas_final_multiplier", 2)
        karkas_s_borta_gaz = karkas_s_borta_gaz * final_multiplier
        karkas_s_borta_gaz -= karkas_s_borta_gaz % -100
        karkas_s_borta_kamaz = karkas_s_borta_kamaz * final_multiplier
        karkas_s_borta_kamaz -= karkas_s_borta_kamaz % -100
        karkas_s_platform_gaz = karkas_s_platform_gaz * final_multiplier
        karkas_s_platform_gaz -= karkas_s_platform_gaz % -100
        karkas_s_platform_kamaz = karkas_s_platform_kamaz * final_multiplier
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

    # Расчет всех компонентов
    msk_cost = calculate_msk_cost(length, width, is_vorota, is_schit)
    shtornik_cost = calculate_shtornik_cost(length)
    tros_cost = calculate_tros_cost(length, width, height_p, is_vorota, is_schit)
    demontazh_cost = calculate_demontazh_cost(length)
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
                      format_cost(demontazh_cost)]
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