#!/usr/bin/env python3
"""
Oficina de Inversión — Briefing multi-activo
Acciones · Forex · Metales · Commodities · Cripto · VIX
Solo Python 3 stdlib. No es consejo de inversión.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

DIR = Path(__file__).resolve().parent
WATCHLIST = DIR / "watchlist.json"
INFORMES = DIR / "informes"
UA = "Mozilla/5.0 (OficinaInversion/1.0)"


def http_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def fetch_quote(symbol: str) -> Optional[Dict[str, Any]]:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + quote(symbol)
        + "?interval=1d&range=5d"
    )
    try:
        raw = http_json(url)
        result = (raw.get("chart") or {}).get("result") or [None]
        result = result[0]
        if not result:
            return None
        meta = result.get("meta") or {}
        quote_ = (result.get("indicators") or {}).get("quote") or [{}]
        closes = (quote_[0] or {}).get("close") or []
        vals = [c for c in closes if c is not None]
        if not vals:
            px = meta.get("regularMarketPrice") or meta.get("previousClose")
            if px is None:
                return None
            return {
                "symbol": symbol,
                "price": float(px),
                "chg_pct": None,
                "prev": None,
                "currency": meta.get("currency") or "",
            }
        price = float(vals[-1])
        prev = float(vals[-2]) if len(vals) >= 2 else float(meta.get("previousClose") or price)
        chg = ((price - prev) / prev * 100.0) if prev else None
        return {
            "symbol": symbol,
            "price": price,
            "chg_pct": chg,
            "prev": prev,
            "currency": meta.get("currency") or "",
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def fmt_px(x: Optional[float], symbol: str = "") -> str:
    if x is None:
        return "—"
    if "JPY" in symbol or "COP" in symbol:
        return f"{x:,.2f}"
    if x >= 1000:
        return f"{x:,.2f}"
    if x >= 1:
        return f"{x:.4f}".rstrip("0").rstrip(".")
    return f"{x:.6f}".rstrip("0").rstrip(".")


def fmt_chg(c: Optional[float]) -> str:
    if c is None:
        return "—"
    sign = "+" if c >= 0 else ""
    return f"{sign}{c:.2f}%"


def load_watchlist() -> dict:
    if not WATCHLIST.exists():
        print("ERROR: falta watchlist.json")
        sys.exit(1)
    return json.loads(WATCHLIST.read_text(encoding="utf-8"))


def seccion(titulo: str, items: List[dict], datos: Dict[str, dict]) -> List[str]:
    lines = [f"## {titulo}", ""]
    lines.append("| Activo | Precio | Var. |")
    lines.append("|--------|--------|------|")
    for it in items:
        s, n = it["s"], it["n"]
        d = datos.get(s) or {}
        if d.get("error"):
            lines.append(f"| {n} (`{s}`) | error | {d['error'][:40]} |")
        else:
            lines.append(
                f"| {n} (`{s}`) | {fmt_px(d.get('price'), s)} | {fmt_chg(d.get('chg_pct'))} |"
            )
    lines.append("")
    return lines


def lectura_rapida(datos: Dict[str, dict]) -> List[str]:
    lines = ["## Lectura rápida (contexto)", ""]
    vix = datos.get("^VIX") or {}
    spy = datos.get("SPY") or {}
    btc = datos.get("BTC-USD") or {}
    oro = datos.get("GC=F") or datos.get("GLD") or {}
    eurusd = datos.get("EURUSD=X") or {}

    if vix.get("price") is not None:
        v = vix["price"]
        if v >= 25:
            lines.append(f"- **VIX {v:.1f}**: miedo elevado; más volatilidad esperable.")
        elif v <= 15:
            lines.append(f"- **VIX {v:.1f}**: complacencia / vol baja (puede cambiar rápido).")
        else:
            lines.append(f"- **VIX {v:.1f}**: zona intermedia.")

    if spy.get("chg_pct") is not None:
        lines.append(f"- **SPY** {fmt_chg(spy['chg_pct'])} en la última sesión disponible.")

    if btc.get("chg_pct") is not None:
        lines.append(f"- **Bitcoin** {fmt_chg(btc['chg_pct'])}.")

    if oro.get("chg_pct") is not None:
        lines.append(f"- **Oro** {fmt_chg(oro['chg_pct'])}.")

    if eurusd.get("chg_pct") is not None:
        lines.append(f"- **EUR/USD** {fmt_chg(eurusd['chg_pct'])}.")

    lines.append("")
    lines.append(
        "> Esto es **contexto de mercado**, no una recomendación de compra o venta."
    )
    lines.append("")
    return lines


def generar() -> str:
    wl = load_watchlist()
    simbolos = []
    for key in ("acciones", "forex", "metales", "commodities", "cripto", "riesgo"):
        for it in wl.get(key) or []:
            simbolos.append(it["s"])

    datos: Dict[str, dict] = {}
    print("Descargando cotizaciones...")
    for s in simbolos:
        print(f"  · {s}")
        datos[s] = fetch_quote(s) or {"symbol": s, "error": "sin datos"}

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Briefing de oficina — {now}",
        "",
        "Multi-activo: acciones · forex · metales · commodities · cripto · riesgo.",
        "",
        "**Uso educativo. No es consejo de inversión ni de trading.**",
        "",
    ]
    lines += lectura_rapida(datos)
    lines += seccion("Acciones / índices ETF", wl.get("acciones") or [], datos)
    lines += seccion("Forex", wl.get("forex") or [], datos)
    lines += seccion("Metales", wl.get("metales") or [], datos)
    lines += seccion("Commodities", wl.get("commodities") or [], datos)
    lines += seccion("Cripto", wl.get("cripto") or [], datos)
    lines += seccion("Riesgo", wl.get("riesgo") or [], datos)
    lines += [
        "---",
        "",
        "### Próximos módulos (oficina)",
        "- Niveles de opciones (CBOE) para SPY/QQQ — conectar Plan B",
        "- Alertas por % de movimiento",
        "- Historial en SQLite",
        "",
        f"_Generado por briefing.py · {now}_",
        "",
    ]
    return "\n".join(lines)


def main():
    INFORMES.mkdir(parents=True, exist_ok=True)
    md = generar()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = INFORMES / f"briefing_{stamp}.md"
    out.write_text(md, encoding="utf-8")
    latest = INFORMES / "ULTIMO.md"
    latest.write_text(md, encoding="utf-8")
    print()
    print(md)
    print()
    print(f"Guardado: {out}")
    print(f"Último:   {latest}")


if __name__ == "__main__":
    main()
