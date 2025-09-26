import sys  
import warnings
from typing import Union
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QPushButton, QStackedLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from core import MyStatInterface, parse_pagination_meta
from collections import defaultdict
from datetime import date
        
warnings.filterwarnings("ignore", category=DeprecationWarning)


class UIBuilder:
    @staticmethod
    def create_card(title: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"background-color: {color};")
        card.setFixedHeight(100)
        layout = QVBoxLayout()
        layout.setSpacing(2)

        label_value = QLabel(value)
        label_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        label_value.setAlignment(Qt.AlignCenter)

        label_title = QLabel(title)
        label_title.setFont(QFont("Segoe UI", 10))
        label_title.setAlignment(Qt.AlignCenter)

        layout.addWidget(label_value)
        layout.addWidget(label_title)
        card.setLayout(layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        return card

    @staticmethod
    def create_block(title: str, content: str, extra_style: str = "", rich_text=False) -> QFrame:
        block = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        header.setFixedHeight(20)

        body = QLabel()
        if rich_text:
            body.setTextFormat(Qt.RichText)
        else:
            body.setTextFormat(Qt.PlainText)
        body.setText(content)
        body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        body.setWordWrap(True)
        body.setFont(QFont("Segoe UI", 9))
        if extra_style:
            body.setStyleSheet(extra_style)

        layout.addWidget(header)
        layout.addWidget(body)
        block.setLayout(layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(0, 3)
        block.setGraphicsEffect(shadow)

        return block


class MyStatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyStat")
        self.setGeometry(100, 100, 1200, 700)

        # Авторизация
        self.mystat = MyStatInterface("Utemb_aa50", "lookism20062007#A")

        if not self.mystat.token:
            print("Ошибка аутентификации")
        else:
            print("Токен получен")

        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', sans-serif;
            }

            #menuButton {
                background-color: transparent;
                border: none;
                color: #333;
            }

            #menuButton:hover {
                background-color: #dcdcdc;
                border-radius: 10px;
            }

            #card {
                border-radius: 10px;
                color: white;
            }

            QFrame {
                background-color: white;
                border-radius: 10px;
            }

            QLabel {
                color: #333;
            }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        side_menu = QVBoxLayout()
        side_menu.setSpacing(15)
        side_menu.setAlignment(Qt.AlignTop)

        icons = ["home", "tasks", "calendar", "grades", "stats", "settings"]
        self.menu_buttons = {}

        for name in icons:
            btn = QPushButton(name.capitalize())
            btn.setObjectName("menuButton")
            btn.setIcon(QIcon(f"icons/{name}.png"))
            btn.setIconSize(QSize(24, 24))
            btn.setFixedHeight(50)
            btn.setStyleSheet("text-align: left; padding-left: 10px;")
            btn.clicked.connect(lambda _, n=name: self.switch_page(n))
            side_menu.addWidget(btn)
            self.menu_buttons[name] = btn

        side_menu_frame = QFrame()
        side_menu_frame.setLayout(side_menu)
        side_menu_frame.setFixedWidth(160)

        self.content_stack = QStackedLayout()

        self.pages = {
            "home": self.create_home_page(),
            "tasks": self.create_placeholder_page("Задания"),
            "calendar": self.create_placeholder_page("Календарь"),
            "grades": self.create_placeholder_page("Оценки"),
            "stats": self.create_placeholder_page("Статистика"),
            "settings": self.create_placeholder_page("Настройки")
        }

        for page in self.pages.values():
            self.content_stack.addWidget(page)

        content_wrapper = QWidget()
        content_wrapper.setLayout(self.content_stack)

        main_layout.addWidget(side_menu_frame)
        main_layout.addWidget(content_wrapper)

        self.setLayout(main_layout)
        self.switch_page("home")

    def switch_page(self, page_name):
        if page_name in self.pages:
            index = list(self.pages.keys()).index(page_name)
            self.content_stack.setCurrentIndex(index)

    def create_home_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("Главная")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(title)

        progress_data = self.mystat.get_progress("year")
        avg_mark = "—"
        if progress_data and isinstance(progress_data, dict):
            avg_mark = progress_data.get("total_average_point", "—")

        marks = self.mystat.get_marks()

        homeworks_response = self.mystat.get_homeworks(status=3, limit=1000, sort="-hw.time")
        total_homeworks = 0
        overdue_homeworks = 0

        if homeworks_response and isinstance(homeworks_response, dict):
            meta = parse_pagination_meta(homeworks_response)
            total_homeworks = meta["totalCount"]

            homeworks_list = homeworks_response.get("data", [])
            overdue_homeworks = sum(1 for hw in homeworks_list if hw.get("isOverdue", False))

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        cards_layout.addWidget(UIBuilder.create_card("Задания к выполнению", str(total_homeworks), "#6C63FF"))
        cards_layout.addWidget(UIBuilder.create_card("Задания просрочено", f"{overdue_homeworks}/{total_homeworks}", "#FF6B6B"))
        layout.addLayout(cards_layout)

        grid = QGridLayout()
        grid.setSpacing(15)
        grid.addWidget(UIBuilder.create_block("Средний балл", str(avg_mark)), 0, 0)

        # Формируем оценки с вертикальным отступом и толстой округлой обводкой
        marks_html_lines = []
        for m in marks[:10]:
            date_str = m.get('mark_date')
            mark_val = m.get('mark')
            if date_str and mark_val is not None:
                marks_html_lines.append(
                    f"<div style='margin-bottom:8px'>{date_str}: "
                    f"<span style='background-color:#6C63FF; color:white; "
                    f"border-radius:12px; padding:4px 10px; font-weight:bold; "
                    f"border: 3px solid #4B47A3; display:inline-block;'>{mark_val}</span></div>"
                )
        marks_html = "".join(marks_html_lines) if marks_html_lines else "Нет данных"

        grid.addWidget(
            UIBuilder.create_block(
                "Оценки",
                marks_html,
                extra_style="line-height:1.5em;",
                rich_text=True
            ), 1, 0
        )

        attendance = self.mystat.get_attendance()
        attendance_str = "Нет данных посещаемости"
        if attendance and isinstance(attendance, dict):
            visit = attendance.get("visit_percent", 100)
            absence = attendance.get("absence_percent", 0)
            late = attendance.get("late_percent", 0)
            attendance_str = f"{visit}% посещение\n{absence}% пропуск\n{late}% опоздание"

        grid.addWidget(UIBuilder.create_block("Посещаемость", attendance_str), 1, 1)

        today = date.today().isoformat()
        schedule = self.mystat.get_week_schedule(today)
        schedule_str = self.format_schedule(schedule) if schedule else "<i>Нет расписания</i>"
        schedule_style = "padding: 4px;"
        grid.addWidget(UIBuilder.create_block("Расписание", schedule_str, extra_style=schedule_style, rich_text=True), 0, 1)

        layout.addLayout(grid)
        widget.setLayout(layout)
        return widget

    def create_placeholder_page(self, title):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"{title} (в разработке)")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 18))
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def format_schedule(self, schedule_data: dict) -> str:
        """
        Форматируем расписание: выводим дату и название урока (lesson_theme) в HTML с вертикальными отступами.
        """
        if not schedule_data or "data" not in schedule_data:
            return "<i>Нет расписания</i>"

        days = defaultdict(list)

        for lesson in schedule_data["data"]:
            date_ = lesson.get("date", "Дата неизвестна")
            theme = lesson.get("lesson_theme") or lesson.get("subject_name") or "Урок"
            days[date_].append(theme)

        sorted_dates = sorted(days.keys())
        result_lines = []

        for date_ in sorted_dates:
            lessons_str = ", ".join(days[date_]) if days[date_] else "Нет уроков"
            result_lines.append(f"<div style='margin-bottom:10px'>{date_}: {lessons_str}</div>")

        return "".join(result_lines)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyStatApp()
    window.show()
    sys.exit(app.exec_())


