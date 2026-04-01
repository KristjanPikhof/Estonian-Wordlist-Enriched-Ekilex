# Combination Logic

No single source had everything this dataset needed.

Ekilex is strong on dictionary metadata. OpenSubtitles is useful for usage frequency. Putting them together gets you a list that is much more practical than either source on its own.

## Why combine multiple sources?

| Need | Ekilex | OpenSubtitles |
|------|--------|---------------|
| Is this a real Estonian word? | Yes, dictionary-backed | Partial, corpus-only |
| How common is it in usage? | No | Yes |
| Part of speech | Yes, 99% coverage | No |
| Proficiency level | Partial, 6.2% | No |
| Inflected forms | Yes, 99.9% | No |

The basic tradeoff is simple: Ekilex gives authority, OpenSubtitles gives frequency.

## Merging Strategy

### Step 1: Use the base word list as the boundary

The 160,316-word base list defines the scope. Every word in the final output comes from that list.

### Step 2: Enrich each word from Ekilex

Each base word was looked up in Ekilex. For each match, we pulled out proficiency, part of speech, and inflected forms.

### Step 3: Map frequency data offline

The Hermit Dave frequency list was intersected with the base word list using case-insensitive matching. If a word appears in both, it gets a frequency rank. If not, its rank is `0`.

### Step 4: Sort in three tiers

The combined dataset is sorted to put the most useful words first:

```text
Tier 1: Has frequency rank (12,493 words, 7.8%)
    Sort by: rank ascending (1 = most common)

Tier 2: Has proficiency level but no frequency rank (3,703 words, 2.3%)
    Sort by: A1 → A2 → B1 → B2 → C1, then alphabetical

Tier 3: Has neither frequency nor proficiency (144,120 words, 89.9%)
    Sort by: alphabetical
```

## Why this tier order?

- **Tier 1 first**: frequency is the best available signal for everyday usefulness. If you are building autocomplete, `kas` should show up before `kaabel`.
- **Tier 2 second**: CEFR levels are less precise than raw frequency, but they still tell you which words matter more for learners.
- **Tier 3 last**: once a word has neither frequency nor proficiency data, alphabetical order is the cleanest fallback.

## Overlap Between Tiers

| Combination | Count |
|-------------|-------|
| Both frequency and proficiency | 6,248 |
| Frequency only | 5,946 |
| Proficiency only | 3,703 |
| Total with any ranking signal | 15,897 (9.9%) |
| Neither | 144,120 (89.9%) |

Words with both frequency and proficiency are placed in Tier 1. Frequency wins because it is the finer-grained signal.

## Deduplication

Words are deduplicated case-insensitively, while keeping the first occurrence from the original list. That preserves the original canonical casing.

## Data Integrity Checks

- All 160,316 input words appear in the output.
- No new words are introduced.
- Frequency ranks increase monotonically within Tier 1.
- Proficiency levels stay within the CEFR set: `A1`, `A2`, `B1`, `B2`, `C1`.
- POS codes stay within the Ekilex POS taxonomy.

## What this combination does not do

| Limitation | What it means |
|------------|---------------|
| **No frequency interpolation** | Tier 3 words do not get guessed frequency ranks. |
| **No proficiency inference** | Missing CEFR levels stay missing. |
| **No form-level frequency** | Inflected forms do not inherit the base word's rank. |
| **No cross-source validation** | If sources disagree, Ekilex is treated as the dictionary authority. |
