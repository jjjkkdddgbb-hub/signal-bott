# -*- coding: utf-8 -*-
"""
الاستراتيجيات المتاحة للمستخدمين.

- bot            : صفقات البوت (نفس إشارات قناة تيليجرام، تُنفَّذ بعد 60 ثانية من الإرسال).
- range_bounce   : ارتداد النطاق (بولنجر + RSI + ذيل رفض).
- trend_pullback : متابعة الاتجاه بعد تصحيح (EMA + MACD).
- stoch_engulf   : ستوكاستك مع شمعة انعكاس (ابتلاع / مطرقة).

كل مستخدم يختار استراتيجيته الخاصة، والمشرف يستطيع تفعيل/تعطيل كل واحدة من اللوحة.
لا توجد استراتيجية تضمن الربح؛ لذلك الإيقاف عند الخسارة/الربح يبقى فعّالاً دائماً.
"""
import time

import numpy as np
import pandas as pd

from database import get_setting

DEFAULT_STRATEGY = "bot"
EXPIRY_SECONDS = 60       # مدة الصفقة لكل الاستراتيجيات الجديدة
MIN_CANDLES = 70

STRATEGIES = [
    {
        "id": "bot",
        "name": "صفقات البوت",
        "icon": "🤖",
        "tagline": "نفس إشارات قناة تيليجرام",
        "desc": "ينفّذ حسابك إشارة البوت المرسلة للقناة بعد دقيقة من إرسالها، على أقوى زوج في السوق وقت الإشارة.",
        "tags": ["صفقة 1 دقيقة", "إشارة كل دقيقتين تقريباً"],
        "scan": False,
    },
    {
        "id": "range_bounce",
        "name": "ارتداد النطاق",
        "icon": "🎯",
        "tagline": "يصطاد الارتداد من حواف السعر",
        "desc": "يدخل عندما يخرج السعر عن نطاق بولنجر مع تشبّع في RSI وشمعة تُظهر رفضاً واضحاً للحركة، فيراهن على العودة نحو المتوسط.",
        "tags": ["صفقة 1 دقيقة", "أفضل في السوق الهادئ"],
        "scan": True,
    },
    {
        "id": "trend_pullback",
        "name": "الاتجاه والتصحيح",
        "icon": "📈",
        "tagline": "يركب الاتجاه بعد التصحيح",
        "desc": "يتحقق من اتجاه واضح عبر المتوسطات، وينتظر تصحيحاً قصيراً ثم عودة الزخم (MACD) ليدخل مع الاتجاه وليس ضده.",
        "tags": ["صفقة 1 دقيقة", "أفضل في السوق المتحرك"],
        "scan": True,
    },
    {
        "id": "stoch_engulf",
        "name": "ستوكاستك والانعكاس",
        "icon": "⚡",
        "tagline": "انعكاس سريع بتأكيد الشمعة",
        "desc": "ينتظر خروج الستوكاستك من منطقة التشبّع بتقاطع، ثم يتأكد من شمعة ابتلاع أو مطرقة تؤكد الانعكاس قبل الدخول.",
        "tags": ["صفقة 1 دقيقة", "إشارات أقل وأدق"],
        "scan": True,
    },
    {
        "id": "waker_block",
        "name": "ووكر بلوك",
        "icon": "🧱",
        "tagline": "أوردر بلوك + كسر الهيكل + إعادة اختبار",
        "desc": "يجمع خمسة شروط في قرار واحد: منطقة أوردر بلوك، وكسر هيكل السوق، وإعادة اختبار المنطقة، وزخم السعر، وRSI. لا يدخل إلا إذا اجتمعت الشروط بدرجة كافية.",
        "tags": ["صفقة 1 دقيقة", "يعتمد على هيكل السوق"],
        "scan": True,
    },
]

_BY_ID = {s["id"]: s for s in STRATEGIES}
STRATEGY_IDS = [s["id"] for s in STRATEGIES]
SCAN_IDS = [s["id"] for s in STRATEGIES if s["scan"]]


