"""«ИИ-проверка»: ЧЕРНОВИК экрана «Текст проверен» переживает выход из Telegram и рестарт сервиса.

После распознавания ученик видит печатный текст работы и правит его (слово/фрагмент через Вишенку). Раньше всё это жило
только в памяти телефона и в сеансе EC_CHECKS (TTL 30 минут): закрыл мини-приложение или сервис перезапустился —
распознанный текст и правки пропали, а фото приходилось снимать и распознавать заново. Теперь черновик пишется в таблицу
essay_draft СРАЗУ после распознавания (данные OCR для привязки ошибок к фото, фото работы и текст), текст обновляется при
каждой правке, а при входе в раздел клиент получает его и возвращает ученика на тот же экран с теми же правками.

Одна запись на пользователя (tg_id): новое распознавание заменяет прежний черновик. Черновик живёт до тех пор, пока проверка
не готова (тогда он удаляется), ученик не вышел кнопкой «Назад» или не истёк TTL. Модуль не зависит от aiohttp: q/run
передаются снаружи (bot.py), поэтому он тестируется на голой sqlite — как essaylast."""
import json
import time

KINDS = ("ege", "oge")
TTL = 3 * 24 * 3600                # черновик живёт трое суток
MAX_TEXT = 20_000                  # как essaycheck.APPLY_MAX
MAX_PHOTOS = 12
MAX_PHOTO_CHARS = 24_000_000       # base64-символов фото на запись: страховка от раздувания БД (как у essaylast)


def put(run, uid, cid, kind, ocr, photos=None, text=None, now=None):
    """Сохраняет черновик после этапа 1: ocr — данные распознавания (essaycheck.recognize), text — текст на экране
    (по умолчанию распознанный). True — записано."""
    if not isinstance(cid, str) or not cid or kind not in KINDS or not isinstance(ocr, dict) or not isinstance(ocr.get("essay"), str):
        return False
    text = ocr["essay"] if text is None else text
    if not isinstance(text, str) or not text.strip():
        return False
    ph = [p for p in (photos or []) if isinstance(p, str) and p][:MAX_PHOTOS]
    blob = json.dumps(ph) if ph and sum(len(p) for p in ph) <= MAX_PHOTO_CHARS else None
    run("insert or replace into essay_draft(tg_id,id,kind,text,ocr,photos,created) values(?,?,?,?,?,?,?)",
        uid, cid, kind, text[:MAX_TEXT], json.dumps(ocr, ensure_ascii=False), blob, now if now is not None else time.time())
    return True


def set_text(q, run, uid, cid, text):
    """Обновляет текст черновика после правки ученика. True — это черновик uid с таким id и он обновлён."""
    if not isinstance(cid, str) or not isinstance(text, str) or not text.strip():
        return False
    if not q("select 1 from essay_draft where tg_id=? and id=?", uid, cid):
        return False
    run("update essay_draft set text=? where tg_id=? and id=?", text[:MAX_TEXT], uid, cid)
    return True


def _row(q, uid, now):
    rows = q("select id, kind, text, ocr, photos, created from essay_draft where tg_id=?", uid)
    if not rows:
        return None
    r = rows[0]
    if (now if now is not None else time.time()) - float(r["created"] or 0) > TTL or r["kind"] not in KINDS:
        return None
    return r


def head(q, uid, now=None):
    """Для клиента: {"id","kind","text"} или None (нет черновика / истёк)."""
    r = _row(q, uid, now)
    return {"id": r["id"], "kind": r["kind"], "text": r["text"]} if r else None


def load(q, uid, now=None):
    """Полный черновик: {"id","kind","text","ocr","photos"} или None. Битые данные — None (как будто черновика нет)."""
    r = _row(q, uid, now)
    if not r:
        return None
    try:
        ocr = json.loads(r["ocr"])
        ph = json.loads(r["photos"]) if r["photos"] else []
    except (TypeError, ValueError):
        return None
    if not isinstance(ocr, dict) or not isinstance(ocr.get("essay"), str) or not isinstance(ph, list):
        return None
    return {"id": r["id"], "kind": r["kind"], "text": r["text"], "ocr": ocr, "photos": [p for p in ph if isinstance(p, str)]}


def drop(run, uid, cid=None):
    """Удаляет черновик uid (если задан cid — только этот: чужой/новый черновик не трогаем)."""
    if cid is None:
        run("delete from essay_draft where tg_id=?", uid)
    else:
        run("delete from essay_draft where tg_id=? and id=?", uid, cid)
