import csv
import argparse
from collections import defaultdict
from datetime import datetime


class Person:
    def __init__(self, ID, first_name, last_name, age, github_account, third_grade_graduation):
        self.ID = ID
        self.first_name = first_name if first_name else None
        self.last_name = last_name if last_name else None
        self.github_account = github_account if github_account else None
        self.third_grade_graduation = third_grade_graduation if third_grade_graduation else None

        try:
            self.third_grade_graduation = datetime.strptime(third_grade_graduation, "%m/%d/%y")
        except ValueError:
            self.third_grade_graduation = None

        try:
            self.age = int(age)
        except ValueError:
            self.age = None

    def __repr__(self):
        return "Person(ID: {}, first: {}, last: {}, age: {}, github: {}, 3rd grade graduation: {})".format(
                    self.ID,
                    self.first_name,
                    self.last_name,
                    self.age,
                    self.github_account,
                    self.third_grade_graduation)

class CSVReporter:
    def __init__(self):
        self.last_name_ids = defaultdict(list)
        self.age_sorted_people = []

    def _update_last_names_to_ids(self, last_name, ID):
        if last_name: # don't group blank last names
            self.last_name_ids[last_name].append(ID)

    def ids_by_last_name(self, last_name):
        return self.last_name_ids[last_name]

    def _update_people_by_age(self, ID, first_name, last_name, age, github_account, third_grade_graduation):
        p = Person(ID, first_name, last_name, age, github_account, third_grade_graduation)
        self.age_sorted_people.append(p)

    def _sort_people_by_age(self):
        self.age_sorted_people.sort(key=lambda p: p.age)

        # move the people without an age to the end
        i = 0
        for i, person in enumerate(self.age_sorted_people):
            if person.age != None:
                break
        self.age_sorted_people = self.age_sorted_people[i:] + self.age_sorted_people[:i]

    def people_by_age(self):
        return self.age_sorted_people

    def parse(self, csv_filename):
        with open(csv_filename, 'rU') as csvfile: # U is for "universal-newline mode", which handles windows and unix line endings
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._update_last_names_to_ids(row['Last'], row['ID'])
                self._update_people_by_age(row['ID'], row['First'],
                                          row['Last'], row['Age'],
                                          row['GithubAcct'], row['Date of 3rd Grade Graduation'])

        self._sort_people_by_age()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV Load, Sort, Report (vanilla approach)')
    parser.add_argument('--data', action='store', dest='data_filename', default='data.csv',
                        help='Location of the data to be parsed')
    flags = parser.parse_args()

    c = CSVReporter()
    c.parse(flags.data_filename)

    print "Enter an operation number followed by any arguments."
    print "1 => last name to ids"
    print "2 => people sorted by age"
    print "exit => exit"

    while True:
        line = raw_input().split()
        operation = line[0]
        if operation == 'exit':
            break
        elif operation == '1':
            print(c.ids_by_last_name(line[1]))
        elif operation == '2':
            print(c.people_by_age())
        else:
            print("Invalid operation")
