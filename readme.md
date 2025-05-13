# Aviseringstjänst

En flexibel aviseringstjänst som stödjer både SMS och e-post notifieringar.

## Funktioner

- SMS-utskick via HelloSMS API
- E-postutskick via SMTP
- Automatisk återförsök vid fel
- Begränsning av förfrågningar (rate limiting)
- Omfattande loggning
- RESTful API

## Installation

1. Klona projektet:
```bash
git clone [projektets-url]
cd Aviseringsservice
```

2. Installera beroenden:
```bash
pip install -r requirements.txt
```

3. Konfigurera miljövariabler:
Kopiera `.env.example` till `.env` och uppdatera med dina inställningar:
- HelloSMS-inställningar
- SMTP-inställningar

## Konfiguration

### HelloSMS
- `HELLOSMS_USERNAME`: Ditt HelloSMS användarnamn
- `HELLOSMS_PASSWORD`: Ditt HelloSMS lösenord
- `HELLOSMS_SENDER`: Avsändarnamn (standard: "TrafikInfo")
- `HELLOSMS_RATE_LIMIT`: Antal tillåtna förfrågningar per minut

### E-post (SMTP)
- `SMTP_SERVER`: SMTP-serveradress
- `SMTP_PORT`: SMTP-port (standard: 587)
- `SMTP_USERNAME`: E-postadress för avsändare
- `SMTP_PASSWORD`: SMTP-lösenord
- `EMAIL_SENDER`: Avsändarens e-postadress

## API-användning

### Skicka SMS
```bash
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sms",
    "to": "+46701234567",
    "message": "Test meddelande",
    "from": "TrafikInfo"
  }'
```

### Skicka E-post
```bash
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "action": "email",
    "to": "mottagare@example.com",
    "subject": "Test ämne",
    "message": "Test meddelande",
    "from": "avsandare@example.com"
  }'
```

## Felhantering

Tjänsten hanterar följande felscenarier:
- Ogiltig autentisering
- Nätverksfel
- Begränsning av förfrågningar
- Ogiltiga inmatningar
- Timeout

## Loggning

Loggar sparas i `logs`-mappen med datumstämpel. Varje avisering loggas med:
- Tidsstämpel
- Typ av avisering (SMS/e-post)
- Mottagare
- Avsändare
- Status
- Eventuella fel

## Deployment

Tjänsten är förberedd för deployment med Gunicorn. Använd medföljande Procfile:

```bash
gunicorn avisering_server:app
```

## Säkerhet

- Använd alltid HTTPS i produktion
- Skydda .env-filen
- Begränsa åtkomst till API:et
- Kontrollera rate limiting-inställningar

## Licens

Detta projekt är licensierat under MIT-licensen – vilket innebär att du fritt får använda, kopiera och ändra koden, så länge denna licenstext inkluderas.

Se mer: https://opensource.org/licenses/MIT

## Support

Vid frågor eller problem, kontakta trafikInformation@maddec.eu
