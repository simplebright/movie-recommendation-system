import time
from pathlib import Path

import pandas as pd
from deep_translator import GoogleTranslator


BASE_DIR = Path(__file__).parent
CSV_FILES = ["top250.csv", "movies_3.csv"]

# columns that may contain Chinese text in these datasets
TRANSLATE_COLUMNS = [
    "title",
    "country",
    "director_description",
    "leader",
    "star",
    "description",
    "all_tags",
    "language",
]

# shared translator and cache across all files/columns
translator = GoogleTranslator(source="zh-CN", target="en")
cache = {}


def translate_text(text: str) -> str:
    """Translate a single cell value with caching and basic error handling."""
    if pd.isna(text):
        return text
    text_str = str(text)
    if not text_str.strip():
        return text_str
    if text_str in cache:
        return cache[text_str]
    try:
        translated = translator.translate(text_str)
        cache[text_str] = translated
        # be gentle to the service
        time.sleep(0.2)
        return translated
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] translate failed, keep original: {text_str!r} ({exc})")
        cache[text_str] = text_str
        return text_str


def translate_file(filename: str) -> None:
    path = BASE_DIR / filename
    if not path.exists():
        print(f"[skip] {filename} not found")
        return

    print(f"\n=== Translating {filename} ===")
    df = pd.read_csv(path)
    total_rows = len(df)
    print(f"[info] rows: {total_rows}")

    for col in TRANSLATE_COLUMNS:
        if col not in df.columns:
            continue

        print(f"[col] {filename} -> {col}")
        new_values = []
        for idx, value in enumerate(df[col]):
            translated = translate_text(value)
            new_values.append(translated)

            # progress output every 50 rows
            if (idx + 1) % 50 == 0 or idx + 1 == total_rows:
                percent = (idx + 1) / total_rows * 100 if total_rows else 100
                print(
                    f"  [{filename}][{col}] {idx + 1}/{total_rows} "
                    f"({percent:5.1f}%)"
                )

        df[col] = new_values

    # overwrite original file with translated content
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"[done] {filename} saved with English translations.")


def main() -> None:
    print("Starting CSV translation...")
    for name in CSV_FILES:
        translate_file(name)
    print("\nAll CSV translations finished.")


if __name__ == "__main__":
    main()