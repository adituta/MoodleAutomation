import csv
import requests

MOODLE_URL = "http://localhost/webservice/rest/server.php"
TOKEN = "PUNE_AICI_TOKENUL_TAU"

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
    if data['courses']:
        return data['courses'][0]['id']
    return None

def creare_si_enrolare_studenti(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = []
        enrolments = []

        for i, row in enumerate(reader):
            users.append({
                'username': row['username'],
                'password': row['password'],
                'firstname': row['firstname'],
                'lastname': row['lastname'],
                'email': row['email'],
            })

        payload = {
            'wstoken': TOKEN,
            'wsfunction': 'core_user_create_users',
            'moodlewsrestformat': 'json',
        }

        for i, user in enumerate(users):
            for key, value in user.items():
                payload[f'users[{i}][{key}]'] = value

        response = requests.post(MOODLE_URL, data=payload)
        created_users = response.json()
        print("Utilizatori creați:", created_users)

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                courseid = get_course_id_by_shortname(row['course_shortname'])
                if not courseid:
                    print(f"Cursul {row['course_shortname']} nu a fost găsit.")
                    continue

                enrolments.append({
                    'roleid': 5,
                    'userid': created_users[i]['id'],
                    'courseid': courseid
                })

        payload = {
            'wstoken': TOKEN,
            'wsfunction': 'enrol_manual_enrol_users',
            'moodlewsrestformat': 'json'
        }

        for i, e in enumerate(enrolments):
            for key, value in e.items():
                payload[f'enrolments[{i}][{key}]'] = value

        enrol_response = requests.post(MOODLE_URL, data=payload)
        print("Înrolare completă:", enrol_response.text)

creare_si_enrolare_studenti('studenti.csv')