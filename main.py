import streamlit as st
import pandas as pd
import math
from typing import Dict, Any, Tuple, List, Optional


class PriceManager:
    """Класс для управления ценами из secrets"""

    def __init__(self):
        self.polog_prices = st.secrets.get("prices", {}).get("polog", {})
        self.auto_prices = st.secrets.get("prices", {}).get("auto", {})
        self.coefficients = st.secrets.get("coefficients", {})
        self.parameters = st.secrets.get("parameters", {})

    def get_polog_price(self, material: str) -> float:
        return self.polog_prices.get(material, 0)

    def get_auto_price(self, material: str) -> float:
        return self.auto_prices.get(material, 0)

    def get_coefficient(self, name: str, default: float = 0) -> float:
        return self.coefficients.get(name, default)

    def get_parameter(self, name: str, default: Any = None) -> Any:
        return self.parameters.get(name, default)


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


class CostCalculator:
    """Класс с методами расчета стоимости"""

    def __init__(self, price_manager: PriceManager):
        self.pm = price_manager

    def format_cost(self, cost: Any) -> str:
        """Форматирование стоимости"""
        if cost == "НЕВЕРНО!" or not isinstance(cost, (int, float)):
            return str(cost)
        return "{:,.2f} руб".format(cost).replace(",", " ")

    def round_to_hundreds(self, cost: float) -> int:
        """Округление до сотен в большую сторону"""
        return int(math.ceil(cost / 100) * 100)

    def apply_legal_discount(self, cost: float, is_legal: bool, discount_percent: float = 0) -> float:
        """Применение наценки для юрлица и скидки"""
        if is_legal:
            cost = cost * (1 + self.pm.get_coefficient("polog_discount_legal", 0.25))

        if discount_percent > 0:
            cost = cost * (1 - discount_percent / 100)

        return self.round_to_hundreds(cost)


