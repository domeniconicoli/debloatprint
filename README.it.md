# debloatprint

Far stampare la stampante, e togliere il resto.

È lo stesso schema dei repo di debloat per le Android TV: una cartella per modello, cosa spegnere, cosa non toccare, e come tornare indietro. Un assistente sulla stessa rete può seguire [PROMPT.md](PROMPT.md). Si può anche eseguire un profilo a mano.

Le stampanti non hanno un comando unico. HP, Brother ed Epson rispondono su pagine diverse. Una scrittura sbagliata le stacca dal Wi-Fi. Un profilo non è uno script universale.

## Cosa si può cambiare

Sonno, registrazione cloud, Wi-Fi Direct, IPv6, e l'annuncio di AirPrint cifrato quando il canale TLS non funziona. Il primo profilo è la HP LaserJet M110w (famiglia M109-M112).

## Cosa non si spegne

Wi-Fi di casa, IPv4, DHCP, IPP, AirPrint e Bonjour. `tools/guard.py` rifiuta questi nomi anche se un profilo se li dimentica. `tools/probe.py` legge soltanto.

## Prova

```bash
python3 tools/probe.py --host 192.168.1.50
python3 tools/probe.py --check ipp    # esce con codice 2
python3 -m unittest discover -s tests
```

Poi leggi `profiles/<modello>/profile.json` e [docs/safety.md](docs/safety.md). Una modifica alla volta, e si controlla `verify` prima della successiva.
