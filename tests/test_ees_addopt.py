"""Tests for the EES Add-Opt demo site.

These test the Flask routes, input validation, error messages, and output
content — everything the *site* is responsible for. The algorithm itself is
tested in the pabutools repository.
"""

from __future__ import annotations

import json
import random
import unittest

from app import app, EXAMPLE, parse_election_from_payload, InputError


def _post(client, payload):
    """POST a JSON payload to /run and return the response."""
    return client.post("/run", data={"payload": json.dumps(payload)})


def _example_payload(**overrides):
    """Return a copy of the built-in EXAMPLE, with optional overrides."""
    data = {
        "budget": EXAMPLE["budget"],
        "projects": [dict(p) for p in EXAMPLE["projects"]],
        "voters": [list(v) for v in EXAMPLE["voters"]],
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_returns_200(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_about_returns_200(self):
        r = self.client.get("/about")
        self.assertEqual(r.status_code, 200)

    def test_favicon_returns_svg(self):
        r = self.client.get("/favicon.ico")
        self.assertEqual(r.status_code, 200)
        self.assertIn("svg", r.content_type)


# ---------------------------------------------------------------------------
# Main page content (requirements: algorithm explanation, paper link,
# input format explanation, random-sample generator)
# ---------------------------------------------------------------------------

class TestIndexContent(unittest.TestCase):
    def setUp(self):
        r = app.test_client().get("/")
        self.html = r.data.decode()

    def test_algorithm_explanation(self):
        self.assertIn("Method of Equal Shares", self.html)

    def test_paper_link(self):
        self.assertIn("https://arxiv.org/abs/2502.11797", self.html)

    def test_input_format_help(self):
        self.assertIn("Set the budget", self.html)
        self.assertIn("List the projects", self.html)
        self.assertIn("Add the votes", self.html)

    def test_random_sample_generator(self):
        self.assertIn("Generate a sample election", self.html)
        self.assertIn("gen-projects", self.html)
        self.assertIn("gen-voters", self.html)


# ---------------------------------------------------------------------------
# About page (requirements: algorithm explanation, personal details)
# ---------------------------------------------------------------------------

class TestAboutContent(unittest.TestCase):
    def setUp(self):
        r = app.test_client().get("/about")
        self.html = r.data.decode()

    def test_algorithm_explanation(self):
        self.assertIn("Method of Equal Shares", self.html)

    def test_paper_link(self):
        self.assertIn("https://arxiv.org/abs/2502.11797", self.html)

    def test_personal_details(self):
        self.assertIn("Yonatan Gabay", self.html)
        self.assertIn("github.com", self.html.lower())
        self.assertIn("linkedin.com", self.html.lower())


# ---------------------------------------------------------------------------
# Input validation (requirement: meaningful error messages)
# ---------------------------------------------------------------------------

class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_missing_budget(self):
        r = _post(self.client, _example_payload(budget=""))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"budget", r.data.lower())

    def test_negative_budget(self):
        r = _post(self.client, _example_payload(budget="-5"))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"negative", r.data.lower())

    def test_no_projects(self):
        r = _post(self.client, _example_payload(projects=[]))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"project", r.data.lower())

    def test_project_without_name(self):
        r = _post(self.client, _example_payload(
            projects=[{"name": "", "cost": "5"}]
        ))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"name", r.data.lower())

    def test_duplicate_project_names(self):
        r = _post(self.client, _example_payload(
            projects=[{"name": "Park", "cost": "3"}, {"name": "Park", "cost": "5"}],
            voters=[[0]],
        ))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Park", r.data)

    def test_invalid_cost(self):
        r = _post(self.client, _example_payload(
            projects=[{"name": "X", "cost": "abc"}],
            voters=[[0]],
        ))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"not a valid number", r.data.lower())

    def test_no_voters(self):
        r = _post(self.client, _example_payload(voters=[]))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"voter", r.data.lower())

    def test_voter_index_out_of_range(self):
        r = _post(self.client, _example_payload(voters=[[99]]))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"does not exist", r.data.lower())

    def test_empty_payload(self):
        r = self.client.post("/run", data={"payload": ""})
        self.assertEqual(r.status_code, 400)

    def test_malformed_json(self):
        r = self.client.post("/run", data={"payload": "{broken"})
        self.assertEqual(r.status_code, 400)


