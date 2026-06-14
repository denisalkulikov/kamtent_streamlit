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

        # Форма входа
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


class PologCalculator:
    """Калькулятор для пологов"""

    def __init__(self, price_manager: PriceManager):
        self.pm = price_manager
        self.material_names = {
            'pp': 'ПП', 'brezent': 'Брезент', 'pvh_300': 'ПВХ300',
            'pvh_500': 'ПВХ500', 'pvh_630': 'ПВХ630', 'pvh_650': 'ПВХ650',
            'pvh_900': 'ПВХ900', 'setka_green': 'Сетка зелёная',
            'setka_not_green': 'Сетка не зелёная', 'tafeta_and_brezent': 'Тафета+брезент',
            'plenka': 'Плёнка', 'tafeta_and_oksford': 'Тафета+оксфорд', 'oksford': 'Оксфорд'
        }
        self.excluded_materials = {'luver', 'work'}

    def format_cost(self, cost: int) -> str:
        """Форматирование стоимости"""
        return "{:,.2f} руб".format(cost).replace(",", " ")

    def calculate_cost(self, material_price: float, length: float, width: float,
                       is_legal: bool, discount_percent: float) -> float:
        """Расчет стоимости одного полога без округления до количества"""
        # Площадь полога с учётом припусков
        sq_pol = (length + 0.2) * (width + 0.2)

        # Количество люверсов (округляем вверх)
        luver_spacing = self.pm.get_polog_coeff("luver_spacing", 0.3)
        luvers_pol = math.ceil((length * 2 + width * 2) / luver_spacing)

        # Расчёт стоимости без округления
        multiplier = self.pm.get_polog_coeff("multiplier", 2.5)
        work_percentage = self.pm.get_polog_coeff("work_percentage", 0.2)

        cost = ((sq_pol * material_price) +
                (luvers_pol * self.pm.get_polog_price('luver')) +
                (sq_pol * work_percentage * self.pm.get_polog_price('work'))) * multiplier

        # Применяем наценку для юрлица
        if is_legal:
            legal_multiplier = self.pm.get_polog_coeff("legal_entity_multiplier", 0.25)
            cost = cost * (1 + legal_multiplier)

        # Применяем скидку
        if discount_percent > 0:
            cost = cost * (1 - discount_percent / 100)

        return cost

    def run(self, length: float, width: float, count: int,
            is_legal: bool, discount_percent: float) -> pd.DataFrame:
        """Запуск расчета для всех материалов"""
        results = []
        rounding = self.pm.get_polog_coeff("rounding", 100)

        for material, price in self.pm.polog_prices.items():
            if material not in self.excluded_materials:
                # Сначала рассчитываем стоимость одного изделия без округления
                cost_per_item_raw = self.calculate_cost(price, length, width, is_legal, discount_percent)

                # Умножаем на количество
                total_cost_raw = cost_per_item_raw * count

                # Округляем до сотен
                cost_per_item = int(math.ceil(cost_per_item_raw / rounding)) * rounding
                total_cost = int(math.ceil(total_cost_raw / rounding)) * rounding

                results.append({
                    'Материал': self.material_names.get(material, material),
                    'Стоимость за 1 изделие': self.format_cost(cost_per_item),
                    'Стоимость за все изделия': self.format_cost(total_cost)
                })

        return pd.DataFrame(results)


class AutoCalculator:
    """Калькулятор для авто"""

    def __init__(self, price_manager: PriceManager):
        self.pm = price_manager

    def format_cost(self, cost: int) -> str:
        """Форматирование стоимости"""
        return "{:,.2f} руб".format(cost).replace(",", " ")

    def calculate_typical_cost(self, material_price: float, area: float, length: float,
                               is_legal: bool, discount_percent: float) -> int:
        """Расчет стоимости типового тента"""
        # Определяем коэффициент в зависимости от длины
        length_small = self.pm.get_auto_coeff("length_small", 5)
        length_large = self.pm.get_auto_coeff("length_large", 10)
        coeff_small = self.pm.get_auto_coeff("coefficient_small", 2.8)
        coeff_medium = self.pm.get_auto_coeff("coefficient_medium", 2.6)
        coeff_large = self.pm.get_auto_coeff("coefficient_large", 2.4)

        if length < length_small:
            cost = material_price * coeff_small
        elif length > length_large:
            cost = material_price * coeff_large
        else:
            cost = material_price * coeff_medium

        # Округляем до десятков
        rounding_step = self.pm.get_auto_coeff("rounding_step", 10)
        cost = math.ceil(cost / rounding_step) * rounding_step

        # Умножаем на площадь
        cost = cost * area

        # Применяем наценку для юрлица
        if is_legal:
            legal_multiplier = self.pm.get_auto_coeff("legal_entity_multiplier", 0.25)
            cost = cost * (1 + legal_multiplier)

        # Применяем скидку
        if discount_percent > 0:
            discount_multiplier = self.pm.get_auto_coeff("discount_multiplier", 0.01)
            cost = cost * (1 - discount_percent * discount_multiplier)

        # Финальное округление до сотен
        rounding_final = self.pm.get_auto_coeff("rounding_final", 100)
        return int(math.ceil(cost / rounding_final) * rounding_final)


