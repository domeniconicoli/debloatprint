# Prompts

Paste one of these to Grok, Claude, Codex, or another assistant that can run commands on a computer on the same network as the printer. The human steps are in [docs/with-an-ai.md](docs/with-an-ai.md).

Answer in the user's language. Do not print the PIN, do not commit it, and do not put it in a profile.

## Apply a listed printer

```text
You are in the debloatprint repo, on a computer that can reach the printer. Apply an existing profile and nothing wider.

1. Find the printer on the local network. Ask before scanning anything outside the user's LAN.
2. Run `python3 tools/probe.py --host HOST` and show the report. Do not write to the printer in this step. If the probe cannot read this brand, stop and say so.
3. Match the model to one folder in `profiles/`. If none matches, stop. Do not invent requests and do not reuse another model's URLs.
4. Show that profile's changes and its never-touch list. Wait for a yes that names which changes to apply.
5. Before each write, run `python3 tools/probe.py --check CHANGE_ID`. Exit code 2 means stop.
6. Apply one change from that profile's `request`. Then run its `verify` check. If verify fails, stop. Do not start the next change.
7. Never turn off home Wi-Fi (`Wifi0`), IPv4, DHCP, IPP, AirPrint, or Bonjour.
8. Never POST to `/cdm/eventing/v1/subscriptions`. Never factory-reset the printer.
9. On an HP advanced-network form, a checkbox you leave out is switched off. Send the profile's full keep-list.
10. The PIN for these HP models is on a label inside the toner door. The username on the LEDM and CDM interfaces is `admin`.
```

## Add a new printer

```text
You are in the debloatprint repo, on a computer that can reach the printer. Document this printer as a new profile. Do not copy requests from another model.

1. Find the printer on the local network. Ask before scanning anything outside the user's LAN.
2. Read only. Run `python3 tools/probe.py --host HOST` when the printer is an HP that speaks LEDM. If the probe fails, do not retry those HP URLs against another brand. Open the printer's own web page and record the model, the firmware string, and which menus exist for cloud, Wi-Fi Direct, sleep, IPv6, and secure printing.
3. Show a plan: what you would turn off, what you will not touch, and the risk of each change. The never-touch floor is home Wi-Fi, IPv4, DHCP, IPP, AirPrint, and Bonjour. Wait for a yes that names which changes to try.
4. Before each write, run `python3 tools/probe.py --check CHANGE_ID`. Exit code 2 means stop, even on a brand the probe cannot read.
5. Try one change. Record the exact request, the status code, and the body you got back. Then check that the printer still answers on the home Wi-Fi and that a local print path still works. If the check fails, stop and write the restore you actually used.
6. A change that was not sent does not go in `profile.json`. Mark any restore you did not run as untested.
7. Write `profiles/<model-id>/profile.json` and `profiles/<model-id>/README.md` in the same shape as `profiles/hp-laserjet-m110w/`. Keep `never_touch`. Run `python3 -m unittest discover -s tests` and fix the profile if a new change id is on the never-touch floor.
8. Never POST an empty body to `/cdm/eventing/v1/subscriptions`. Never factory-reset the printer. Never print or store the PIN.
```
