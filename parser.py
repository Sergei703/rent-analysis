import re, time, requests, pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://realty.yandex.ru"
LIST_URL = "https://realty.yandex.ru/arhangelsk/snyat/kvartira/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


def get_soup(url):
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def parse_number(text):
    m = re.search(r"\d+(?:[,.]\d+)?", text)
    return float(m.group().replace(",", ".")) if m else None


def parse_rooms(soup):
    el = soup.select_one("h1.OfferCardSummaryInfo__description--3-iC7")
    m = re.search(r"(\d+)-комнатн", el.get_text(" ", strip=True), re.I) if el else None
    return int(m.group(1)) if m else None


def parse_price(soup):
    el = soup.select_one("div.OfferCardSummaryInfo__price--2FD3C")
    if el is None:
        return None
    text = el.get_text(" ", strip=True).replace("\xa0", " ")
    m = re.search(r"(\d[\d\s]*)\s*₽", text)
    return int(m.group(1).replace(" ", "")) if m else None


def parse_deposit(soup):
    for row in soup.select("li.OfferCardCheck__row--hbOhK"):
        key = row.select_one("span.OfferCardCheck__rowKey--3_Agm")
        value = row.select_one("span.OfferCardCheck__rowValue--bcPJA")
        if not key or not value or key.get_text(" ", strip=True) != "Залог":
            continue
        text = value.get_text(" ", strip=True).replace("\xa0", " ")
        m = re.search(r"(\d[\d\s]*)\s*₽", text)
        return int(m.group(1).replace(" ", "")) if m else None
    return None


def parse_coordinates(soup):
    el = soup.select_one("div.OfferCardSummary__location--3Yxze")
    if el is None:
        return None, None
    lat, lon = el.get("data-latitude"), el.get("data-longtitude")
    return (float(lat) if lat else None, float(lon) if lon else None)


def parse_tech_features(soup):
    container = soup.select_one("ul.OfferCard__techFeatures--3Zoaa")
    if container is None:
        return {}
    result = {}
    for item in container.find_all("li", recursive=False):
        value_el = item.select_one("div.OfferCardHighlight__value--HMVgP")
        label_el = item.select_one("div.OfferCardHighlight__label--2uMCy")
        if not value_el or not label_el:
            continue
        value, label = value_el.get_text(" ", strip=True), label_el.get_text(" ", strip=True)

        if label == "общая":
            result["area_total"] = parse_number(value)
        elif label == "жилая":
            result["area_living"] = parse_number(value)
        elif label == "кухня":
            result["area_kitchen"] = parse_number(value)
        elif label == "потолки":
            result["ceiling_height"] = parse_number(value)
        elif label == "год постройки":
            number = parse_number(value)
            if number is not None:
                result["building_year"] = int(number)
        elif label.startswith("из"):
            floor_m = re.search(r"(\d+)\s*этаж", value)
            total_m = re.search(r"из\s*(\d+)", label)
            if floor_m:
                result["floor"] = int(floor_m.group(1))
            if total_m:
                result["floors_total"] = int(total_m.group(1))
    return result


def parse_offer(url):
    try:
        soup = get_soup(url)
        lat, lon = parse_coordinates(soup)
        data = {
            "offer_id": re.search(r"/offer/(\d+)", url).group(1),
            "url": url,
            "rooms": parse_rooms(soup),
            "price_month": parse_price(soup),
            "deposit": parse_deposit(soup),
            "latitude": lat,
            "longitude": lon,
        }
        data.update(parse_tech_features(soup))
        return data
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None


def get_offer_links(url):
    soup = get_soup(url)
    links = set()
    for a in soup.select('a[href*="/offer/"]'):
        href = a.get("href")
        if not href:
            continue
        full_url = urljoin(BASE_URL, href).split("?")[0]
        if re.search(r"/offer/\d+/?$", full_url):
            links.add(full_url)
    return links


def collect_all_offer_links(max_pages=30):
    all_links = set()
    for page in range(1, max_pages + 1):
        url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
        print(f"\nСтраница {page}: {url}")
        try:
            links = get_offer_links(url)
        except Exception as e:
            print(f"Ошибка страницы: {e}")
            break
        new_links = links - all_links
        print(f"Найдено: {len(links)}, новых: {len(new_links)}")
        if not new_links:
            print("Новых объявлений нет. Останавливаемся.")
            break
        all_links.update(new_links)
        print(f"Всего объявлений: {len(all_links)}")
        time.sleep(1)
    return sorted(all_links)


def main():
    print("=" * 70, "\n1. Собираем ссылки на объявления\n", "=" * 70)
    offer_links = collect_all_offer_links()
    print(f"\nВсего найдено объявлений: {len(offer_links)}")
    pd.DataFrame({"url": offer_links}).to_csv("yandex_offer_moscow_links.csv", index=False)

    print("\n" + "=" * 70, "\n2. Парсим объявления\n", "=" * 70)
    results = []
    for i, url in enumerate(offer_links, start=1):
        print(f"[{i}/{len(offer_links)}] {url}")
        data = parse_offer(url)
        if data is not None:
            results.append(data)
        time.sleep(0.5)

    df = pd.DataFrame(results)
    print("\n" + "=" * 70, "\nГОТОВО\n", "=" * 70)
    print(f"Получено строк: {len(df)}")
    print(f"Получено столбцов: {len(df.columns)}")
    print("\nСтолбцы:", df.columns.tolist())
    print("\nПервые строки:\n", df.head())

    df.to_csv("yandex_arhangelsk_rent.csv", index=False, encoding="utf-8-sig")
    print("\nФайлы сохранены:")
    print("yandex_offer_arhangelsk_links.csv")
    print("yandex_arhangelsk_rent.csv")


if __name__ == "__main__":
    main()
