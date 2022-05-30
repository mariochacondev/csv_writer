import pandas as pd
import csv
from pydantic import BaseModel
from typing import Optional

COMMAND_PALETTE = """Available commands:
l: display all persons
+: add a person
-: delete a person
find: find a person
order : order list
exit: exit this program"""

ORDERING_PALETTE = """asc: to order ascending
dsc: to order descending"""

GREET = """Hi... for info type the word info, or if you know the commands just enter your command"""

"""ITERATING OVER THIS SET WON'T KEEP THE RIGHT ORDER TO WRITE IN THE FILE """
#PERSON_KEYS = {'first_name', 'last_name', 'email', 'phone'}

PERSON_KEYS = {'first_name': None, 'last_name': None, 'email': None, 'phone': None}

FILE_PATH = 'all_persons.csv'


class PersonM(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]


class PersonDB:

    def __init__(self, file_path):
        self.file_path = file_path

    def person_has_name(self, person, first_name, last_name):
        return person['first_name'] == first_name and person['last_name'] == last_name

    def person_exists_with_name(self, first_name, last_name):
        all_persons = self.read_persons()
        for index, person in all_persons.iterrows():
            if self.person_has_name(person, first_name, last_name):
                return True
        return False

    def person_has_value(self, person, value):
        # THIS METHOD WOULD NEED A DICTIONARY
        # cannot convert dictionary update sequence element #0 to a sequence
        for key in PERSON_KEYS:
            if person[key] == value:
                return True
        return False

    def write_persons(self, lines):
        with open(self.file_path, 'w') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(lines)

    def read_persons(self):
        return pd.read_csv(self.file_path)

    def sort_list(self, ref, col):
        all_persons = pd.read_csv(self.file_path)
        ref = True if 'asc' in ref else False

        # THE COMMENTED CONDITIONS ASSURE THAT THE USER INPUTS THE ORDER WITH THE RIGHT SYNTAX AND THE WAY IN USE
        # TAKES ASC AND IF THE USER INPUTS ANYTHING ELSE IT WOULD STILL ORDER IN DSC

        # if 'asc' in ref:
        #     ref = True
        # elif 'dsc' in ref:
        #     ref = False
        # else:
        #     return f'Order not valid'

        if col in all_persons:
            return all_persons.sort_values(by=[col], ascending=ref)
        raise ValueError("Column %s not found" % col)

    def delete_person(self, first_name, last_name):
        all_persons = pd.read_csv(self.file_path)
        lines = list()
        deleted_person_count = 0
        # REQUIRES A COPY WITHOUT THE PERSON AND THEN REWRITE THE FILE
        if first_name and last_name in all_persons.values:
            with open(self.file_path, 'r') as read_file:
                reader = csv.reader(read_file)
                for row in reader:
                    lines.append(row)
                    if first_name in row[0] and last_name in row[1]:
                        lines.remove(row)
                        deleted_person_count += 1
            self.write_persons(lines)
        return deleted_person_count

    def add_person(self, person_data):
        if self.person_exists_with_name(person_data.first_name, person_data.last_name):
            raise ValueError("Person %s %s already exists" % (person_data.first_name, person_data.last_name))
        # WITH PANDAS IS REQUIRED .to_csv TO ADD A ROW TO A CSV
        new_row = pd.DataFrame(person_data.dict(), index=[0])
        new_row.to_csv(self.file_path,
                       mode='a',
                       index=False,
                       header=False)
        return self.read_persons()

    def find_person(self, value):
        all_persons = self.read_persons()
        person_found = []
        for row in all_persons.itertuples(index=False):
            if value in row:
                person_found.append(row)
        if person_found:
            df = pd.DataFrame(person_found)
            return df
        raise ValueError("Person %s ... not found" % value)


def main():
    person_db = PersonDB(FILE_PATH)
    print(GREET)

    while True:
        command = input('Enter your command: ')
        if command == 'l':
            print(person_db.read_persons())
        elif command == '+':
            for key in PERSON_KEYS:
                PERSON_KEYS[key] = input(f'Enter {key}: ').capitalize()
            person_data = PersonM(**PERSON_KEYS)
            print(person_db.add_person(person_data))
        elif command == '-':
            first_name = input('Enter the name of the person to delete: ').capitalize()
            last_name = input('Enter the last name of the person to delete: ').capitalize()
            print(person_db.delete_person(first_name, last_name))
        elif command == 'find':
            ref = input('Enter the name or last name to find person: ').capitalize()
            print(person_db.find_person(ref))
        elif command == 'info':
            print(COMMAND_PALETTE)
        elif command == 'order':
            print(ORDERING_PALETTE)
            ref = input('How would you like to order the list?: ')
            col = input('By which column?: ')
            print(person_db.sort_list(ref, col))
        elif command == 'exit':
            print('Exiting the program')
            break
        else:
            print('Command not valid')


if __name__ == "__main__":
    main()
