import csv
import requests

MOODLE_URL = "http://localhost/webservice/rest/server.php"
TOKEN = "PUNE_AICI_TOKENUL_TAU"
FUNCTION = "core_course_create_courses"

def creare_cursuri_din_csv(csv_file):
    cursuri = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursuri.append({
                "fullname": row["fullname"],
                "shortname": row["shortname"],
                "categoryid": int(row["categoryid"]),
                "summary": row["summary"],
                "visible": int(row["visible"])
            })

    payload = {
        'wstoken': TOKEN,
        'moodlewsrestformat': 'json',
        'wsfunction': FUNCTION
    }

    for i, course in enumerate(cursuri):
        for key, value in course.items():
            payload[f'courses[{i}][{key}]'] = value

    response = requests.post(MOODLE_URL, data=payload)
    print("Rezultat creare cursuri:")
    print(response.json())

creare_cursuri_din_csv('cursuri.csv')