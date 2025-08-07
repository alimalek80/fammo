import geoip2.database

GEOIP_DB_PATH = "d:/FAMO-PET/GeoLite2-Country.mmdb"

def get_country_from_ip(ip_address):
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.country(ip_address)
            return response.country.name or "Unknown"
    except Exception:
        return "Unknown"