# debloatprint

Make a printer print, and strip the rest.

Same idea as the Android TV debloat repos: one folder per model, a list of what to turn off, a list of what must stay, and a way back. An assistant on the same network can follow [PROMPT.md](PROMPT.md). You can also follow a profile by hand.

Printers do not have one shared switch the way a TV has `pm disable-user`. HP, Brother and Epson expose different pages. A wrong write can drop the printer off Wi-Fi. Profiles are not a universal script.

This project is not affiliated with any printer maker. Using a profile can affect the manufacturer's warranty and support. Read [DISCLAIMER.md](DISCLAIMER.md) before you change a printer.

## What a profile is allowed to change

Sleep, cloud registration, Wi-Fi Direct, IPv6, and a broken secure-AirPrint advertisement. The first profile is the HP LaserJet M110w (M109-M112 family), taken from a printer that was slow from an iPhone and signed in to HP's cloud.

## What never gets turned off

Home Wi-Fi, IPv4, DHCP, IPP, AirPrint and Bonjour. `tools/guard.py` refuses those names even if a profile forgets them. `tools/probe.py` only reads.

## Try the read-only probe

```bash
python3 tools/probe.py --host 192.168.1.50
python3 tools/probe.py --profiles     # every folder under profiles/
python3 tools/probe.py --check ipp    # exits 2; also refuses a name any profile lists
python3 -m unittest discover -s tests
```

The probe prints power-save, auto-off, Wi-Fi Direct, the cloud registration and any telemetry subscriptions. It does not ask for the PIN and it does not write.

## Apply a profile

Read `profiles/<model>/profile.json` and [docs/safety.md](docs/safety.md). Do one change, then check the `verify` line before the next change. The advanced network form treats a missing checkbox as off, so the keep-list in the M110w profile is the whole request, not a suggestion.

With Grok or another assistant that can run commands on the same network, paste the apply prompt. The steps are in [docs/with-an-ai.md](docs/with-an-ai.md).

## Printers measured without a profile

[Brother HL-L2350DW](docs/brother-hl-l2350dw.md): timings, what it exposes, and why no profile was written.

## Add a printer

Copy `profiles/hp-laserjet-m110w/` and replace every request with one you have run. A profile that was not tried on that model does not belong here. See [CONTRIBUTING.md](CONTRIBUTING.md).

An assistant can do that discovery for you. Paste the "Add a new printer" prompt in [PROMPT.md](PROMPT.md) and follow [docs/with-an-ai.md](docs/with-an-ai.md). It may write a profile only from requests it actually sent.
