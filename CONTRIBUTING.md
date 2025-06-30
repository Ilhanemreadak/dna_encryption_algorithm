# Contributing to **DNA Encryption Algorithm**

> Thank you for taking the time to contribute! \:tada:
>
> This guide explains the workflow, coding standards, and review process we follow. Before starting, please read our [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## 💡 Quick start checklist

1. **Fork** the repo and create your branch:

   ```bash
   git clone https://github.com/<your‑user>/dna_encryption_algorithm
   cd dna_encryption_algorithm
   git checkout -b feat/my-awesome-improvement
   ```
2. **Set up** the dev environment (Python ≥ 3.10):

   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"       # includes test + lint deps
   pre-commit install              # git hook: auto‑format & lint
   ```
3. **Code** → **lint/format** → **test**:

   ```bash
   # Auto-format & sort imports
   pre-commit run --all-files      # runs black, isort, ruff, mypy
   # Unit tests & benchmarks
   pytest -q
   ```
4. **Commit** with [Conventional Commits](https://www.conventionalcommits.org/) style:

   ```
   feat(encrypt): add GPU batch mode
   ```
5. **Push & open a Pull Request** targeting the `main` branch. Fill in the PR template and ensure all CI checks pass.

---

## 🛠️ Local development details

| Task                             | Command                         |
| -------------------------------- | ------------------------------- |
| Install core deps only           | `pip install -e .`              |
| Build Cython extensions in place | `python -m build_ext --inplace` |
| Run type‑checker                 | `mypy dna_encrypt`              |
| Generate coverage report         | `pytest --cov=.`                |

> **Tip:** The project ships with a `Makefile` – run `make help` to see common shortcuts.

### Architecture overview (TL;DR)

```
├── dna_encrypt/          # Library code (encrypt.py, decrypt.py, utils.py …)
├── cyext/                # High‑perf .pyx modules (logistic.pyx, chaos_utils.pyx …)
├── examples/             # Jupyter / Colab notebooks
└── tests/                # pytest test‑suite
```

---

## 🔍 Testing guidelines

* Use `pytest`. Each public function/class should have at least one test.
* Follow **Arrange‑Act‑Assert** pattern.
* Keep test data ≤ 50 KB – larger fixtures belong in `tests/assets/` and are `.gitignored` in LFS.
* Performance‑critical code: include a quick benchmark (`pytest-benchmark`).

---

## 🧹 Code style & static analysis

We enforce the following via **pre‑commit** hooks & CI:

* **black** – auto‑format (line length = 88)
* **isort** – deterministic import order
* **ruff** – lint rules (select = `E,F,I,UP,NPY,B`)
* **mypy** – static typing (PEP 561‑compliant stubs)
* **Cython** – compile with `-O3` & boundscheck=false

Run `pre-commit run --all-files` before every push; CI will block PRs that fail.

---

## 📝 Commit message convention

| Type    | Scope example | Message example                             |
| ------- | ------------- | ------------------------------------------- |
| `feat`  | `encrypt`     | `feat(encrypt): add AES‑fallback option`    |
| `fix`   | `decrypt`     | `fix(decrypt): correct key length check`    |
| `perf`  | `chaos`       | `perf(chaos): vectorize logistic map`       |
| `docs`  | `readme`      | `docs(readme): add demo GIF`                |
| `test`  | `utils`       | `test(utils): cover edge cases for dna2bin` |
| `chore` | `ci`          | `chore(ci): upgrade ruff to 0.4`            |

> **Scope** = folder or module being changed; keep subject ≤ 50 chars, use imperative mood.

---

## 🔄 Pull Request process

* PR must reference an open **Issue** (`Resolves #123`).
* Complete the PR checklist – unchecked items will delay review.
* One or more reviewers will offer feedback within **3 business days**.
* Squash‑merge default; maintainers may re‑title commits for clarity.
* After merge, remember to **delete your branch**.

### PR checklist (auto‑generated via template)

* [ ] Lint (`pre‑commit`) & tests pass locally
* [ ] CI checks green
* [ ] Docs updated (README / docstrings)
* [ ] Added / updated unit tests
* [ ] Follows Code of Conduct

---

## 🛡️ Security disclosures

Please do **not** open a public issue for security bugs. Instead, e‑mail **[dev.adak.ie@outlook.com](mailto:dev.adak.ie@outlook.com)** – we’ll respond within 72 hours and coordinate a private fix.

---

## 🌱 Good first issues

We label beginner‑friendly contributions as **`good first issue`** and **`help wanted`**. Check the [issue tracker](https://github.com/Ilhanemreadak/dna_encryption_algorithm/issues) to get started!

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).

---

## 🙏 Thanks

Your time and talent make this project thrive. Welcome aboard – happy hacking! 🎉
