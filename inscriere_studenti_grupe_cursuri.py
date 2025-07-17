import csv
import requests
from config import MOODLE_URL, TOKEN

# === Obține ID-ul unui curs după shortname ===
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

# === Obține ID-ul unui utilizator după username ===
def get_user_id_by_username(username):
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

# === Încarcă asocierile grupe–materii ===
def load_grupe_materii_map(file):
    grupe_materii = {}
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            grupa = row['grupanume']
            materie = row['course_shortname']
            grupe_materii.setdefault(grupa, []).append(materie)
    return grupe_materii

# === Creează utilizatori noi și înrolează toți studenții ===
def creare_si_inscriere_studenti(student_csv, asocieri_csv):
    grupe_materii = load_grupe_materii_map(asocieri_csv)

    # 1. Citește studenții
    with open(student_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        studenti = list(reader)

    # 2. Creează doar utilizatorii care nu există deja
    create_payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_create_users',
        'moodlewsrestformat': 'json',
    }
    users_to_create = []
    user_ids = {}

    for i, student in enumerate(studenti):
        username = student['username']
        existing_id = get_user_id_by_username(username)
        if existing_id:
            user_ids[username] = existing_id
            print(f"🔁 Utilizatorul {username} există deja (id={existing_id})")
        else:
            users_to_create.append((i, student))

    for i, (index, student) in enumerate(users_to_create):
        create_payload[f'users[{i}][username]'] = student['username']
        create_payload[f'users[{i}][password]'] = 'Parola123!'
        create_payload[f'users[{i}][firstname]'] = student['firstname']
        create_payload[f'users[{i}][lastname]'] = student['lastname']
        create_payload[f'users[{i}][email]'] = f"{student['username']}@example.com"

    if users_to_create:
        resp = requests.post(MOODLE_URL, data=create_payload)
        result = resp.json()
        print("✅ Utilizatori creați:", result)
        for i, user in enumerate(result):
            user_ids[users_to_create[i][1]['username']] = user['id']
    else:
        print("ℹ️ Nu sunt utilizatori noi de creat.")

    # 3. Înrolează toți studenții în cursurile grupei lor
    enrolments = []
    for student in studenti:
        username = student['username']
        grupa = student['grupanume']
        userid = user_ids.get(username)

        if not userid:
            print(f"⚠️ Nu am ID pentru utilizatorul {username}.")
            continue

        for materie in grupe_materii.get(grupa, []):
            course_id = get_course_id_by_shortname(materie)
            if not course_id:
                print(f"❌ Cursul {materie} nu a fost găsit.")
                continue
            enrolments.append({
                'roleid': 5,
                'userid': userid,
                'courseid': course_id
            })

    # 4. Trimite înrolările în loturi de câte 50
    batch_size = 50
    for start in range(0, len(enrolments), batch_size):
        batch = enrolments[start:start+batch_size]
        batch_payload = {
            'wstoken': TOKEN,
            'wsfunction': 'enrol_manual_enrol_users',
            'moodlewsrestformat': 'json'
        }
        for i, e in enumerate(batch):
            for key, value in e.items():
                batch_payload[f'enrolments[{i}][{key}]'] = value
        resp = requests.post(MOODLE_URL, data=batch_payload)
        print(f"📌 Lot {start+1}-{start+len(batch)}:", resp.text)

# === Executare ===
creare_si_inscriere_studenti('studenti.csv', 'asociere_materii_grupa.csv')
