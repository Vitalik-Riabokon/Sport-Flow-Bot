import os

import aiohttp
import asyncio
from datetime import datetime, time, timedelta
from dotenv import load_dotenv

load_dotenv()


async def get_last_incoming_transaction_today():
    base_url = "https://api.monobank.ua"
    headers = {"X-Token": os.getenv("X_TOKEN")}

    async with aiohttp.ClientSession(headers=headers) as session:
        # Отримуємо інформацію про клієнта
        try:
            async with session.get(f"{base_url}/personal/client-info") as response:
                client_info = await response.json()
                account_id = client_info['accounts'][0]['id']

            # Встановлюємо часовий діапазон на сьогоднішній день
            today = datetime.now().date()
            start_of_day = int(datetime.combine(today, time.min).timestamp())
            end_of_day = int(datetime.combine(today, time.max).timestamp())
            # Отримуємо транзакції за сьогодні
            url = f"{base_url}/personal/statement/{account_id}/{start_of_day}/{end_of_day}"
            async with session.get(url) as response:
                transactions = sorted(await response.json(), key=lambda x: x['time'])
        except Exception as e:
            print(e)
            return 'Забагато запитів на оновлення!\nЗачекайте протягом 30с'

        text_transaction = ''
        if transactions:
            print(transactions)
            for last_transaction in transactions[-2:]:
                if last_transaction['amount']:
                    text_transaction += (f"Дата: {datetime.fromtimestamp(last_transaction['time'])}\n"
                                         f"Сума: {last_transaction['amount'] / 100}\n"
                                         f"Опис: {last_transaction['description']}\n\n")
                else:
                    return "Остання транзакція за сьогодні не є вхідною."
        else:
            return "Сьогодні не було транзакцій."
        return text_transaction


if __name__ == "__main__":
    text = asyncio.run(get_last_incoming_transaction_today())
    print(text)
