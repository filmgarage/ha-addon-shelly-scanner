# Shelly Device Scanner Add-on voor Home Assistant

Deze add-on scant je lokale netwerk naar Shelly devices en toont gedetailleerde informatie over elk gevonden device.

## Installatie

1. Voeg deze repository toe aan je Home Assistant add-on stores
2. Installeer de "Shelly Device Scanner" add-on
3. Start de add-on
4. Open de web UI via de sidebar

## Configuratie

```yaml
admin_password: "jouw_wachtwoord"
```

### Optie: `admin_password`

Het admin wachtwoord dat is ingesteld op je Shelly devices. Dit is nodig om de device instellingen uit te kunnen lezen. Als je geen wachtwoord instelt, kan de add-on alleen basis informatie ophalen.

## Gebruik

1. Open de add-on via de Home Assistant sidebar (je ziet een "Shelly Scanner" icoon)
2. Klik op "Scan Netwerk" om te beginnen met scannen
3. De add-on scant het volledige /24 subnet waar Home Assistant op draait
4. Gevonden Shelly devices worden weergegeven met hun informatie

## Weergegeven Informatie

Voor elk gevonden Shelly device wordt het volgende getoond:

- Device naam
- Device type (bijv. SHSW-25, SHPLG-S, etc.)
- IP adres
- MAC adres
- Firmware versie
- Authenticatie status

## Bestandsstructuur

```
shelly-scanner/
├── config.yaml          # Add-on configuratie
├── Dockerfile          # Docker image definitie
├── run.sh              # Startup script
├── README.md           # Deze documentatie
├── build.yaml          # Build configuratie
└── app/
    ├── app.py          # Python applicatie
    └── templates/
        └── index.html  # Web interface
```

## Technische Details

- De add-on draait op poort 8099
- Gebruikt Python 3 met Flask voor de web interface
- Scant alle IP adressen in het /24 subnet parallel voor snelle resultaten
- Communiceert met Shelly devices via hun HTTP API

## Support

Voor problemen of vragen, open een issue op GitHub.

## Licentie

MIT License
