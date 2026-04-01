# Collection Process

This dataset was built in three passes: load frequency data, enrich each word from Ekilex, then export the final files.

The slow part was the Ekilex API pass. Everything else was basically instant compared to that.

## Timeline

| Date | Phase | Duration |
|------|-------|----------|
| 2026-03-28 | Script development and testing | ~4 hours |
| 2026-03-28 to 2026-03-31 | Ekilex API querying, across multiple sessions | ~27 hours total |
| 2026-03-31 | Final export and verification | ~1 hour |

## Phase 1: Frequency Ranking

This part runs offline and finishes quickly.

1. Download Hermit Dave's `et_50k.txt` from GitHub, or use a cached copy.
2. Parse each line as `word<space>count`.
3. Sort by count descending and assign ranks (`1` = most common).
4. Build a lookup map: `word → (rank, count)`.
5. Intersect that list with the 160,316-word base list.

Result: 12,493 words got a frequency rank.

## Phase 2: Ekilex API Enrichment

This part is resumable and took about 27 hours total.

### Request pattern per word

Each word requires two API calls:

```text
1. GET /api/word/search/{word}
   Headers: ekilex-api-key: <key>
   Returns: word ID, language, word class

2. GET /api/word/details/{word_id}
   Headers: ekilex-api-key: <key>
   Returns: proficiency, POS, inflected forms
```

### Rate limiting

- Wait `0.3` seconds between requests.
- Handle `429` responses with exponential backoff, up to 10 seconds.
- Stop automatically after 10 consecutive errors, then resume on the next run.

### Resumability

The script writes a JSONL checkpoint file, `ekilex_checkpoint.jsonl`. Each successful word is appended as one JSON object.

```json
{"word": "koer", "ekilex_found": true, "word_id": 183007, "lang": "est", "word_class": null, "proficiency": "A1", "pos": ["s", "adj"], "inflected_forms": ["koer", "koera", "koerasse", "..."], "timestamp": "2026-03-30T14:58:29"}
```

On restart, the script:

1. Loads all checkpoint entries into a set of processed words.
2. Skips words that are already done.
3. Re-processes the last checkpoint word, in case the previous run stopped mid-write.
4. Continues with the rest.

The process was interrupted and resumed multiple times during collection, with no data loss.

### Error handling

- Words that fail API lookup are logged to `ekilex_errors.jsonl`.
- HTTP errors other than `429` are logged, then the word is skipped.
- Network timeouts use a 15-second limit, then the word is skipped.
- The script can be stopped with `Ctrl+C` and resumed safely later.

### Extraction logic

From the API responses, the script extracts:

1. **Language**: filter search results for `lang == "est"`, otherwise fall back to the first result.
2. **Proficiency**: first non-null `lexemeProficiencyLevelCode` across all lexemes.
3. **POS**: all unique `pos[].code` values across all lexemes.
4. **Inflected forms**: all unique `forms[].value` values across all paradigms.

## Phase 3: Export

`export_from_checkpoint.py` reads the checkpoint plus the frequency list, then writes the final dataset files.

1. Load 160,316 entries from `ekilex_checkpoint.jsonl`.
2. Load 50,000 frequency entries from `hermit_dave_et_50k.txt`.
3. Deduplicate words case-insensitively.
4. Sort by the three-tier order: frequency, then proficiency, then alphabetical.
5. Export 5 output files.

See `README.md` for the file descriptions.

## Raw Data Sizes

| File | Size | Description |
|------|------|-------------|
| `ekilex_checkpoint.jsonl` | 123 MB | Raw API responses, not included in this repo |
| `hermit_dave_et_50k.txt` | 608 KB | Cached frequency download |
| `est_words_enriched.tsv` | 3.1 MB | Intermediate export in the source project |

The checkpoint file is not included here because it is large. If you have it, the export script can regenerate the published data files.

## Reproducibility

To reproduce the dataset from scratch:

1. Get an Ekilex API key from https://ekilex.ee.
2. Run the enrichment script from the source project:
   ```bash
   EKILEX_API_KEY=your_key python3 scripts/ekilex_word_enricher.py
   ```
3. Wait about 27 hours for all 160,316 words to be processed.
4. Run the export script:
   ```bash
   python3 scripts/export_from_checkpoint.py
   ```

The enrichment step is resumable, so you can stop and restart it whenever needed.
