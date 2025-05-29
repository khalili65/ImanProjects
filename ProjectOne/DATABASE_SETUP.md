# Quran Database Setup for Workshop

## Database Overview

You've been provided with a SQLite database (`quran_workshop.db`) containing the complete text of the Quran. This database will serve as the foundation for your Quran recitation application.

## Database Statistics
- **Size**: ~1.7 MB
- **Suras**: 114 (complete Quran)
- **Verses**: 6,236 total verses
- **Pages**: 891 (organized with ~7 verses per page)
- **Encoding**: UTF-8 (full Arabic text support)

## Database Schema

### Table: `suras`
Contains information about each Surah (chapter) of the Quran.

| Column | Type | Description |
|--------|------|-------------|
| `sura` | INTEGER | Surah number (1-114) |
| `name` | TEXT | Arabic name of the Surah |
| `name_en` | TEXT | English name of the Surah |
| `num_ayahs` | INTEGER | Number of verses in the Surah |

**Example:**
```sql
SELECT * FROM suras WHERE sura = 1;
-- Result: 1, "سُورَةُ ٱلْفَاتِحَةِ", "Al-Faatiha", 7
```

### Table: `verses`
Contains the actual text of each verse.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `sura` | INTEGER | Surah number |
| `ayah` | INTEGER | Verse number within the Surah |
| `text` | TEXT | Arabic text of the verse |

**Example:**
```sql
SELECT text FROM verses WHERE sura = 1 AND ayah = 1;
-- Result: "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
```

### Table: `page_mapping`
Maps verses to page numbers for navigation purposes.

| Column | Type | Description |
|--------|------|-------------|
| `page` | INTEGER | Page number |
| `sura` | INTEGER | Surah number |
| `ayah` | INTEGER | Verse number |

**Example:**
```sql
SELECT * FROM page_mapping WHERE page = 1;
-- Returns all verses on page 1
```

## Quick Start Guide

### 1. Database Connection
```python
import sqlite3

def connect_to_quran_db(db_path="quran_workshop.db"):
    """Connect to the Quran database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Optional: for dict-like access
    return conn

# Usage
conn = connect_to_quran_db()
```

### 2. Basic Queries

#### Get a specific verse:
```python
def get_verse(conn, surah, ayah):
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM verses WHERE sura = ? AND ayah = ?", (surah, ayah))
    result = cursor.fetchone()
    return result[0] if result else None

# Example
verse_text = get_verse(conn, 1, 1)  # Gets Bismillah
print(verse_text)  # بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
```

#### Get all verses in a Surah:
```python
def get_surah_verses(conn, surah):
    cursor = conn.cursor()
    cursor.execute("SELECT ayah, text FROM verses WHERE sura = ? ORDER BY ayah", (surah,))
    return cursor.fetchall()

# Example
al_fatiha = get_surah_verses(conn, 1)
for ayah, text in al_fatiha:
    print(f"{ayah}: {text}")
```

#### Get page content:
```python
def get_page_content(conn, page_num):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pm.sura, pm.ayah, v.text, s.name as surah_name
        FROM page_mapping pm
        JOIN verses v ON pm.sura = v.sura AND pm.ayah = v.ayah
        JOIN suras s ON pm.sura = s.sura
        WHERE pm.page = ?
        ORDER BY pm.sura, pm.ayah
    """, (page_num,))
    return cursor.fetchall()

# Example
page_1 = get_page_content(conn, 1)
for sura, ayah, text, surah_name in page_1:
    print(f"Surah {sura} ({surah_name}), Ayah {ayah}: {text}")
```

#### Get Surah information:
```python
def get_surah_info(conn, surah):
    cursor = conn.cursor()
    cursor.execute("SELECT name, name_en, num_ayahs FROM suras WHERE sura = ?", (surah,))
    return cursor.fetchone()

# Example
info = get_surah_info(conn, 1)
if info:
    name, name_en, num_ayahs = info
    print(f"{name} ({name_en}) - {num_ayahs} verses")
```

### 3. Database Helper Class
Here's a complete helper class you can use in your application:

