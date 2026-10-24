from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_names(path: Path) -> list[str]:
    names: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = NAME_RE.match(line)
        if match:
            names.append(normalize(match.group(1)))
    return names


def installed_distributions() -> dict[str, md.Distribution]:
    result: dict[str, md.Distribution] = {}
    for dist in md.distributions():
        name = dist.metadata.get("Name")
        if name:
            result[normalize(name)] = dist
    return result


def dependency_name(requirement: str) -> str | None:
    match = NAME_RE.match(requirement)
    return normalize(match.group(1)) if match else None


def runtime_closure(roots: list[str], installed: dict[str, md.Distribution]) -> list[md.Distribution]:
    pending = list(roots)
    seen: set[str] = set()
    selected: list[md.Distribution] = []
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        dist = installed.get(current)
        if dist is None:
            raise RuntimeError(f"Runtime dependency is not installed: {current}")
        selected.append(dist)
        for requirement in dist.requires or []:
            dep = dependency_name(requirement)
            if dep and dep in installed and dep not in seen:
                pending.append(dep)
    return sorted(selected, key=lambda d: normalize(d.metadata.get("Name", "")))


def license_text(dist: md.Distribution) -> str:
    metadata = dist.metadata
    value = metadata.get("License-Expression") or metadata.get("License")
    if value and value.strip():
        return " ".join(value.split())
    classifiers = metadata.get_all("Classifier") or []
    license_classifiers = [c.removeprefix("License :: ").strip() for c in classifiers if c.startswith("License :: ")]
    return "; ".join(license_classifiers) if license_classifiers else "NOASSERTION"


def homepage(dist: md.Distribution) -> str:
    metadata = dist.metadata
    if metadata.get("Home-page"):
        return metadata["Home-page"].strip()
    for value in metadata.get_all("Project-URL") or []:
        if "," in value:
            label, url = value.split(",", 1)
            if label.strip().lower() in {"homepage", "home", "source", "repository"}:
                return url.strip()
    return "NOASSERTION"


def spdx_id(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]+", "-", name).strip("-") or "package"
    return f"SPDXRef-Package-{safe}"


def build_spdx(dists: list[md.Distribution], created: str) -> dict:
    packages = []
    relationships = []
    for dist in dists:
        name = dist.metadata.get("Name") or "unknown"
        pid = spdx_id(f"{name}-{dist.version}")
        packages.append(
            {
                "SPDXID": pid,
                "name": name,
                "versionInfo": dist.version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "licenseComments": f"Installed package metadata reports: {license_text(dist)}",
                "homepage": homepage(dist),
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": pid,
            }
        )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "Workflow Automation Hub runtime dependency inventory",
        "documentNamespace": f"https://local.invalid/workflow-automation-hub/spdx/{uuid.uuid4()}",
        "creationInfo": {"created": created, "creators": ["Tool: generate_dependency_evidence.py"]},
        "packages": packages,
        "relationships": relationships,
    }


def build_notice(dists: list[md.Distribution], created: str) -> str:
    lines = [
        "Workflow Automation Hub — Third-Party Dependency Review Inventory",
        f"Generated: {created}",
        "",
        "This inventory is generated from the installed runtime dependency closure.",
        "It does not replace the product LICENSE, legal review, or inclusion of any license/NOTICE text required by the upstream package.",
        "A release operator must review the metadata below against the exact packaged artifact before sales release.",
        "",
    ]
    for dist in dists:
        name = dist.metadata.get("Name") or "unknown"
        lines.extend(
            [
                f"{name} {dist.version}",
                f"  License metadata: {license_text(dist)}",
                f"  Homepage/source: {homepage(dist)}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", default="requirements.txt")
    parser.add_argument("--out-dir", default="dist")
    args = parser.parse_args()

    requirements = Path(args.requirements)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    roots = requirement_names(requirements)
    installed = installed_distributions()
    dists = runtime_closure(roots, installed)
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    (out_dir / "SBOM.spdx.json").write_text(
        json.dumps(build_spdx(dists, created), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "THIRD_PARTY_NOTICES_REVIEW.txt").write_text(build_notice(dists, created), encoding="utf-8")
    print(f"Dependency evidence generated for {len(dists)} runtime package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
