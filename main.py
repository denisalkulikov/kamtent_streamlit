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

    def round_to_hundreds(self, cost: float) -> float:
        """Округление до сотен в большую сторону"""
        return math.ceil(cost / 100) * 100

    def apply_legal_discount(self, cost: float, is_legal: bool, discount_percent: float = 0) -> float:
        """Применение наценки для юрлица и скидки"""
        if is_legal:
            cost *= (1 + self.pm.get_coefficient("polog_discount_legal", 0.25))

        if discount_percent > 0:
            cost *= (1 - discount_percent / 100)

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
                       is_legal: bool, discount_percent: float) -> Tuple[float, float]:
        """Расчет стоимости одного полога и общей стоимости"""
        sq_pol = (length + 0.2) * (width + 0.2)
        luvers_pol = math.ceil((length * 2 + width * 2) / self.pm.get_parameter("polog_luver_spacing", 0.3))

        cost = ((sq_pol * material_price) +
                (luvers_pol * self.pm.get_polog_price('luver')) +
                (sq_pol * 0.2 * self.pm.get_polog_price('work'))) * self.pm.get_parameter("polog_multiplier", 2.5)

        cost = self.apply_legal_discount(cost, is_legal, discount_percent)
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


class AutoCalculator(CostCalculator):
    """Калькулятор для авто"""

    def __init__(self, price_manager: PriceManager):
        super().__init__(price_manager)
        self.excluded_materials = {'babochka', 'work', 'shnur_8', 'remeshok', 'reklama'}
        self.materials_list = ['pvh_630', 'pvh_650', 'pvh_750', 'pvh_900']

    def calculate_area(self, length: float, width: float, height_g: float, is_vorota: bool, is_schit: bool) -> float:
        """Расчет площади ткани"""
        if is_vorota and is_schit:
            return (length * height_g * 2) + (length * width)
        elif is_vorota or is_schit:
            return (length * height_g * 2) + (width * height_g) + (length * width)
        else:
            return (length * height_g * 2) + (width * height_g * 2) + (length * width)

    def calculate_typical_cost(self, material_price: float, area: float, is_legal: bool,
                               discount_percent: float) -> float:
        """Расчет стоимости типового тента"""
        length = st.session_state.get('auto_length', 1.0)

        if length < self.pm.get_parameter("polog_length_small", 5):
            cost = material_price * self.pm.get_parameter("polog_coefficient_small", 2.8)
        elif length > self.pm.get_parameter("polog_length_large", 10):
            cost = material_price * self.pm.get_parameter("polog_coefficient_large", 2.4)
        else:
            cost = material_price * self.pm.get_parameter("polog_coefficient_medium", 2.6)

        cost = self.round_to_hundreds(cost) * area
        return self.apply_legal_discount(cost, is_legal, discount_percent)

    def calculate_chulok_cost(self, material_price: float, area: float, length: float,
                              is_legal: bool, discount_percent: float) -> float:
        """Расчет стоимости тента-чулка"""
        fabric_cost = self.round_to_hundreds(material_price * area)
        babochka_count = ((round(length / self.pm.get_parameter("chulok_babochka_step", 0.65))) -
                          self.pm.get_parameter("chulok_babochka_base", 6)) * 3 + 6 * 5
        babochka_cost = babochka_count * self.pm.get_auto_price('babochka')
        work_cost = self.pm.get_auto_price('work') * (length / self.pm.get_parameter("chulok_work_step", 0.4))

        total_cost = (fabric_cost + babochka_cost + work_cost) * self.pm.get_parameter("chulok_multiplier", 2)
        return self.apply_legal_discount(total_cost, is_legal, discount_percent)

    def calculate_sdvizhnoy_krysha_cost(self, material_price: float, length: float, width: float,
                                        is_legal: bool, discount_percent: float) -> float:
        """Расчет стоимости тента со сдвижной крышей"""
        s_krysha = (length + self.pm.get_parameter("sdvizhnoy_add_length", 0.6)) * (width + 0.6)
        p_shnur = length * 2 + 2

        count_plastin_650 = math.ceil((length - 1) / self.pm.get_parameter("sdvizhnoy_plastin_step", 0.65) * 2)
        if count_plastin_650 % 2 != 0:
            count_plastin_650 += 1

        count_remeshki = ((round(count_plastin_650 / 2 + 1)) - 4) * 3 + 20
        p_usilitel = (round(count_plastin_650 / 2 + 1) * width * 0.1) + ((length * 2 + width * 2) * 0.15)
        count_work = length * 1.5

        total_cost = (s_krysha * material_price + p_shnur * self.pm.get_auto_price('shnur_8') +
                      count_remeshki * self.pm.get_auto_price('remeshok') + p_usilitel * material_price +
                      count_work * self.pm.get_auto_price('work'))

        total_cost = self.apply_legal_discount(total_cost, is_legal, discount_percent)
        return self.round_to_hundreds(total_cost * self.pm.get_parameter("sdvizhnoy_coefficient", 1.7))

    def run_typical(self, area: float, is_legal: bool, discount_percent: float) -> List[float]:
        """Расчет для типовых тентов"""
        results = []
        for material in self.materials_list:
            price = self.pm.get_auto_price(material)
            if price:
                results.append(self.calculate_typical_cost(price, area, is_legal, discount_percent))
        return results


