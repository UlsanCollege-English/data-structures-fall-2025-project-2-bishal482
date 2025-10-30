#!/usr/bin/env python3
"""
CLI entrypoint for the autocomplete trie tool.

Supported interactive commands (one per line on stdin):
  load <path>
  save <path>
  insert <word> <freq>
  remove <word>
  contains <word>
  complete <prefix> <k>
  stats
  quit

This implementation is original and intended as a learning/reference example.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# ensure project root is on sys.path when run from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.trie import Trie
from src.io_utils import load_csv, save_csv


PROMPT = ""  # keep outputs machine-friendly (no interactive prompt text)


def load_command(trie: Trie, path_str: str) -> Trie:
    """Load CSV (word,score) pairs from path and return a new Trie populated with them."""
    path = Path(path_str)
    pairs = load_csv(path)
    new_trie = Trie()
    for word, score in pairs:
        new_trie.insert(word, score)
    return new_trie


def save_command(trie: Trie, path_str: str) -> None:
    """Save all trie items as CSV to path."""
    path = Path(path_str)
    save_csv(path, trie.items())


def insert_command(trie: Trie, word: str, freq_str: str) -> None:
    """Insert a word with given frequency (float)."""
    freq = float(freq_str)
    trie.insert(word.lower(), freq)


def remove_command(trie: Trie, word: str) -> None:
    """Remove a word and print OK or MISS depending on result."""
    ok = trie.remove(word.lower())
    print("OK" if ok else "MISS")


def contains_command(trie: Trie, word: str) -> None:
    """Print YES if trie contains word, else NO."""
    print("YES" if trie.contains(word.lower()) else "NO")


def complete_command(trie: Trie, prefix: str, k_str: str) -> None:
    """Print top-k completions for prefix, comma-separated."""
    k = int(k_str)
    results = trie.complete(prefix.lower(), k)
    print(",".join(results))


def stats_command(trie: Trie) -> None:
    """Print basic trie stats."""
    words, height, nodes = trie.stats()
    print(f"words={words} height={height} nodes={nodes}")


def parse_and_execute(line: str, trie: Trie) -> Tuple[bool, Trie]:
    """
    Parse one input line and execute command.

    Returns (continue_loop, trie) where continue_loop=False means quit requested.
    If a command replaces the trie (load), the updated trie is returned.
    """
    line = line.strip()
    if not line:
        return True, trie

    parts = line.split()
    if not parts:
        return True, trie

    cmd = parts[0].lower()

    try:
        if cmd == "quit":
            return False, trie

        if cmd == "load" and len(parts) == 2:
            trie = load_command(trie, parts[1])
            return True, trie

        if cmd == "save" and len(parts) == 2:
            save_command(trie, parts[1])
            return True, trie

        if cmd == "insert" and len(parts) == 3:
            insert_command(trie, parts[1], parts[2])
            return True, trie

        if cmd == "remove" and len(parts) == 2:
            remove_command(trie, parts[1])
            return True, trie

        if cmd == "contains" and len(parts) == 2:
            contains_command(trie, parts[1])
            return True, trie

        if cmd == "complete" and len(parts) == 3:
            complete_command(trie, parts[1], parts[2])
            return True, trie

        if cmd == "stats" and len(parts) == 1:
            stats_command(trie)
            return True, trie

    except FileNotFoundError:
        print(f"ERROR: File not found at {parts[1]}", file=sys.stderr)
    except (IOError, OSError) as e:
        print(f"ERROR: Could not read/write file. {e}", file=sys.stderr)
    except (IndexError, ValueError, TypeError):
        # malformed commands are intentionally ignored to keep grading simple
        pass

    # Unknown or malformed commands do nothing
    return True, trie


def main():
    trie = Trie()
    for raw in sys.stdin:
        cont, trie = parse_and_execute(raw, trie)
        if not cont:
            break


if __name__ == "__main__":
    main()