def is_valid(sid):
    return sid in _BY_ID


def normalize(sid):
    return sid if sid in _BY_ID else DEFAULT_STRATEGY


def parse_list(raw):
    """يحوّل النص المخزّن (مثل 'range_bounce,waker_block') إلى قائمة صحيحة بلا تكرار."""
    if isinstance(raw, (list, tuple)):
        parts = [str(x).strip() for x in raw]
    else:
        parts = [p.strip() for p in str(raw or "").split(",")]
    out = []
    for p in parts:
        if p in _BY_ID and p not in out:
            out.append(p)
    return out or [DEFAULT_STRATEGY]


def join_list(items):
    return ",".join(parse_list(items))


def is_enabled(sid):
    """هل فعّل المشرف هذه الاستراتيجية؟ (الافتراضي: نعم)."""
    try:
        return get_setting(f"strategy_enabled_{sid}", "1") == "1"
    except Exception:
        return True


def public_list():
    """القائمة كما تُعرض للمستخدم والمشرف."""
    out = []
    for s in STRATEGIES:
        item = {k: s[k] for k in ("id", "name", "icon", "tagline", "desc", "tags")}
        item["enabled"] = is_enabled(s["id"])
        out.append(item)
    return out


def name_of(sid):
    return _BY_ID.get(sid, _BY_ID[DEFAULT_STRATEGY])["name"]


# ───────────────────────── الشموع ─────────────────────────
def parse_ohlc(raw, now=None):
    """يحوّل رد pyquotex إلى قائمة شموع مرتبة {t,o,h,l,c} بدون الشمعة الجارية."""
    now = now or time.time()
    rows = {}
    for c in raw or []:
        try:
            if isinstance(c, dict):
                t = c.get("time") or c.get("timestamp") or c.get("from")
                o = c.get("open")
                cl = c.get("close")
                h = c.get("high", c.get("max"))
                lo = c.get("low", c.get("min"))
            else:
                t, o, cl = c[0], c[1], c[2]
                h = c[3] if len(c) > 3 else None
                lo = c[4] if len(c) > 4 else None
            if t is None or o is None or cl is None:
                continue
            o, cl = float(o), float(cl)
            h = float(h) if h is not None else max(o, cl)
            lo = float(lo) if lo is not None else min(o, cl)
            h, lo = max(h, o, cl), min(lo, o, cl)
            rows[int(t)] = {"t": int(t), "o": o, "h": h, "l": lo, "c": cl}
        except Exception:
            continue
    candles = [rows[k] for k in sorted(rows)]
    # الشمعة الجارية لم تكتمل بعد
    while candles and candles[-1]["t"] + 60 > now + 1:
        candles.pop()
    return candles


def _frame(candles):
    df = pd.DataFrame(candles)
    return df.astype({"o": float, "h": float, "l": float, "c": float})


def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def _rsi(s, n):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, 1e-9)
    return 100 - 100 / (1 + rs)


def _fresh(candles, max_age=150):
    """يرفض البيانات القديمة (آخر شمعة مكتملة يجب أن تكون حديثة)."""
    return bool(candles) and (time.time() - (candles[-1]["t"] + 60)) <= max_age


