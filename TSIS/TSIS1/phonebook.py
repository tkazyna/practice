import psycopg2
import json
import csv
from config import config

def get_connection():
    return psycopg2.connect(**config())

class PhoneBook:
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()
    
    # 1. Фильтр по группе
    def filter_by_group(self, group_name):
        self.cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, 
                   g.name as group_name,
                   STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            WHERE g.name = %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """, (group_name,))
        return self.cur.fetchall()
    
    # 2. Поиск по email
    def search_by_email(self, email_pattern):
        self.cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name as group_name,
                   STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """, (f'%{email_pattern}%',))
        return self.cur.fetchall()
    
    # 3. Сортировка контактов
    def get_sorted_contacts(self, sort_by='first_name'):
        valid_sort_fields = {
            'name': 'first_name',
            'birthday': 'birthday',
            'date added': 'created_at'
        }
        
        sort_column = valid_sort_fields.get(sort_by.lower(), 'first_name')
        
        self.cur.execute(f"""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, c.created_at,
                   g.name as group_name,
                   STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, c.created_at, g.name
            ORDER BY {sort_column}
        """)
        return self.cur.fetchall()
    
    # 4. Пагинация (используя LIMIT/OFFSET)
    def get_paginated_contacts(self, limit, offset):
        self.cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name as group_name,
                   STRING_AGG(p.phone || ' (' || p.type || ')', ', ') as phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return self.cur.fetchall()
    
    def get_total_count(self):
        self.cur.execute("SELECT COUNT(*) FROM contacts")
        return self.cur.fetchone()[0]
    
    # 5. Поиск через stored function (из Practice 8 расширенная)
    def search_contacts(self, query):
        try:
            self.cur.callproc('search_contacts', (query,))
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error calling search_contacts: {e}")
            return []
    
    # 6. Добавление телефона через процедуру
    def add_phone(self, contact_name, phone, phone_type):
        try:
            self.cur.callproc('add_phone', (contact_name, phone, phone_type))
            self.conn.commit()
            print(f"✓ Phone {phone} added to {contact_name}")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            self.conn.rollback()
            return False
    
    # 7. Перемещение в группу через процедуру
    def move_to_group(self, contact_name, group_name):
        try:
            self.cur.callproc('move_to_group', (contact_name, group_name))
            self.conn.commit()
            print(f"✓ {contact_name} moved to group '{group_name}'")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            self.conn.rollback()
            return False
    
    # 8. Экспорт в JSON
    def export_to_json(self, filename):
        try:
            self.cur.execute("""
                SELECT c.first_name, c.last_name, c.email, c.birthday,
                       g.name as group_name,
                       COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type)), '[]') as phones
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                ORDER BY c.first_name
            """)
            
            contacts = []
            for row in self.cur.fetchall():
                contact = {
                    "first_name": row[0],
                    "last_name": row[1],
                    "email": row[2],
                    "birthday": str(row[3]) if row[3] else None,
                    "group": row[4],
                    "phones": row[5] if row[5] != '[]' else []
                }
                contacts.append(contact)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported {len(contacts)} contacts to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to JSON: {e}")
            return False
    
    # 9. Импорт из JSON с обработкой дубликатов
    def import_from_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
            
            imported_count = 0
            for contact in contacts:
                # Проверяем существование контакта
                self.cur.execute("""
                    SELECT id FROM contacts 
                    WHERE first_name = %s AND last_name = %s
                """, (contact['first_name'], contact['last_name']))
                existing = self.cur.fetchone()
                
                if existing:
                    choice = input(f"Contact {contact['first_name']} {contact['last_name']} exists. Skip/Overwrite? (s/o): ")
                    if choice.lower() == 's':
                        continue
                    elif choice.lower() == 'o':
                        # Удаляем старый контакт (телефоны удалятся каскадно)
                        self.cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                        self.conn.commit()
                
                # Находим или создаем группу
                group_id = None
                if contact.get('group'):
                    self.cur.execute("SELECT id FROM groups WHERE name = %s", (contact['group'],))
                    group = self.cur.fetchone()
                    if group:
                        group_id = group[0]
                    else:
                        self.cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (contact['group'],))
                        group_id = self.cur.fetchone()[0]
                
                # Вставляем контакт
                self.cur.execute("""
                    INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (contact['first_name'], contact['last_name'], 
                      contact.get('email'), contact.get('birthday'), group_id))
                
                contact_id = self.cur.fetchone()[0]
                
                # Вставляем телефоны
                for phone_data in contact.get('phones', []):
                    self.cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s, %s, %s)
                    """, (contact_id, phone_data['phone'], phone_data['type']))
                
                self.conn.commit()
                print(f"✓ Imported: {contact['first_name']} {contact['last_name']}")
                imported_count += 1
            
            print(f"✓ Successfully imported {imported_count} contacts")
            return True
        except Exception as e:
            print(f"✗ Error importing JSON: {e}")
            self.conn.rollback()
            return False
    
    # 10. Импорт из CSV (расширенный для новых полей)
    def import_from_csv(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                contacts_data = {}
                
                # Группируем телефоны по контактам
                for row in reader:
                    key = (row['first_name'], row['last_name'])
                    if key not in contacts_data:
                        contacts_data[key] = {
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'email': row.get('email'),
                            'birthday': row.get('birthday'),
                            'group': row.get('group'),
                            'phones': []
                        }
                    if row.get('phone') and row.get('phone_type'):
                        contacts_data[key]['phones'].append({
                            'phone': row['phone'],
                            'type': row['phone_type']
                        })
                
                # Вставляем каждый контакт
                for key, contact in contacts_data.items():
                    # Находим или создаем группу
                    group_id = None
                    if contact.get('group'):
                        self.cur.execute("SELECT id FROM groups WHERE name = %s", (contact['group'],))
                        group = self.cur.fetchone()
                        if group:
                            group_id = group[0]
                        else:
                            self.cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (contact['group'],))
                            group_id = self.cur.fetchone()[0]
                    
                    # Вставляем контакт
                    self.cur.execute("""
                        INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """, (contact['first_name'], contact['last_name'], 
                          contact.get('email'), contact.get('birthday'), group_id))
                    
                    contact_id = self.cur.fetchone()[0]
                    
                    # Вставляем телефоны
                    for phone_data in contact['phones']:
                        self.cur.execute("""
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s)
                        """, (contact_id, phone_data['phone'], phone_data['type']))
                    
                    self.conn.commit()
                    print(f"✓ Imported: {contact['first_name']} {contact['last_name']}")
            
            print(f"✓ Successfully imported {len(contacts_data)} contacts")
            return True
        except Exception as e:
            print(f"✗ Error importing CSV: {e}")
            self.conn.rollback()
            return False
    
    # Закрытие соединения
    def close(self):
        self.cur.close()
        self.conn.close()

