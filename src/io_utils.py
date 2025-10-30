"""
CSV load/save helpers for (word, score) pairs.
File format: two columns with no header →  word,score
"""

import csv   # no other imports required


def load_csv(path):
    """
    Load a 2-column CSV file and return list of (word, score),
    where score is parsed as float (defaults to 0.0 if invalid).
    """
    results = []

    try:
        with open(path, encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)

            for row in reader:
                if not row:     # skip blank rows
                    continue

                raw_word = row[0]
                word = raw_word.strip().lower()

                score = 0.0
                if len(row) > 1:
                    try:
                        score = float(row[1])
                    except ValueError:
                        score = 0.0

                results.append((word, score))

    except FileNotFoundError:
        print(f"ERROR: File not found at {path}")
        return []
    except Exception as exc:
        print(f"ERROR: Could not read {path}: {exc}")
        return []

    return results


def save_csv(path, items):
    """
    Save a list of (word, score) pairs to a CSV file.
    Overwrites any existing file at the path.
    """
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            for word, score in items:
                writer.writerow([word, score])

    except OSError as exc:
        print(f"ERROR: Could not write to file {path}: {exc}")
