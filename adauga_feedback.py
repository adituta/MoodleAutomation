#pot face o interfata prin care sa pot adauga linkul si titlul formularului in functie de nevoia adminului
#aceasta sursa poate avea ca parametru dinamic linkul si titlul formularului care sa fie transmise din
#alta sursa .py

#Tot ce este aici functioneaza doar daca am functia: core_course_create_modules
#   In cazul meu, aceasta functie nu este disponibila, deci nu pot adauga linkul
#
#

import csv
import requests
from config import MOODLE_URL, TOKEN

CURSURI_CSV = "CSV/structura_materii_facultati.csv"
FORMULAR_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSegqCGjCqSZ0UIpVJnlFuYbi7LmPlx1dKv3Fe8lkIM4xo9RCQ/viewform?usp=header"
FORMULAR_TITLE = "Formular Apreciere Disciplina"

def get_course_id_by_shortname(shortname):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_course_get_courses_by_field',
        'moodlewsrestformat': 'json',
        'field': 'shortname',
        'value': shortname
    }
    response = requests.post(MOODLE_URL, data=payload)
    data = response.json()
    if 'courses' in data and data['courses']:
        return data['courses'][0]['id']
    return None

def adauga_linkuri_feedback():
    with open(CURSURI_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cursuri = list(reader)

    for curs in cursuri:
        shortname = curs['shortname']
        course_id = get_course_id_by_shortname(shortname)
        if not course_id:
            print(f"Cursul {shortname} nu a fost găsit.")
            continue

        payload = {
            'wstoken': TOKEN,
            'wsfunction': 'core_course_create_modules',
            'moodlewsrestformat': 'json',
            'modules[0][courseid]': course_id,
            'modules[0][section]': 0,  # "General" section
            'modules[0][modulename]': 'url',
            'modules[0][name]': FORMULAR_TITLE,
            'modules[0][visible]': 1,
            'modules[0][url][externalurl]': FORMULAR_LINK,
            'modules[0][url][intro]': 'Completează formularul pentru a evalua serviciile cantinei.',
            'modules[0][url][introformat]': 1
        }

        r = requests.post(MOODLE_URL, data=payload)
        print(f"Link adăugat la cursul {shortname}: {r.text}")

if __name__ == "__main__":
    adauga_linkuri_feedback()

