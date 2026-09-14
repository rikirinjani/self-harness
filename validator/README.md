# Phase 3: Validator — How to Use

## You need:
A separate GPT account (or any LLM you trust as an independent evaluator).

## Steps:

### 1. Open a prompt file
Pick any file from `validator/prompts/BENCH-X-NN.txt`

Example: `validator/prompts/BENCH-R-03.txt`

### 2. Copy the full content into GPT
The prompt contains:
- Benchmark spec (task, success criteria, failure criteria)
- The output I produced (analysis, code, or plan)
- A scoring sheet for 8 quality axes (1-5)
- Space for weaknesses and strengths

### 3. Fill in scores
Replace `___` with numbers 1-5:
```
1. correctness (1-5): 4
   note: Good analysis but missing one axis
```

### 4. Save the response
Save GPT's full response (with scores filled in) to:
`validator/responses/BENCH-X-NN.txt`

### 5. Run the comparison
```bash
python validator/compare_scores.py
```

This compares Phase 2 scores vs GPT scores:
- Per-benchmark diff per axis
- Average agreement rate
- Flagged benchmarks where diff > 1.5 points

### File structure
```
validator/
├── prompts/          # 20 prompt files (for GPT)
│   ├── BENCH-R-01.txt
│   ├── BENCH-R-02.txt
│   └── ...
├── responses/        # Save GPT responses here
├── comparisons/      # Generated comparison reports
├── generate_prompts.py
└── compare_scores.py
```

### Optional: bulk export
If you want all prompts as a single file for batch processing:
```bash
python validator/generate_prompts.py --all-in-one
```
(Doesn't exist yet — let me know if needed)
