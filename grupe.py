import pandas as pd
import requests
from config import MOODLE_URL, TOKEN

studenti_grupe = pd.read_csv("studenti_grupe.csv")
materii_grupe = pd.read_csv("materii_grupe.csv")

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
    if data.get("courses"):
        return data["courses"][0]["id"]
    return None

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
    if data.get("users"):
        return data["users"][0]["id"]
    return None

def create_group(courseid, groupname):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_group_create_groups',
        'moodlewsrestformat': 'json',
        'groups[0][courseid]': courseid,
        'groups[0][name]': groupname
    }
    response = requests.post(MOODLE_URL, data=payload)
    result = response.json()
    if isinstance(result, list) and result:
        return result[0]['id']
    return None

def add_user_to_group(groupid, userid):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_group_add_group_members',
        'moodlewsrestformat': 'json',
        'members[0][groupid]': groupid,
        'members[0][userid]': userid
    }
    requests.post(MOODLE_URL, data=payload)

grupe_materii = materii_grupe.groupby("grupanume")["course_shortname"].apply(list).to_dict()
grupe_studenti = studenti_grupe.groupby("grupanume")["username"].apply(list).to_dict()

for grupanume, student_list in grupe_studenti.items():
    materii = grupe_materii.get(grupanume, [])
    
    for shortname in materii:
        courseid = get_course_id_by_shortname(shortname)
        if not courseid:
            print(f"❌ Cursul {shortname} nu a fost găsit.")
            continue

        groupid = create_group(courseid, grupanume)
        if not groupid:
            print(f"❌ Nu s-a putut crea grupul {grupanume} în cursul {shortname}.")
            continue

        for username in student_list:
            userid = get_user_id_by_username(username)
            if userid:
                add_user_to_group(groupid, userid)
                print(f"✅ {username} adăugat în grupul {grupanume} (curs: {shortname})")
            else:
                print(f"⚠️ Utilizatorul {username} nu a fost găsit.")

print("✅ Finalizat: Grupe, utilizatori și asociere completă.")