"""
Модуль моделей данных
Определяет модели данных, используемые в приложении
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """Модель пользователя"""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"

    # TODO: Добавить методы валидации пользователя


@dataclass
class Product:
    """Модель продукта"""
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None

    def is_in_stock(self) -> bool:
        """Проверить наличие на складе"""
        return self.stock > 0

    def apply_discount(self, percentage: float) -> float:
        """
        Применить скидку

        Args:
            percentage: Процент скидки

        Returns:
            Цена со скидкой
        """
        # TODO: Добавить валидацию скидки
        return self.price * (1 - percentage / 100)


@dataclass
class Order:
    """Модель заказа"""
    id: int
    user_id: int
    products: List[Product]
    total_amount: float
    status: str
    created_at: datetime

    def calculate_total(self) -> float:
        """Рассчитать итоговую сумму заказа"""
        # TODO: Учесть скидки и налоги
        return sum(p.price for p in self.products)

    def is_completed(self) -> bool:
        """Проверить, завершён ли заказ"""
        return self.status == "completed"


@dataclass
class Transaction:
    """Модель транзакции"""
    id: int
    order_id: int
    amount: float
    payment_method: str
    timestamp: datetime
    status: str

    # TODO: Добавить функцию возврата средств
