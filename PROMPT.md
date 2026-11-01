# Prompt

You are on a computer that can reach the printer. The repo is debloatprint. Do this and nothing wider.

1. Find the printer on the local network. Ask before scanning anything outside the user's LAN.
2. Run `python3 tools/probe.py --host HOST` and show the report. Do not write to the printer in this step.
3. Match the model to one folder in `profiles/`. If none matches, stop and say so. Do not invent requests.
4. Show the profile's changes and the never-touch list. Wait for a yes that names which changes to apply.
5. Before each write, run `python3 tools/probe.py --check CHANGE_ID`. Exit code 2 means stop.
6. Apply one change from that profile's `request`. Then run the `verify` check. If verify fails, stop. Do not start the next change.
7. Never turn off home Wi-Fi (`Wifi0`), IPv4, DHCP, IPP, AirPrint or Bonjour.
8. Never POST to `/cdm/eventing/v1/subscriptions`. Never factory-reset the printer.
9. On an HP advanced-network form, a checkbox you leave out is switched off. Send the profile's full keep-list.
10. Do not print the PIN, do not commit it, and do not put it in a profile.

The PIN for these HP models is on a label inside the toner door. The username on the LEDM and CDM interfaces is `admin`.
