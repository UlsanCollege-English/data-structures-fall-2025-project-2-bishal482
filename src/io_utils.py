"""CSV load/save helpers for (word, score) pairs.
The file format is two columns without header: word,score
"""

import csv
# (There should be NO other imports in this file)

def load_csv(path):
    """
    Loads words from a 2-column CSV file.
    Format: word,score
    """
    words = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                if not row:
                    continue
                w = row[0].strip().lower()
                try:
                    s = float(row[1]) if len(row) > 1 else 0.0
                except ValueError:
                    s = 0.0
                words.append((w, s))
    except FileNotFoundError:
        print(f"ERROR: File not found at {path}")
        return [] # Return empty list on error
    except Exception as e:
        print(f"ERROR: Could not read {path}. {e}")
        return [] # Return empty list on error
    return words

def save_csv(path, items):
    """
    Saves a list of (word, score) pairs to a CSV file.
    """
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for w, s in items:
                writer.writerow([w, s])
    except IOError as e:
        print(f"ERROR: Could not write to file {path}. {e}")

