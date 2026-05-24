"""
Модуль API-клиента
Для взаимодействия с внешними API
"""

import requests
from typing import Dict, Any, Optional


class APIClient:
    """Базовый класс API-клиента"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Инициализация API-клиента

        Args:
            base_url: Базовый URL API
            api_key: Ключ API
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Отправить GET-запрос

        Args:
            endpoint: Конечная точка API
            params: Параметры запроса

        Returns:
            Данные ответа
        """
        # TODO: Добавить логику повторных попыток
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправить POST-запрос

        Args:
            endpoint: Конечная точка API
            data: Данные запроса

        Returns:
            Данные ответа
        """
        # TODO: Добавить обработку ошибок
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправить PUT-запрос

        Args:
            endpoint: Конечная точка API
            data: Данные запроса

        Returns:
            Данные ответа
        """
        url = f"{self.base_url}/{endpoint}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str) -> None:
        """
        Отправить DELETE-запрос

        Args:
            endpoint: Конечная точка API
        """
        # TODO: Добавить механизм подтверждения
        url = f"{self.base_url}/{endpoint}"
        response = self.session.delete(url)
        response.raise_for_status()
