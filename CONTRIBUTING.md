# Contributing

Add a folder under `profiles/` named after the model you actually changed.

The folder needs:

- `profile.json` with `id`, `models`, `never_touch`, and a `changes` array.
- Every change needs `why`, `risk`, the request you sent, the status you got, how you checked printing afterwards, and how to undo it.
- Mark restore steps you did not run. Do not describe them as tested.
- Keep the floor in `tools/guard.py`. A profile may add protected names. It must not drop home Wi-Fi, IPv4, DHCP, IPP, AirPrint or Bonjour.

Do not send a profile for a model you have not had on the network. A copied request from a different brand is how a printer gets stranded.
