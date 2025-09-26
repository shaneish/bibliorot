import spacy
from collections import Counter
from pathlib import Path
from json import dumps


def chunk_frequency(text: str, nlp) -> tuple[Counter, int]:
    parsed_doc = nlp(text)
    words = [token.text.lower() for token in parsed_doc if token.is_alpha and not token.is_stop]
    word_freq = Counter(words)
    return word_freq, len(words)


def word_frequencies(doc: Path, chunks: int = -1, max_length: int = 3_500_00) -> tuple[Counter, int]:
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = max_length # i really hope this is long enough for stormlight
    c0 = Counter([])
    word_count = 0
    with doc.open("r", encoding="utf-8") as f:
        while (chunk := f.read(chunks)):
            c, n = chunk_frequency(chunk, nlp)
            c0 += c
            word_count += n

    return c0, word_count


if __name__ == "__main__":
    BOOK_DIR = Path("../sources/books")
    COUNT_ARCHIVE =  Path("./outputs/word_counts/")
    TOP_N = 50

    # iterate over all da books and count 'em
    c0 = Counter([])
    max_length = 3_500_000
    word_count = 0
    for p in BOOK_DIR.rglob("*.md"):
        archive_name = f'{"standalone" if p.parent == BOOK_DIR else p.parent.name}__{p.stem}__word_count.json'
        archive_path = COUNT_ARCHIVE / archive_name
        print(f"\nProcessing {p.name}...")
        try: # the lengths i go to handle kaladin's thicc...mind
            c, n = word_frequencies(p, max_length=max_length)
        except ValueError as e:
            if "[E088]" in str(e):
                print(f"Document too long with {max_length = }, increasing by 1_000_000 and retrying...")
                max_length += 1_000_000
                c, n = word_frequencies(p, max_length=max_length)
            else:
                print(f"*** Skipping due to error: {e} ***")
                continue
        c0 += c
        word_count += n
        print(f"Top {TOP_N} words (out of {n}):", c.most_common(TOP_N))
        if True: # not archive_path.exists(): # if we already have it, no need to buck that horse again
            print(f"Writing counts to {archive_path}...")
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(dumps({"words_processed": n, "words": dict(c.most_common())}, indent=2))
        else:
            print(f"Archive {archive_path} already exists, skipping...")

    # combine dem all together!!!
    print(f"Top {3 * TOP_N} words across all books:", c0.most_common(3 * TOP_N))
    archive_path = COUNT_ARCHIVE / "all_books__word_count.json"
    if not archive_path.exists():
        print(f"Writing counts to {archive_path}...")
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(dumps({"words_processed": word_count, "words": dict(c0.most_common())}))
