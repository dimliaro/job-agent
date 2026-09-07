# Job Agent (v1)

Βρίσκει job posts, τα βαθμολογεί σε σχέση με το προφίλ σου, και για τα καλύτερα
ξαναγράφει το βιογραφικό σου στοχευμένα ανά θέση. Σου στέλνει email (ή τυπώνει)
τα top matches.

## Δομή
- `config.py` — ρυθμίσεις, το προφίλ σου, thresholds
- `sources.py` — από πού έρχονται οι αγγελίες: **JSearch API** (live, Ελλάδα) ή `file` (offline test)
- `llm.py` — οι δύο κλήσεις στο Claude: `score_job`, `tailor_cv`
- `notify.py` — email digest
- `agent.py` — ο orchestrator (τρέξε αυτόν)
- `master_cv.md` — το master βιογραφικό σου (συμπλήρωσέ το)
- `jobs_sample.json` — δείγμα αγγελιών για να τρέξει άμεσα

## Setup
```bash
cd job-agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # και βάλε το ANTHROPIC_API_KEY σου μέσα
```

## Τρέξιμο
```bash
python agent.py
```
Χωρίς email ρυθμισμένο, το digest τυπώνεται στην κονσόλα και τα προσαρμοσμένα
βιογραφικά αποθηκεύονται στον φάκελο `output/`.

## Πηγή αγγελιών
Από προεπιλογή τραβάει live αγγελίες μέσω **JSearch** (Google for Jobs — καλύπτει
kariera.gr, skywalker.gr, LinkedIn, Indeed για Ελλάδα). Χρειάζεσαι δωρεάν
RapidAPI key (`RAPIDAPI_KEY` στο `.env`). Τι ψάχνει το ρυθμίζεις στο
`config.py` (`SEARCH_QUERIES`, `SEARCH_COUNTRY`, `SEARCH_DATE_POSTED`).

Για δοκιμές χωρίς να ξοδεύεις κλήσεις, βάλε `SOURCE = "file"` στο `config.py`
και θα διαβάζει το `jobs_sample.json`.

## Επόμενα βήματα (roadmap)
1. Γέμισε σωστά το `master_cv.md` (μόνο αληθινά στοιχεία — το μοντέλο δεν εφευρίσκει).
2. ~~Πραγματική πηγή αγγελιών~~ ✅ έτοιμο (JSearch στο `sources.py`).
3. ~~Export του CV σε `.docx`~~ ✅ έτοιμο (`export.py`).
4. Βάλε το να τρέχει μόνο του: cron ή GitHub Actions κάθε πρωί.
5. Αργότερα: κάνε το πραγματικό agent με tool-calling (το μοντέλο αποφασίζει
   ποια εργαλεία να καλέσει), αντί για σταθερό pipeline.
```