# ───────────────────────── الاستراتيجيات ─────────────────────────
def _range_bounce(df):
    c, o, h, l = df["c"], df["o"], df["h"], df["l"]
    mid = c.rolling(20).mean()
    sd = c.rolling(20).std(ddof=0)
    upper, lower = mid + 2 * sd, mid - 2 * sd
    rsi7 = _rsi(c, 7)
    ema50 = _ema(c, 50)

    i = len(df) - 1
    price = c.iloc[i]
    if not np.isfinite(sd.iloc[i]) or sd.iloc[i] <= 0:
        return None
    width_pct = (upper.iloc[i] - lower.iloc[i]) / price * 100
    if width_pct < 0.02:                      # سوق ميت
        return None
    # ميل المتوسط الطويل: إذا كان الاتجاه قوياً جداً نتجنب الارتداد ضده
    slope = abs(ema50.iloc[i] - ema50.iloc[i - 10]) / price * 100
    if slope > width_pct * 0.9:
        return None

    rng = max(h.iloc[i] - l.iloc[i], 1e-12)
    lower_wick = (min(o.iloc[i], c.iloc[i]) - l.iloc[i]) / rng
    upper_wick = (h.iloc[i] - max(o.iloc[i], c.iloc[i])) / rng

    if l.iloc[i] <= lower.iloc[i] and c.iloc[i] >= lower.iloc[i] * 0.99995 and rsi7.iloc[i] <= 28 and lower_wick >= 0.35:
        score = (28 - rsi7.iloc[i]) + lower_wick * 30 + (lower.iloc[i] - l.iloc[i]) / sd.iloc[i] * 10
        return {"dir": "call", "score": float(score), "why": "ارتداد من الحد السفلي"}
    if h.iloc[i] >= upper.iloc[i] and c.iloc[i] <= upper.iloc[i] * 1.00005 and rsi7.iloc[i] >= 72 and upper_wick >= 0.35:
        score = (rsi7.iloc[i] - 72) + upper_wick * 30 + (h.iloc[i] - upper.iloc[i]) / sd.iloc[i] * 10
        return {"dir": "put", "score": float(score), "why": "ارتداد من الحد العلوي"}
    return None


def _trend_pullback(df):
    c, o, h, l = df["c"], df["o"], df["h"], df["l"]
    e9, e21, e50 = _ema(c, 9), _ema(c, 21), _ema(c, 50)
    macd = _ema(c, 12) - _ema(c, 26)
    hist = macd - _ema(macd, 9)
    rsi14 = _rsi(c, 14)

    i = len(df) - 1
    price = c.iloc[i]
    gap = abs(e21.iloc[i] - e50.iloc[i]) / price * 100
    if gap < 0.012:                           # لا اتجاه واضح
        return None

    up_trend = e21.iloc[i] > e50.iloc[i] and e50.iloc[i] > e50.iloc[i - 5]
    down_trend = e21.iloc[i] < e50.iloc[i] and e50.iloc[i] < e50.iloc[i - 5]

    recent = slice(i - 4, i)                  # آخر 4 شموع قبل الحالية
    if up_trend:
        pulled = (l.iloc[recent] <= e21.iloc[recent]).any() or (c.iloc[recent] < e9.iloc[recent]).any()
        resumed = c.iloc[i] > o.iloc[i] and c.iloc[i] > e9.iloc[i] and hist.iloc[i] > hist.iloc[i - 1]
        if pulled and resumed and 40 <= rsi14.iloc[i] <= 68:
            score = gap * 100 + (hist.iloc[i] - hist.iloc[i - 1]) / price * 1e5
            return {"dir": "call", "score": float(score), "why": "اتجاه صاعد بعد تصحيح"}
    if down_trend:
        pulled = (h.iloc[recent] >= e21.iloc[recent]).any() or (c.iloc[recent] > e9.iloc[recent]).any()
        resumed = c.iloc[i] < o.iloc[i] and c.iloc[i] < e9.iloc[i] and hist.iloc[i] < hist.iloc[i - 1]
        if pulled and resumed and 32 <= rsi14.iloc[i] <= 60:
            score = gap * 100 + (hist.iloc[i - 1] - hist.iloc[i]) / price * 1e5
            return {"dir": "put", "score": float(score), "why": "اتجاه هابط بعد تصحيح"}
    return None


