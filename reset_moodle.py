import requests
from config import MOODLE_URL, TOKEN

def get_all_users():
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_get_users',
        'criteria[0][key]': 'email',
        'criteria[0][value]': '@',
        'moodlewsrestformat': 'json'
    }
    response = requests.post(MOODLE_URL, data=payload)
    return response.json().get('users', [])

def delete_users(user_ids):
    if not user_ids:
        print("Niciun utilizator de șters.")
        return

    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_delete_users',
        'moodlewsrestformat': 'json',
    }
    for i, uid in enumerate(user_ids):
        payload[f'userids[{i}]'] = uid

    response = requests.post(MOODLE_URL, data=payload)
    print("Utilizatori șterși:", response.text)

def get_all_courses():
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_course_get_courses',
        'moodlewsrestformat': 'json'
    }
    response = requests.post(MOODLE_URL, data=payload)
    return response.json()

def delete_courses(course_ids):
    if not course_ids:
        print("Niciun curs de șters.")
        return

    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_course_delete_courses',
        'moodlewsrestformat': 'json'
    }
    for i, cid in enumerate(course_ids):
        payload[f'courseids[{i}]'] = cid

    response = requests.post(MOODLE_URL, data=payload)
    print("Cursuri șterse:", response.text)

def reset_moodle():
    print("🔍 Obțin toți utilizatorii...")
    users = get_all_users()
    user_ids_to_delete = [u['id'] for u in users if u['username'] != 'admin']
    print(f"Se vor șterge {len(user_ids_to_delete)} utilizatori.")
    delete_users(user_ids_to_delete)

    print("Obțin toate cursurile...")
    courses = get_all_courses()
    course_ids_to_delete = [c['id'] for c in courses if c['id'] != 1]  # nu ștergem site course
    print(f"Se vor șterge {len(course_ids_to_delete)} cursuri.")
    delete_courses(course_ids_to_delete)

reset_moodle()
