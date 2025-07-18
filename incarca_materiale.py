import os
import base64
import requests
from config import MOODLE_URL, TOKEN

DIRECTOR_FISIERE = "Materiale_Cursuri/Materiale_Programare"
CURS_SHORTNAME = "programare_calc"

# --- Obține ID-ul cursului
def get_course_id(shortname):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_course_get_courses_by_field',
        'moodlewsrestformat': 'json',
        'field': 'shortname',
        'value': shortname
    }
    r = requests.post(MOODLE_URL, data=payload)
    data = r.json()
    if data.get('courses'):
        return data['courses'][0]['id']
    return None

# --- Trimite fișierul codificat Base64 către plugin
def incarca_fisier(courseid, filepath):
    with open(filepath, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
        filename = os.path.basename(filepath)
        payload = {
            'wstoken': TOKEN,
            'wsfunction': 'local_createfile_add_resource',
            'moodlewsrestformat': 'json',
            'courseid': courseid,
            'filename': filename,
            'filecontent': encoded
        }
        response = requests.post(MOODLE_URL, data=payload)
        return response.json()

# --- MAIN
def incarca_materiale():
    course_id = get_course_id(CURS_SHORTNAME)
    if not course_id:
        print(f"[Eroare] Cursul '{CURS_SHORTNAME}' nu a fost găsit.")
        return

    fisiere = os.listdir(DIRECTOR_FISIERE)
    for fisier in fisiere:
        path = os.path.join(DIRECTOR_FISIERE, fisier)
        if os.path.isfile(path):
            print(f"Încarc {fisier}...")
            rezultat = incarca_fisier(course_id, path)
            print(f"Rezultat pentru {fisier}: {rezultat}")

if __name__ == "__main__":
    incarca_materiale()
