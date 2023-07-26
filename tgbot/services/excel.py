from datetime import timedelta

from openpyxl import Workbook
from openpyxl.styles import Font
import os


async def create_excel(orders: list):
    wb = Workbook()
    ws = wb.active
    ws.append(
        (
            'Номер',
            'Дата-время',
            'ID клиента',
            'Username клиента',
            "Монета",
            "Объём",
            "Банк",
            "Реквизиты",
            "Выплата клиенту",
            "Выплата воркеру",
            "Статус",
            "Модератор",
            "Воркер",
            "Комментарий",
        )
    )
    ft = Font(bold=True)
    for row in ws['A1:T1']:
        for cell in row:
            cell.font = ft

    for order in orders:
        create_datetime = (order["dtime"] + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")
        ws.append(
            (
                order['id'],
                create_datetime,
                order['client_id'],
                order["client_username"],
                order["coin"],
                order["coin_value"] / 100,
                order["bank_name"],
                order["bank_account"],
                order["client_fiat"] / 100,
                order["worker_fiat"] / 100,
                order["status"].upper(),
                order["moderator_id"],
                order["worker_id"],
                order["comment"]
            )
        )

    wb.save(f'{os.getcwd()}/all_orders.xlsx')
