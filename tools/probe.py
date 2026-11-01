#!/usr/bin/env python3
"""Read a printer and report the knobs a debloatprint profile cares about.

This tool does not change the printer. Applying a profile is a separate,
reviewed step. See PROMPT.md.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guard import Refused, assert_allowed

TIMEOUT = 8
PROFILE_ROOT = Path(__file__).resolve().parents[1] / "profiles"
# Names a profile must keep in never_touch. guard.FLOOR still blocks these,
# plus mdns and infrastructure-wifi, even when a profile omits them.
REQUIRED_NEVER_TOUCH = ("wifi0", "ipv4", "dhcp", "ipp", "airprint", "bonjour")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(element: ET.Element, name: str) -> str | None:
    for child in element.iter():
        if _local(child.tag) == name and child.text and child.text.strip():
            return child.text.strip()
    return None


def parse_product_config(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    return {
        "power_save": _text(root, "PowerSave"),
        "power_save_timeout": _text(root, "PowerSaveTimeout"),
        "shutdown_delay": _text(root, "ShutDownDelay"),
        "friendly_name": _text(root, "FriendlyName"),
    }


def parse_netapps(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    return {
        "direct_print": _text(root, "DirectPrint"),
        "ipp": _text(root, "IPPSupport"),
        "mdns": _text(root, "MDNSSupport"),
    }


def _decode_ssid(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return bytes.fromhex(value).decode()
    except ValueError:
        return value


def parse_adapters(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    adapters = []
    for node in root.iter():
        if _local(node.tag) != "Adapter":
            continue
        name = _text(node, "Name")
        if not name:
            continue
        adapters.append(
            {
                "name": name,
                "power": _text(node, "Power"),
                "mode": _text(node, "CommunicationMode"),
                "connected": _text(node, "IsConnected"),
                "ssid": _decode_ssid(_text(node, "SSID")),
            }
        )
    return adapters


def parse_cloud(payload: str) -> dict:
    data = json.loads(payload)
    registration = data.get("registration") or {}
    return {
        "registered": bool(registration),
        "registration_state": registration.get("registrationState"),
        "signaling": (registration.get("signalingConnectionState")),
        "cloud_services_enabled": data.get("cloudServicesEnabled"),
    }


def parse_subscriptions(payload: str) -> dict:
    data = json.loads(payload)
    hosts: dict[str, list[str]] = {}
    for item in data.get("subscriptions") or []:
        host = urlparse(item.get("callbackUri") or "").netloc or "?"
        hosts.setdefault(host, []).append(item.get("eventCategory") or "?")
    return {"count": sum(len(v) for v in hosts.values()), "hosts": hosts}


def _fetch(url: str) -> str:
    context = ssl._create_unverified_context()
    request = urllib.request.Request(url, headers={"Accept": "*/*"})
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def read_printer(host: str) -> dict:
    base = host if host.startswith("http") else f"http://{host}"
    secure = "https://" + urlparse(base).netloc if base.startswith("http") else f"https://{host}"
    if base.startswith("http://"):
        secure = "https://" + base[len("http://") :]
    product = parse_product_config(_fetch(f"{base}/DevMgmt/ProductConfigDyn.xml"))
    netapps = parse_netapps(_fetch(f"{secure}/DevMgmt/NetAppsDyn.xml"))
    adapters = parse_adapters(_fetch(f"{base}/IoMgmt/Adapters"))
    cloud = parse_cloud(_fetch(f"{secure}/cdm/cloudServices/v1/avatarRegistration"))
    subscriptions = parse_subscriptions(_fetch(f"{secure}/cdm/eventing/v1/subscriptions"))
    return {
        "product": product,
        "netapps": netapps,
        "adapters": adapters,
        "cloud": cloud,
        "subscriptions": subscriptions,
    }


def format_report(host: str, state: dict) -> str:
    product = state["product"]
    netapps = state["netapps"]
    lines = [
        f"host: {host}",
        f"name: {product.get('friendly_name') or '?'}",
        f"power save: {product.get('power_save') or '?'} after {product.get('power_save_timeout') or '?'}",
        f"auto off: {product.get('shutdown_delay') or '?'}",
        f"ipp: {netapps.get('ipp') or '?'}",
        f"bonjour: {netapps.get('mdns') or '?'}",
        f"wi-fi direct: {netapps.get('direct_print') or '?'}",
    ]
    for adapter in state["adapters"]:
        ssid = adapter.get("ssid") or ""
        lines.append(
            f"radio {adapter['name']}: power={adapter.get('power')} "
            f"mode={adapter.get('mode')} connected={adapter.get('connected')} {ssid}".rstrip()
        )
    cloud = state["cloud"]
    lines.append(
        "hp cloud: "
        + (
            f"registered ({cloud.get('registration_state')}, signaling {cloud.get('signaling')})"
            if cloud.get("registered")
            else "not registered"
        )
        + f", services flag {cloud.get('cloud_services_enabled')}"
    )
    subs = state["subscriptions"]
    if subs["count"] == 0:
        lines.append("telemetry subscriptions: 0")
    else:
        for target, categories in subs["hosts"].items():
            lines.append(
                f"telemetry subscriptions: {subs['count']} toward {target} ({', '.join(categories)})"
            )
    return "\n".join(lines)


def profile_paths(root: Path | None = None) -> list[Path]:
    base = Path(root) if root is not None else PROFILE_ROOT
    if not base.is_dir():
        return []
    return sorted(path for path in base.glob("*/profile.json") if path.is_file())


def _never_touch(data: dict) -> list[str]:
    names = data.get("never_touch")
    if not isinstance(names, list):
        return []
    return [str(name).strip().lower() for name in names if str(name).strip()]


def collected_never_touch(root: Path | None = None) -> list[str]:
    """Never-touch names from every profile. Unreadable files are skipped."""
    names: list[str] = []
    for path in profile_paths(root):
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            names.extend(_never_touch(data))
    return names


def verify_profile(path: Path) -> list[str]:
    """Problems in one profile. An empty list means it is safe to follow."""
    folder = path.parent.name
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        return [f"{folder}: invalid JSON ({error.msg})"]
    except OSError as error:
        return [f"{folder}: {error.strerror}"]
    if not isinstance(data, dict):
        return [f"{folder}: profile must be a JSON object"]

    problems: list[str] = []
    if data.get("id") != folder:
        problems.append(f"{folder}: id is {data.get('id')!r}, folder name is {folder!r}")

    models = data.get("models")
    if (
        not isinstance(models, list)
        or not models
        or not all(isinstance(model, str) and model.strip() for model in models)
    ):
        problems.append(f"{folder}: models must be a non-empty list of names")

    if not isinstance(data.get("never_touch"), list):
        problems.append(f"{folder}: never_touch must be a list")
        blocked: list[str] = []
    else:
        blocked = _never_touch(data)
        missing = [name for name in REQUIRED_NEVER_TOUCH if name not in blocked]
        if missing:
            problems.append(f"{folder}: never_touch drops {', '.join(missing)}")

    changes = data.get("changes")
    if not isinstance(changes, list) or not changes:
        problems.append(f"{folder}: changes must list at least one change")
        return problems

    seen: set[str] = set()
    for change in changes:
        if not isinstance(change, dict):
            problems.append(f"{folder}: a change is not an object")
            continue
        change_id = str(change.get("id") or "").strip()
        label = change_id or "(no id)"
        if not change_id:
            problems.append(f"{folder}: a change has no id")
        elif change_id.lower() in seen:
            problems.append(f"{folder}: duplicate change {change_id}")
        else:
            seen.add(change_id.lower())
            try:
                assert_allowed(change_id, blocked)
            except Refused:
                problems.append(f"{folder}: {change_id} is on the never-touch list")
        for field in ("why", "risk", "verify", "restore"):
            if not str(change.get(field) or "").strip():
                problems.append(f"{folder}: {label} has no {field}")
        request = change.get("request")
        if (
            not isinstance(request, dict)
            or not str(request.get("method") or "").strip()
            or not str(request.get("url") or "").strip()
        ):
            problems.append(f"{folder}: {label} has no request method and url")
    return problems


def verify_profiles(root: Path | None = None) -> list[str]:
    paths = profile_paths(root)
    if not paths:
        return ["no profiles found"]
    problems: list[str] = []
    for path in paths:
        problems.extend(verify_profile(path))
    return problems


def format_profile_report(root: Path | None = None) -> str:
    lines = []
    for path in profile_paths(root):
        data = json.loads(path.read_text())
        count = len(data.get("changes") or [])
        lines.append(f"{data.get('id')}: {count} changes, never-touch ok")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read printer debloat state. Changes nothing.")
    parser.add_argument("--host", help="printer IP or host name")
    parser.add_argument(
        "--check",
        metavar="CHANGE",
        help="exit 2 when CHANGE is on the floor or on any profile never-touch list",
    )
    parser.add_argument(
        "--profiles",
        action="store_true",
        help="check every profiles/*/profile.json; does not contact a printer",
    )
    args = parser.parse_args(argv)
    if args.profiles and (args.check or args.host):
        parser.error("pass --profiles on its own")
    if args.profiles:
        problems = verify_profiles()
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        print(format_profile_report())
        return 0
    if args.check:
        try:
            assert_allowed(args.check, collected_never_touch())
        except Refused as refusal:
            print(refusal, file=sys.stderr)
            return 2
        print(f"{args.check} is not on the never-touch list")
        return 0
    if not args.host:
        parser.error("pass --host, --check CHANGE, or --profiles")
    try:
        state = read_printer(args.host)
    except urllib.error.URLError as error:
        print(f"{args.host} did not answer ({error.reason})", file=sys.stderr)
        return 1
    print(format_report(args.host, state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
