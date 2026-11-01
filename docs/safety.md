# Safety

These rules came from breaking, and then recovering, one HP LaserJet M110w.

- Read first. `tools/probe.py` is the only tool that talks to a printer, and it only sends GET.
- One write, then a check that printing still works. A later change is what makes a failure hard to undo.
- The home radio is `Wifi1`'s neighbour, `Wifi0`. Turning off `Wifi1` disables Wi-Fi Direct. Turning off `Wifi0` removes the printer from the network.
- The advanced settings form disables every checkbox missing from the POST. Copy the keep-list. Do not send a "small" form with only the box you want to clear.
- Do not POST a body to `/cdm/eventing/v1/subscriptions`. On the reference printer an empty POST left HTTP and IPP unanswered for several minutes. The printer answered ping the whole time, so it looked alive and was not.
- Do not delete the telemetry subscription URLs. They return 404. The registration DELETE is the call that actually signs the printer out. The seven subscriptions can remain, pointed at `telemetry.pod6.prod.avatar.ext.hp.com`, with no session behind them.
- Do not factory-reset. The printer warns that this clears the network settings.
- Secure AirPrint (`_ipps._tcp`, TLS on port 631) can fail the handshake on this firmware. Turning the advertisement off is a printing fix. Turning IPP off is not.
- Auto-off `never` keeps the printer asleep after an hour, but a network job can wake it. It does not keep the fuser hot. That is `PowerSave off`, which this profile does not set.