def _stoch_engulf(df):
    c, o, h, l = df["c"], df["o"], df["h"], df["l"]
    lo14, hi14 = l.rolling(14).min(), h.rolling(14).max()
    k_raw = (c - lo14) / (hi14 - lo14).replace(0, 1e-9) * 100
    k = k_raw.rolling(3).mean()
    d = k.rolling(3).mean()

    i = len(df) - 1
    if not np.isfinite(d.iloc[i]) or not np.isfinite(d.iloc[i - 1]):
        return None

    body = abs(c.iloc[i] - o.iloc[i])
    pbody = abs(c.iloc[i - 1] - o.iloc[i - 1])
    rng = max(h.iloc[i] - l.iloc[i], 1e-12)
    if rng / c.iloc[i] * 100 < 0.004:         # شمعة صغيرة جداً
        return None

    bull = c.iloc[i] > o.iloc[i]
    bear = c.iloc[i] < o.iloc[i]
    bull_engulf = bull and c.iloc[i - 1] < o.iloc[i - 1] and c.iloc[i] >= o.iloc[i - 1] and o.iloc[i] <= c.iloc[i - 1] and body >= pbody
    bear_engulf = bear and c.iloc[i - 1] > o.iloc[i - 1] and c.iloc[i] <= o.iloc[i - 1] and o.iloc[i] >= c.iloc[i - 1] and body >= pbody
    lw = min(o.iloc[i], c.iloc[i]) - l.iloc[i]
    uw = h.iloc[i] - max(o.iloc[i], c.iloc[i])
    hammer = bull and lw >= 2 * max(body, rng * 0.05) and uw <= rng * 0.25
    star = bear and uw >= 2 * max(body, rng * 0.05) and lw <= rng * 0.25

    cross_up = k.iloc[i - 1] <= d.iloc[i - 1] and k.iloc[i] > d.iloc[i] and min(k.iloc[i - 3:i]) < 25
    cross_dn = k.iloc[i - 1] >= d.iloc[i - 1] and k.iloc[i] < d.iloc[i] and max(k.iloc[i - 3:i]) > 75

    if cross_up and (bull_engulf or hammer):
        return {"dir": "call", "score": float(60 + (25 - min(k.iloc[i - 3:i])) + (10 if bull_engulf else 0)), "why": "انعكاس صاعد مؤكد"}
    if cross_dn and (bear_engulf or star):
        return {"dir": "put", "score": float(60 + (max(k.iloc[i - 3:i]) - 75) + (10 if bear_engulf else 0)), "why": "انعكاس هابط مؤكد"}
    return None


# ───────────────────────── ووكر بلوك ─────────────────────────
WAKER_THRESHOLD = 55
_WAKER_WEIGHTS = {"orderBlock": 26, "breakout": 24, "retest": 20, "momentum": 18, "rsi": 12}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _atr(df, n=14):
    prev = df["c"].shift(1)
    tr = pd.concat([df["h"] - df["l"], (df["h"] - prev).abs(), (df["l"] - prev).abs()], axis=1).max(axis=1)
    return float(tr.tail(n).mean())


def _momentum_pct(c, n=10):
    if len(c) <= n:
        return 0.0
    base = float(c.iloc[-1 - n])
    return (float(c.iloc[-1]) - base) / base * 100.0 if base else 0.0


def _find_order_block(df, atr_value):
    """آخر شمعة اندفاع قوية؛ الشمعة المعاكسة قبلها هي الأوردر بلوك."""
    min_body = max(atr_value * 1.25, 1e-9)
    n = len(df)
    o, c, h, l = df["o"].values, df["c"].values, df["h"].values, df["l"].values
    for i in range(n - 2, max(4, n - 26) - 1, -1):
        if abs(c[i] - o[i]) < min_body:
            continue
        bullish = c[i] > o[i]
        if bullish == (c[i - 1] >= o[i - 1]):
            continue
        return {
            "direction": "CALL" if bullish else "PUT",
            "impulse": i,
            "top": max(o[i - 1], c[i - 1]) if bullish else h[i - 1],
            "bottom": l[i - 1] if bullish else min(o[i - 1], c[i - 1]),
        }
    return None


def _waker_rsi_strength(v, bias):
    if bias == "CALL":
        if 52 <= v <= 70:
            return 1.0
        if 45 <= v <= 78:
            return 0.6
        return 0.2 if v > 78 else 0.1
    if 30 <= v <= 48:
        return 1.0
    if 22 <= v <= 55:
        return 0.6
    return 0.2 if v < 22 else 0.1


