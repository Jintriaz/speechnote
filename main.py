import json
from datetime import datetime
import speech_recognition as sr
import streamlit as st
from gtts import gTTS
import io
import os

# Speech Recognition Initialisierung
recognizer = sr.Recognizer()

# Funktion zum Hinzufügen einer Notiz
def add_note(note_text):
    note_date = datetime.now()  # aktuelles Datum und Uhrzeit
    notes = get_notes()  # Funktion zum Abrufen vorhandener Notizen
    notes.append({'date': note_date, 'content': note_text})  # Notiz hinzufügen
    save_notes(notes)

# Funktion zum Speichern der Notizen in einer JSON-Datei
def save_notes(notes):
    with open('notes.json', 'w') as f:
        # Konvertiere jedes Datum in einen String
        for note in notes:
            note['date'] = note['date'].strftime('%Y-%m-%d %H:%M:%S')  # Datum in String umwandeln
        json.dump(notes, f)

# Funktion zum Abrufen aller Notizen aus der JSON-Datei
def get_notes():
    try:
        with open('notes.json', 'r') as f:
            notes = json.load(f)
            # Konvertiere die Strings zurück in datetime-Objekte
            for note in notes:
                note['date'] = datetime.strptime(note['date'], '%Y-%m-%d %H:%M:%S')
            return notes
    except FileNotFoundError:
        return []  # Rückgabe einer leeren Liste, wenn die Datei nicht gefunden wird
    except json.JSONDecodeError:
        with open('notes.json', 'w') as f:
            json.dump([], f)  # Leere Liste speichern
        return []  # Rückgabe einer leeren Liste

# Funktion zum Löschen einer Notiz
def delete_note(index):
    notes = get_notes()
    if 0 <= index < len(notes):
        notes.pop(index)  # Notiz entfernen
        save_notes(notes)  # Notizen speichern

# Funktion zum Aufzeichnen von Notizen
def record_note():
    with sr.Microphone() as source:
        st.write("Bitte sprechen Sie Ihre Notiz.")
        audio = recognizer.listen(source)

        try:
            note_text = recognizer.recognize_google(audio, language='de-DE')  # Sprache auf Deutsch setzen
            st.write("Erkannte Notiz: ", note_text)
            add_note(note_text)
            st.success("Notiz erfolgreich gespeichert.")
        except sr.UnknownValueError:
            st.error("Spracherkennung konnte nicht verstehen.")
        except sr.RequestError as e:
            st.error(f"Fehler bei der Anfrage: {e}")

# Hauptanwendung
def main():
    st.title("Sprachnotiz App")

    # Notiz aufzeichnen
    if st.button("Notiz aufzeichnen"):
        record_note()

    # Textarea für Benutzereingaben
    note_input = st.text_area("Geben Sie Ihre Notiz hier ein:")

    # Button zum Speichern der Textarea-Notiz
    if st.button("Notiz speichern"):
        if note_input:
            add_note(note_input)
            st.success("Notiz erfolgreich gespeichert.")
            st.experimental_rerun()  # Seite neu laden, um die Änderungen zu zeigen
        else:
            st.warning("Bitte geben Sie eine Notiz ein.")

    # Anzeige der gespeicherten Notizen
    notes = get_notes()
    if notes:
        st.write("Gespeicherte Notizen:")
        for index, note in enumerate(notes):
            note_text = note['content']
            note_audio = gTTS(text=note_text, lang='de')

            # Temporäre Datei für das Audio erstellen
            audio_file_path = "temp_audio.mp3"
            note_audio.save(audio_file_path)  # Speichern in einer temporären Datei

            # Audio-Datei in den Puffer laden
            with open(audio_file_path, "rb") as f:
                audio_buffer = io.BytesIO(f.read())  # In den Puffer lesen

            # Text der Notiz anzeigen
            st.write(f"{note['date']}: {note_text}")

            # Audio-Player für die Notiz
            st.audio(audio_buffer, format="audio/mp3")

            # Button zum Löschen der Notiz
            if st.button(f"Notiz {index + 1} löschen", key=f"delete_{index}"):
                delete_note(index)
                st.success("Notiz erfolgreich gelöscht.")
                st.experimental_rerun()  # Seite neu laden, um die Änderungen zu zeigen

        # Temporäre Audio-Datei löschen
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

    else:
        st.write("Keine Notizen gefunden.")

if __name__ == "__main__":
    main()
