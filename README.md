# EES Add-Opt Demo Site

A Flask web app that demonstrates the **Method of Equal Shares** with
add-opt completion for participatory budgeting.

Set a budget, add projects with costs, mark which projects each voter approves,
and the site shows which projects get funded — with step-by-step explanations
of why the result is fair.

The algorithm is from
[*Streamlining Equal Shares*](https://arxiv.org/abs/2502.11797)
by Sonja Kraiczy, Isaac Robinson, and Edith Elkind (2024).

The algorithm implementation lives in a separate repository:
[yonatang8675/pabutools](https://github.com/yonatang8675/pabutools)
(a fork of [COMSOC-Community/pabutools](https://github.com/COMSOC-Community/pabutools)).

## Quick start

```bash
# 1. Create a virtual environment (optional)
python -m venv .venv
# Windows:  .\.venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate

# 2. Install dependencies (installs Flask + pabutools from GitHub)
pip install -r requirements.txt

# 3. Run the site
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

## Running tests

```bash
python -m pytest tests/ -v
```

## Project structure

```
├── app.py                  Flask app: input parsing, algorithm execution, result rendering
├── requirements.txt        Flask + pabutools (from GitHub)
├── static/
│   ├── builder.js          Visual election builder (vanilla JS)
│   └── styles.css          Site styles
├── templates/
│   ├── base.html           Shared layout with navigation and paper link
│   ├── index.html          Home page: algorithm overview, random-sample generator, election builder
│   ├── result.html         Step-by-step results with fairness numbers and logs
│   └── about.html          How the method works + about the author
└── tests/
    └── test_ees_addopt.py  Algorithm and site integration tests
```

## Site features

- **Algorithm overview** on the main page with a link to the research paper.
- **Visual election builder** — set a budget, add projects, tick voter approvals.
- **Random sample generator** — enter the number of projects and voters, click
  a button, and the form fills with a realistic random election.
- **Input validation** with clear error messages for invalid data.
- **Step-by-step results** — the output page shows the input, the final funded
  projects, and the fairness guarantees (equal shares per voter, who paid what,
  leftover budget usage across completion rounds).
- **Algorithm logs** — a collapsible log section shows every decision the
  algorithm made.
- **About page** with method explanation and author details.

## Dependencies

| Package | Purpose |
|---|---|
| [Flask](https://flask.palletsprojects.com/) | Web framework |
| [pabutools](https://github.com/yonatang8675/pabutools) | EES add-opt algorithm and election model (installed from GitHub) |