def page_polog_calculator(price_manager: PriceManager):
    """Страница калькулятора пологов"""
    st.title("Калькулятор пологов")

    calculator = PologCalculator(price_manager)

    # Ввод данных
    length = st.number_input("Введите длину изделия (м)", value=1.0, min_value=0.01, step=0.1)
    width = st.number_input("Введите ширину изделия (м)", value=1.0, min_value=0.01, step=0.1)
    count = st.number_input("Введите количество изделий", value=1, min_value=1, step=1)

    # Чекбоксы в две колонки
    col1, col2 = st.columns(2)
    with col1:
        is_legal_entity = st.checkbox("Юридическое лицо")
    with col2:
        apply_discount = st.checkbox("Предоставить скидку")

    # Поле для ввода скидки
    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

    # Расчет и отображение результатов
    results_df = calculator.run(length, width, count, is_legal_entity, discount_percent)
    st.dataframe(results_df, hide_index=True, use_container_width=True)


def page_auto_calculator(price_manager: PriceManager):
    """Страница калькулятора авто"""
    st.title("Калькулятор продукции на авто")
    st.write("Цены актуальны на 10.10.2025")

    # Инициализация состояния для хранения значений
    if 'auto_length' not in st.session_state:
        st.session_state.auto_length = 1.0

    # Ввод данных
    length = st.number_input("Введите длину (м)", value=st.session_state.auto_length,
                             min_value=0.01, step=0.1, key="auto_length_input")
    st.session_state.auto_length = length

    width = st.number_input("Введите ширину (м)", value=1.0, min_value=0.01, step=0.1)
    height_g = st.number_input("Введите высоту готовой стенки (м)", value=1.0, min_value=0.01, step=0.1)

    # Чекбоксы для ворот и щита
    col1, col2 = st.columns(2)
    with col1:
        is_vorota = st.checkbox("Наличие ворот")
        is_schit = st.checkbox("Наличие щита")
    with col2:
        is_legal_entity = st.checkbox("Юридическое лицо", key="auto_legal")
        apply_discount = st.checkbox("Предоставить скидку", key="auto_discount")

    # Поле для ввода скидки
    discount_percent = 0
    if apply_discount:
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0, max_value=100)

    # Функция для расчета площади
    def calculate_area(length, width, height_g, is_vorota, is_schit):
        if is_vorota and is_schit:
            return (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            return (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            return (length * height_g * 2) + (width * height_g * 2) + (length * width)

    # Расчет площади и стоимости
    area = calculate_area(length, width, height_g, is_vorota, is_schit)
    calculator = AutoCalculator(price_manager)

    # Материалы для расчета
    materials = {
        'ПВХ630': price_manager.get_auto_price('pvh_630'),
        'ПВХ650': price_manager.get_auto_price('pvh_650'),
        'ПВХ750': price_manager.get_auto_price('pvh_750'),
        'ПВХ900': price_manager.get_auto_price('pvh_900')
    }

    # Расчет результатов
    results_typical = []
    for material_name, material_price in materials.items():
        if material_price:
            cost = calculator.calculate_typical_cost(material_price, area, length, is_legal_entity, discount_percent)
            results_typical.append(cost)

    # Создание DataFrame
    results_df = pd.DataFrame({
        "Тент": ["Тент типовой"],
        "ПВХ630": [calculator.format_cost(results_typical[0]) if len(results_typical) > 0 else "N/A"],
        "ПВХ650": [calculator.format_cost(results_typical[1]) if len(results_typical) > 1 else "N/A"],
        "ПВХ750": [calculator.format_cost(results_typical[2]) if len(results_typical) > 2 else "N/A"],
        "ПВХ900": [calculator.format_cost(results_typical[3]) if len(results_typical) > 3 else "N/A"],
    })

    # Вывод результатов
    st.dataframe(results_df, hide_index=True, use_container_width=True)

    # Дополнительная информация
    st.info(
        "Примечание: Полная версия калькулятора авто включает расчеты МСК, шторных механизмов, сдвижных стенок и других компонентов.")


def page_info():
    """Страница с дополнительной информацией"""
    st.title("Ещё калькулятор")
    st.write("Место для ещё какого-нибудь калькулятора...")


def main():
    """Главная функция приложения"""
    # Инициализация состояния сессии
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    auth_manager = AuthManager()

    # Проверка авторизации
    if not auth_manager.check_password():
        return

    # Боковое меню
    st.sidebar.title("Меню")
    page = st.sidebar.radio("Выберите страницу",
                            ["Калькулятор пологов", "Калькулятор авто", "Ещё калькулятор"])

    # Кнопка выхода
    auth_manager.logout()

    # Инициализация менеджера цен
    price_manager = PriceManager()

    # Отображение выбранной страницы
    if page == "Калькулятор пологов":
        page_polog_calculator(price_manager)
    elif page == "Калькулятор авто":
        page_auto_calculator(price_manager)
    elif page == "Ещё калькулятор":
        page_info()


if __name__ == "__main__":
    main()