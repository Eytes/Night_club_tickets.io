import sqlite3
from random import randrange
from prettytable import PrettyTable

db = sqlite3.connect('db.db')
cur = db.cursor()


# декоратор
def ticket_is_exist(func):
    def wrapper(number: int):
        exist_the_ticket: bool = cur.execute('''
        SELECT 
            EXISTS(SELECT number FROM tickets WHERE number = ?)''', [number]).fetchone()[0]
        if exist_the_ticket:
            return func(number)
        else:
            return f"Билета {number} не существует"

    return wrapper


def get_ticket_cost(ticket_type: str) -> int:
    match ticket_type.lower():
        case "первокурсник" | "первак":
            return 200
        case "репост" | "история" | "нижка":
            return 300
        case "обычный":
            return 400
        case "на входе" | "в последний день":
            return 500
        case "vip":
            return 1000


@ticket_is_exist
def get_ticket_type(number: int) -> str:
    return cur.execute('SELECT type FROM tickets WHERE number = ?', [number]).fetchone()[0]


def get_number() -> int:
    """
    возвращает случайное значение от 1_000_000_000 до 9_999_999_999,
    которого нет в таблице tikets
    """
    tickets_numbers: list[tuple[int,]] = cur.execute('SELECT number FROM tickets').fetchall()
    tickets_numbers: list[int] = [number[0] for number in tickets_numbers]

    number = randrange(1_000_000_000, 9_999_999_999)
    while number in tickets_numbers:
        number = randrange(1_000_000_000, 9_999_999_999)

    return number


def add_buyer(ticket_type: str, second_name: str, name: str, phone_number: str, inside: int = 0,
              vk_link: str = "NULL") -> None:
    number = get_number()

    try:
        cur.executescript(f"""
            BEGIN;
            
            INSERT INTO buyers
            VALUES ({number}, '{second_name.title()}', '{name.title()}', '{phone_number}', '{vk_link}', {inside});
     
            INSERT INTO tickets
            VALUES ({number}, {get_ticket_cost(ticket_type)}, date('now'), time('now'), '{ticket_type}')""")
        db.commit()

    except sqlite3.Error as e:
        db.rollback()
        print("Ошибка добавления покупателя\n", e)


@ticket_is_exist
def is_inside(ticket_number: int) -> bool:
    return bool(cur.execute('''
    SELECT is_inside 
    FROM buyers 
    WHERE ticket_number = ?''', [ticket_number]).fetchone()[0])


@ticket_is_exist
def come_in(ticket_number: int) -> None:
    """человек заходит внутрь"""
    try:
        if is_inside(ticket_number):
            raise AttributeError

        cur.executescript(f"""
            BEGIN;
            UPDATE buyers
            SET is_inside = 1 
            WHERE ticket_number = {ticket_number}""")
        db.commit()

    except sqlite3.Error as e:
        db.rollback()
        print("Не удается впустить человека из-за ошибки БД")

    except AttributeError:
        db.rollback()
        print("Человек уже внутри")


@ticket_is_exist
def come_out(ticket_number: int) -> None:
    """человек выходит наружу"""
    try:
        if not is_inside(ticket_number):
            raise AttributeError

        cur.executescript(f"""
            BEGIN;
            UPDATE buyers
            SET is_inside = 0 
            WHERE ticket_number = {ticket_number}""")
        db.commit()

    except sqlite3.Error as e:
        db.rollback()
        print("Не удается выпустить человека из-за ошибки БД")

    except AttributeError:
        db.rollback()
        print("Человек уже снаружи")


def tickets_sold_amount() -> PrettyTable:
    """возвращает таблицу сводки по проданным билетам"""
    main_table: list[tuple[str, int]] = cur.execute("""
        SELECT type, COUNT(*) 
        FROM tickets
        GROUP BY type""").fetchall()

    tickets_amount: int = cur.execute('SELECT COUNT(number) FROM tickets').fetchone()[0]
    money_amount: int = cur.execute('SELECT SUM(cost) FROM tickets').fetchone()[0]

    table = PrettyTable()
    for column in main_table:
        table.add_column(column[0], [column[1]])

    table.add_column("Всего билетов", [tickets_amount])
    table.add_column("Собранно средств", [money_amount] if money_amount else [0])

    return table


def buyers_table():
    data = cur.execute("""
        SELECT * 
        FROM buyers""").fetchall()

    table = PrettyTable()
    table.field_names = ['ticket_type', 'second_name', 'name', 'phone_number', 'vk_link', 'is_inside']
    for row in data:
        table.add_row(row)

    return table
