import streamlit as st
import pandas as pd
import math
from typing import Dict, Any, Tuple, List, Optional


class PriceManager:
    """Класс для управления ценами из secrets"""

    def __init__(self):
        self.polog_prices = st.secrets.get("prices", {}).get("polog", {})
        self.auto_prices = st.secrets.get("prices", {}).get("auto", {})
        self.polog_coeffs = st.secrets.get("polog_coefficients", {})
        self.auto_coeffs = st.secrets.get("auto_coefficients", {})
        self.chulok_coeffs = st.secrets.get("chulok_coefficients", {})
        self.sdvizhnoy_coeffs = st.secrets.get("sdvizhnoy_coefficients", {})
        self.additional_coeffs = st.secrets.get("additional_coefficients", {})

    def get_polog_price(self, material: str) -> float:
        return self.polog_prices.get(material, 0)

    def get_auto_price(self, material: str) -> float:
        return self.auto_prices.get(material, 0)

    def get_polog_coeff(self, name: str, default: Any = None) -> Any:
        return self.polog_coeffs.get(name, default)

    def get_auto_coeff(self, name: str, default: Any = None) -> Any:
        return self.auto_coeffs.get(name, default)

    def get_chulok_coeff(self, name: str, default: Any = None) -> Any:
        return self.chulok_coeffs.get(name, default)

    def get_sdvizhnoy_coeff(self, name: str, default: Any = None) -> Any:
        return self.sdvizhnoy_coeffs.get(name, default)

    def get_additional_coeff(self, name: str, default: Any = None) -> Any:
        return self.additional_coeffs.get(name, default)


class AuthManager:
    """Класс для управления авторизацией"""

    def __init__(self):
        self.username = st.secrets.get("auth", {}).get("username", "")
        self.password = st.secrets.get("auth", {}).get("password", "")

    def check_password(self) -> bool:
        """Проверка пароля"""
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
        """Выход из системы"""
        if st.sidebar.button("Выйти"):
            st.session_state.authenticated = False
            st.rerun()


