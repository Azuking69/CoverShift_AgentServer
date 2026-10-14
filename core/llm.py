"""Claudeの呼び出し。環境変数 ANTHROPIC_API_KEY があれば本物のClaude API、なければ偽物（固定文）。
どちらの場合も、**送る直前の本文**を outbound.log に追記する（E4：実名が出ていないかの確認用）。
モデル名は環境変数 CLAUDE_MODEL（既定 claude-haiku-5-5。Anthropicの公開モデル名一覧にある名前。使えない場合はエラーになるので、その場合は変える）。
"""
import json, os, time

LOG = os.getenv("OUTBOUND_LOG", os.path.join(os.getcwd(), "outbound.log"))
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")
SYSTEM = ("あなたはドラッグストアのシフト案を、店長向けに短く説明する補助役です。"
          "入力の『スタッフA』などは仮の記号です。実名を推測したり書いたりしないこと。説明は日本語で5行以内。")


def _log(kind: str, body: dict) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.time(), "kind": kind, **body}, ensure_ascii=False) + "\n")


def call_claude(prompt: str) -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        _log("fake", {"prompt": prompt})
        return "（偽のClaudeの固定文）シフト案を確認しました。"
    import anthropic
    req = {"model": MODEL, "max_tokens": 400, "system": SYSTEM,
           "messages": [{"role": "user", "content": prompt}]}
    _log("real", {"request": req})            # 送る直前の本文をそのまま記録
    resp = anthropic.Anthropic(api_key=key).messages.create(**req)
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    _log("real_usage", {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens})
    return text
