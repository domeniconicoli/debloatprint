# HP LaserJet M110w

Family M109-M112. The embedded site calls itself that, and AirPrint advertises `HP LaserJet M109-M112`.

The printer's own Bonjour host looks like `NPI000000.local`. After IPv6 is turned off, that name resolves to the IPv4 address only. "Show printer web page" opening that host is the right page.

## What was slow

From a Mac, IPP to the IPv4 address answered in under a second and a page finished in about fifteen seconds. From an iPhone the same printer took a minute or two.

The phone looks up the Bonjour name, which had two IPv6 addresses plus IPv4, and it tries secure AirPrint first because the printer advertises TLS 1.2. The TLS handshake on port 631 failed. The printer also sleeps after an hour and, after four hours, used to shut down so that Wi-Fi could not wake it.

## Order

Apply in this order, one at a time, from [profile.json](profile.json):

1. `wifi-direct`
2. `hp-cloud`
3. `auto-off`
4. `ipv6-and-ipps`

Details and the requests that returned a success status are in the JSON. Read [docs/safety.md](../../docs/safety.md) before the fourth one. That POST turns off every checkbox it does not mention.

## Left as they were

- Power save stays on, at one hour.
- Syslog stays enabled with no server address, so it has nowhere to send.
- The cloud services flag can still read `true` after the registration is gone.
- Seven telemetry subscriptions toward HP can remain. The printer does not let an admin delete them.
