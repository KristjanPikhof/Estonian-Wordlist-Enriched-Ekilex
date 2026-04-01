# Estonian Word List with Ekilex and Frequency Data

This repo contains an open Estonian word list with 160,316 base words, enriched with Ekilex metadata and OpenSubtitles frequency data.

If you only need one file, start with `data/est_words_160k.tsv`. It includes the base word, frequency rank, CEFR level when available, and part of speech.

Snapshot date: 2026-04-01.

## At a Glance

| Metric | Value |
|--------|-------|
| Base words | 160,316 |
| Inflected forms | 5,454,775 |
| Found in Ekilex | 160,312 (99.99%) |
| With frequency rank | 12,493 (7.8%) |
| With CEFR proficiency level | 9,951 (6.2%) |
| With POS tag | 158,729 (99.0%) |
| Unique POS categories | 14 |
| Proficiency levels | A1, A2, B1, B2, C1 |

## Files

### `data/est_words_160k.tsv`
Main dataset. Contains all 160,316 words with frequency rank, proficiency level, and part of speech.

Sort order:
1. Frequency rank
2. Proficiency level
3. Alphabetical order

| Column | Type | Description |
|--------|------|-------------|
| `word` | string | Base form of the word |
| `freq_rank` | int | Frequency rank from the OpenSubtitles corpus (`1` = most common, `0` = no data) |
| `proficiency` | string | CEFR level (`A1`, `A2`, `B1`, `B2`, `C1`, or empty) |
| `pos` | string | Part-of-speech codes, comma-separated |

```tsv
word	freq_rank	proficiency	pos
ma	2	A1	pron
ei	3	A1	adv,interj
koer	2866	A1	s,adj
```

### `data/est_inflected_forms.tsv`
Inflected forms dataset. Contains 160,173 words with grammatical forms such as cases, declensions, and conjugations.

| Column | Type | Description |
|--------|------|-------------|
| `word` | string | Base form (dictionary headword) |
| `forms` | string | All inflected forms, comma-separated |

```tsv
word	forms
koer	koer,koera,koerasse,koeras,koerast,koerale,koeral,koeralt,...
maja	maja,majja,majasse,majas,majast,majale,majal,majalt,...
```

Estonian has 14 grammatical cases and a lot of verb inflection, so a single word can easily have 30 to 50+ forms.

### `data/est_proficiency_words.tsv`
CEFR-tagged subset. Contains 9,951 words with language proficiency levels.

| Column | Type | Description |
|--------|------|-------------|
| `word` | string | Base form |
| `proficiency` | string | CEFR level from `A1` (beginner) to `C1` (advanced) |
| `pos` | string | Part of speech |

```tsv
word	proficiency	pos
aadress	A1	s
aasta	A1	s
aabits	B1	s
```

Distribution: A1: 685, A2: 997, B1: 2,509, B2: 5,020, C1: 740

### `data/est_frequency_ranked.tsv`
Frequency-ranked subset. Contains 12,493 words with corpus frequency from OpenSubtitles.

| Column | Type | Description |
|--------|------|-------------|
| `word` | string | Word form |
| `rank` | int | Frequency rank (`1` = most common) |
| `corpus_count` | int | Raw occurrence count in the subtitle corpus |

```tsv
word	rank	corpus_count
ma	2	1864911
ei	3	1572717
koer	2866	13805
```

### `data/est_words_simple.txt`
Plain word list, one word per line, in the same sort order as the main dataset. Use this when you just need the words and none of the metadata.

## Part of Speech Tags

| Code | Meaning | Count |
|------|---------|-------|
| `s` | Noun | 116,122 |
| `adj` | Adjective | 18,232 |
| `prop` | Proper noun | 8,901 |
| `v` | Verb | 8,729 |
| `adv` | Adverb | 7,129 |
| `interj` | Interjection | 718 |
| `postp` | Postposition | 295 |
| `vrm` | Verb form | 239 |
| `num` | Numeral | 190 |
| `adjg` | Adjective (genitive attribute) | 173 |
| `pron` | Pronoun | 128 |
| `prep` | Preposition | 79 |
| `konj` | Conjunction | 29 |
| `adjid` | Adjective (plural only) | 1 |

