# IPK projekt 1

## Autor: Adam Múdry (xmudry01)

### Spustenie

Pre spustenie servera na základnom 5353 porte, v termináli v tomto priečinku napíšte: ```make run```

Pre spustenie servera na používateľom špecifikovanom porte, v termináli v tomto priečinku napíšte ```make run PORT=x```, kde "x" je číslo portu

### Technológia

Na vytvorenie servera som použil Python 3 a knižnice: http.server, socket, socketserver, sys, re, cgi

### Fukcionalita

Server na požiadavky reaguje HTTP odpoveďovými kódmi:

- 200 pre správnu požiadavku a jej vyriešenie
- 400 pre zlé vstupné URL, zlé požiadavky, zlý formát vstupu
- 404 pre správnu požiadavku, no nevyriešenú
- 405 pre nepodporovanú operáciu (všetky okrem GET a POST)
- 500 pre neštandarné prípady chýb

Pri vyriešenej požiadavke server odpovedá aj výstupom na STDIN

Príklad GET:

- Vstup: ```curl "localhost:5353/resolve?name=www.fit.vutbr.cz&type=A"```
- Výstup: ```www.fit.vutbr.cz:A=147.229.9.23```

Príklad POST:

- Vstup: ```curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query```
- Výstup:

```plain
www.fit.vutbr.cz:A
www.google.com:A
www.seznam.cz:A
147.229.14.131:PTR
ihned.cz:A
```
