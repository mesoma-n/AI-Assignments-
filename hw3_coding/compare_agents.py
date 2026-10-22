import subprocess
from pathlib import Path

manager = Path("GameManager.py")
original = manager.read_text()

try:
    with open("comparison.txt", "w") as output:
        for version, module in [(1, "IntelligentAgent"), (2, "IntelligentAgent2")]:
            modified = original.replace(
                "from IntelligentAgent import IntelligentAgent",
                f"from {module} import IntelligentAgent"
            )

            if modified == original and version == 2:
                raise RuntimeError("Could not find the expected import in GameManager.py")

            manager.write_text(modified)

            heading = f"===== VERSION {version} ====="
            print(heading, flush=True)
            output.write(heading + "\n")

            for i in range(1, 6):
                result = subprocess.run(
                    ["python3", "GameManager.py"],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

                last_line = result.stdout.strip().splitlines()[-1]
                line = f"Game {i}: {last_line}"
                print(line, flush=True)
                output.write(line + "\n")
                output.flush()

            output.write("\n")
finally:
    manager.write_text(original)

print("\nResults saved to comparison.txt")
