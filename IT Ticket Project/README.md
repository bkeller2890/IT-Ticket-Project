Project utilities

Pre-commit
---------
Install project hooks locally:

```bash
python3 -m pip install -r requirements-dev.txt
pre-commit install
```

To run hooks across the repo (used in CI):

```bash
pre-commit run --all-files
```

Bandit in CI
------------
CI runs Bandit across the repository but skips rule B101 (use of `assert`) because test code commonly uses `assert` statements for test assertions. Treating these as security issues creates noise and false positives in CI. We chose to run Bandit across the whole repo but skip B101 so production code is still scanned while tests don't cause failures.

How to change this behavior
- Scan tests but ignore only B101 (current CI setting):

	- The workflow uses:

		```bash
		bandit -r . -q --skip B101
		```

	- This runs Bandit everywhere (including `tests/`) while ignoring only the `assert`-related findings.

- Exclude the entire `tests/` directory instead:

	- Edit `.github/workflows/pytest.yml` and replace the bandit step with:

		```bash
		bandit -r . -q --exclude tests
		```

	- This avoids scanning tests altogether and is useful when test code contains patterns that would otherwise generate many findings.

- Use targeted suppressions in tests:

	- If a specific test line legitimately triggers a Bandit finding (for example dynamic SQL used only in test setup), prefer adding a localized `# nosec` comment on that line with an explanatory note. This keeps the scan strict while acknowledging specific, reviewed exceptions.

Pick the approach that fits your team's tolerance for false positives vs. strict scanning. The repository currently uses `--skip B101` which balances coverage and noise.

CI / pre-commit badge
---------------------
Pre-commit workflow badge: (appears after pushing to GitHub)

```
[![Pre-commit](https://github.com/username/repository/actions/workflows/precommit.yml/badge.svg)](https://github.com/username/repository/actions/workflows/precommit.yml)
```

Local pre-commit CI script
-------------------------
There is a helper script to run the same check locally and show diffs:

```bash
./scripts/precommit_check.sh
```
