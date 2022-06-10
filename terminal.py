from datetime import datetime
from pydantic import BaseModel
from creds import *
import pymongo
from statistics import mean

COMMAND_PALETTE = """
================================
Available commands:
--------------------------------
list: show list of all persons
+: add a person
-: delete a person
find: find a person 
exit: exit this program
age: to get a persons age
stats: to get age average
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


class PersonNotFound(Exception):
    pass


class PersonAlreadyExists(Exception):
    pass


class Person(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: datetime | None = None

    def person_has_name(self, first_name, last_name):
        return self.first_name == first_name and self.last_name == last_name

    @property
    def age(self):
        today = datetime.now()
        age = str(today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)))
        return age


class PersonDB:
    def __init__(self, db):
        self.db = db
        self.persons: list[Person] = self.read()

    def person_exists_with_name(self, first_name, last_name):
        for person in self.persons:
            if person.person_has_name(first_name, last_name):
                return True
        return False

    def save(self):
        for row in self.persons:
            if row not in self.read():
                self.db.users.insert_one(row.dict())
        for elem in self.read():
            if elem not in self.persons:
                self.db.users.delete_one(elem.dict())

    def read(self):
        return [Person.parse_obj(person) for person in self.db.users.find()]

    def delete_person(self, first_name, last_name):
        person_exists = False
        deleted_person_count = 0
        for row in self.persons:
            if first_name in row.first_name and last_name in row.last_name:
                person_exists = True
                deleted_person_count += 1
                self.persons.remove(row)
        if person_exists:
            return deleted_person_count
        raise PersonNotFound(f"Person: {first_name} {last_name} does not exists")

    def add_person(self, person_data):
        if self.person_exists_with_name(person_data.first_name, person_data.last_name):
            raise PersonAlreadyExists(f"Person: {person_data.first_name} {person_data.last_name} already exists")
        self.persons.append(person_data)
        return f'Person: {person_data} has been added to the list'

    def persons_with_name(self, value):
        return [elem for elem in self.persons if value in elem.first_name or value in elem.last_name]

    def show_age(self, first_name, last_name):
        person_exist = False
        age = str
        for row in self.persons:
            if first_name in row.first_name and last_name in row.last_name:
                age = row.age
                person_exist = True
        if person_exist:
            return f'{first_name} {last_name} is {age} years old'
        else:
            raise PersonNotFound(f"Person: {first_name} {last_name} does not exists")

    def age_average(self):
        persons_age = []
        for row in self.persons:
            persons_age.append(int(row.age))
        age_average = mean(persons_age)
        return str(round(age_average, 2))


def main():
    mongo_client = pymongo.MongoClient(DB_CREDS)
    db = mongo_client['socialhub']
    person_db = PersonDB(db)
    user_modifications = False
    print(GREET)

    while True:
        command = input('Enter your command: ')
        if command == 'list':
            for elem in person_db.persons:
                print(elem)
            print(len(person_db.persons), ' persons in the list')
        elif command == '+':
            person_data = Person(first_name=input('Enter first_name: ').capitalize(),
                                 last_name=input('Enter last_name: ').capitalize(),
                                 date_of_birth=datetime.strptime(input('Enter your date of birth with the following format [dd/mm/yyy]: '), '%d/%m/%Y'))
            try:
                print(person_db.add_person(person_data))
                user_modifications = True
            except Exception as e:
                print(e)
        elif command == '-':
            first_name = input('Enter the first name of the person: ').capitalize()
            last_name = input('Enter the last name of the person: ').capitalize()
            try:
                print(person_db.delete_person(first_name, last_name))
                user_modifications = True
            except Exception as e:
                print(e)
        elif command == 'find':
            ref = input('Enter the name or last name to find person: ').capitalize()
            print(person_db.persons_with_name(ref))
        elif command == 'info':
            print(COMMAND_PALETTE)
        elif command == 'age':
            first_name = input('Enter the first name of the person to delete: ').capitalize()
            last_name = input('Enter the last name of the person to delete: ').capitalize()
            try:
                print(person_db.show_age(first_name, last_name))
            except Exception as e:
                print(e)
        elif command == 'stats':
            print(f'The age average of the persons is {person_db.age_average()}')
        elif command == 'exit':
            if user_modifications:
                print('Before exiting the programme, would you like to save your changes?')
                save_changes = input('Yes/No: ').capitalize()
                if 'Yes' in save_changes:
                    person_db.save()
            mongo_client.close()
            print('Exiting the program')
            break
        else:
            print('Command not valid')


if __name__ == "__main__":
    main()
