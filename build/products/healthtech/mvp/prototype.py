# Quick 0-to-1 MVP script for HealthTech / ClinicOps
import sqlite3

conn = sqlite3.connect('healthtech___clinicops.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, status TEXT)')
c.execute('INSERT INTO events (title, status) VALUES (?, ?)', ('Initial Scan', 'success'))
conn.commit()
print('MVP Database initialized for HealthTech / ClinicOps')