def page_polog_calculator(price_manager: PriceManager):
    """Страница калькулятора пологов"""
    st.title("Калькулятор пологов")

    # Словарь с русскими названиями материалов
    material_names = {
        'pp': 'ПП', 'brezent': 'Брезент', 'pvh_300': 'ПВХ300',
        'pvh_500': 'ПВХ500', 'pvh_630': 'ПВХ630', 'pvh_650': 'ПВХ650',
        'pvh_900': 'ПВХ900', 'setka_green': 'Сетка зелёная',
        'setka_not_green': 'Сетка не зелёная', 'tafeta_and_brezent': 'Тафета+брезент',
        'plenka': 'Плёнка', 'tafeta_and_oksford': 'Тафета+оксфорд', 'oksford': 'Оксфорд'
    }

    # Ввод данных
    length = st.number_input("Введите длину изделия (м)", value=1.0, min_value=0.01)
    width = st.number_input("Введите ширину изделия (м)", value=1.0, min_value=0.01)
    count = st.number_input("Введите количество изделий", value=1, min_value=1, step=1)

    col1, col2 = st.columns(2)
    with col1:
        is_legal_entity = st.checkbox("Юридическое лицо")
    with col2:
        apply_discount = st.checkbox("Предоставить скидку")

    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

    # Функция расчёта стоимости одного полога (как в оригинале)
    def calculate_cost(material_price, length, width):
        sq_pol = (length + 0.2) * (width + 0.2)
        luvers_pol = (length * 2 + width * 2) / 0.3
        luvers_pol -= luvers_pol % -1  # Округляем до целого числа вверх
        cost = ((sq_pol * material_price) + (luvers_pol * price_manager.get_polog_price('luver')) +
                (sq_pol * 0.2 * price_manager.get_polog_price('work'))) * 2.5
        cost -= cost % -100  # Округляем до сотен вверх

        if is_legal_entity:
            cost = cost * 0.25 + cost

        # Применяем скидку ДО округления до сотен
        if discount_percent > 0:
            cost = cost * (1 - discount_percent / 100)
            cost = int(cost // 100 * 100)  # Округляем до сотен вниз

        return int(cost)

    # Создаём список для хранения результатов
    results = []

    # Расчёт для каждого материала
    for material, price in price_manager.polog_prices.items():
        if material not in ['luver', 'work']:
            cost_per_item = calculate_cost(price, length, width)
            total_cost = cost_per_item * count

            results.append({
                'Материал': material_names.get(material, material),
                'Стоимость за 1 изделие': "{:,.2f} руб".format(cost_per_item).replace(",", " "),
                'Стоимость за все изделия': "{:,.2f} руб".format(total_cost).replace(",", " ")
            })

    results_df = pd.DataFrame(results)
    st.dataframe(results_df, hide_index=True, use_container_width=True)


def page_auto_calculator(price_manager: PriceManager):
    """Страница калькулятора авто (полная версия)"""
    st.title("Калькулятор продукции на авто")
    st.write("Цены актуальны на 10.10.2025")

    # Ввод данных
    length = st.number_input("Введите длину (м)", value=1.0, min_value=0.01)
    width = st.number_input("Введите ширину (м)", value=1.0, min_value=0.01)
    height_p = st.number_input("Введите полезную высоту (м)", value=1.0, min_value=0.01)
    height_g = st.number_input("Введите высоту готовой стенки (м)", value=1.0, min_value=0.01)
    height_b = st.number_input("Введите высоту борта (м)", value=1.0, min_value=0.01)
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
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

    # Функция для расчёта площади изделия
    def calculate_area(length, width, height_g, is_vorota, is_schit):
        if is_vorota and is_schit:
            sq = (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            sq = (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            sq = (length * height_g * 2) + (width * height_g * 2) + (length * width)
        return sq

    # Функция для расчёта стоимости ткани (типовой тент)
    def calculate_typical_cost(material_price, area, length, is_legal_entity, discount_percent):
        if length < 5:
            cost = material_price * 2.8
        elif length > 10:
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
        return int(cost)

    # Функция для расчёта стоимости "Тент (чулок)"
    def calculate_chulok_cost(material_price, area, length, is_legal_entity, discount_percent):
        fabric_cost = material_price * area
        fabric_cost -= fabric_cost % -100

        babochka_count = ((round(length / 0.65)) - 6) * 3 + 6 * 5
        babochka_cost = babochka_count * price_manager.get_auto_price('babochka')
        work_cost = price_manager.get_auto_price('work') * (length / 0.4)

        total_cost = (fabric_cost + babochka_cost + work_cost) * 2

        if is_legal_entity:
            total_cost *= 1.25

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost -= total_cost % -100
        return int(total_cost)

    # Функция для расчёта стоимости "Тент сдвижной крыши"
    def calculate_sdvizhnoy_krysha_cost(material_price, length, width, is_legal_entity, discount_percent):
        s_krysha = (length + 0.6) * (width + 0.6)
        p_shnur = length * 2 + 2

        if math.ceil((length - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2) + 1

        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width * 0.1) + ((length * 2 + width * 2) * 0.15)
        count_work = length * 1.5

        total_cost = (s_krysha * material_price + p_shnur * price_manager.get_auto_price('shnur_8') +
                      count_remeshki * price_manager.get_auto_price('remeshok') + p_usilitel * material_price +
                      count_work * price_manager.get_auto_price('work'))

        if is_legal_entity:
            total_cost *= 1.25

        if discount_percent > 0:
            total_cost *= (1 - discount_percent / 100)

        total_cost = total_cost * 1.7
        total_cost -= total_cost % -100
        return int(total_cost)

    # Функция для расчёта стоимости МСК (пластины)
    def calculate_msk_cost(length, is_legal_entity, discount_percent):
        if math.ceil(length / 0.65 * 2) % 2 == 0:
            kronshtein_count = math.ceil(length / 0.65 * 2)
        else:
            kronshtein_count = math.ceil(length / 0.65 * 2) + 1

        truba_30_30_count = (kronshtein_count / 2 * 2.55) / 6
        truba_30_30_count -= truba_30_30_count % -1
        truba_60_40_count = length / 6 * 2
        truba_60_40_count -= truba_60_40_count % -1
        shveler_count = length / 2.48 * 2
        shveler_count -= shveler_count % -1

        if math.ceil((length - 1) / 0.65 * 2) % 2 == 0:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2)
        else:
            count_plastin_650 = math.ceil((length - 1) / 0.65 * 2) + 1
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
                        length * 6 * price_manager.get_auto_price('work')) * 2)

        if is_legal_entity:
            msk_cost *= 1.2

        if discount_percent > 0:
            msk_cost *= (1 - discount_percent / 100)

        msk_cost -= msk_cost % -100
        return int(msk_cost)

    # Функция для расчёта стоимости Шторного механизма
    def calculate_shtornik_cost(length, is_legal_entity, discount_percent):
        shtorn_profile_count = length / 6 * 2
        shtorn_profile_count -= shtorn_profile_count % -1
        shtorn_work_count = length * 0.73
        shtorn_work_count -= shtorn_work_count % -1

        shtornik_cost = int((shtorn_profile_count * price_manager.get_auto_price('shtorn_profil') +
                             shtorn_work_count * price_manager.get_auto_price('work')) * 2)

        if is_legal_entity:
            shtornik_cost *= 1.2

        if discount_percent > 0:
            shtornik_cost *= (1 - discount_percent / 100)

        shtornik_cost -= shtornik_cost % -100
        return int(shtornik_cost)

    # Функция для расчёта стоимости Троса
    def calculate_tros_cost(length, width, height_p, is_vorota, is_schit, is_legal_entity, discount_percent):
        perimetr_total = length * 2 + width * 2 + height_p * 4
        perimetr_half = length * 2 + width * 2 + height_p * 2
        perimetr_min = length * 2 + width * 2

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
        return int(tros_cost)

    # Функция для расчёта стоимости Демонтажа тента
    def calculate_demontazh_cost(length, is_legal_entity, discount_percent):
        demontazh_cost = int(length * 0.6 * price_manager.get_auto_price('work'))

        if is_legal_entity:
            demontazh_cost *= 1.2

        if discount_percent > 0:
            demontazh_cost *= (1 - discount_percent / 100)

        demontazh_cost -= demontazh_cost % -100
        return int(demontazh_cost)

    # Функция для расчёта стоимости Ворот
    def calculate_vorota_cost(width, height_g, marka, is_legal_entity, discount_percent):
        ramka_vorot = (width * 2 + height_g * 2) / 6
        ramka_vorot -= ramka_vorot % -1
        zapory_count = width * 2 / 6
        zapory_count -= zapory_count % -1

        vorota_gazel = int((price_manager.get_auto_price('fanera_18') * 2 +
                            price_manager.get_auto_price('petlya_gaz') * 6 +
                            price_manager.get_auto_price('zamki_gaz') * 2 +
                            (width * 2 + height_g * 3) * price_manager.get_auto_price('uplotnitel_18') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_gazel -= vorota_gazel % -100

        vorota_kamaz = int((price_manager.get_auto_price('fanera_21_2') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width * 2 + height_g * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_kamaz -= vorota_kamaz % -100

        vorota_other = int((price_manager.get_auto_price('fanera_21_3') * 2 +
                            price_manager.get_auto_price('petlya_kamaz') * 8 +
                            price_manager.get_auto_price('zamki_kamaz') * 2 +
                            (width * 2 + height_g * 3) * price_manager.get_auto_price('uplotnitel_21') +
                            ramka_vorot * price_manager.get_auto_price('truba_60_40_3') +
                            zapory_count * price_manager.get_auto_price('du_15') +
                            32 * price_manager.get_auto_price('work')) * 2)
        vorota_other -= vorota_other % -100

        if marka == "Газель":
            vorota_cost = vorota_gazel
        elif marka == "Иное" and height_g > 2.4:
            vorota_cost = vorota_other
        elif marka == "Иное" and height_g <= 2.4:
            vorota_cost = vorota_kamaz
        else:
            vorota_cost = 0

        if is_legal_entity:
            vorota_cost *= 1.2

        if discount_percent > 0:
            vorota_cost *= (1 - discount_percent / 100)

        vorota_cost -= vorota_cost % -100
        return int(vorota_cost)

    # Рассчитываем площадь
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

    # Создаём список материалов для расчета
    materials = {
        'ПВХ630': price_manager.get_auto_price('pvh_630'),
        'ПВХ650': price_manager.get_auto_price('pvh_650'),
        'ПВХ750': price_manager.get_auto_price('pvh_750'),
        'ПВХ900': price_manager.get_auto_price('pvh_900')
    }

    # Форматирование стоимости
    def format_cost(cost):
        if cost == 0:
            return "Не выбрано"
        return "{:,.2f} руб".format(cost).replace(",", " ")

    # Расчет для каждого типа тента
    results_typical = []
    results_chulok = []
    results_sdvizhnoy = []

    for material_name, material_price in materials.items():
        if material_price:
            results_typical.append(
                calculate_typical_cost(material_price, area, length, is_legal_entity, discount_percent))
            results_chulok.append(
                calculate_chulok_cost(material_price, area, length, is_legal_entity, discount_percent))
            results_sdvizhnoy.append(
                calculate_sdvizhnoy_krysha_cost(material_price, length, width, is_legal_entity, discount_percent))

    # Расчет дополнительных компонентов
    msk_cost = calculate_msk_cost(length, is_legal_entity, discount_percent)
    shtornik_cost = calculate_shtornik_cost(length, is_legal_entity, discount_percent)
    tros_cost = calculate_tros_cost(length, width, height_p, is_vorota, is_schit, is_legal_entity, discount_percent)
    demontazh_cost = calculate_demontazh_cost(length, is_legal_entity, discount_percent)
    vorota_cost = calculate_vorota_cost(width, height_g, marka, is_legal_entity, discount_percent) if marka else 0

    # Создаём DataFrame для основной таблицы
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

        # Дополнительные компоненты
        st.subheader("Дополнительные компоненты")

        additional_df = pd.DataFrame({
            "Компонент": ["МСК (пластины)", "Шторный механизм", "Трос", "Демонтаж тента", "Ворота"],
            "Стоимость": [format_cost(msk_cost), format_cost(shtornik_cost), format_cost(tros_cost),
                          format_cost(demontazh_cost), format_cost(vorota_cost)]
        })

        st.dataframe(additional_df, hide_index=True, use_container_width=True)
    else:
        st.warning("Недостаточно данных для расчета")


def page_info():
    """Страница с дополнительной информацией"""
    st.title("Ещё калькулятор")
    st.write("Место для ещё какого-нибудь калькулятора...")


def main():
    """Главная функция приложения"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    auth_manager = AuthManager()

    if not auth_manager.check_password():
        return

    st.sidebar.title("Меню")
    page = st.sidebar.radio("Выберите страницу",
                            ["Калькулятор пологов", "Калькулятор авто", "Ещё калькулятор"])

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