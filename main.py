import pandas as pd
import time

# Имитация ответов API (в реальном проекте сюда пойдут запросы через requests)
MOCK_RESPONSES = {
    "Центральный": [
        {"name": "Бургерная №1", "description": "Классика жанра", "rating": 4.8},
        {"name": "Пицца Хаус", "description": "Тонкое тесто и много сыра", "rating": 4.9}
    ],
    "Северный": [
        {"name": "Суши-бар Восток", "description": "Свежайшие морепродукты", "rating": 4.7}
    ],
    "Южный": [],  # Пустой ответ — проверка устойчивости
    "Западный": [
        {"name": "Кафе Уют", "description": "Домашняя кухня", "rating": None},  # None вместо рейтинга
        {"name": "Кофейня Мокко", "description": "Лучший эспрессо в городе", "rating": 4.6}
    ]
}

def fetch_data():
    """Шаг 1: собираем данные по районам, безопасно обрабатывая пустые ответы."""
    all_records = []
    districts = ["Центральный", "Северный", "Южный", "Западный"]

    for district in districts:
        time.sleep(0.5)  # Пауза для имитации лимитов API

        try:
            # Получаем список организаций или пустой список, если ключа нет
            organizations = MOCK_RESPONSES.get(district, [])

            # Если список пустой — пропускаем итерацию, скрипт не падает
            if not organizations:
                continue

            for org in organizations:
                # .get() с дефолтами защищает от KeyError
                # rating оставляем None, если его нет — pandas корректно учтёт это в mean()
                record = {
                    "district": district,
                    "name": org.get("name", "Без названия"),
                    "description": org.get("description", "Нет описания"),
                    "rating": org.get("rating")
                }
                all_records.append(record)

        except Exception as e:
            print(f"Ошибка при обработке района {district}: {e}")
            continue

    return all_records

def save_to_excel(data, filename="fastfood_demo.xlsx"):
    """Шаг 2: сохраняем собранные данные в Excel."""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Данные успешно сохранены в {filename}")

def calculate_avg_rating(filename="fastfood_demo.xlsx"):
    """Шаг 3: считаем средний рейтинг по районам и сохраняем сводку."""
    df = pd.read_excel(filename)

    avg_rating_by_district = df.groupby("district")["rating"].mean().reset_index()
    avg_rating_by_district.rename(columns={"rating": "avg_rating"}, inplace=True)

    print(avg_rating_by_district)
    avg_rating_by_district.to_excel("avg_rating_by_district.xlsx", index=False)
    print("Сводка сохранена в avg_rating_by_district.xlsx")

if __name__ == "__main__":
    data = fetch_data()
    save_to_excel(data)
    calculate_avg_rating()