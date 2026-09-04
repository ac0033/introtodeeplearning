"""Fast import and device checks for the local MIT 6.S191 environment."""

from __future__ import annotations

import importlib
import platform
import sys


MODULES = (
    "mitdeeplearning",
    "numpy",
    "scipy",
    "matplotlib",
    "pandas",
    "h5py",
    "torch",
    "torchvision",
    "tensorflow",
    "transformers",
    "datasets",
    "peft",
    "opik",
    "comet_ml",
    "music21",
    "pretty_midi",
)


def version_of(module: object) -> str:
    return str(getattr(module, "__version__", "installed"))


def main() -> int:
    print(f"Python: {sys.version.split()[0]} ({platform.platform()})")
    failures: list[tuple[str, str]] = []
    loaded: dict[str, object] = {}

    for name in MODULES:
        try:
            module = importlib.import_module(name)
            loaded[name] = module
            print(f"[OK] {name}: {version_of(module)}")
        except Exception as exc:  # import failures need to be reported together
            failures.append((name, f"{type(exc).__name__}: {exc}"))
            print(f"[FAIL] {name}: {failures[-1][1]}")

    torch = loaded.get("torch")
    if torch is not None:
        print(f"PyTorch CUDA available: {torch.cuda.is_available()}")

    tensorflow = loaded.get("tensorflow")
    if tensorflow is not None:
        print(f"TensorFlow devices: {tensorflow.config.list_physical_devices()}")

    if failures:
        print("\nEnvironment verification failed:")
        for name, error in failures:
            print(f"- {name}: {error}")
        return 1

    print("\nAll core lab imports passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
