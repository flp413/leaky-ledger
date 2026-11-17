# Threat model

## System

```
client --HTTPS--> Django/DRF API --> SQLite (accounts, transactions)
                       |
                       +--> outbound HTTP (avatar URL fetch)
                       +--> risk engine (fraud_check, stubbed)
                       +--> LedgerBot (LLM stand-in) --> tools: list_transactions, get_balance, send_money
```

**Assets:** account balances (EUR, USD), transaction history, password hashes, JWT signing secret, the server's network position (it can reach internal hosts).

**Actors:** anonymous visitor, logged-in customer, malicious logged-in customer, attacker with a stolen or forged token.

**Trust boundaries:** internet to API; API to database; API to anything it fetches over HTTP; text written by one customer (transaction notes) that ends up in another customer's assistant context.

## Entry points

| Endpoint | Auth | Touches |
|----------|------|---------|
| `POST /api/auth/register` | none | creates user + account |
| `POST /api/auth/login` | none | password check, issues JWT |
| `GET/PATCH /api/me` | JWT | own account, outbound fetch |
| `GET /api/accounts/{iban}` | JWT | any account |
| `POST /api/transfers` | JWT | two balances, ledger |
| `POST /api/exchange` | JWT | own balances |
| `GET /api/transactions`, `/search`, `/{id}` | JWT | ledger |
| `POST /api/assistant` | JWT | ledger (incl. notes written by other users), can move money |
| `GET /receipt/{id}` | none | ledger, HTML output |

## STRIDE

TODO: fill in per entry point. For each one: what can go wrong, how likely, how bad, and which control stops it.

| Threat | Example here | Control | Status |
|--------|--------------|---------|--------|
| Spoofing | | | |
| Tampering | | | |
| Repudiation | | | |
| Information disclosure | | | |
| Denial of service | | | |
| Elevation of privilege | | | |
