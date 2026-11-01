# Farlo con un'AI

Grok, Claude, Codex o un altro assistente di codice può applicare un profilo già presente nel repo, oppure studiare una stampante che non c'è e aggiungerla. L'assistente deve poter eseguire comandi su un computer nella stessa rete della stampante. Una chat senza terminale può spiegare i passi. Non vede la stampante.

Le frasi da incollare sono in [PROMPT.md](../PROMPT.md). Questa pagina dice come usarle.

## Prima di iniziare

1. Clona questo repo sul computer che parlerà con la stampante.
2. Metti quel computer sulla stessa Wi-Fi della stampante. Una rete ospite che nasconde i dispositivi non funziona.
3. Apri l'assistente in quel clone. In Grok è una sessione il cui spazio di lavoro è il repo. Vale lo stesso per qualunque assistente che lì possa eseguire `python3`.
4. Leggi [safety.md](safety.md) e [l'avviso su garanzia e responsabilità](../DISCLAIMER.it.md). Confermi tu ogni modifica. L'assistente non riceve un sì generico. Il progetto non è affiliato al produttore, e una modifica può incidere su garanzia e assistenza.

Il PIN, quando un profilo lo chiede, è sull'etichetta dentro la stampante. Dallo all'assistente nella sessione, se un passo lo richiede. Non va messo in un file.

## Una stampante già censita

Guarda in `profiles/`. Oggi c'è la HP LaserJet M110w (famiglia M109-M112). Se il tuo modello è uno di quei nomi, usa il prompt di applicazione.

1. Incolla il blocco "Apply a listed printer" da [PROMPT.md](../PROMPT.md).
2. Aggiungi una riga con quello che sai, per esempio modello e indirizzo: `The printer is an HP LaserJet M110w at 192.168.1.50.`
3. L'assistente legge la stampante e mostra il rapporto. Non cambia ancora nulla.
4. Indica la cartella che corrisponde e le modifiche di quel profilo. Rispondi con quelle che vuoi, oppure di no.
5. Ne applica una, controlla che la stampa funzioni ancora, poi si ferma o chiede prima della successiva. Se un controllo fallisce, si ferma.

`tools/probe.py` conosce solo le pagine HP usate dal profilo della M110w. Se non riesce a leggere la stampante, l'assistente si ferma. Non indovina gli indirizzi di un altro modello.

## Una stampante nuova

Usa il blocco "Add a new printer" da [PROMPT.md](../PROMPT.md). È così che nasce una cartella nuova in `profiles/`.

1. Incolla quel blocco e aggiungi il modello, oppure di' che non lo conosci.
2. L'assistente all'inizio legge soltanto: il probe se è un'HP di questo tipo, altrimenti la pagina web della stampante. Annota modello, stringa del firmware e i menu di cloud, Wi-Fi Direct, sonno, IPv6 e stampa cifrata.
3. Propone un piano e aspetta. Una richiesta copiata dalla M110w, o da una Brother su una Epson, non è un piano.
4. Tu indichi l'unica modifica che può provare.
5. Invia quella richiesta, conserva il codice di stato e controlla che la stampante sia ancora sulla Wi-Fi di casa e accetti un lavoro locale.
6. In `profiles/<model-id>/profile.json` finisce solo una richiesta davvero inviata, insieme a un `README.md` con la stessa forma del profilo della M110w. Un ripristino non eseguito si segna come non provato.
7. Esegue `python3 tools/probe.py --profiles` e `python3 -m unittest discover -s tests`. Quei controlli passano ogni cartella in `profiles/` e rifiutano una modifica che spegnerebbe Wi-Fi di casa, IPv4, DHCP, IPP, AirPrint o Bonjour.

Quando quella cartella c'è, chi ha lo stesso modello usa il prompt di applicazione, senza rifare la scoperta.

## Cosa decidi ancora tu

L'assistente non pubblica il repo, non fa il ripristino di fabbrica e non salva il PIN. Spegnere del tutto il risparmio energia, lasciando il fusore caldo, è un sì a parte. Non fa parte del profilo della M110w.
