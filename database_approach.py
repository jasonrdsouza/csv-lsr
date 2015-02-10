import csv
import sqlite3
import argparse


def create_db(filename):
    conn = sqlite3.connect(filename)
    return conn.cursor()

def create_people_table(c):
    c.execute("""
        -- Create destination table
        CREATE TABLE people(
            id INT PRIMARY KEY,
            first TEXT,
            last TEXT,
            age INT,
            githubAcct TEXT,
            thirdGradeGraduation DATE
        );
    """)

def populate_people_table(c, input_filename):
    INSERT_TABLE_STMT = """
        INSERT into people (id, first, last, age, githubAcct, thirdGradeGraduation)
        VALUES (?, ?, ?, ?, ?, ?);
    """

    with open(input_filename, 'rU') as csvfile: # U is for "universal-newline mode", which handles windows and unix line endings
        reader = csv.DictReader(csvfile)
        for row in reader:
            # batch these inserts for efficiency?
            values = (row['ID'], row['First'], row['Last'], row['Age'], row['GithubAcct'], row['Date of 3rd Grade Graduation'])
            c.execute(INSERT_TABLE_STMT, values)

def create_people_indexes(c):
    c.execute("""CREATE INDEX lastNameIdx ON people(last);""")
    c.execute("""CREATE INDEX ageIdx ON people(age)""")

def last_name_ids(c, last_name):
    c.execute("""SELECT id from people where last = ?""", (last_name,))
    return [el[0] for el in c.fetchall()]

def people_by_age(c):
    c.execute("""SELECT * from people order by age""")
    return c.fetchall()

def arbitrary_sql(c, statement):
    """Allows for arbitrary sql statements to be performed on the backing db"""
    if sqlite3.complete_statement(statement):
        try:
            c.execute(statement)

            if statement.lstrip().upper().startswith("SELECT"):
                return c.fetchall()
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])
    else:
        print("Invalid SQL statement")
    return None

def setup(db_filename, data_filename):
    """Initialize and populate the database"""
    c = create_db(db_filename)
    create_people_table(c)
    populate_people_table(c, data_filename)
    create_people_indexes(c)
    return c

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV Load, Sort, Report (sqlite approach)')
    parser.add_argument('--db', action='store', dest='db_filename', default='csv.db',
                        help='Location to store the backing (sqlite) database')
    parser.add_argument('--data', action='store', dest='data_filename', default='data.csv',
                        help='Location of the data to be parsed')
    flags = parser.parse_args()

    c = setup(flags.db_filename, flags.data_filename)

    print "Enter an operation number followed by any arguments."
    print "0 => direct SQL access"
    print "1 => last name to ids"
    print "2 => people sorted by age"
    print "exit => exit"

    while True:
        line = raw_input().split()
        operation = line[0]
        if operation == 'exit':
            break
        elif operation == '1':
            print(last_name_ids(c, line[1]))
        elif operation == '2':
            print(people_by_age(c))
        elif operation == '0':
            statement = " ".join(line[1:])
            print(arbitrary_sql(c, statement))
        else:
            print("Invalid operation")
