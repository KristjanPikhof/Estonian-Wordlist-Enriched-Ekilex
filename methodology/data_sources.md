# Data Sources

This dataset is built from three ingredients: a base Estonian word list, Ekilex metadata, and OpenSubtitles frequency counts.

Each source does a different job. The base list defines scope, Ekilex adds linguistic structure, and OpenSubtitles adds a rough signal for real-world usage.

## 1. Base Word List (160,316 words)

The foundation is a 160,316-word Estonian word list compiled from publicly available dictionary sources.

It includes:

- common vocabulary
- proper nouns, including place names and personal names
- compound words
- technical and specialized terms

The list is stored as a zlib-compressed UTF-8 text file, `est_words.txt.zlib`, with one word per line.

## 2. Ekilex, Eesti Keele Instituut (EKI)

**URL:** https://ekilex.ee  
**API:** REST API using the `ekilex-api-key` header  
**License:** CC-BY 4.0

Ekilex is the official dictionary and terminology system of the Estonian Language Institute. It is the authoritative source in this project for part of speech, CEFR level, and inflected forms.

### What we extracted per word

| Field | API endpoint | Description |
|-------|-------------|-------------|
| `word_id` | `/api/word/search/{word}` | Internal Ekilex identifier |
| `lang` | `/api/word/search/{word}` | Language code, `est` for our words |
| `word_class` | `/api/word/search/{word}` | Word class field, empty for all collected words |
| `proficiency` | `/api/word/details/{id}` → `lexemes[].lexemeProficiencyLevelCode` | CEFR level: `A1`, `A2`, `B1`, `B2`, `C1` |
| `pos` | `/api/word/details/{id}` → `lexemes[].pos[].code` | Part-of-speech codes |
| `inflected_forms` | `/api/word/details/{id}` → `word.paradigms[].forms[].value` | All grammatical forms |

### API endpoints used

1. **Word search**: `GET /api/word/search/{word}`  
   Returns matching words with basic metadata such as `wordId`, `lang`, and `wordClass`. We keep the first result where `lang == "est"`.

2. **Word details**: `GET /api/word/details/{word_id}`  
   Returns paradigms, lexemes, proficiency, part of speech, and other metadata.

### Coverage

- **160,312 of 160,316 words found** (99.99%)
- **4 words not found**: `i̇skele`, `i̇skenderun`, `i̇stanbul`, `i̇zmir`
- **9,951 words with proficiency levels**
- **158,729 words with POS tags**
- **160,173 words with inflected forms**, totaling 5.45M forms

The missing four are Turkish place names that use the Unicode dotted-I character.

### What we did not extract

- **Frequency data**: Ekilex has frequency-related fields in the schema, but they were unpopulated for these Estonian words.
- **Usage examples**: would require more API calls per lexeme.
- **Definitions**: not extracted, partly because the licensing implications for bulk definition reuse were unclear.
- **Etymology**: not extracted.

## 3. Hermit Dave / OpenSubtitles Frequency List

**URL:** https://github.com/hermitdave/FrequencyWords  
**Dataset:** `content/2018/et/et_50k.txt`  
**License:** CC-BY-SA 4.0 for content, MIT for code  
**Underlying data:** OpenSubtitles 2018 corpus (http://opus.nlpl.eu/OpenSubtitles2018.php)

### What it provides

This source is a frequency list derived from Estonian movie and TV subtitles. Each line is a word plus its raw corpus count:

```text
on 2143343
ma 1864911
ei 1572717
```

- 50,000 words in the source list
- 12,493 overlaps with the 160,316-word base list
- Rank `1` means most common word in the subtitle corpus

### Known biases

| Bias | What it means |
|------|---------------|
| **Conversational bias** | Spoken and informal language is overrepresented. |
| **Genre bias** | Subtitle language does not match written Estonian very well. |
| **Missing formal vocabulary** | Academic, legal, medical, and technical terms are often absent. |
| **Temporal bias** | The data reflects media available through 2018. |

## Source Comparison

| Aspect | Ekilex (EKI) | Hermit Dave / OpenSubtitles |
|--------|-------------|----------------------------|
| Type | Dictionary metadata | Corpus frequency |
| Coverage of our list | 99.99% | 7.8% |
| Provides frequency | No | Yes |
| Provides POS | Yes | No |
| Provides proficiency | Yes | No |
| Provides inflected forms | Yes | No |
| License | CC-BY 4.0 | CC-BY-SA 4.0 |
| Authority | Official Estonian Language Institute | Community-derived |

## Other Sources Considered but Not Used

| Source | Why it was not used |
|--------|---------------------|
| `wordfreq` Python library | No Estonian support |
| Leipzig Corpora Collection | Would need separate download and parsing, while OpenSubtitles already gave a workable frequency signal |
| Estonian National Corpus (ENC) | Not freely available as a machine-readable frequency list |
