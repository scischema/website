import csv
import json
import re
import shutil
from html import escape
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WEBSITE_ROOT = SCRIPT_DIR.parent

SOURCE_DIR = SCRIPT_DIR / "schema-json"
METADATA_FILE = SCRIPT_DIR / "schema-metadata.csv"
TARGET_DIR = WEBSITE_ROOT / "schemas"

SKIP_EXISTING = True


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def prop_type(prop: dict) -> str:
    if "$ref" in prop:
        return "Object"

    value = prop.get("type", "Object")

    if isinstance(value, list):
        return " or ".join(v.title() for v in value)

    return str(value).title()


def table_rows(schema: dict) -> str:
    required = set(schema.get("required", []))
    rows = []

    for name, prop in schema.get("properties", {}).items():
        rows.append(f"""          <tr>
            <td>{escape(name)}</td>
            <td>{escape(prop_type(prop))}</td>
            <td>{escape(prop.get("description", ""))}</td>
            <td>{"Yes" if name in required else "No"}</td>
          </tr>""")

    return "\n".join(rows)


def load_metadata() -> list[dict]:
    with METADATA_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def orkg_html(orkg_url: str) -> str:
    if orkg_url.strip():
        return f"""          <li>
            <a href="{escape(orkg_url.strip())}">View template in ORKG</a>
            <span> — ORKG template / SHACL representation</span>
          </li>"""

    return """          <li>
            <span>ORKG template / SHACL representation — forthcoming</span>
          </li>"""


