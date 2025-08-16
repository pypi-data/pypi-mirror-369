import sys
import os
from practicejapanese import __version__ as VERSION

def run_dev_mode():
    print("Developer mode activated!")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Available quizzes: vocab_quiz, kanji_quiz, filling_quiz")
    print("Dev options:")
    print("1. Save all scores")
    print("2. Load all scores (overwrite current)")
    print("3. Exit dev mode")
    dev_choice = input("Enter dev option: ").strip()
    if dev_choice == "1":
        from practicejapanese.core.vocab import load_vocab
        from practicejapanese.core.kanji import load_kanji
        vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Vocab.csv"))
        kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Kanji.csv"))
        vocab_list = load_vocab(vocab_path)
        kanji_list = load_kanji(kanji_path)
        # Determine output directory and ensure it exists
        home_dir = os.path.expanduser("~")
        out_dir = os.path.join(home_dir, "Public", "practicejapanese")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "scores.txt")

        # Build content to write
        lines = []
        lines.append(f"PracticeJapanese Scores (version {VERSION})")
        lines.append("")
        lines.append("Kanji Scores:")
        for entry in kanji_list:
            if isinstance(entry, tuple) and len(entry) >= 4:
                kanji = entry[0]
                score = entry[-1]
                lines.append(f"{kanji}: {score}")
        lines.append("")
        lines.append("Vocab Scores:")
        for entry in vocab_list:
            if isinstance(entry, tuple) and len(entry) >= 5:
                word = entry[0]
                vocab_score = entry[3]
                filling_score = entry[4]
                lines.append(f"{word}: Vocab Quiz Score = {vocab_score}, Filling Quiz Score = {filling_score}")

        try:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print(f"All scores saved to: {out_file}")
        except OSError as e:
            print(f"Failed to save scores to {out_file}: {e}")
    elif dev_choice == "2":
        # Load scores from saved file and overwrite CSV score columns
        home_dir = os.path.expanduser("~")
        in_file = os.path.join(home_dir, "Public", "practicejapanese", "all_scores.txt")
        if not os.path.exists(in_file):
            print(f"Scores file not found: {in_file}")
            return
        try:
            with open(in_file, encoding="utf-8") as f:
                raw_lines = [l.rstrip('\n') for l in f]
        except OSError as e:
            print(f"Failed to read {in_file}: {e}")
            return

        # Parse sections
        kanji_scores = {}
        vocab_scores = {}  # word -> (vocab_score, filling_score)
        section = None
        for line in raw_lines:
            if not line.strip():
                continue
            if line.startswith("Kanji Scores:"):
                section = "kanji"
                continue
            if line.startswith("Vocab Scores:"):
                section = "vocab"
                continue
            if section == "kanji":
                # Format: <kanji>: <score>
                if ':' in line:
                    parts = line.split(':', 1)
                    k = parts[0].strip()
                    try:
                        sc = int(parts[1].strip())
                    except ValueError:
                        continue
                    kanji_scores[k] = sc
            elif section == "vocab":
                # Format: <word>: Vocab Quiz Score = X, Filling Quiz Score = Y
                if ':' in line:
                    word, rest = line.split(':', 1)
                    word = word.strip()
                    # Extract numbers
                    vs = None
                    fs = None
                    for piece in rest.split(','):
                        piece = piece.strip()
                        if piece.startswith('Vocab Quiz Score ='):
                            try:
                                vs = int(piece.split('=')[1].strip())
                            except ValueError:
                                pass
                        elif piece.startswith('Filling Quiz Score ='):
                            try:
                                fs = int(piece.split('=')[1].strip())
                            except ValueError:
                                pass
                    if vs is not None or fs is not None:
                        vocab_scores[word] = (vs if vs is not None else 0, fs if fs is not None else 0)

        # Update Kanji.csv
        kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Kanji.csv"))
        vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Vocab.csv"))
        import csv
        # Kanji
        try:
            temp_path = kanji_path + '.temp'
            with open(kanji_path, 'r', encoding='utf-8') as infile, open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in reader:
                    k = (row.get('Kanji') or '').strip()
                    if k in kanji_scores and 'Score' in fieldnames:
                        row['Score'] = str(kanji_scores[k])
                    writer.writerow(row)
            os.replace(temp_path, kanji_path)
            print(f"Updated Kanji scores in {kanji_path}")
        except OSError as e:
            print(f"Failed updating Kanji.csv: {e}")

        # Vocab
        try:
            temp_path = vocab_path + '.temp'
            with open(vocab_path, 'r', encoding='utf-8') as infile, open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in reader:
                    w = (row.get('Kanji') or '').strip()
                    if w in vocab_scores:
                        vs, fs = vocab_scores[w]
                        if 'VocabScore' in fieldnames:
                            row['VocabScore'] = str(vs)
                        if 'FillingScore' in fieldnames:
                            row['FillingScore'] = str(fs)
                    writer.writerow(row)
            os.replace(temp_path, vocab_path)
            print(f"Updated Vocab scores in {vocab_path}")
        except OSError as e:
            print(f"Failed updating Vocab.csv: {e}")
    else:
        print("Exiting dev mode.")