class PologCalculator(CostCalculator):
    """Калькулятор для пологов"""

    def __init__(self, price_manager: PriceManager):
        super().__init__(price_manager)
        self.material_names = {
            'pp': 'ПП', 'brezent': 'Брезент', 'pvh_300': 'ПВХ300',
            'pvh_500': 'ПВХ500', 'pvh_630': 'ПВХ630', 'pvh_650': 'ПВХ650',
            'pvh_900': 'ПВХ900', 'setka_green': 'Сетка зелёная',
            'setka_not_green': 'Сетка не зелёная', 'tafeta_and_brezent': 'Тафета+брезент',
            'plenka': 'Плёнка', 'tafeta_and_oksford': 'Тафета+оксфорд', 'oksford': 'Оксфорд'
        }
        self.excluded_materials = {'luver', 'work'}

    def calculate_cost(self, material_price: float, length: float, width: float, count: int,
                       is_legal: bool, discount_percent: float) -> Tuple[int, int]:
        """Расчет стоимости одного полога и общей стоимости"""
        # Площадь полога с учётом припусков
        sq_pol = (length + 0.2) * (width + 0.2)
        # Количество люверсов (округляем вверх)
        luvers_pol = math.ceil((length * 2 + width * 2) / self.pm.get_parameter("polog_luver_spacing", 0.3))

        # Расчёт стоимости без округления
        cost = ((sq_pol * material_price) +
                (luvers_pol * self.pm.get_polog_price('luver')) +
                (sq_pol * 0.2 * self.pm.get_polog_price('work'))) * self.pm.get_parameter("polog_multiplier", 2.5)

        # Применяем наценку для юрлица и скидку
        if is_legal:
            cost = cost * (1 + self.pm.get_coefficient("polog_discount_legal", 0.25))

        if discount_percent > 0:
            cost = cost * (1 - discount_percent / 100)

        # Округляем до сотен
        cost = int(math.ceil(cost / 100) * 100)

        total_cost = cost * count
        return cost, total_cost

    def run(self, length: float, width: float, count: int, is_legal: bool, discount_percent: float) -> pd.DataFrame:
        """Запуск расчета для всех материалов"""
        results = []

        for material, price in self.pm.polog_prices.items():
            if material not in self.excluded_materials:
                cost_per_item, total_cost = self.calculate_cost(price, length, width, count, is_legal, discount_percent)
                results.append({
                    'Материал': self.material_names.get(material, material),
                    'Стоимость за 1 изделие': self.format_cost(cost_per_item),
                    'Стоимость за все изделия': self.format_cost(total_cost)
                })

        return pd.DataFrame(results)


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
    if 'auto_width' not in st.session_state:
        st.session_state.auto_width = 1.0
    if 'auto_height_p' not in st.session_state:
        st.session_state.auto_height_p = 1.0
    if 'auto_height_g' not in st.session_state:
        st.session_state.auto_height_g = 1.0
    if 'auto_height_b' not in st.session_state:
        st.session_state.auto_height_b = 1.0
    if 'auto_count_s' not in st.session_state:
        st.session_state.auto_count_s = 1

    # Ввод данных с использованием session_state
    length = st.number_input("Введите длину (м)", value=st.session_state.auto_length,
                             min_value=0.01, step=0.1, key="auto_length_input")
    st.session_state.auto_length = length

    width = st.number_input("Введите ширину (м)", value=st.session_state.auto_width,
                            min_value=0.01, step=0.1, key="auto_width_input")
    st.session_state.auto_width = width

    height_p = st.number_input("Введите полезную высоту (м)", value=st.session_state.auto_height_p,
                               min_value=0.01, step=0.1, key="auto_height_p_input")
    st.session_state.auto_height_p = height_p

    height_g = st.number_input("Введите высоту готовой стенки (м)", value=st.session_state.auto_height_g,
                               min_value=0.01, step=0.1, key="auto_height_g_input")
    st.session_state.auto_height_g = height_g

    height_b = st.number_input("Введите высоту борта (м)", value=st.session_state.auto_height_b,
                               min_value=0.01, step=0.1, key="auto_height_b_input")
    st.session_state.auto_height_b = height_b

    count_s = st.number_input("Введите количество стоек (шт)", value=st.session_state.auto_count_s,
                              min_value=1, step=1, key="auto_count_s_input")
    st.session_state.auto_count_s = count_s

    marka = st.selectbox("Выберите марку авто", ("Газель", "Иное"), index=None, placeholder="Выбрать вариант")

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
            sq = (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            sq = (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            sq = (length * height_g * 2) + (width * height_g * 2) + (length * width)
        return sq

    # Функция для расчета стоимости ткани
    def calculate_typical_cost(material_price, area, length, is_legal_entity, discount_percent):
        if length < 5:
            cost = material_price * 2.8
        elif length > 10:
            cost = material_price * 2.4
        else:
            cost = material_price * 2.6
        cost = math.ceil(cost / 10) * 10
        cost = cost * area

        if is_legal_entity:
            cost = cost * 1.25

        if discount_percent > 0:
            cost = cost * (1 - discount_percent / 100)

        return int(math.ceil(cost / 100) * 100)

    # Функция для форматирования
    def format_cost(cost):
        return "{:,.2f} руб".format(cost).replace(",", " ")

    # Расчет площади и стоимости для разных материалов
    area = calculate_area(length, width, height_g, is_vorota, is_schit)

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
            cost = calculate_typical_cost(material_price, area, length, is_legal_entity, discount_percent)
            results_typical.append(cost)

    # Создание DataFrame
    results_df = pd.DataFrame({
        "Тент": ["Тент типовой"],
        "ПВХ630": [format_cost(results_typical[0]) if len(results_typical) > 0 else "N/A"],
        "ПВХ650": [format_cost(results_typical[1]) if len(results_typical) > 1 else "N/A"],
        "ПВХ750": [format_cost(results_typical[2]) if len(results_typical) > 2 else "N/A"],
        "ПВХ900": [format_cost(results_typical[3]) if len(results_typical) > 3 else "N/A"],
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