"""Run the established pipeline without silently rerunning held-out evaluation."""
import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="VinUni Day06 pipeline; default is read-only validation")
    parser.add_argument("--stage", choices=["validate", "ingest", "benchmark"], default="validate")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    args = parser.parse_args()
    starter = Path(__file__).resolve().parents[1]
    def run(name, *arguments):
        subprocess.run([sys.executable, str(starter / "scripts" / name), *arguments], cwd=starter, check=True)
    if args.stage == "validate":
        run("check_benchmark.py", "--verify-pdf")
        run("validate_artifacts.py")
    elif args.stage == "ingest":
        for name in ["extract_pages.py", "clean_pages.py", "chunk_pages.py", "chunk_paragraphs.py"]:
            run(name)
        run("check_benchmark.py", "--verify-pdf")
        for strategy in "AB":
            run("embed_chunks.py", "--strategy", strategy)
        run("create_table.py")
        for strategy in "AB":
            run("load_vectors.py", "--strategy", strategy)
    else:
        run(f"benchmark_{args.split}.py")


if __name__ == "__main__":
    main()
