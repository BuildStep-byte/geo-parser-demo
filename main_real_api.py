import os
import time
import pandas as pd
import requests

# ============================================================
# НАСТРОЙКИ
# Ключ можно задать двумя способами:
# 1) через переменную окружения:  set YANDEX_MAPS_API_KEY=ваш_ключ
# 2) вписать прямо сюда (не рекомендуется для публичных репозиториев)
# ============================================================
API_KEY = os.environ.get("YANDEX_MAPS_API_KEY", "")

SEARCH_URL = "https://search-maps.yandex.ru/v1/"
DISTRICTS = ["Центральный", "Северный", "Южный", "Западный"]
SEARCH_QUERY = "кафе"  # что ищем: кафе, пиццерии, салоны красоты и т.д.


def fetch_data(districts=DISTRICTS, query=SEARCH_QUERY):
    """Шаг 1: собираем данные по районам через реальный API.

    Возвращает список словарей с полями:
    district, name, description, rating.
    """
    all_records = []

    if not API_KEY:
        print("API-ключ не задан. Установите переменную окружения YANDEX_MAPS_API_KEY")
        print("или впишите ключ в переменную API_KEY в начале файла.")
        return all_records

    for district in districts:
        time.sleep(0.5)  # пауза, чтобы не превышать лимиты API

        try:
            response = requests.get(
                SEARCH_URL,
                params={
                    "apikey": API_KEY,
                    "text": f"{query}, {district}",
                    "lang": "ru_RU",
                    "results": 50,
                },
                timeout=10,
            )
            response.raise_for_status()  # ошибка HTTP -> исключение
            data = response.json()

            # структура ответа: список организаций лежит в data["features"]
            features = data.get("features", [])

            if not features:
                print(f"По району {district} ничего не найдено — пропускаем.")
                continue

            for feature in features:
                # в реальном ответе поля вложены в properties
                props = feature.get("properties", {})
                org_meta = props.get("CompanyMetaData", {})

                record = {
                    "district": district,
                    "name": org_meta.get("name", "Без названия"),
                    "description": props.get("description", "Нет описания"),
                    # рейтинга может не быть — оставляем None,
                    # pandas корректно пропустит его при усреднении
                    "rating": props.get("rating"),
                }
                all_records.append(record)

        except requests.RequestException as e:
            print(f"Ошибка запроса по району {district}: {e}")
            continue
        except (KeyError, ValueError) as e:
            print(f"Неожиданный формат ответа по району {district}: {e}")
            continue

    return all_records


def save_to_excel(data, filename="fastfood_real.xlsx"):
    """Шаг 2: сохраняем собранные данные в Excel."""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Данные успешно сохранены в {filename} ({len(df)} записей)")


def calculate_avg_rating(filename="fastfood_real.xlsx"):
    """Шаг 3: считаем средний рейтинг по районам и сохраняем сводку."""
    df = pd.read_excel(filename)

    if df.empty:
        print("Данных нет — сводку не формируем.")
        return

    avg_rating_by_district = df.groupby("district")["rating"].mean().reset_index()
    avg_rating_by_district.rename(columns={"rating": "avg_rating"}, inplace=True)

    print(avg_rating_by_district)
    avg_rating_by_district.to_excel("avg_rating_by_district_real.xlsx", index=False)
    print("Сводка сохранена в avg_rating_by_district_real.xlsx")


if __name__ == "__main__":
    data = fetch_data()
    if data:
        save_to_excel(data)
        calculate_avg_rating()
    else:
        print("Сбор данных не дал результатов — проверьте API-ключ и параметры запроса.")