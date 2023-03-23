import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import requests

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ROOT_NAME = os.getenv("DATABASE_ROOT_NAME")

conn = psycopg2.connect(
    host=DATABASE_HOST if DATABASE_HOST!=None else "localhost",
    database=DATABASE_ROOT_NAME if DATABASE_ROOT_NAME!=None else "aspectdatabase",
    user=DATABASE_USER if DATABASE_USER!=None else "postgres",
    password=DATABASE_PASSWORD if DATABASE_PASSWORD!=None else "Xiaokeai0717"
)

cur = conn.cursor()

def get_price_from_database(company_id):
	cur.execute(f"""
          SELECT price_list from prices WHERE company_id='{company_id}';
        """)
	price = list(cur.fetchone()[0])
	return price

index_price = get_price_from_database("index")
ast_price = get_price_from_database("ast")
dsc_price = get_price_from_database("dsc")
fsin_price = get_price_from_database("fsin")
hhw_price = get_price_from_database("hhw")
jky_price = get_price_from_database("jky")
sgo_price = get_price_from_database("sgo")
wrkn_price = get_price_from_database("wrkn")








# import requests

# url = "http://127.0.0.1:5000/get-order-book"

# payload = "\"wrkn\""
# headers = {
#   'Content-Type': 'text/plain'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)
