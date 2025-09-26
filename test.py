from core import MyStatInterface
from datetime import date

def test_auth():
    mystat = MyStatInterface("Utemb_aa50", "lookism20062007#A")
    return mystat.token is not None

def test_wrong_auth():
    mystat = MyStatInterface("test", "test")
    return mystat.token is None or mystat.token == ""

def test_marks():
    mystat = MyStatInterface("Utemb_aa50", "lookism20062007#A")
    marks = mystat.get_marks()
    return isinstance(marks, list)

def test_schedule_today():
    mystat = MyStatInterface("Utemb_aa50", "lookism20062007#A")
    today_str = date.today().isoformat()
    schedule = mystat.get_schedule(today_str)
    return isinstance(schedule, dict)

if __name__ == "__main__":
    print("Авторизация:", test_auth())
    print("Неверная авторизация:", test_wrong_auth())
    print("Получение оценок:", test_marks())
    print("Расписание на сегодня:", test_schedule_today())