def generate_html(process_name, domain_name, schema_title, description, rows, orkg_url):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SciSchema — {escape(process_name)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="icon" type="image/png" href="/assets/logo.png">
  <link rel="stylesheet" href="/style.css">
</head>

<body>
  <header>
    <a class="logo" href="/">
      <img src="/assets/logo.png" alt="SciSchema Logo">
      <span>SciSchema</span>
    </a>
    <nav>
      <a href="/docs/">Docs</a>
      <a href="/schemas/">Schemas</a>
      <a href="/about/">About</a>
      <a href="https://github.com/scischema">GitHub</a>
    </nav>
  </header>

  <main class="schema-page">
    <p class="schema-breadcrumb">
      <a href="/schemas/">Schemas</a> ›
      {escape(domain_name)} ›
      {escape(process_name)}
    </p>

    <section class="schema-hero">
      <h1>{escape(process_name)}</h1>
      <p class="schema-subtitle">A SciSchema.org Process Schema</p>

      <p class="schema-meta">
        Domain: {escape(domain_name)}<br>
        Schema: {escape(schema_title)}
      </p>

      <p class="schema-description">
        {escape(description)}
      </p>
    </section>

    <section class="schema-section">
      <h2>Properties from {escape(process_name)}</h2>

      <p class="schema-description">
        The table below lists the top-level properties of this master schema.
        Each property may contain more detailed nested fields in the JSON Schema representation.
      </p>

      <table class="schema-table">
        <thead>
          <tr>
            <th>Property</th>
            <th>Expected Type</th>
            <th>Description</th>
            <th>Required</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>

      <div class="schema-download">
        <h2>Machine-readable schema representations</h2>

        <p>
          This schema is available in two machine-readable representations:
          as an ORKG template, which can be exported as SHACL, and as a JSON Schema
          document for download and reuse.
        </p>

        <ul>
{orkg_html(orkg_url)}
          <li>
            <a href="master-schema.json">Download master-schema.json</a>
            <span> — JSON Schema representation</span>
          </li>
        </ul>
      </div>
    </section>
  </main>

  <footer>
    <a href="/terms/">Terms and conditions</a>
    <span>•</span>
    <span>SciSchema</span>
    <span>•</span>
    <span>V0.1.0</span>
    <span>|</span>
    <span>2026-06-04</span>
  </footer>
</body>
</html>
"""


def generate_schema_index(metadata: list[dict]) -> str:
    domains: dict[str, dict] = {}

    for item in metadata:
        process_name = item["process_name"].strip()
        domain_slug = item["domain_slug"].strip()
        domain_name = item["domain_name"].strip()
        slug = item["slug"].strip() or slugify(process_name)

        if not process_name or not domain_slug or not domain_name:
            continue

        if domain_slug not in domains:
            domains[domain_slug] = {
                "name": domain_name,
                "schemas": []
            }

        schema_url = f"/schemas/{domain_slug}/{slug}/"

        if not any(schema["url"] == schema_url for schema in domains[domain_slug]["schemas"]):
            domains[domain_slug]["schemas"].append({
                "name": process_name,
                "url": schema_url
            })

    domain_sections = []

    for domain_slug, domain in domains.items():
        items = "\n".join(
            f'      <li><a href="{escape(schema["url"])}">{escape(schema["name"])}</a></li>'
            for schema in domain["schemas"]
        )

        domain_sections.append(f"""    <h2 id="{escape(domain_slug)}">{escape(domain["name"])}</h2>
    <ul>
{items}
    </ul>""")

    sections_html = "\n\n".join(domain_sections)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SciSchema — Scientific Process Schemas</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="icon" type="image/png" href="/assets/logo.png">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header>
    <a class="logo" href="/">
      <img src="/assets/logo.png" alt="SciSchema Logo">
      <span>SciSchema</span>
    </a>
    <nav>
      <a href="/docs/">Docs</a>
      <a href="/schemas/">Schemas</a>
      <a href="/about/">About</a>
      <a href="https://github.com/scischema">GitHub</a>
    </nav>
  </header>

  <main>
    <h1>Schemas</h1>

    <h2>Organization of SciSchemas</h2>

    <p>
      SciSchema schemas describe scientific process types, each associated with a set
      of structured properties. The schemas are organized by scientific domain.
    </p>

    <p>
      Browse the current schema collection below.
    </p>

{sections_html}
  </main>

  <footer>
    <a href="/terms/">Terms and conditions</a>
    <span>•</span>
    <span>SciSchema</span>
    <span>•</span>
    <span>V0.1.0</span>
    <span>|</span>
    <span>2026-06-04</span>
  </footer>
</body>
</html>
"""


def write_schema_index(metadata: list[dict]) -> None:
    index_path = TARGET_DIR / "index.html"
    html = generate_schema_index(metadata)
    index_path.write_text(html, encoding="utf-8")
    print(f"UPDATED: {index_path}")


def main() -> None:
    for path in [SOURCE_DIR, METADATA_FILE, TARGET_DIR]:
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")

    metadata = load_metadata()

    for item in metadata:
        filename = item["filename"].strip()
        process_name = item["process_name"].strip()
        domain_slug = item["domain_slug"].strip()
        domain_name = item["domain_name"].strip()
        slug = item["slug"].strip() or slugify(process_name)
        description = item["description"].strip()
        orkg_url = item.get("orkg_url", "").strip()

        source_json = SOURCE_DIR / filename
        if not source_json.exists():
            print(f"WARNING: Missing JSON file: {source_json}")
            continue

        out_dir = TARGET_DIR / domain_slug / slug
        index_path = out_dir / "index.html"
        json_path = out_dir / "master-schema.json"

        if SKIP_EXISTING and index_path.exists():
            print(f"SKIPPED existing page: {index_path}")
            continue

        try:
            with source_json.open("r", encoding="utf-8") as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON file: {source_json}")
            print(f"Reason: {e}")
            continue

        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_json, json_path)

        html = generate_html(
            process_name=process_name,
            domain_name=domain_name,
            schema_title=schema.get("title", process_name),
            description=description or schema.get("description", ""),
            rows=table_rows(schema),
            orkg_url=orkg_url,
        )

        index_path.write_text(html, encoding="utf-8")
        print(f"CREATED: {index_path}")

    write_schema_index(metadata)


if __name__ == "__main__":
    main()
