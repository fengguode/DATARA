"""Service-only, private-file PostgreSQL preflight diagnostics CLI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

# Import the isolated package without loading Django application modules.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datara.preflight.canonical import FORMAT, canonical_bytes
from datara.preflight.compare import compare


def load_json(path):
    """Public parser interface; main uses the paired exact-byte evidence helper."""
    return load_json_with_hash(path)[0]


def load_json_with_hash(path):
    """Parse and hash the same single byte read, including any UTF-8 BOM."""
    raw = Path(path).read_bytes()
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def invalid_number(value):
        raise ValueError("UNSUPPORTED_JSON_NUMBER")
    value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs,
                       parse_float=invalid_number, parse_constant=invalid_number)
    canonical_bytes(value)
    return value, hashlib.sha256(raw).hexdigest()


def private_output(path, report):
    target = Path(path).resolve()
    root = Path(__file__).resolve().parents[1]
    if target == root or root in target.parents or not target.parent.is_dir():
        raise ValueError("OUTPUT_REQUIRES_EXISTING_PRIVATE_DIRECTORY_OUTSIDE_REPOSITORY")
    # O_EXCL preserves existing evidence and refuses symlink/overwrite races.
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_bytes(report))
        stream.write(b"\n")


class SanitizedParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's original message may repeat a credential-shaped argument.
        raise ValueError("INVALID_CLI_ARGUMENTS")


def main(argv=None):
    parser = SanitizedParser(description="Read-only diagnostic preflight; incomplete coverage refuses eligibility")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("collect", "compare"):
        sub = commands.add_parser(command)
        sub.add_argument("--manifest", required=True)
        sub.add_argument("--policy", required=True)
        sub.add_argument("--output", required=True)
        sub.add_argument("--connection-service" if command == "collect" else "--inventory", required=True)
    try:
        args = parser.parse_args(argv)
    except ValueError:
        return 3
    try:
        manifest, manifest_hash = load_json_with_hash(args.manifest)
        policy, policy_hash = load_json_with_hash(args.policy)
        input_hashes = {"manifest": manifest_hash, "policy": policy_hash}
        if args.command == "collect":
            from datara.preflight.catalog import collect
            inventory = collect(args.connection_service, manifest, policy)
            report = compare(manifest, inventory, policy)
            report["inventory"] = inventory
        else:
            inventory, inventory_hash = load_json_with_hash(args.inventory)
            input_hashes["inventory"] = inventory_hash
            report = compare(manifest, inventory, policy)
        report["input_file_hashes"] = input_hashes
        source_root = Path(__file__).resolve().parents[1]
        source_files = (
            "scripts/syncdb_preflight.py", "datara/preflight/__init__.py",
            "datara/preflight/catalog.py", "datara/preflight/canonical.py",
            "datara/preflight/compare.py", "datara/preflight/data_checks.py",
        )
        source_manifest = {relative: hashlib.sha256((source_root / relative).read_bytes()).hexdigest()
                           for relative in source_files}
        report["source_file_hashes"] = source_manifest
        report["implementation_source_hash"] = hashlib.sha256(canonical_bytes(source_manifest)).hexdigest()
        private_output(args.output, report)
        return report["exit_code"]
    except Exception:
        # No exception text, path, connection material or server DETAIL is emitted.
        try:
            private_output(args.output, {"format": FORMAT, "exit_code": 3, "eligible": False,
                                        "reason_codes": ["UNKNOWN_INPUT_COLLECTION_OR_OUTPUT_ERROR"]})
        except Exception:
            pass
        return 3


if __name__ == "__main__":
    raise SystemExit(main())


