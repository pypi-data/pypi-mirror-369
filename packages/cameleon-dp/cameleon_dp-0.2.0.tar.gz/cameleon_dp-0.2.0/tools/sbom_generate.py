"""
Generate a minimal SBOM (CycloneDX JSON) for Python dependencies using pip.

Usage:
  python -m tools.sbom_generate --out sbom.json
"""
import argparse
import json
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    try:
        # Use pip list --format json as a simple source of components
        res = subprocess.run(["python", "-m", "pip", "list", "--format", "json"], capture_output=True, text=True, check=False)
        comps = json.loads(res.stdout or "[]")
    except Exception:
        comps = []
    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "components": [
            {
                "type": "library",
                "name": c.get("name"),
                "version": c.get("version"),
                "purl": f"pkg:pypi/{c.get('name')}@{c.get('version')}"
            } for c in comps
        ]
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(bom, f, indent=2)


if __name__ == "__main__":
    main()


