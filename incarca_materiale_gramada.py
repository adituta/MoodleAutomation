import os
import base64
import csv
import requests
from config import MOODLE_URL, TOKEN

# -- se ruleaza folosind urmatoarea scriere: python incarca_materiale_bulk.py asocieri_materiale.csv
#unde asocieri csv este un fisier CSV cu coloanele: folder, curs_shortname

# === Obține ID-ul cursului
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

# === Trimite fișierul codificat Base64 către pluginul local
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

# === Parcurge toate folderele definite în CSV
def incarca_din_csv(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            folder = row['folder']
            shortname = row['curs_shortname']
            print(f"\n=== Încep încărcarea pentru cursul '{shortname}' din folderul '{folder}' ===")
            course_id = get_course_id(shortname)
            if not course_id:
                print(f"[Eroare] Cursul '{shortname}' nu a fost găsit.")
                continue
            if not os.path.exists(folder):
                print(f"[Eroare] Folderul '{folder}' nu există.")
                continue
            for fisier in os.listdir(folder):
                path = os.path.join(folder, fisier)
                if os.path.isfile(path):
                    print(f" → Încarc {fisier}...")
                    rezultat = incarca_fisier(course_id, path)
                    print(f"   ↳ Rezultat: {rezultat}")

# === Rulare
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Încarcă materiale în cursuri Moodle pe baza unui fișier CSV.')
    parser.add_argument('csv_path', help='Calea către fișierul CSV cu foldere și shortname-uri')
    args = parser.parse_args()

    incarca_din_csv(args.csv_path)