def _waker_block(df):
    n = len(df)
    c, o, h, l = df["c"], df["o"], df["h"], df["l"]
    price = float(c.iloc[-1])
    atr_v = _atr(df, 14)
    if not np.isfinite(atr_v) or atr_v <= 0:
        return None
    rsi_v = float(_rsi(c, 14).iloc[-1])
    mom = _momentum_pct(c, 10)

    # هيكل السوق: قمة وقاع الشموع قبل آخر 4 شموع
    struct = df.iloc[max(0, n - 18): n - 4]
    if len(struct) < 5:
        struct = df.iloc[: n - 1].tail(max(2, n - 2))
    s_high, s_low = float(struct["h"].max()), float(struct["l"].min())
    tail = df.iloc[-4:]

    broke_high = bool(((tail["c"] > s_high) | (tail["h"] > s_high)).any())
    broke_low = bool(((tail["c"] < s_low) | (tail["l"] < s_low)).any())
    block = _find_order_block(df, atr_v)

    if broke_high and not broke_low:
        bias = "CALL"
    elif broke_low and not broke_high:
        bias = "PUT"
    elif block:
        bias = block["direction"]
    else:
        bias = "CALL" if mom >= 0 else "PUT"

    level = s_high if bias == "CALL" else s_low
    if bias == "CALL":
        brk_close, brk_wick = bool((tail["c"] > level).any()), bool((tail["h"] > level).any())
    else:
        brk_close, brk_wick = bool((tail["c"] < level).any()), bool((tail["l"] < level).any())
    breakout = 1.0 if brk_close else (0.6 if brk_wick else 0.0)

    if block:
        zone_top, zone_bot = float(block["top"]), float(block["bottom"])
        after = df.iloc[block["impulse"] + 1:]
        touched = bool(((after["l"] <= zone_top) & (after["h"] >= zone_bot)).any()) if len(after) else False
    else:
        zone_top, zone_bot, touched = s_high, s_low, False
    near = abs(price - (zone_top if bias == "CALL" else zone_bot)) <= atr_v * 0.6
    retest = 1.0 if touched else (0.5 if near else 0.0)

    ob = (1.0 if block["direction"] == bias else 0.35) if block else 0.0
    signed = mom if bias == "CALL" else -mom
    momentum = _clamp(signed / 0.3, 0.0, 1.0)
    rsi_s = _waker_rsi_strength(rsi_v, bias)

    strengths = {"orderBlock": ob, "breakout": breakout, "retest": retest, "momentum": momentum, "rsi": rsi_s}
    score = sum(_WAKER_WEIGHTS[k] * strengths[k] for k in _WAKER_WEIGHTS) * 0.92
    final = float(round(_clamp(score, 0, 99)))
    if final < WAKER_THRESHOLD:
        return None

    parts = []
    if ob >= 1:
        parts.append("أوردر بلوك")
    if breakout >= 1:
        parts.append("كسر الهيكل")
    if retest >= 1:
        parts.append("إعادة اختبار")
    why = "ووكر بلوك: " + (" + ".join(parts) if parts else "تجمّع شروط") + f" ({int(final)}%)"
    return {"dir": "call" if bias == "CALL" else "put", "score": final, "why": why}


_FUNCS = {
    "range_bounce": _range_bounce,
    "trend_pullback": _trend_pullback,
    "stoch_engulf": _stoch_engulf,
    "waker_block": _waker_block,
}


def evaluate(sid, candles):
    """يرجع {'dir','score','why'} أو None. candles: ناتج parse_ohlc."""
    fn = _FUNCS.get(sid)
    if fn is None or len(candles) < MIN_CANDLES or not _fresh(candles):
        return None
    try:
        return fn(_frame(candles[-200:]))
    except Exception as e:
        print(f"[STRATEGY] {sid} error: {e}", flush=True)
        return None