# Консольное меню
def print_contact(contact):
    """Красивый вывод контакта"""
    if len(contact) >= 7:
        print(f"  {contact[1]} {contact[2]}")
        print(f"    Email: {contact[3] or 'No email'}")
        print(f"    Birthday: {contact[4] or 'Not specified'}")
        print(f"    Group: {contact[5] or 'No group'}")
        print(f"    Phones: {contact[6] or 'No phones'}")
        print()

def main():
    pb = PhoneBook()
    
    while True:
        print("\n" + "="*60)
        print("                 PHONE BOOK MENU")
        print("="*60)
        print("1. Filter by group")
        print("2. Search by email")
        print("3. Sort contacts (name/birthday/date added)")
        print("4. Paginated navigation (next/prev)")
        print("5. Search contacts (full text - uses stored function)")
        print("6. Add phone to contact (stored procedure)")
        print("7. Move contact to group (stored procedure)")
        print("8. Import from JSON")
        print("9. Export to JSON")
        print("10. Import from CSV")
        print("0. Exit")
        print("-"*60)
        
        choice = input("Your choice: ").strip()
        
        if choice == '1':
            group = input("Enter group name (Family/Work/Friend/Other): ")
            results = pb.filter_by_group(group)
            if results:
                print(f"\n--- Contacts in group '{group}' ---")
                for r in results:
                    print_contact(r)
            else:
                print(f"No contacts found in group '{group}'")
        
        elif choice == '2':
            email = input("Enter email pattern (e.g., 'gmail'): ")
            results = pb.search_by_email(email)
            if results:
                print(f"\n--- Contacts with email containing '{email}' ---")
                for r in results:
                    print_contact(r)
            else:
                print("No contacts found")
        
        elif choice == '3':
            print("\nSort by: name, birthday, date added")
            sort = input("Enter sort field: ").lower()
            results = pb.get_sorted_contacts(sort)
            if results:
                print(f"\n--- Sorted by {sort} ---")
                for r in results:
                    print_contact(r)
            else:
                print("No contacts found")
        
        elif choice == '4':
            limit = 5
            offset = 0
            total = pb.get_total_count()
            if total == 0:
                print("No contacts in database")
                continue
                
            while True:
                results = pb.get_paginated_contacts(limit, offset)
                current_page = offset // limit + 1
                total_pages = (total + limit - 1) // limit
                
                print(f"\n--- Page {current_page} of {total_pages} (showing {len(results)} of {total} contacts) ---")
                for r in results:
                    print_contact(r)
                
                cmd = input("\n[next/prev/quit]: ").lower()
                if cmd == 'next' and offset + limit < total:
                    offset += limit
                elif cmd == 'prev' and offset >= limit:
                    offset -= limit
                elif cmd == 'quit':
                    break
                elif cmd not in ['next', 'prev', 'quit']:
                    print("Invalid command. Use next, prev, or quit")
        
        elif choice == '5':
            query = input("Enter search query (searches name, email, phone): ")
            results = pb.search_contacts(query)
            if results:
                print(f"\n--- Search results for '{query}' ---")
                # Группируем результаты по контактам
                current_id = None
                for r in results:
                    if current_id != r[0]:
                        print(f"\n  {r[1]} {r[2]}")
                        print(f"    Email: {r[3] or 'No email'}")
                        print(f"    Birthday: {r[4] or 'Not specified'}")
                        print(f"    Group: {r[5] or 'No group'}")
                        current_id = r[0]
                    if r[6] and r[7]:
                        print(f"    Phone: {r[6]} ({r[7]})")
            else:
                print("No contacts found")
        
        elif choice == '6':
            name = input("Contact name (first or last name): ")
            phone = input("Phone number: ")
            ptype = input("Type (home/work/mobile): ")
            pb.add_phone(name, phone, ptype)
        
        elif choice == '7':
            name = input("Contact name (first or last name): ")
            group = input("Group name: ")
            pb.move_to_group(name, group)
        
        elif choice == '8':
            filename = input("JSON filename (e.g., contacts.json): ")
            pb.import_from_json(filename)
        
        elif choice == '9':
            filename = input("JSON filename (e.g., export.json): ")
            pb.export_to_json(filename)
        
        elif choice == '10':
            filename = input("CSV filename (e.g., contacts.csv): ")
            pb.import_from_csv(filename)
        
        elif choice == '0':
            pb.close()
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()