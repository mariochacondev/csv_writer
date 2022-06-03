import pandas as pd
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


def person_has_name(person, first_name, last_name):
    return person['first_name'] == first_name and person['last_name'] == last_name


class PersonDB:
    def __init__(self, file_path):
        self.file_path = file_path
        self.persons_list_copy = []
        self.added_persons = []
        self.user_add_person = False
        self.user_delete_person = False
        with open(self.file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.persons_list_copy.append(row)

    def person_exists_with_name(self, first_name, last_name):
        for index, person in self.read().iterrows():
            if person_has_name(person, first_name, last_name):
                return True
        return False

    def save(self):
        if self.user_delete_person:
            with open(self.file_path, 'w') as f:
                fieldnames = ['first_name', 'last_name', 'email', 'phone']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.persons_list_copy)
        if self.user_add_person:
            with open(self.file_path, 'a', newline='') as f:
                fieldnames = ['first_name', 'last_name', 'email', 'phone']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                for elem in self.added_persons:
                    writer.writerow({'first_name': elem['first_name'],
                                     'last_name': elem['last_name'],
                                     'email': elem['email'],
                                     'phone': elem['phone']})

    def read(self):
        return pd.DataFrame(self.persons_list_copy)

    def sort(self, order_type, key):
        if key in self.read():
            return self.read().sort_values(by=[key], ascending=order_type)
        raise ValueError(f"Column {key} not found")

    def delete_person(self, first_name, last_name):
        deleted_person_count = 0
        for row in range(len(self.persons_list_copy)):
            if first_name in self.persons_list_copy[row]['first_name'] and last_name in self.persons_list_copy[row]['last_name']:
                deleted_person_count += 1
                del self.persons_list_copy[row]
                self.user_delete_person = True
                break
        return deleted_person_count

    def add_person(self, person_data):
        if self.person_exists_with_name(person_data.first_name, person_data.last_name):
            return f"Person {person_data.first_name} {person_data.last_name} already exists"
        self.persons_list_copy.append(dict(person_data))
        self.added_persons.append(dict(person_data))
        self.user_add_person = True
        return self.read()

    def find_person(self, value):
        person_found = []
        for elem in self.persons_list_copy:
            if value in elem['first_name'] or value in elem['last_name']:
                person_found.append(elem)
        if person_found:
            df = pd.DataFrame(person_found)
            return df
        raise ValueError(f"Person {value} ... not found")


def main():
    person_db = PersonDB(FILE_PATH)
    print(GREET)

    while True:
        command = input('Enter your command: ')
        if command == 'list':
            print(person_db.read())
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
        elif command == 'order':
            print(ORDERING_PALETTE)
            order_type = input('How would you like to order the list?: ')
            key = input('By which column?: ')
            order_type = True if 'asc' in order_type else False
            print(person_db.sort(order_type, key))
        elif command == 'exit':
            if person_db.user_add_person or person_db.user_delete_person:
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
