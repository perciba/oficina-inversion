# Oficina de Inversión (IA + datos)

Briefing multi-activo **sin API key**:

- Acciones / ETF (SPY, QQQ, AAPL, NVDA…)
- Forex (EURUSD, GBPUSD, USDJPY, **USDCOP**)
- Metales (oro, plata)
- Commodities (petróleo)
- Cripto (BTC, ETH)
- Riesgo (VIX)

**No es consejo de inversión.** Uso educativo.

## Cómo usar (PC)

```bash
cd oficina-inversion
python3 briefing.py
```

Abre el informe:

- `informes/ULTIMO.md` — siempre el más reciente
- `informes/briefing_YYYYMMDD_HHMM.md` — historial

## Personalizar watchlist

Edita `watchlist.json` (símbolos de Yahoo Finance).

## Requisitos

Solo **Python 3**. No hace falta `pip install`.

## Otros proyectos

| Repo | Rol |
|------|-----|
| `oficina-inversion` | Este briefing multi-activo |
| `mapa-calor-opciones` | Opciones CBOE (GEX, Max Pain) |

## Próximos pasos

1. Unir niveles CBOE de SPY/QQQ al briefing
2. Alertas Telegram si un activo se mueve más de X%
3. GitHub Action cada mañana
