from sqlalchemy import create_engine, text

db = {
    'user': 'root',
    'password': 'test1234',
    'host': 'localhost',
    'port': 3306,
    'database': 'miniter'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
# db = create_engine(db_url, encoding='utf-8', max_overflow=0)
# params = {'name': '이현승'}
# rows = db.execute(text("SELECT * FROM users WHERE name = :name"), params).fetchall()
# for row in rows:
#     print(f"name:{row['name']}")
#     print(f"email:{row['email']}")
