# EES Add-Opt Demo Site

**Live site:** <https://yonatangabay.csariel.xyz>

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

# 2. Install dependencies (Flask, pabutools from GitHub, and gunicorn)
pip install -r requirements.txt

# 3. Run the site
python app.py
```

Open <http://127.0.0.1:5000> in your browser. Set the `PORT` environment
variable to run on a different port.

## Running tests

```bash
python -m pytest tests/ -v
```

## Deployment

The site is built to run on the School of Computer Science server
(see the [service guide](https://csariel.xyz/how-to/service)), where it is
served by **Gunicorn** behind **Nginx** through a socket. In outline:

1. Clone the repo into an `app` folder in your server home directory.
2. Create and activate a virtual environment, then run
   `pip install -r requirements.txt`.
3. Keep the `app.run(debug=True, host="0.0.0.0", port=...)` block in `app.py`
   — the managed service relies on it — then start the service with
   `sudo myservice start`.

Notes:

- `requirements.txt` installs the algorithm straight from the GitHub fork, so
  the server always tracks the latest branch.
- The live site is served at <https://yonatangabay.csariel.xyz>
  (the URL follows the `https://<username>.csariel.xyz` pattern).
- View server logs for debugging with `sudo myservice log`.

## Project structure

```
├── app.py                  Flask app: input parsing, algorithm execution, result rendering
├── requirements.txt        Flask + pabutools (from GitHub) + gunicorn
├── static/
│   ├── builder.js          Visual election builder (vanilla JS)
│   └── styles.css          Site styles
├── templates/
│   ├── base.html           Shared layout with navigation and paper link
│   ├── index.html          Home page: algorithm overview, random-sample generator, election builder
│   ├── result.html         Step-by-step results with fairness numbers and logs
│   └── about.html          How the method works + about the author
└── tests/
    └── test_ees_addopt.py  Site route, validation, and integration tests
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
| [gunicorn](https://gunicorn.org/) | Production WSGI server used on the deployment host |
