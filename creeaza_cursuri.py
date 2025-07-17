import csv
import requests
from config import MOODLE_URL, TOKEN

def creare_cursuri_din_csv(csv_file):
    cursuri = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curs = {
                "fullname": f"{row['nume_curs']} - Anul {row['an']} Semestrul {row['semestru']} - {row['facultate']}",
                "shortname": row['shortname'],
                "categoryid": 1,  # asigură-te că ai categoria 1 existentă sau modifică aici cu ce trebuie
                "summary": f"Curs pentru {row['nume_curs']} ({row['facultate']}) - Anul {row['an']}, Semestrul {row['semestru']}",
                "visible": 1
            }
            cursuri.append(curs)

    payload = {
        'wstoken': TOKEN,
        'moodlewsrestformat': 'json',
        'wsfunction': 'core_course_create_courses',
    }

    for i, course in enumerate(cursuri):
        for key, value in course.items():
            payload[f'courses[{i}][{key}]'] = value

    response = requests.post(MOODLE_URL, data=payload)
    print("Rezultat creare cursuri:")
    print(response.json())

# Rulează funcția
creare_cursuri_din_csv("CSV\structura_materii_facultati.csv")
