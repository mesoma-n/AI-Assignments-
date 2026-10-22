
import re
import subprocess
import sys
from pathlib import Path

manager = Path("GameManager.py")
agent2 = Path("IntelligentAgent2.py")
results_file = Path("comparison.txt")

if not manager.exists() or not agent2.exists():
    raise FileNotFoundError(
        "Make sure GameManager.py and IntelligentAgent2.py "
        "are in this folder."
    )

original = manager.read_text()

# Handles one or more spaces in the import statement
pattern = r"from\s+IntelligentAgent\s+import\s+IntelligentAgent"

replacement = "from IntelligentAgent2 import IntelligentAgent"

modified, count = re.subn(pattern, replacement, original, count=1)

if count != 1:
    raise RuntimeError(
        "Could not find the IntelligentAgent import in GameManager.py"
    )

try:
    # Temporarily make GameManager use Version 2
    manager.write_text(modified)

    with results_file.open("a") as output:
        output.write("\n===== VERSION 2 =====\n")
        output.flush()

        print("===== VERSION 2 =====", flush=True)

        for i in range(1, 6):
            result = subprocess.run(
                [sys.executable, "GameManager.py"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Game {i} failed:\n{result.stderr}"
                )

            lines = result.stdout.strip().splitlines()

            if not lines:
                raise RuntimeError(
                    f"Game {i} produced no output."
                )

            last_line = lines[-1]
            line = f"Game {i}: {last_line}"

            print(line, flush=True)
            output.write(line + "\n")
            output.flush()

finally:
    # Always restore the original GameManager
    manager.write_text(original)

print("\n===== FINAL COMPARISON =====")
print(results_file.read_text())
