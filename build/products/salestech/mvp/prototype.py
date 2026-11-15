# Quick 0-to-1 MVP script for SalesTech / B2B Growth
import sqlite3

conn = sqlite3.connect('salestech___b2b_growth.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, status TEXT)')
c.execute('INSERT INTO events (title, status) VALUES (?, ?)', ('Initial Scan', 'success'))
conn.commit()
print('MVP Database initialized for SalesTech / B2B Growth')