```python
import sqlite3
from typing import List, Tuple, Optional

class QuranDB:
    def __init__(self, db_path: str = "quran_workshop.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    def get_verse(self, surah: int, ayah: int) -> Optional[str]:
        """Get a specific verse"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT text FROM verses WHERE sura = ? AND ayah = ?", (surah, ayah))
        result = cursor.fetchone()
        return result['text'] if result else None
    
    def get_surah_verses(self, surah: int) -> List[Tuple[int, str]]:
        """Get all verses in a surah"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ayah, text FROM verses WHERE sura = ? ORDER BY ayah", (surah,))
        return [(row['ayah'], row['text']) for row in cursor.fetchall()]
    
    def get_page_content(self, page: int) -> List[dict]:
        """Get all verses on a specific page"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pm.sura, pm.ayah, v.text, s.name as surah_name
            FROM page_mapping pm
            JOIN verses v ON pm.sura = v.sura AND pm.ayah = v.ayah
            JOIN suras s ON pm.sura = s.sura
            WHERE pm.page = ?
            ORDER BY pm.sura, pm.ayah
        """, (page,))
        
        return [
            {
                'surah': row['sura'],
                'ayah': row['ayah'],
                'text': row['text'],
                'surah_name': row['surah_name']
            }
            for row in cursor.fetchall()
        ]
    
    def get_surah_info(self, surah: int) -> Optional[dict]:
        """Get information about a surah"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, name_en, num_ayahs FROM suras WHERE sura = ?", (surah,))
        result = cursor.fetchone()
        
        if result:
            return {
                'name': result['name'],
                'name_en': result['name_en'],
                'num_ayahs': result['num_ayahs']
            }
        return None
    
    def get_all_surahs(self) -> List[dict]:
        """Get information about all surahs"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT sura, name, name_en, num_ayahs FROM suras ORDER BY sura")
        
        return [
            {
                'sura': row['sura'],
                'name': row['name'],
                'name_en': row['name_en'],
                'num_ayahs': row['num_ayahs']
            }
            for row in cursor.fetchall()
        ]
    
    def get_total_pages(self) -> int:
        """Get the total number of pages"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(page) as max_page FROM page_mapping")
        result = cursor.fetchone()
        return result['max_page'] if result else 0

# Usage example
quran_db = QuranDB()

# Get Bismillah
bismillah = quran_db.get_verse(1, 1)
print(bismillah)

# Get Al-Fatiha info
fatiha_info = quran_db.get_surah_info(1)
print(fatiha_info)

# Get first page
page_1 = quran_db.get_page_content(1)
for verse in page_1:
    print(f"Surah {verse['surah']}, Ayah {verse['ayah']}: {verse['text']}")

# Don't forget to close
quran_db.close()
```

## Important Notes

### Text Encoding
- All Arabic text is stored in UTF-8 encoding
- The text includes diacritics (تشكيل)
- When comparing with speech recognition output, you may need to remove diacritics

### Arabic Text Processing
For speech recognition comparison, you'll often need to clean the text:

```python
def clean_arabic_text(text):
    """Remove diacritics for comparison"""
    diacritics = [
        '\u064B', '\u064C', '\u064D', '\u064E', '\u064F',
        '\u0650', '\u0651', '\u0652', '\u0653', '\u0654',
        '\u0655', '\u0656', '\u0657', '\u0658', '\u0659',
        '\u065A', '\u065B', '\u065C', '\u065D', '\u065E',
        '\u065F', '\u0670'
    ]
    
    for diacritic in diacritics:
        text = text.replace(diacritic, '')
    
    return ' '.join(text.split())  # Normalize spaces

# Example
original = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
cleaned = clean_arabic_text(original)
print(f"Original: {original}")
print(f"Cleaned:  {cleaned}")
```

### Page Navigation
The `page_mapping` table organizes verses into pages with approximately 7 verses per page. This is useful for:
- Creating a page-based navigation interface
- Displaying manageable chunks of text
- Progress tracking through the Quran

### Database Integrity
- All foreign key relationships are maintained
- No duplicate verses (enforced by UNIQUE constraint)
- Complete Quran text (verified: 114 surahs, 6,236 verses)

## Testing Your Database Connection

Use this simple test to verify your database setup:

```python
import sqlite3

def test_database():
    try:
        conn = sqlite3.connect("quran_workshop.db")
        cursor = conn.cursor()
        
        # Test 1: Count verses
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        print(f"✓ Found {verse_count} verses (expected: 6236)")
        
        # Test 2: Get Bismillah
        cursor.execute("SELECT text FROM verses WHERE sura = 1 AND ayah = 1")
        bismillah = cursor.fetchone()[0]
        print(f"✓ Bismillah: {bismillah}")
        
        # Test 3: Check page mapping
        cursor.execute("SELECT COUNT(*) FROM page_mapping")
        mapping_count = cursor.fetchone()[0]
        print(f"✓ Page mappings: {mapping_count}")
        
        conn.close()
        print("✅ Database test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()
```

## Next Steps

1. **Copy the database file** (`quran_workshop.db`) to your project directory
2. **Test the connection** using the code above
3. **Integrate with your FastAPI application** using the helper class
4. **Build your speech recognition features** using the verse text as reference

Good luck with your workshop! 🚀 