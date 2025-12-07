HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 15; Mobile; rv:1.17.11b) Gecko/1.17.11b Firefox/1.17.11b",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

META_PAYLOAD = {
  "jsonQuery": {
    "_type": "commercialsale",
    "engine_version": {
      "type": "term",
      "value": 2
    },
    "office_type": {
      "type": "terms",
      "value": [
        1
      ]
    },
    "price": {
      "type": "range",
      "value": {
        "gte": 1000000,
        "lte": 100000000
      }
    },
    "total_area": {
      "type": "range",
      "value": {
        "gte": 10,
        "lte": 10000
      }
    },
    "region": {
      "type": "terms",
      "value": [
        4743
      ]
    }
  }
}

COLUMN_MAP = {
    "ID  объявления": "ID",
    "Тип": "type",
    "Площадь": "area",
    "Возможное назначение": "possible_purpose",
    "Класс": "building_class",
    "Метро": "metro",
    "Адрес": "address",
    "Здание": "building",
    "Этаж": "floor",
    "Высота потолков, м": "ceiling_height_m",
    "Цена": "price",
    "Тип аренды": "rent_type",
    "Телефоны": "phones",
    "Описание": "description",
    "Парковка": "parking",
    "Планировка": "layout",
    "Вход": "entrance",
    "Доступ": "access",
    "Дополнительно": "additional",
    "Лифт": "elevator",
    "Ссылка на объявление": "listing_url",
}