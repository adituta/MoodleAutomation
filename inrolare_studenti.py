import csv
import requests
from config import MOODLE_URL, TOKEN

# === Config ===
STUDENTI_CSV = 'CSV\studenti_grupe.csv'
CURSURI_CSV = 'CSV\structura_materii_facultati.csv'
DEFAULT_PASSWORD = 'Parola123!'

# === Funcție pentru obținere ID curs după shortname ===
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

# === Funcție pentru obținerea ID utilizator după username ===
def get_userid_by_username(username):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_get_users',
        'moodlewsrestformat': 'json',
        'criteria[0][key]': 'username',
        'criteria[0][value]': username
    }
    response = requests.post(MOODLE_URL, data=payload)
    data = response.json()
    if 'users' in data and data['users']:
        return data['users'][0]['id']
    return None

# === Funcție pentru creare utilizatori ===
def creeaza_utilizatori(studenti):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_create_users',
        'moodlewsrestformat': 'json'
    }

    for i, student in enumerate(studenti):
        payload[f'users[{i}][username]'] = student['username']
        payload[f'users[{i}][password]'] = DEFAULT_PASSWORD
        payload[f'users[{i}][firstname]'] = student['firstname']
        payload[f'users[{i}][lastname]'] = student['lastname']
        payload[f'users[{i}][email]'] = student['email']

    response = requests.post(MOODLE_URL, data=payload)
    try:
        return response.json()
    except:
        print("Unii utilizatori există deja sau a apărut o eroare.")
        return []

# === Funcție pentru înrolare ===
def inroleaza_studenti():
    # 1. Citește cursuri
    with open(CURSURI_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cursuri = list(reader)

    # 2. Citește studenți
    with open(STUDENTI_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        studenti = list(reader)

    creeaza_utilizatori(studenti)

    enrol_payload = {
        'wstoken': TOKEN,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json'
    }

    enrolments = []

    for student in studenti:
        facultate = student['facultate']
        an = str(student['an'])
        username = student['username']
        userid = get_userid_by_username(username)

        if not userid:
            print(f"Studentul {username} nu a fost găsit.")
            continue

        # caută cursuri pentru facultatea și anul lui
        for curs in cursuri:
            if curs['facultate'] == facultate and curs['an'] == an:
                course_id = get_course_id_by_shortname(curs['shortname'])
                if not course_id:
                    print(f"Cursul {curs['shortname']} nu a fost găsit.")
                    continue

                enrolments.append({
                    'roleid': 5,
                    'userid': userid,
                    'courseid': course_id
                })

    # 3. Trimite înrolările
    for i, e in enumerate(enrolments):
        for key, value in e.items():
            enrol_payload[f'enrolments[{i}][{key}]'] = value

    r = requests.post(MOODLE_URL, data=enrol_payload)
    print("Înrolare finalizată:", r.text)

# === Rulează scriptul ===
if __name__ == "__main__":
    inroleaza_studenti()
