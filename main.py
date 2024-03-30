import cv2
import sqlite3
from pyzbar.pyzbar import decode
import datetime

conn = sqlite3.connect('barcodeR')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS entries
             (id INTEGER PRIMARY KEY,
             code TEXT,
             entry_time TEXT,
             exit_time TEXT)''')

authorized_codes = ['0051111407592']

def barcodeRLog(code):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if code in authorized_codes :
        c.execute("SELECT * FROM entries WHERE code=? ORDER BY id DESC LIMIT 1", (code,))
        lastEntry = c.fetchone()
        if lastEntry is None or lastEntry[3] is not None:
            c.execute("INSERT INTO entries (code, entry_time) VALUES (?, ?)", (code, currentTime))
            print("Entry user for", code)
        else:
            c.execute("UPDATE entries SET exit_time=? WHERE id=?", (currentTime, lastEntry[0]))
            print("Exit user for", code)
        conn.commit()
    else:
        print("Unauthorized user:", code)

def barcodeREader():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture .")
            break
        greyScale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(greyScale)
        for obj in decoded_objects:
            code = obj.data.decode('utf-8')
            barcodeRLog(code)
        cv2.imshow('Barcode Scanner', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

barcodeREader()
