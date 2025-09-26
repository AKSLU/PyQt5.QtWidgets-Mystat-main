import requests
from typing import Optional, Union, List, Dict


class MyStatInterface:
    """
    Базовый класс (интерфейс) для работы с API MyStat
    """

    DEFAULT_BASE_URL = "https://mapi.itstep.org/v1/mystat/aqtobe"
    AUTH_URL = "https://mapi.itstep.org/v1/mystat/auth/login"

    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        auth_token: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.token: Optional[str] = auth_token
        self.session = requests.Session()

        if not self.token and login and password:
            self.login = login
            self.password = password
            self.authenticate()

    def authenticate(self) -> bool:
        """
        Авторизация в системе MyStat. Получает и сохраняет токен.
        """
        try:
            response = self.session.post(self.AUTH_URL, data={
                "login": self.login,
                "password": self.password
            })
            response.raise_for_status()
            self.token = response.text
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка авторизации: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """
        Заголовки авторизации для запросов.
        """
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get_marks(self) -> Union[bool, List[Dict]]:
        """
        Получение списка оценок.
        """
        try:
            url = f"{self.base_url}/statistic/marks"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения оценок: {e}")
            return False

    def get_leader_table(self, page: int = None, per_page: int = None) -> Union[bool, List[Dict]]:
        """
        Получение таблицы лидеров.
        """
        try:
            params = {}
            if page is not None:
                params["page"] = page
            if per_page is not None:
                params["per_page"] = per_page

            url = f"{self.base_url}/progress/leader-table"
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения таблицы лидеров: {e}")
            return False

    def get_progress(self, period: str = "year") -> Union[bool, Dict]:
        """
        Получение прогресса за указанный период.
        """
        try:
            url = f"{self.base_url}/statistic/progress"
            params = {"period": period}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения прогресса: {e}")
            return False

    def get_schedule(self, date_filter: str = None) -> Union[bool, Dict[str, List[Dict]]]:
        """
        Получение расписания по дате 
        """
        try:
            url = f"{self.base_url}/schedule/get-existing-schedule"
            params = {}
            if date_filter:
                params["date_filter"] = date_filter

            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения расписания: {e}")
            return False

    def get_week_schedule(self, date_filter: str, type_filter: str = "week") -> Union[bool, Dict]:
        """
        Получение расписания на неделю с указанной даты.
        """
        try:
            url = f"{self.base_url}/schedule/get-month"
            params = {
                "date_filter": date_filter,
                "type": type_filter
            }
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения недельного расписания: {e}")
            return False

    def get_attendance(self, period: str = "month") -> Union[bool, Dict]:
        """
        Получение посещаемости за указанный период.
        """
        try:
            url = f"{self.base_url}/statistic/attendance"
            params = {"period": period}
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения посещаемости: {e}")
            return False

    def get_homeworks(self, status: int = 3, limit: int = 1000, sort: str = "-hw.time") -> Union[bool, Dict]:
        """
        Получение списка домашних заданий с фильтрацией по статусу.
        status=3 — например, задания к выполнению
        """
        try:
            params = {
                "status": status,
                "limit": limit,
                "sort": sort
            }
            url = f"{self.base_url}/homework/list"
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения домашних заданий: {e}")
            return False


def parse_pagination_meta(response_json: dict) -> dict:
    """
    Извлекает из ответа API данные пагинации:
    currentPage, totalPages, totalCount
    """
    meta = response_json.get("_meta", {})
    return {
        "currentPage": meta.get("currentPage", 0),
        "totalPages": meta.get("totalPages", 0),
        "totalCount": meta.get("totalCount", 0)
    }



        
        
    
