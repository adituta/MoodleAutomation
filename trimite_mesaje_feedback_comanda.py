import csv
import sys
import requests
from config import MOODLE_URL, TOKEN

# --- se apeleaza asa: python trimite_mesaje_studenti_comanda.py studenti_feedback.csv "https://docs.google.com/forms/..."

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

def trimite_mesaje(csv_path, link_formular):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        studenti = list(reader)

    messages = {}
    for i, student in enumerate(studenti):
        userid = get_user_id_by_username(student["username"])
        if not userid:
            print(f"Utilizatorul {student['username']} nu a fost găsit.")
            continue

        mesaj = (
            f"Salut {student['firstname']},\n\n"
            f"Te rugăm să completezi formularul de feedback: {link_formular}\n\n"
            "Mulțumim!"
        )

        messages[f"messages[{i}][touserid]"] = userid
        messages[f"messages[{i}][text]"] = mesaj
        messages[f"messages[{i}][textformat]"] = 1

    if not messages:
        print("Nu s-au găsit destinatari validați.")
        return

    payload = {
        'wstoken': TOKEN,
        'wsfunction': 'core_message_send_instant_messages',
        'moodlewsrestformat': 'json',
    }
    payload.update(messages)

    r = requests.post(MOODLE_URL, data=payload)
    print("Răspuns de la server:", r.json())

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilizare: python trimite_mesaje_studenti.py <cale_csv> <link_formular>")
    else:
        csv_path = sys.argv[1]
        link = sys.argv[2]
        trimite_mesaje(csv_path, link)
