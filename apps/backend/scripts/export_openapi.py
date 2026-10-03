import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "openapi.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"
    output.write_text(payload, encoding="utf-8")
    print(f"OpenAPI exported to {output}")


if __name__ == "__main__":
    main()
