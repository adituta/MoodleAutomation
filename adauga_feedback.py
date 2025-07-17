import csv
import requests
from config import MOODLE_URL, TOKEN

CURSURI_CSV = "CSV\structura_materii_facultati.csv"
FORMULAR_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSegqCGjCqSZ0UIpVJnlFuYbi7LmPlx1dKv3Fe8lkIM4xo9RCQ/viewform?usp=header"         #link-ul catre formularul de feedback
FORMULAR_TITLE = "Formular Apreciere Disciplina"  #titlul formularului de feedback

#pot face o interfata prin care sa pot adauga linkul si titlul formularului in functie de nevoia adminului
#aceasta sursa poate avea ca parametru dinamic linkul si titlul formularului care sa fie transmise din
#alta sursa .py

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
            'wsfunction': 'mod_url_create_urls',
            'moodlewsrestformat': 'json',
            'urls[0][courseid]': course_id,
            'urls[0][name]': FORMULAR_TITLE,
            'urls[0][externalurl]': FORMULAR_LINK,
            'urls[0][intro]': 'Completează formularul pentru a evalua serviciile cantinei.',
            'urls[0][introformat]': 1,
        }

        r = requests.post(MOODLE_URL, data=payload)
        print(f"Link adăugat la cursul {shortname}: {r.status_code}")

if __name__ == "__main__":
    adauga_linkuri_feedback()
