# Do it with an AI

Grok, Claude, Codex, or another coding assistant can apply a profile that is already in this repo, or study a printer that is not and add it. The assistant has to run commands on a computer on the same network as the printer. A chat box with no shell can explain the steps. It cannot see the printer.

The words to paste are in [PROMPT.md](../PROMPT.md). This page is how to use them.

## Before you start

1. Clone this repo on the computer that will talk to the printer.
2. Put that computer on the same Wi-Fi as the printer. A guest network that hides devices from each other will not work.
3. Open the assistant in that clone. In Grok, that is a session whose workspace is the repo. The same applies to any other assistant that can run `python3` there.
4. Read [safety.md](safety.md) and [the disclaimer](../DISCLAIMER.md). You confirm each change. The assistant does not get a blanket yes. The project is not affiliated with the printer maker, and a change can affect warranty and support.

The PIN, when a profile needs one, is on a label inside the printer. Tell it to the assistant in the session if a step asks. Do not put it in a file.

## A printer that is already listed

Look in `profiles/`. Today that is the HP LaserJet M110w (the M109-M112 family). If your model is one of those names, use the apply prompt.

1. Paste the "Apply a listed printer" block from [PROMPT.md](../PROMPT.md).
2. Add one line with what you know, for example the model and the address: `The printer is an HP LaserJet M110w at 192.168.1.50.`
3. The assistant reads the printer and shows the report. It does not change anything yet.
4. It names the matching folder and the changes in that profile. Reply with the ones you want, or with no.
5. It applies one change, checks that printing still works, then stops or asks before the next. If a check fails, it stops.

`tools/probe.py` only knows the HP pages used by the M110w profile. If it cannot read the printer, the assistant must stop rather than guess URLs from another model.

## A printer that is not listed

Use the "Add a new printer" block from [PROMPT.md](../PROMPT.md). This is how a new folder gets into `profiles/`.

1. Paste that block and add the model, or say you do not know it.
2. The assistant only reads first: the probe when the printer is an HP of this kind, otherwise the printer's own web page. It writes down the model, the firmware string, and the menus for cloud, Wi-Fi Direct, sleep, IPv6, and secure printing.
3. It proposes a plan and waits. A request copied from the M110w, or from a Brother onto an Epson, is not a plan.
4. You name which single change it may try.
5. It sends that one request, keeps the status code, and checks that the printer is still on the home Wi-Fi and still accepts a local job.
6. Only a request it actually sent is written into `profiles/<model-id>/profile.json`, next to a `README.md` in the same shape as the M110w profile. A restore it did not run is marked untested.
7. It runs `python3 -m unittest discover -s tests`. Those tests refuse a change that would turn off home Wi-Fi, IPv4, DHCP, IPP, AirPrint, or Bonjour.

When that folder exists, the next person with the same model uses the apply prompt instead of discovering it again.

## What you still decide

The assistant does not publish the repo, does not factory-reset the printer, and does not store the PIN. Turning power-save fully off, which keeps the fuser hot, is a separate yes. It is not part of the M110w profile.
