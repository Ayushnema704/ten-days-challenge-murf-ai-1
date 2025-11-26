"""
Initialize the fraud cases database with sample data for Day 6.
This script creates a SQLite database with fake fraud cases.
"""
import sqlite3
import json
from datetime import datetime, timedelta

def init_database():
    """Create and populate the fraud cases database."""
    conn = sqlite3.connect('fraud_cases.db')
    cursor = conn.cursor()
    
    # Create fraud_cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL,
            securityIdentifier TEXT NOT NULL,
            securityQuestion TEXT NOT NULL,
            securityAnswer TEXT NOT NULL,
            cardEnding TEXT NOT NULL,
            transactionAmount REAL NOT NULL,
            transactionName TEXT NOT NULL,
            transactionTime TEXT NOT NULL,
            transactionCategory TEXT NOT NULL,
            transactionSource TEXT NOT NULL,
            transactionLocation TEXT NOT NULL,
            caseStatus TEXT DEFAULT 'pending_review',
            outcomeNote TEXT,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')
    
    # Clear existing data
    cursor.execute('DELETE FROM fraud_cases')
    
    # Sample fraud cases with fake data
    fraud_cases = [
        {
            'userName': 'John Smith',
            'securityIdentifier': '12345',
            'securityQuestion': 'What is your favorite color?',
            'securityAnswer': 'blue',
            'cardEnding': '4242',
            'transactionAmount': 2499.99,
            'transactionName': 'ABC Electronics Store',
            'transactionTime': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'transactionCategory': 'e-commerce',
            'transactionSource': 'alibaba.com',
            'transactionLocation': 'Shanghai, China',
            'caseStatus': 'pending_review'
        },
        {
            'userName': 'Sarah Johnson',
            'securityIdentifier': '67890',
            'securityQuestion': 'What city were you born in?',
            'securityAnswer': 'delhi',
            'cardEnding': '5678',
            'transactionAmount': 15999.00,
            'transactionName': 'Luxury Fashion Boutique',
            'transactionTime': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'transactionCategory': 'retail',
            'transactionSource': 'fashionstore.com',
            'transactionLocation': 'Paris, France',
            'caseStatus': 'pending_review'
        },
        {
            'userName': 'Michael Brown',
            'securityIdentifier': '11223',
            'securityQuestion': 'What is your mothers maiden name?',
            'securityAnswer': 'sharma',
            'cardEnding': '9012',
            'transactionAmount': 899.50,
            'transactionName': 'Gaming Paradise Store',
            'transactionTime': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'transactionCategory': 'gaming',
            'transactionSource': 'gamingparadise.net',
            'transactionLocation': 'Tokyo, Japan',
            'caseStatus': 'pending_review'
        },
        {
            'userName': 'Emily Davis',
            'securityIdentifier': '44556',
            'securityQuestion': 'What is your pets name?',
            'securityAnswer': 'max',
            'cardEnding': '3456',
            'transactionAmount': 5299.99,
            'transactionName': 'Tech Gadgets International',
            'transactionTime': (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'transactionCategory': 'electronics',
            'transactionSource': 'techgadgets.co',
            'transactionLocation': 'Singapore',
            'caseStatus': 'pending_review'
        },
        {
            'userName': 'David Wilson',
            'securityIdentifier': '78901',
            'securityQuestion': 'What is your favorite food?',
            'securityAnswer': 'pizza',
            'cardEnding': '7890',
            'transactionAmount': 12500.00,
            'transactionName': 'Premium Watch Collection',
            'transactionTime': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'transactionCategory': 'luxury-goods',
            'transactionSource': 'luxurywatches.com',
            'transactionLocation': 'Dubai, UAE',
            'caseStatus': 'pending_review'
        }
    ]
    
    # Insert fraud cases
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for case in fraud_cases:
        cursor.execute('''
            INSERT INTO fraud_cases (
                userName, securityIdentifier, securityQuestion, securityAnswer,
                cardEnding, transactionAmount, transactionName, transactionTime,
                transactionCategory, transactionSource, transactionLocation,
                caseStatus, createdAt, updatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case['userName'], case['securityIdentifier'], case['securityQuestion'],
            case['securityAnswer'], case['cardEnding'], case['transactionAmount'],
            case['transactionName'], case['transactionTime'], case['transactionCategory'],
            case['transactionSource'], case['transactionLocation'], case['caseStatus'],
            now, now
        ))
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM fraud_cases')
    count = cursor.fetchone()[0]
    print(f"✅ Database initialized successfully!")
    print(f"✅ Created {count} fraud cases")
    
    # Show sample cases
    cursor.execute('SELECT userName, cardEnding, transactionAmount, transactionName FROM fraud_cases LIMIT 3')
    print("\n📋 Sample fraud cases:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: ₹{row[2]:.2f} at {row[3]} (Card ending {row[1]})")
    
    conn.close()

if __name__ == '__main__':
    init_database()