# ---------------------------------------------------------------------------
# Result page (requirements: shows input, final result, fairness
# guarantees, and logs)
# ---------------------------------------------------------------------------

class TestResultPage(unittest.TestCase):
    def setUp(self):
        r = _post(app.test_client(), _example_payload())
        self.assertEqual(r.status_code, 200)
        self.html = r.data.decode()

    def test_shows_input_recap(self):
        for p in EXAMPLE["projects"]:
            self.assertIn(p["name"], self.html)

    def test_shows_funded_projects(self):
        self.assertIn("Final result", self.html)
        self.assertIn("Funded", self.html)

    def test_shows_equal_share(self):
        # Step 1: each voter's equal share
        self.assertIn("equal share", self.html.lower())

    def test_shows_voter_spent_kept(self):
        # Step 2: table with what each voter spent and kept
        self.assertIn("Spent", self.html)
        self.assertIn("Kept", self.html)

    def test_shows_fairness_note(self):
        self.assertIn("Fits budget", self.html)

    def test_shows_step_by_step(self):
        self.assertIn("Round", self.html)
        self.assertIn("EES", self.html)

    def test_shows_logs_section(self):
        self.assertIn("log", self.html.lower())
        self.assertIn("toggle-logs", self.html)

    def test_logs_have_content(self):
        # The algorithm should produce at least some log messages
        self.assertIn("log-list", self.html)
        # At least one log badge inside the log list
        import re
        log_items = re.findall(r'log-badge-(?:info|debug)', self.html)
        self.assertGreater(len(log_items), 0, "Logs should contain algorithm messages")

    def test_budget_meter(self):
        self.assertIn("budget-meter", self.html)

    def test_paper_link_in_nav(self):
        self.assertIn("https://arxiv.org/abs/2502.11797", self.html)


# ---------------------------------------------------------------------------
# Random input smoke tests (requirement: test with random inputs,
# verify results are reasonable and readable including logs)
# ---------------------------------------------------------------------------

class TestRandomInputs(unittest.TestCase):
    """Run the algorithm through the site with several random elections."""

    def _random_payload(self, num_projects, num_voters):
        projects = [
            {"name": f"Proj{i+1}", "cost": str(1 + random.randint(1, 9))}
            for i in range(num_projects)
        ]
        total_cost = sum(int(p["cost"]) for p in projects)
        budget = str(max(int(projects[0]["cost"]), round(total_cost * 0.6)))
        voters = []
        for _ in range(num_voters):
            approvals = [i for i in range(num_projects) if random.random() < 0.5]
            if not approvals:
                approvals = [random.randint(0, num_projects - 1)]
            voters.append(approvals)
        return {"budget": budget, "projects": projects, "voters": voters}

    def _assert_result_ok(self, payload):
        r = _post(app.test_client(), payload)
        self.assertEqual(r.status_code, 200, f"Failed for payload: {payload}")
        html = r.data.decode()
        # Must contain input recap
        for p in payload["projects"]:
            self.assertIn(p["name"], html)
        # Must contain final result section
        self.assertIn("Final result", html)
        self.assertIn("Funded", html)
        # Must contain rounds summary
        self.assertIn("All rounds", html)
        # Must contain logs section
        self.assertIn("toggle-logs", html)
        return html

    def test_small_election(self):
        self._assert_result_ok(self._random_payload(2, 3))

    def test_medium_election(self):
        self._assert_result_ok(self._random_payload(5, 10))

    def test_large_election(self):
        self._assert_result_ok(self._random_payload(10, 20))

    def test_single_project_single_voter(self):
        payload = {"budget": "10", "projects": [{"name": "Solo", "cost": "5"}], "voters": [[0]]}
        html = self._assert_result_ok(payload)
        self.assertIn("Solo", html)

    def test_no_project_can_be_funded(self):
        """Budget too small for any project — should still return 200 with an explanation."""
        payload = {
            "budget": "1",
            "projects": [{"name": "Expensive", "cost": "100"}],
            "voters": [[0]],
        }
        r = _post(app.test_client(), payload)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"No project", r.data)


if __name__ == "__main__":
    unittest.main()
