# Praxia Security Hub — Known Limitations & Risk Mitigation

1. **Large Spacy Model Initialization:**
   - Spacy's `en_core_web_lg` model is ~400 MB. First-time module load in cold Python processes takes 3-4 seconds.
   - *Mitigation:* The FastAPI server loads the model once at startup into memory, ensuring subsequent HTTP requests respond in sub-millisecond latencies.
2. **BLA CLI Execution Time on Large Builds:**
   - Protecting large production bundles with `bankrupt` intensity executes deep AST traversal and complex tarpit synthesis.
   - *Mitigation:* Subprocess timeouts are configured to 120 seconds, and builds run in background staging directories.
3. **Non-Overlapping Token Replacement:**
   - When text contains nested entities (e.g. an email address containing a person's name), greedy regex matches could create malformed surrogates.
   - *Mitigation:* The `PrivacyGatewayProcessor` resolves interval overlaps by prioritizing the longest match and highest confidence score before right-to-left substitution.
