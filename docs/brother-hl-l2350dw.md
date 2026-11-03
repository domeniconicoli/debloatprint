# Brother HL-L2350DW: measured, no profile

One unit, measured in November 2026. Nothing was written to the printer. The only job sent was a single test page. This is a record of what was looked at, so the next person does not repeat it. It is not a profile and it does not say the printer is safe to change.

## Result

No defect was found that a printer setting could remove, so there is no `profiles/` folder for this model. An iPhone took about 8 seconds longer than a test page sent from a Mac. The cause of that gap is not known.

## What the probe does

`python3 tools/probe.py --host HOST` is HP-only. On this printer it prints `did not answer (Not Found)`. That is the "probe cannot read this brand" case in [PROMPT.md](../PROMPT.md): stop, and do not try the HP URLs here.

## What the printer exposes

- **Web page.** Embedded server `debut/1.30`. `/general/status.html` opens without a login, over HTTP and HTTPS. Settings are behind a password-only login, and forms are POSTed with a `CSRFToken`. The menus listed before login are Status, Maintenance Information, Lists/Reports, Find Device, Contact & Location, Sleep Time, Auto Power Off, Language, Panel and Replace Toner. The Network tab was never opened. Firmware was not read.
- **Bonjour.** `_ipp._tcp` (path `ipp/print`, port 631) and `_pdl-datastream._tcp` are advertised. `_ipps._tcp` was not found. The `.local` name resolves to two link-local IPv6 addresses and the IPv4 address.
- **Print formats.** Only `application/octet-stream`, `image/urf` and `image/pwg-raster`. Plain text and PDF are not accepted directly. `pwg-raster` is 600 dpi, `sgray_8`.
- **Secure IPP.** A TLS handshake to port 631 fails at once with an unexpected EOF, with both Python `ssl` and `openssl s_client`. HTTPS on port 443 answers.

## Timings

From a Mac on the same Wi-Fi, to the IPv4 address. One sample each unless stated.

| Test | Time |
|---|---|
| IPP `Get-Printer-Attributes`, printer asleep, first request | 0.34 s |
| IPP `Get-Printer-Attributes`, printer awake (2 runs) | 0.11 s |
| IPP via the `.local` name | 0.24 s |
| Status web page | 0.10 s |
| `Print-Job` of one test page, printer asleep | accepted in 0.07 s, job completed at 12.3 s |

From an iPhone, one page, stopwatch from tapping Print:

| Printer state | Starts printing | Page done |
|---|---|---|
| Asleep | 12 s | 20 s |
| Awake | 10 s | 18 s |

Sleep costs about 2 s. The iPhone is about 8 s behind the Mac job (12.3 s against 20 s). The Mac figure is the IPP `job-state` reaching *completed*, which is not the moment the sheet leaves the printer.

## What was not tested

- Auto Power Off: whether the printer shuts down by itself, and after how long.
- Anything behind the login, including the Network settings and any IPv6 switch.
- A second sample, or a print from the iPhone with IPv6 or Bonjour changed.
- Which part of the 8 s is iOS, Bonjour, or the printer.

## Tips for the next attempt

- The Mac test page has to be raster. On macOS `cupsfilter -m image/pwg-raster` on a PDF stopped with status 2 (`cgpdftoraster`). A PWG raster page written by hand (A4, 600 dpi, `sgray_8`) was accepted by `Print-Job`.
- Poll `job-state` with `Get-Job-Attributes`. The printer's web page can still read *Printing* after the job is *completed*.
- Before a profile is worth writing, find a defect first. Without a measured delay or a shutdown problem, there is nothing for a request to fix.

Independent of the printer maker. Read [DISCLAIMER.md](../DISCLAIMER.md) before you change any printer.
