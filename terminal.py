import csv
from pydantic import BaseModel
from typing import Optional

COMMAND_PALETTE = """
================================
Available commands:
--------------------------------
list: show list of all persons
+: add a person
-: delete a person
find: find a person 
order : order persons list
exit: exit this program
===============================
"""

ORDERING_PALETTE = """
=============================
Type asc: to order ascending
Type dsc: to order descending
=============================
"""

GREET = """
======================================================================================
Hi... for info type the word info, or if you know the commands just enter your command
======================================================================================
"""


FILE_PATH = 'all_persons.csv'


class Person(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]

    @staticmethod
    def person_has_name(row, first_name, last_name):
        return row.first_name == first_name and row.last_name == last_name


class PersonDB:
    def __init__(self, file_path):
        self.file_path = file_path
        self.p = Person
        self.added_persons = []
        self.user_modifications = False
        self.persons: list[Person] = self.read()

    def person_exists_with_name(self, first_name, last_name):
        for row in self.persons:
            if self.p.person_has_name(row, first_name, last_name):
                return True
        return False

    def save(self):
        if self.user_modifications:
            with open(self.file_path, 'w') as f:
                fieldnames = ['first_name', 'last_name', 'email', 'phone']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.persons:
                    writer.writerow({'first_name': row.first_name,
                                     'last_name': row.last_name,
                                     'email': row.email,
                                     'phone': row.phone})

    def read(self):
        with open(self.file_path) as f:
            reader = csv.DictReader(f)
            return [Person(first_name=row['first_name'],
                           last_name=row['last_name'],
                           email=row['email'],
                           phone=row['phone']) for row in reader]

    def delete_person(self, first_name, last_name):
        deleted_person_count = 0
        for row in self.persons:
            if first_name in row.first_name \
                    and last_name in row.last_name:
                deleted_person_count += 1
                self.persons.remove(row)
                self.user_modifications = True
                break
        return deleted_person_count

    def add_person(self, person_data):
        if self.person_exists_with_name(person_data.first_name, person_data.last_name):
            return f"Person {person_data.first_name} {person_data.last_name} already exists"
        self.persons.append(person_data)
        self.user_modifications = True
        return self.persons

    def find_person(self, value):
        return [elem for elem in self.persons if value in elem.first_name or value in elem.last_name]


def main():
    person_db = PersonDB(FILE_PATH)
    print(GREET)

    while True:
        command = input('Enter your command: ')
        if command == 'list':
            print(person_db.persons)
        elif command == '+':
            person_data = Person(first_name=input('Enter first_name: ').capitalize(),
                                 last_name=input('Enter last_name: ').capitalize(),
                                 email=input('Enter email: '),
                                 phone=input('Enter phone: '))
            print(person_db.add_person(person_data))
        elif command == '-':
            first_name = input('Enter the first name of the person to delete: ').capitalize()
            last_name = input('Enter the last name of the person to delete: ').capitalize()
            print(person_db.delete_person(first_name, last_name))
        elif command == 'find':
            ref = input('Enter the name or last name to find person: ').capitalize()
            print(person_db.find_person(ref))
        elif command == 'info':
            print(COMMAND_PALETTE)
        elif command == 'exit':
            if person_db.user_modifications:
                print('Before exiting the programme, would you like to save your changes?')
                save_changes = input('Yes/No: ').capitalize()
                if 'Yes' in save_changes:
                    person_db.save()
            print('Exiting the program')
            break
        else:
            print('Command not valid')


if __name__ == "__main__":
    main()
