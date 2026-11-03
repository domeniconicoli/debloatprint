# Brother HL-L2350DW: measured, no profile

One unit, main firmware 1.71, measured in November 2026. No setting on the printer was changed. The only jobs sent were test pages: one from a Mac and two from an iPhone. This is a record of what was looked at, so the next person does not repeat it. It is not a profile and it does not say the printer is safe to change.

## Result

No defect was measured, so there is no `profiles/` folder for this model. An iPhone page took 10 to 12 s to start, and sleep added about 2 s. The settings behind the login were not read, so a slower path that a setting could fix is not ruled out.

## What the probe does

`python3 tools/probe.py --host HOST` is HP-only. On this printer it prints `HOST did not answer (Not Found)`: the printer answers 404 to the HP URLs. Follow step 2 of "Add a new printer" in [PROMPT.md](../PROMPT.md): do not retry those URLs, read the printer's own web page.

## What the printer exposes

- **Web page.** Embedded server `debut/1.30`. `/general/status.html` opens without a login, over HTTP and HTTPS. Maintenance Information shows the model and the main firmware version without a login too. Settings are behind a password-only login, and forms are POSTed with a `CSRFToken`. The menus listed before login are Status, Maintenance Information, Lists/Reports, Find Device, Contact & Location, Sleep Time, Auto Power Off, Language, Panel and Replace Toner. The Network tab was never opened.
- **Bonjour.** `_ipp._tcp` (path `ipp/print`, port 631) and `_pdl-datastream._tcp` are advertised. `_ipps._tcp` was not found. The `.local` name resolves to two link-local IPv6 addresses and the IPv4 address.
- **Print formats.** `document-format-supported` lists only `application/octet-stream`, `image/urf` and `image/pwg-raster`. PDF and plain text are not listed. `pwg-raster` is 600 dpi, `sgray_8`.
- **Secure IPP.** A TLS handshake to port 631 fails at once with an unexpected EOF, with both Python `ssl` and `openssl s_client`. HTTPS on port 443 answers.

The M110w had the same broken TLS on port 631, and its iPhone delay came from advertising secure AirPrint. This printer does not advertise `_ipps._tcp`, so an iPhone should not try TLS first. That is a deduction from the advertisement, not something observed on the phone.

## Timings

From a Mac on the same network, to the IPv4 address. One sample each unless stated.

| Test | Time |
|---|---|
| IPP `Get-Printer-Attributes`, printer asleep, first request | 0.34 s |
| IPP `Get-Printer-Attributes`, printer awake | 0.11 s both runs |
| IPP via the `.local` name (address family not recorded) | 0.24 s |
| Status web page | 0.10 s |
| `Print-Job` of one test page, printer asleep | accepted in 0.07 s, job *completed* at 12.3 s |

From an iPhone, one page, stopwatch from tapping Print:

| Printer state | Starts printing | Page done |
|---|---|---|
| Asleep | 12 s | 20 s |
| Awake | 10 s | 18 s |

The Mac and iPhone figures do not measure the same moment. The Mac figure is the IPP `job-state` reaching *completed*, which is not when the sheet leaves the printer. The iPhone figures are a stopwatch on the paper. Any iPhone overhead is somewhere between nothing and about 8 s.

## What was not tested

- Auto Power Off: whether the printer shuts down by itself, and after how long.
- Anything behind the login, including the Network settings and any IPv6 switch.
- A second iPhone sample, and a stopwatch on the Mac page.
- Whether the `.local` request went over IPv6 or IPv4.

## Tips for the next attempt

- The Mac test page has to be raster. On macOS `cupsfilter -m image/pwg-raster` on a PDF stopped with status 2 (`cgpdftoraster`). A PWG raster page written by hand (A4, 600 dpi, `sgray_8`) was accepted by `Print-Job`. macOS also ships `ipptool` with a `print-job-and-wait.test` file, which sends a job and polls it. It was not tried here.
- Poll `job-state` with `Get-Job-Attributes`. The printer's web page can still read *Printing* after the job is *completed*.
- Time the Mac page with a stopwatch on the paper as well, so it compares with the iPhone.
- Find a defect before you write a profile. Without a delay traced to a setting, there is nothing for a request to fix.

Independent of the printer maker. Read [DISCLAIMER.md](../DISCLAIMER.md) before you change any printer.
