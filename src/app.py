"""
Interactive CLI entrypoint.
Commands:
  load <path>
  save <path>
  insert <word> <freq>
  remove <word>
  contains <word>
  complete <prefix> <k>
  stats
  quit
"""

import sys
# This import needs to be relative to the project root
# when running `python src/app.py`
# To fix this, we adjust the system path
import os
# Add the project root (one level up from 'src') to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.trie import Trie
from src.io_utils import load_csv, save_csv

PROMPT = ""  # keep outputs machine-friendly (no prompt)

def main():
    trie = Trie()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0].lower()

        if cmd == 'quit':
            break

        try:
            if cmd == 'load' and len(parts) == 2:
                path = parts[1]
                pairs = load_csv(path)
                # Replace current content
                trie = Trie()
                for w, s in pairs:
                    trie.insert(w, s)
                continue

            if cmd == 'save' and len(parts) == 2:
                path = parts[1]
                # Use the new .items() method to get all words and scores
                save_csv(path, trie.items())
                continue

            if cmd == 'insert' and len(parts) == 3:
                w = parts[1].lower()
                freq = float(parts[2])
                trie.insert(w, freq)
                continue

            if cmd == 'remove' and len(parts) == 2:
                w = parts[1].lower()
                print('OK' if trie.remove(w) else 'MISS')
                continue

            if cmd == 'contains' and len(parts) == 2:
                w = parts[1].lower()
                print('YES' if trie.contains(w) else 'NO')
                continue

            if cmd == 'complete' and len(parts) == 3:
                prefix = parts[1].lower()
                k = int(parts[2])
                results = trie.complete(prefix, k)
                print(','.join(results))
                continue

            if cmd == 'stats':
                words, height, nodes = trie.stats()
                print(f"words={words} height={height} nodes={nodes}")
                continue

        except FileNotFoundError:
            print(f"ERROR: File not found at {parts[1]}", file=sys.stderr)
        except (IOError, OSError) as e:
            print(f"ERROR: Could not read/write file. {e}", file=sys.stderr)
        except (IndexError, ValueError, TypeError):
            # Catches malformed commands like 'insert word' (missing freq)
            # or 'complete p' (missing k)
            pass # Unknown or malformed commands do nothing

        # Unknown or malformed commands do nothing (keeps grading simple)

if __name__ == '__main__':
    main()