## Data Sources

### 1. Ekilex, Eesti Keele Instituut (EKI)
Source: [ekilex.ee](https://ekilex.ee)

Ekilex is the official dictionary and terminology system maintained by the Estonian Language Institute. We queried it for:

- part of speech
- CEFR proficiency level
- inflected forms

160,312 out of 160,316 words were found. The 4 missing words are Turkish place names written with dotted-I Unicode characters.

### 2. Hermit Dave / OpenSubtitles Frequency List
Source: [github.com/hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords)

This list is derived from the OpenSubtitles 2018 corpus. It gives raw occurrence counts for about 50,000 Estonian words. Of those, 12,493 overlap with this project's base word list.

This frequency signal is useful, but it comes with bias. Subtitle data reflects spoken and conversational language much better than formal, technical, or literary Estonian.

### 3. Base Word List
The base 160,316-word list was compiled from publicly available Estonian dictionary sources. See `methodology/` for the collection details.

## Sorting Logic

The main dataset, `est_words_160k.tsv`, uses a three-tier sort so the most useful words show up first.

| Tier | Words | Criteria | Sort within tier |
|------|-------|----------|-----------------|
| 1 | 12,493 | Has frequency rank from OpenSubtitles | Rank ascending, most common first |
| 2 | 3,703 | Has proficiency level but no frequency rank | `A1 → A2 → B1 → B2 → C1`, then alphabetical |
| 3 | 144,120 | Has neither frequency nor proficiency data | Alphabetical |

## Use Cases

- **Keyboard autocomplete**: use the tier-sorted list for better suggestion order
- **Spellcheckers**: use `est_words_simple.txt` or the inflected forms dataset for broader coverage
- **Language learning apps**: use `est_proficiency_words.tsv` for graded vocabulary
- **NLP and morphological analysis**: use inflected forms for lemmatization and stemming
- **Text analysis**: use frequency data as one input for difficulty scoring

## Regenerating the Data

Use `scripts/export_from_checkpoint.py` to regenerate the published data files from the raw Ekilex checkpoint:

```bash
python3 scripts/export_from_checkpoint.py \
    --checkpoint /path/to/ekilex_checkpoint.jsonl \
    --frequency /path/to/hermit_dave_et_50k.txt \
    --output-dir data/
```

The raw checkpoint file is not included in this repo because it is large (123 MB, 160K JSONL entries). See `methodology/collection_process.md` for how it was produced.

## License

CC-BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)

## Attribution

If you use this dataset, please include attribution like this:

> Estonian word list data sourced from:
> 1. **Eesti Keele Instituut (EKI)** via [Ekilex](https://ekilex.ee): word entries, parts of speech, proficiency levels, and inflected forms. License: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> 2. **Hermit Dave / OpenSubtitles** via [FrequencyWords](https://github.com/hermitdave/FrequencyWords): frequency ranks derived from the OpenSubtitles 2018 corpus. License: [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
>
> Combined and processed by Kristjan Pikhof. Modifications include Ekilex enrichment for POS, proficiency, and inflected forms, plus frequency mapping from OpenSubtitles data. Results were deduplicated and sorted by frequency and proficiency tiers.

## Limitations

- **Frequency coverage is limited**: only 7.8% of words have frequency data. OpenSubtitles is useful, but it misses a lot of formal, technical, and specialized vocabulary.
- **Proficiency tagging is sparse**: only 6.2% of words have CEFR levels. Ekilex mainly provides proficiency data for commonly taught vocabulary.
- **Subtitle frequency is biased**: movie and TV subtitles overrepresent spoken and informal language.
- **No sentence context**: this is a word-level dataset. It does not include bigrams, collocations, or example sentences.
- **Inflected forms may include archaic variants**: Ekilex paradigms include grammatically valid forms that are rare in modern usage.
