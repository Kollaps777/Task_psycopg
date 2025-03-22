import psycopg2

class ClientManager:
    def __init__(self, conn):
        self.conn = conn

    # Функция, создающая структуру БД
    def create_db(self):
        with self.conn.cursor() as cur:
            # Создание таблицы client
            cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE       
                );
            """)

            # Создание таблицы client_phone
            cur.execute("""
                CREATE TABLE IF NOT EXISTS client_phone(
                    id SERIAL PRIMARY KEY,
                    client_id INT NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES client(id) ON DELETE CASCADE   
                );            
            """)

            # Фиксация изменений
            self.conn.commit()
            print("Таблицы успешно созданы.")

    # Функция, позволяющая добавить нового клиента
    def add_client(self, first_name, last_name, email, phones=None):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO client (first_name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (first_name, last_name, email))
            client_id = cur.fetchone()[0]
            self.conn.commit()
            print(f"Клиент добавлен с ID: {client_id}")

            # Добавление телефонов, если они переданы
            if phones:
                for phone in phones:
                    self.add_phone(client_id, phone)

            return client_id

    # Функция для поиска ID существующего клиента
    def find_client_id(self, first_name=None, last_name=None, email=None):
        with self.conn.cursor() as cur:
            query = "SELECT id FROM client WHERE "
            conditions = []
            if first_name:
                conditions.append(f"first_name = '{first_name}'")
            if last_name:
                conditions.append(f"last_name = '{last_name}'")
            if email:
                conditions.append(f"email = '{email}'")

            if conditions:
                query += " AND ".join(conditions) + ";"
                cur.execute(query)
                result = cur.fetchone()
                if result:
                    return result[0]  # Возвращаем id клиента
                else:
                    print("Клиент не найден.")
                    return None
            else:
                print("Укажите параметры для поиска.")
                return None

    # Функция, позволяющая добавить телефон для существующего клиента
    def add_phone(self, client_id, phone):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO client_phone (client_id, phone)
                VALUES (%s, %s);
            """, (client_id, phone))
            self.conn.commit()
            print(f"Телефон {phone} добавлен для клиента с ID: {client_id}")

    # Функция, позволяющая изменить данные о клиенте
    def change_client(self, client_id, first_name=None, last_name=None, email=None, phones=None):
        with self.conn.cursor() as cur:
            updates = []
            if first_name:
                updates.append(f"first_name = '{first_name}'")
            if last_name:
                updates.append(f"last_name = '{last_name}'")
            if email:
                updates.append(f"email = '{email}'")

            if updates:
                update_query = "UPDATE client SET " + ", ".join(updates) + f" WHERE id = {client_id};"
                cur.execute(update_query)
                self.conn.commit()
                print(f"Данные клиента с ID {client_id} обновлены.")

            # Обновление телефонов, если они переданы
            if phones:
                # Удаляем старые телефоны
                cur.execute("DELETE FROM client_phone WHERE client_id = %s;", (client_id,))
                # Добавляем новые телефоны
                for phone in phones:
                    self.add_phone(client_id, phone)

    # Функция для удаления номера телефона существующего клиента
    def delete_phone(self, client_id, phone):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM client_phone
                WHERE client_id = %s AND phone = %s;
            """, (client_id, phone))
            self.conn.commit()
            print(f"Телефон {phone} удален для клиента с ID: {client_id}")

    # Функция для удаления существующего клиента
    def delete_client(self, client_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM client
                WHERE id = %s;
            """, (client_id,))
            self.conn.commit()
            print(f"Клиент с ID {client_id} удален.")

    # Функция для поиска клиента
    def find_client(self, first_name=None, last_name=None, email=None, phone=None):
        with self.conn.cursor() as cur:
            query = """
                SELECT c.id, c.first_name, c.last_name, c.email, p.phone
                FROM client c
                LEFT JOIN client_phone p ON c.id = p.client_id
                WHERE """
            conditions = []
            if first_name:
                conditions.append(f"c.first_name = '{first_name}'")
            if last_name:
                conditions.append(f"c.last_name = '{last_name}'")
            if email:
                conditions.append(f"c.email = '{email}'")
            if phone:
                conditions.append(f"p.phone = '{phone}'")

            if conditions:
                query += " AND ".join(conditions) + ";"
                cur.execute(query)
                results = cur.fetchall()
                if results:
                    print("Найденные клиенты:")
                    for row in results:
                        print(f"ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Email: {row[3]}, Телефон: {row[4]}")
                else:
                    print("Клиенты не найдены.")
            else:
                print("Укажите параметры для поиска.")

# Основной код
if __name__ == "__main__":
    # Установка соединения с базой данных
    conn = psycopg2.connect(database="netology_db", user="postgres", password="1Azamat1")

    # Создание экземпляра класса ClientManager
    client_manager = ClientManager(conn)

    # Создание таблиц
    client_manager.create_db()

    # Добавление клиента с телефонами
    client_id = client_manager.add_client("Алексей", "Иванов", "aleks@example.com", phones=["+79181234567", "+79167654321"])

    # Поиск клиента
    client_manager.find_client(first_name="Алексей")

    # Удаление телефона
    client_manager.delete_phone(client_id, "+79181234567")

    # Удаление клиента
    client_manager.delete_client(client_id)

    # Закрытие соединения
    conn.close()