def init_session_state():
    """Инициализация состояния сессии"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False


def page_polog_calculator(price_manager: PriceManager):
    """Страница калькулятора пологов"""
    st.title("Калькулятор пологов")

    calculator = PologCalculator(price_manager)

    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("Введите длину изделия (м)", value=1.0, min_value=0.01)
        width = st.number_input("Введите ширину изделия (м)", value=1.0, min_value=0.01)
        count = st.number_input("Введите количество изделий", value=1, min_value=1, step=1)

    with col2:
        is_legal_entity = st.checkbox("Юридическое лицо")
        apply_discount = st.checkbox("Предоставить скидку")
        discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0,
                                           max_value=100) if apply_discount else 0

    results_df = calculator.run(length, width, count, is_legal_entity, discount_percent)
    st.dataframe(results_df, hide_index=True, use_container_width=True)


def page_auto_calculator(price_manager: PriceManager):
    """Страница калькулятора авто"""
    st.title("Калькулятор продукции на авто")
    st.write("Цены актуальны на 10.10.2025")

    # Сохраняем length в session_state для доступа из методов
    st.session_state.auto_length = st.number_input("Введите длину (м)", value=1.0, min_value=0.01, key="auto_length")
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
        is_legal_entity = st.checkbox("Юридическое лицо", key="auto_legal")
        apply_discount = st.checkbox("Предоставить скидку", key="auto_discount")

    discount_percent = st.number_input("Введите размер скидки (в %)", value=0, min_value=0,
                                       max_value=100) if apply_discount else 0

    calculator = AutoCalculator(price_manager)
    area = calculator.calculate_area(st.session_state.auto_length, width, height_g, is_vorota, is_schit)

    # Простые расчеты для демонстрации
    results = calculator.run_typical(area, is_legal_entity, discount_percent)

    results_df = pd.DataFrame({
        "Тент": ["Тент типовой", "Тент сдвижной крыши", "Тент (чулок)"],
        "ПВХ630": [calculator.format_cost(results[0]) if len(results) > 0 else "N/A"] * 3,
        "ПВХ650": [calculator.format_cost(results[1]) if len(results) > 1 else "N/A"] * 3,
        "ПВХ750": [calculator.format_cost(results[2]) if len(results) > 2 else "N/A"] * 3,
        "ПВХ900": [calculator.format_cost(results[3]) if len(results) > 3 else "N/A"] * 3,
    })

    st.dataframe(results_df, hide_index=True, use_container_width=True)


def page_info():
    """Страница с дополнительной информацией"""
    st.title("Ещё калькулятор")
    st.write("Место для ещё какого-нибудь калькулятора...")


def main():
    """Главная функция приложения"""
    init_session_state()

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