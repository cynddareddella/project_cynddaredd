#Python 3.12.
import requests
import sqlite3
from ipaddress import ip_network 
from collections import defaultdict


ip_list = ["185.12.30.76", "213.209.133.185", "15.204.40.211", "89.113.144.217",
    "188.170.177.78", "83.217.200.199", "213.186.1.154", "31.10.97.225",
    "146.185.196.19", "94.247.111.51", "128.204.77.80", "5.255.231.149",
    "113.20.159.50", "79.134.203.30", "92.38.128.71"]


def group_ips_by_subnet(ips):
    subnet_dict = defaultdict(list)
    for ip in ips:
        network = ip_network(f"{ip}/24", strict=False)
        subnet_dict[str(network)].append(ip)
    return subnet_dict


def get_ip_info(ip):
    response = requests.get(f"http://ip-api.com/json/{ip}?fields=country,isp")
    if response.status_code == 200:
        data = response.json()
        return data.get("country", "N/A"), data.get("isp", "N/A")
    return None, None


def save_to_db(subnet_data):
    conn = sqlite3.connect("ip_info.db")
    cursor = conn.cursor()

    # Создаём таблицу
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_subnets (
            subnet TEXT PRIMARY KEY,
            provider TEXT,
            country TEXT,
            IP TEXT
        )
    """)

    # Добавим данные
    for subnet, ips in subnet_data.items():
        IP = ips[0] if ips else "N/A"
        country, provider = get_ip_info(IP)

        if country and provider:
            cursor.execute(
                "INSERT OR REPLACE INTO ip_subnets VALUES (?, ?, ?, ?)",
                (subnet, provider, country, ", ".join(ips))
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    subnet_data = group_ips_by_subnet(ip_list)
    save_to_db(subnet_data)
    print("Данные сохранены в базу ip_info.db")