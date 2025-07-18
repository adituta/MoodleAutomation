import csv
import requests
from config import MOODLE_URL, TOKEN

LINK_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLScw7rVDHBkpO45pfqpcEifZEmhJ8YXD4QM7ADEE3VKcQbDu5A/viewform?usp=header"

def get_user_id_by_username(username):
    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_user_get_users_by_field',
        'moodlewsrestformat': 'json',
        'field': 'username',
        'values[0]': username
    }
    response = requests.post(MOODLE_URL, data=payload)
    data = response.json()
    if data:
        return data[0]['id']
    return None

def trimite_mesaje(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['username']
            prenume = row['firstname']
            user_id = get_user_id_by_username(username)

            if not user_id:
                print(f"Utilizatorul {username} nu a fost găsit.")
                continue

            mesaj = f"Salut {prenume},\n\nTe rugăm să completezi chestionarul de feedback:\n{LINK_FORMULAR}\n\nMulțumim!"

            payload = {
                'wstoken': TOKEN,
                'wsfunction': 'core_message_send_instant_messages',
                'moodlewsrestformat': 'json',
                'messages[0][touserid]': user_id,
                'messages[0][text]': mesaj,
                'messages[0][textformat]': 1
            }

            r = requests.post(MOODLE_URL, data=payload)
            print(f"Mesaj trimis către {username}: {r.status_code}")

if __name__ == "__main__":
    trimite_mesaje("CSV\studenti_feedback.csv")
