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

        # HAVING A READING OF THE LIST ONLY IN THE INIT OF THE CLASS WON'T UPDATE THE LIST
        # AFTER DOING MODIFICATIONS WITH THE METHODS
        # self.persons = pd.read_csv(self.file_path)

    def person_exists_with_name(self, first_name, last_name):
        for index, person in self.read().iterrows():
            if person_has_name(person, first_name, last_name):
                return True
        return False


    def save(self, lines, mode):
        if 'w' in mode:
            with open(self.file_path, mode) as f:
                fieldnames = ['first_name', 'last_name', 'email', 'phone']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(lines)
        if 'a' in mode:
            with open(self.file_path, mode, newline='') as f:
                fieldnames = ['first_name', 'last_name', 'email', 'phone']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow({'first_name': lines.first_name,
                                 'last_name': lines.last_name,
                                 'email': lines.email,
                                 'phone': lines.phone})

    def read(self):
        return pd.read_csv(self.file_path)

    def sort(self, order_type, key):
        if key in self.read():
            return self.read().sort_values(by=[key], ascending=order_type)
        raise ValueError(f"Column {key} not found")

    def delete_person(self, first_name, last_name):
        lines = list()
        deleted_person_count = 0
        # # REQUIRES A COPY WITHOUT THE PERSON AND THEN REWRITE THE FILE
        with open(self.file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if first_name in row['first_name'] and last_name in row['last_name']:
                    deleted_person_count += 1
                else:
                    lines.append(row)
            self.save(lines, mode='w')
            return deleted_person_count

    def add_person(self, person_data):
        if self.person_exists_with_name(person_data.first_name, person_data.last_name):
            raise ValueError(f"Person {person_data.first_name} {person_data.last_name} already exists")
        self.save(person_data, mode='a')
        return self.read()

    def find_person(self, value):
        person_found = []
        with open(self.file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if value in row['first_name'] or value in row['last_name']:
                    person_found.append(row)
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
            print('Exiting the program')
            break
        else:
            print('Command not valid')


if __name__ == "__main__":
    main()
