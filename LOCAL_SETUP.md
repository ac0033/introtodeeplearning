# Local setup for MIT 6.S191 (2026)

This repository uses an isolated Python 3.11 environment for the core 2026 labs in
`lab1`, `lab2`, and `lab3`. It does not depend on the machine-wide Conda setup.

## One-time setup (PowerShell)

```powershell
.\scripts\setup-local.ps1
```

The script selects a uv-managed Python 3.11 runtime (reusing an existing cached copy
when available), creates `.venv`, installs the versions pinned in
`requirements-local.lock`, installs this checkout of `mitdeeplearning` in editable
mode, and runs import/device checks. All generated environment files are ignored by
Git.

To rebuild the environment from scratch:

```powershell
.\scripts\setup-local.ps1 -Recreate
```

## Run the labs

```powershell
.\scripts\start-jupyter.ps1
```

Open a notebook under `lab1`, `lab2`, or `lab3` and select the Python kernel whose
path is this repository's `.venv`. The environment already contains the local
`mitdeeplearning` package, so notebook `pip install mitdeeplearning` cells should
report that the requirement is satisfied.

## Service credentials

Some official notebooks require external accounts for experiment tracking or LLM
evaluation. Copy `.env.example` to `.env.local`, add only the keys you intend to use,
and load them from the environment instead of committing them into notebook cells.
The relevant services are Comet, OpenRouter, Opik, and optionally Hugging Face.

`.env.local` is ignored by Git. Before every push, check that no key was accidentally
saved into a notebook:

```powershell
git diff --check
git status --short
```

## Git workflow without a fork

- `origin` is your writable repository: `https://github.com/ac0033/introtodeeplearning.git`
- `upstream` is the read-only course repository: `https://github.com/MITDeepLearning/introtodeeplearning.git`
- Push your work directly with `git push origin main`.
- Fetch course changes with `git fetch upstream`, then compare and apply selected
  changes deliberately. The personal repository uses an independent snapshot history
  to avoid republishing an old leaked credential, so do not merge unrelated histories
  or overwrite completed notebook work.

## Hardware note

The current machine exposes no NVIDIA CUDA device, so TensorFlow and PyTorch use the
CPU. Lab 1 and Lab 2 can run locally but training will be slower. Lab 3 fine-tunes a
1.2-billion-parameter model and may require substantial RAM and time on CPU; the code
and dependencies are local, while model/data downloads and evaluation APIs still
require internet access and the relevant service credentials.

The legacy notebooks under `xtra_labs` target older Colab/Linux stacks (including
system packages and obsolete TensorFlow Probability versions). They are intentionally
not part of the reproducible 2026 core environment.
