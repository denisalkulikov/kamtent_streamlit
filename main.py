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
        self.typical_coeffs = st.secrets.get("typical_coefficients", {})
        self.chulok_coeffs = st.secrets.get("chulok_coefficients", {})
        self.sdvizhnoy_coeffs = st.secrets.get("sdvizhnoy_coefficients", {})
        self.reklama_coeffs = st.secrets.get("reklama_coefficients", {})
        self.msk_coeffs = st.secrets.get("msk_coefficients", {})
        self.shtornik_coeffs = st.secrets.get("shtornik_coefficients", {})
        self.tros_coeffs = st.secrets.get("tros_coefficients", {})
        self.demontazh_coeffs = st.secrets.get("demontazh_coefficients", {})
        self.vorota_coeffs = st.secrets.get("vorota_coefficients", {})
        self.sdvig_coeffs = st.secrets.get("sdvig_coefficients", {})
        self.karkas_coeffs = st.secrets.get("karkas_coefficients", {})

    def get_polog_price(self, material: str) -> float:
        return self.polog_prices.get(material, 0)

    def get_auto_price(self, material: str) -> float:
        return self.auto_prices.get(material, 0)

    def get_polog_coeff(self, name: str) -> Any:
        return self.polog_coeffs[name]

    def get_typical_coeff(self, name: str) -> Any:
        return self.typical_coeffs[name]

    def get_chulok_coeff(self, name: str) -> Any:
        return self.chulok_coeffs[name]

    def get_sdvizhnoy_coeff(self, name: str) -> Any:
        return self.sdvizhnoy_coeffs[name]

    def get_reklama_coeff(self, name: str) -> Any:
        return self.reklama_coeffs[name]

    def get_msk_coeff(self, name: str) -> Any:
        return self.msk_coeffs[name]

    def get_shtornik_coeff(self, name: str) -> Any:
        return self.shtornik_coeffs[name]

    def get_tros_coeff(self, name: str) -> Any:
        return self.tros_coeffs[name]

    def get_demontazh_coeff(self, name: str) -> Any:
        return self.demontazh_coeffs[name]

    def get_vorota_coeff(self, name: str) -> Any:
        return self.vorota_coeffs[name]

    def get_sdvig_coeff(self, name: str) -> Any:
        return self.sdvig_coeffs[name]

    def get_karkas_coeff(self, name: str) -> Any:
        return self.karkas_coeffs[name]


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

    # Получаем коэффициенты из secrets
    luver_spacing = price_manager.get_polog_coeff("luver_spacing")
    multiplier = price_manager.get_polog_coeff("multiplier")
    work_percentage = price_manager.get_polog_coeff("work_percentage")
    legal_multiplier = price_manager.get_polog_coeff("legal_entity_multiplier")

    def calculate_cost(material_price, length, width):
        sq_pol = (length + 0.2) * (width + 0.2)
        luvers_pol = (length * 2 + width * 2) / luver_spacing
        luvers_pol -= luvers_pol % -1

        cost = ((sq_pol * material_price) +
                (luvers_pol * price_manager.get_polog_price('luver')) +
                (sq_pol * work_percentage * price_manager.get_polog_price('work'))) * multiplier

        # Округление до сотен вверх
        cost -= cost % -100

        # Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + legal_multiplier)

        # Скидка применяется ПОСЛЕ наценки юрлица
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

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
            return (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            return (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            return (length * height_g * 2) + (width * height_g * 2) + (length * width)

    # Функция для расчёта стоимости ткани (типовой тент) - ТОЧНО КАК В ПОЛОГАХ
    def calculate_typical_cost(material_price, area, length_val):
        typical = price_manager.get_typical_coeff

        # 1. Базовая стоимость
        if length_val < typical("length_small"):
            cost = material_price * typical("coefficient_small")
        elif length_val > typical("length_large"):
            cost = material_price * typical("coefficient_large")
        else:
            cost = material_price * typical("coefficient_medium")

        # Округление до десятков
        cost -= cost % -typical("rounding_step")

        # Умножаем на площадь
        cost = cost * area

        # 2. Округление до сотен вверх
        cost -= cost % -typical("rounding_final")

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (typical("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости "Тент (чулок)"
    def calculate_chulok_cost(material_price, area, length_val):
        chulok = price_manager.get_chulok_coeff

        # 1. Базовая стоимость
        fabric_cost = material_price * area
        fabric_cost -= fabric_cost % -100

        babochka_count = ((round(length_val / chulok("babochka_step"))) - chulok("babochka_base")) * 3 + 6 * 5
        babochka_cost = babochka_count * price_manager.get_auto_price('babochka')

        work_cost = price_manager.get_auto_price('work') * (length_val / chulok("work_step"))

        cost = (fabric_cost + babochka_cost + work_cost) * chulok("multiplier")

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (chulok("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости "Тент сдвижной крыши"
    def calculate_sdvizhnoy_krysha_cost(material_price, length_val, width_val):
        sdvizhnoy = price_manager.get_sdvizhnoy_coeff

        # 1. Базовая стоимость
        s_krysha = (length_val + sdvizhnoy("add_length")) * (width_val + 0.6)
        p_shnur = length_val * 2 + 2

        if math.ceil((length_val - 1) / sdvizhnoy("plastin_step") * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / sdvizhnoy("plastin_step") * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / sdvizhnoy("plastin_step") * 2) + 1

        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width_val * 0.1) + ((length_val * 2 + width_val * 2) * 0.15)
        count_work = length_val * 1.5

        cost = (s_krysha * material_price + p_shnur * price_manager.get_auto_price('shnur_8') +
                count_remeshki * price_manager.get_auto_price('remeshok') + p_usilitel * material_price +
                count_work * price_manager.get_auto_price('work'))

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (sdvizhnoy("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        # 5. Умножаем на коэффициент
        cost = cost * sdvizhnoy("multiplier")

        # 6. Финальное округление
        cost -= cost % -100

        return int(cost)

    # Функция для расчёта стоимости тента с рекламой
    def calculate_reklama_cost(reklama_area, total_area, material_price, length_val):
        reklama = price_manager.get_reklama_coeff

        # 1. Базовая стоимость
        reklama_cost = reklama_area * price_manager.get_auto_price('reklama')
        fabric_cost = (total_area - reklama_area) * material_price
        work_cost = (length_val / reklama("work_step")) * price_manager.get_auto_price('work')

        cost = (reklama_cost + fabric_cost + work_cost) * reklama("multiplier")

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (reklama("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости МСК (пластины)
    def calculate_msk_cost(length_val):
        msk = price_manager.get_msk_coeff

        # 1. Базовая стоимость
        if math.ceil(length_val / msk("kronshtein_step") * 2) % 2 == 0:
            kronshtein_count = math.ceil(length_val / msk("kronshtein_step") * 2)
        else:
            kronshtein_count = math.ceil(length_val / msk("kronshtein_step") * 2) + 1

        truba_30_30_count = (kronshtein_count / 2 * msk("truba_coeff")) / msk("truba_divider")
        truba_30_30_count -= truba_30_30_count % -1

        truba_60_40_count = length_val / 6 * 2
        truba_60_40_count -= truba_60_40_count % -1

        shveler_count = length_val / msk("shveler_step") * 2
        shveler_count -= shveler_count % -1

        if math.ceil((length_val - 1) / msk("plastin_step") * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length_val - 1) / msk("plastin_step") * 2)
        else:
            count_plastin_650 = math.ceil((length_val - 1) / msk("plastin_step") * 2) + 1
        count_plastin_black = count_plastin_650 + 2

        cost = (kronshtein_count * price_manager.get_auto_price('kronshtein') +
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
                msk("work_hours") * price_manager.get_auto_price('work') +
                length_val * msk("work_per_meter") * price_manager.get_auto_price('work'))

        # 2. Умножаем на мультипликатор
        cost = cost * msk("multiplier")

        # 3. Округление до сотен вверх
        cost -= cost % -100

        # 4. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (msk("legal_multiplier") - 1))

        # 5. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости Шторного механизма
    def calculate_shtornik_cost(length_val):
        shtornik = price_manager.get_shtornik_coeff

        # 1. Базовая стоимость
        shtorn_profile_count = length_val / shtornik("profile_divider") * 2
        shtorn_profile_count -= shtorn_profile_count % -1

        shtorn_work_count = length_val * shtornik("work_coeff")
        shtorn_work_count -= shtorn_work_count % -1

        cost = (shtorn_profile_count * price_manager.get_auto_price('shtorn_profil') +
                shtorn_work_count * price_manager.get_auto_price('work')) * shtornik("multiplier")

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (shtornik("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости Троса
    def calculate_tros_cost(length_val, width_val, height_p_val, is_vorota, is_schit):
        tros = price_manager.get_tros_coeff

        # 1. Базовая стоимость
        perimetr_total = length_val * 2 + width_val * 2 + height_p_val * 4
        perimetr_half = length_val * 2 + width_val * 2 + height_p_val * 2
        perimetr_min = length_val * 2 + width_val * 2

        if is_vorota and is_schit:
            cost = perimetr_total * price_manager.get_auto_price('tros') * tros("multiplier")
        elif not is_vorota and not is_schit:
            cost = perimetr_min * price_manager.get_auto_price('tros') * tros("multiplier")
        else:
            cost = perimetr_half * price_manager.get_auto_price('tros') * tros("multiplier")

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (tros("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости Демонтажа тента
    def calculate_demontazh_cost(length_val):
        demontazh = price_manager.get_demontazh_coeff

        # 1. Базовая стоимость
        cost = length_val * demontazh("multiplier") * price_manager.get_auto_price('work')

        # 2. Округление до сотен вверх
        cost -= cost % -100

        # 3. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (demontazh("legal_multiplier") - 1))

        # 4. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта стоимости ворот
    def calculate_vorota_cost(width_val, height_g_val, marka_val):
        vorota = price_manager.get_vorota_coeff

        # 1. Базовая стоимость
        ramka_vorot = (width_val * 2 + height_g_val * 2) / vorota("ramka_divider")
        ramka_vorot -= ramka_vorot % -1

        zapory_count = width_val * 2 / vorota("zapory_divider")
        zapory_count -= zapory_count % -1

        vorota_gazel = (price_manager.get_auto_price('fanera_18') * 2 +
                        price_manager.get_auto_price('petlya_gaz') * 6 +
                        price_manager.get_auto_price('zamki_gaz') * 2 +
                        (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_18') +
                        ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                        zapory_count * price_manager.get_auto_price('du_15') +
                        vorota("work_hours") * price_manager.get_auto_price('work'))

        vorota_kamaz = (price_manager.get_auto_price('fanera_21_2') * 2 +
                        price_manager.get_auto_price('petlya_kamaz') * 8 +
                        price_manager.get_auto_price('zamki_kamaz') * 2 +
                        (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                        ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                        zapory_count * price_manager.get_auto_price('du_15') +
                        vorota("work_hours") * price_manager.get_auto_price('work'))

        vorota_other = (price_manager.get_auto_price('fanera_21_3') * 2 +
                        price_manager.get_auto_price('petlya_kamaz') * 8 +
                        price_manager.get_auto_price('zamki_kamaz') * 2 +
                        (width_val * 2 + height_g_val * 3) * price_manager.get_auto_price('uplotnitel_21') +
                        ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                        zapory_count * price_manager.get_auto_price('du_15') +
                        vorota("work_hours") * price_manager.get_auto_price('work'))

        if marka_val == "Газель":
            cost = vorota_gazel
        elif marka_val == "Иное" and height_g_val > vorota("height_threshold"):
            cost = vorota_other
        elif marka_val == "Иное" and height_g_val <= vorota("height_threshold"):
            cost = vorota_kamaz
        else:
            cost = 0

        # 2. Умножаем на 2
        cost = cost * 2

        # 3. Округление до сотен вверх
        cost -= cost % -100

        # 4. Наценка юрлица
        if is_legal_entity:
            cost = cost * (1 + (vorota("legal_multiplier") - 1))

        # 5. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

        return int(cost)

    # Функция для расчёта сдвижных стенок
    def calculate_sdvig_stenki_cost(length_val, height_g_val):
        sdvig = price_manager.get_sdvig_coeff

        # 1. Базовая стоимость
        square_sdvig_stenok = (length_val + sdvig("add_length")) * height_g_val + (length_val + sdvig("add_length"))

        rolik_sd = round(length_val / sdvig("rolik_step"))
        zamok = round(length_val / sdvig("rolik_step"))
        lenta = (rolik_sd * (height_g_val + sdvig("lenta_add"))) + length_val
        mehanizm = 2
        profil = 2
        perehodnik = 4

        luver_40 = math.ceil(length_val / sdvig("luver_step"))
        luver_40 -= luver_40 % -sdvig("luver_rounding")
        espander = math.ceil(length_val * sdvig("espander_multiplier"))
        kruchok = math.ceil(luver_40 / 2)
        luver_12 = math.ceil(length_val / sdvig("luver_step"))
        luver_12 -= luver_12 % -sdvig("luver_rounding")
        rabota = length_val * sdvig("work_multiplier")

        cost_new = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
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

        cost_furnitura = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                          lenta * price_manager.get_auto_price('lenta_F1300') +
                          rabota * price_manager.get_auto_price('work'))

        cost_luvers = (square_sdvig_stenok * price_manager.get_auto_price('pvh_900') +
                       luver_40 * price_manager.get_auto_price('luvers_40') +
                       luver_12 * price_manager.get_auto_price('luvers_12') +
                       kruchok * price_manager.get_auto_price('kruchok_s') +
                       espander * price_manager.get_auto_price('espander') +
                       rabota * price_manager.get_auto_price('work'))

        # 2. Умножаем на коэффициенты
        cost_new = cost_new * sdvig("walls_multiplier") * sdvig("final_multiplier")
        cost_furnitura = cost_furnitura * sdvig("walls_multiplier") * sdvig("final_multiplier")
        cost_luvers = cost_luvers * sdvig("walls_multiplier") * sdvig("final_multiplier")

        # 3. Округление до сотен
        cost_new -= cost_new % 100
        cost_furnitura -= cost_furnitura % 100
        cost_luvers -= cost_luvers % 100

        # 4. Наценка юрлица
        if is_legal_entity:
            cost_new = cost_new * (1 + (sdvig("legal_multiplier") - 1))
            cost_furnitura = cost_furnitura * (1 + (sdvig("legal_multiplier") - 1))
            cost_luvers = cost_luvers * (1 + (sdvig("legal_multiplier") - 1))

        # 5. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost_new *= (1 - discount_percent / 100)
            cost_furnitura *= (1 - discount_percent / 100)
            cost_luvers *= (1 - discount_percent / 100)

        return int(cost_new), int(cost_furnitura), int(cost_luvers)

    # Функция для расчёта стоимости каркаса
    def calculate_karkas_cost(length_val, width_val, height_p_val, height_b_val, count_s_val, marka_val):
        karkas = price_manager.get_karkas_coeff

        # 1. Базовая стоимость
        s_borta_niz = (length_val * 2 + width_val) / karkas("borta_divider")
        s_borta_niz -= s_borta_niz % -1

        stoiki = count_s_val * (height_p_val - height_b_val) / karkas("stoiki_divider")
        stoiki -= stoiki % -1

        verh = (length_val * 2 + width_val * 3) / karkas("verh_divider")
        verh -= verh % -1

        usil_verh = length_val * 3 / karkas("usil_verh_divider")
        usil_verh -= usil_verh % -1

        usil_bok_2 = (height_p_val - height_b_val) / karkas("usil_bok_step")
        usil_bok_2 -= usil_bok_2 % -1
        usil_bok = (length_val * 2 + width_val) * usil_bok_2 / karkas("borta_divider")
        usil_bok -= usil_bok % -1

        naborn_bort = (length_val * 2 + width_val) / karkas("naborn_bort_divider")
        naborn_bort -= naborn_bort % -1
        naborn_bort = naborn_bort * karkas("naborn_bort_multiplier")

        karkas_s_borta_gaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                              stoiki * price_manager.get_auto_price('truba_40_40_3') +
                              verh * price_manager.get_auto_price('truba_40_40_2') +
                              usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                              usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                              length_val / karkas("gaz_work_rate") * price_manager.get_auto_price('work'))

        karkas_s_borta_kamaz = (s_borta_niz * price_manager.get_auto_price('truba_40_20_2') +
                                stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                verh * price_manager.get_auto_price('truba_60_40_2') +
                                usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                length_val / karkas("kamaz_work_rate") * price_manager.get_auto_price('work'))

        karkas_s_platform_gaz = (stoiki * price_manager.get_auto_price('truba_40_40_3') +
                                 verh * price_manager.get_auto_price('truba_40_40_2') +
                                 usil_verh * price_manager.get_auto_price('truba_40_20_2') +
                                 usil_bok * price_manager.get_auto_price('truba_40_20_2') +
                                 naborn_bort * price_manager.get_auto_price('doska') +
                                 length_val / karkas("platform_gaz_rate") * price_manager.get_auto_price('work'))

        karkas_s_platform_kamaz = (stoiki * price_manager.get_auto_price('truba_60_40_3') +
                                   verh * price_manager.get_auto_price('truba_60_40_2') +
                                   usil_verh * price_manager.get_auto_price('truba_40_40_2') +
                                   usil_bok * price_manager.get_auto_price('truba_40_40_2') +
                                   naborn_bort * price_manager.get_auto_price('doska') +
                                   length_val / karkas("platform_kamaz_rate") * price_manager.get_auto_price('work'))

        if marka_val == "Газель":
            cost_borta = karkas_s_borta_gaz
            cost_platform = karkas_s_platform_gaz
            cost_razborn = (
                        karkas_s_platform_gaz * 2 + karkas("razborn_work") * price_manager.get_auto_price('work') * 2)
        else:
            cost_borta = karkas_s_borta_kamaz
            cost_platform = karkas_s_platform_kamaz
            cost_razborn = (
                        karkas_s_platform_kamaz * 2 + karkas("razborn_work") * price_manager.get_auto_price('work') * 2)

        # 2. Умножаем на финальный множитель
        cost_borta = cost_borta * karkas("final_multiplier")
        cost_platform = cost_platform * karkas("final_multiplier")

        # 3. Округление до сотен вверх
        cost_borta -= cost_borta % -100
        cost_platform -= cost_platform % -100
        cost_razborn -= cost_razborn % -100

        # 4. Наценка юрлица
        if is_legal_entity:
            cost_borta = cost_borta * (1 + (karkas("legal_multiplier") - 1))
            cost_platform = cost_platform * (1 + (karkas("legal_multiplier") - 1))
            cost_razborn = cost_razborn * (1 + (karkas("legal_multiplier") - 1))

        # 5. Скидка (БЕЗ дополнительного округления)
        if discount_percent > 0:
            cost_borta *= (1 - discount_percent / 100)
            cost_platform *= (1 - discount_percent / 100)
            cost_razborn *= (1 - discount_percent / 100)

        return int(cost_borta), int(cost_platform), int(cost_razborn)

    # Рассчитываем площадь
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

    # Расчет всех компонентов
    msk_cost = calculate_msk_cost(length)
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
            results_typical.append(calculate_typical_cost(material_price, area, length))
            results_chulok.append(calculate_chulok_cost(material_price, area, length))
            results_sdvizhnoy.append(calculate_sdvizhnoy_krysha_cost(material_price, length, width))
            results_reklama_2_stenki.append(calculate_reklama_cost(reklama_2_stenki, area, material_price, length))

            if not is_vorota:
                results_reklama_2_stenki_and_klapan.append(
                    calculate_reklama_cost(reklama_2_stenki_and_klapan, area, material_price, length))
            else:
                results_reklama_2_stenki_and_klapan.append("НЕВЕРНО!")

            results_reklama_2_stenki_and_krysha.append(
                calculate_reklama_cost(reklama_2_stenki_and_krysha, area, material_price, length))

            if not is_vorota:
                results_reklama_2_stenki_and_klapan_and_krysha.append(
                    calculate_reklama_cost(reklama_2_stenki_and_klapan_and_krysha, area, material_price, length))
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