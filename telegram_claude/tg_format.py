"""Convert Claude's Markdown replies into Telegram-safe HTML and send them in
chunks that never split a word, line, or code block.

Telegram has no tables and only a small HTML subset (b, i, s, code, pre, a,
blockquote), so tables become bullet lines and headings become bold lines.
If Telegram still rejects a chunk, it is resent as plain text.
"""
import html
import re

from telegram.error import BadRequest

LIMIT = 4000  # Telegram max is 4096; leave room for closing tags

_CODE_FENCE = re.compile(r"^\s*```")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_QUOTE = re.compile(r"^\s*>\s?(.*)$")


def _inline(text: str) -> str:
    """Escape HTML and convert inline Markdown (code, links, bold, italic, strike)."""
    stash: list[str] = []

    def keep(s: str) -> str:
        stash.append(s)
        return f"\x00{len(stash) - 1}\x00"

    # inline code first, so its contents are never touched
    text = re.sub(r"`([^`\n]+)`", lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)
    # links
    text = re.sub(
        r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)",
        lambda m: keep(f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'),
        text,
    )
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])__(?=\S)(.+?)(?<=\S)__(?![\w*])", r"<b>\1</b>", text)
    text = re.sub(r"~~(?=\S)(.+?)(?<=\S)~~", r"<s>\1</s>", text)
    text = re.sub(r"(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"(?<![\w_])_(?=[^\s_])(.+?)(?<=[^\s_])_(?![\w_])", r"<i>\1</i>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _table(rows: list[str]) -> list[str]:
    """Turn a Markdown table into bullet lines: '• a — b — c'."""
    header, body = _cells(rows[0]), [_cells(r) for r in rows[2:]]
    out = []
    if len(header) > 2 and any(header):
        out.append("<i>" + " · ".join(_inline(h) for h in header if h) + "</i>")
    for cells in body:
        cells = [c for c in cells if c]
        if not cells:
            continue
        if len(header) == 2 and len(cells) == 2:
            out.append(f"• <b>{_inline(cells[0])}</b>: {_inline(cells[1])}")
        else:
            out.append("• " + " — ".join(_inline(c) for c in cells))
    return out


def to_blocks(md: str) -> list[str]:
    """Convert Markdown to a list of Telegram-HTML blocks (paragraphs, lists,
    code blocks). Each block is self-contained: no tag spans two blocks."""
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    cur: list[str] = []

    def flush():
        if cur:
            blocks.append("\n".join(cur))
            cur.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        if _CODE_FENCE.match(line):
            flush()
            code = []
            i += 1
            while i < len(lines) and not _CODE_FENCE.match(lines[i]):
                code.append(lines[i])
                i += 1
            blocks.append("<pre>" + html.escape("\n".join(code)) + "</pre>")
            i += 1
            continue
        if _TABLE_ROW.match(line) and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]):
            flush()
            rows = []
            while i < len(lines) and (_TABLE_ROW.match(lines[i]) or _TABLE_SEP.match(lines[i])):
                rows.append(lines[i])
                i += 1
            blocks.append("\n".join(_table(rows)))
            continue
        if not line.strip():
            flush()
        elif _HR.match(line):
            flush()
            blocks.append("──────────")
        elif m := _HEADING.match(line):
            flush()
            cur.append(f"<b>{_inline(m.group(1))}</b>")
        elif m := _QUOTE.match(line):
            quote = [m.group(1)]
            while i + 1 < len(lines) and (q := _QUOTE.match(lines[i + 1])):
                quote.append(q.group(1))
                i += 1
            flush()
            blocks.append("<blockquote>" + "\n".join(_inline(q) for q in quote) + "</blockquote>")
        elif m := _BULLET.match(line):
            indent = "   " * (len(m.group(1).expandtabs(2)) // 2)
            cur.append(f"{indent}• {_inline(m.group(2))}")
        else:
            cur.append(_inline(line.strip() if not line.startswith("    ") else line))
        i += 1
    flush()
    return [b for b in blocks if b.strip()]


def _split_long(block: str) -> list[str]:
    """Split a single oversized block by lines, keeping <pre> wrapping valid."""
    is_pre = block.startswith("<pre>") and block.endswith("</pre>")
    body = block[5:-6] if is_pre else block
    parts, cur = [], ""
    for line in body.split("\n"):
        while len(line) > LIMIT - 20:  # pathological single line
            parts.append(line[: LIMIT - 20])
            line = line[LIMIT - 20:]
        if len(cur) + len(line) + 1 > LIMIT - 20:
            parts.append(cur)
            cur = ""
        cur = f"{cur}\n{line}" if cur else line
    if cur:
        parts.append(cur)
    return [f"<pre>{p}</pre>" for p in parts] if is_pre else parts


def to_chunks(md: str) -> list[str]:
    """Markdown -> Telegram HTML messages, each under the size limit."""
    chunks, cur = [], ""
    for block in to_blocks(md):
        for piece in (_split_long(block) if len(block) > LIMIT else [block]):
            if cur and len(cur) + len(piece) + 2 > LIMIT:
                chunks.append(cur)
                cur = ""
            cur = f"{cur}\n\n{piece}" if cur else piece
    if cur:
        chunks.append(cur)
    return chunks or ["(no output)"]


def to_plain(html_text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", html_text))


async def send_with(send, text: str) -> None:
    """Send formatted chunks via `send(text, **kwargs)` (e.g. message.reply_text or a
    partial of bot.send_message); falls back to plain text if Telegram rejects HTML."""
    for chunk in to_chunks(text):
        try:
            await send(chunk, parse_mode="HTML", disable_web_page_preview=True)
        except BadRequest:
            plain = to_plain(chunk)
            for i in range(0, len(plain), 4096):
                await send(plain[i:i + 4096], disable_web_page_preview=True)


async def send_formatted(message, text: str) -> None:
    """Reply to a telegram Message with formatted chunks; plain-text fallback."""
    await send_with(message.reply_text, text)
