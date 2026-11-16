"""LedgerBot, the in-app support assistant.

The "model" here is a small rule-based stand-in for an LLM, so the project runs
without an API key. It is naive in the same way real instruction-following
models are: it cannot tell the user's instructions apart from text that shows
up inside tool results.
"""
import re
from decimal import Decimal

from .models import Account, Transaction
from .services import TransferError, send_money

SYSTEM_PROMPT = (
    "You are LedgerBot, a friendly banking assistant. Tools: list_transactions(), "
    "get_balance(), send_money(to, amount). Only send money when the user asks."
)

USER_SEND_RE = re.compile(r"(?i)\bsend\s+(\d+(?:\.\d{1,2})?)\s*(?:eur|€)?\s+to\s+(SI56\d{10,30})")
# Anything in the context that reads like an instruction addressed to the bot
INSTRUCTION_RE = re.compile(
    r"(?i)\b(?:ledgerbot|assistant|ai)\b[^\n]{0,40}?\b(?:send|transfer)\s+"
    r"(\d+(?:\.\d{1,2})?)\s*(?:eur|€)?\s+to\s+(SI56\d{10,30})"
)


class MockLLM:
    def next_step(self, messages):
        user_msg = next(m["content"] for m in reversed(messages) if m["role"] == "user")
        tool_msgs = [m for m in messages if m["role"] == "tool"]
        done = {(m["name"], m.get("args_key")) for m in tool_msgs}

        if not tool_msgs:
            m = USER_SEND_RE.search(user_msg)
            if m:
                return {"tool": "send_money", "args": {"amount": m.group(1), "to": m.group(2)}}
            if re.search(r"(?i)transaction|spen[dt]|history|summar|payment", user_msg):
                return {"tool": "list_transactions", "args": {}}
            if re.search(r"(?i)balance|how much", user_msg):
                return {"tool": "get_balance", "args": {}}
            return {"reply": "I can show your balance, summarise your transactions or send money."}

        # The model "reads" its whole context, tool output included, and
        # follows anything that looks like an instruction to it.
        context = "\n".join(m["content"] for m in messages)
        for amount, to in INSTRUCTION_RE.findall(context):
            key = f"{to}:{amount}"
            if ("send_money", key) not in done:
                return {"tool": "send_money", "args": {"amount": amount, "to": to}}

        return {"reply": "Here is what I found:\n" + "\n".join(m["content"] for m in tool_msgs)}


def _run_tool(user, name, args):
    acc = Account.objects.get(user=user)
    if name == "list_transactions":
        txs = (Transaction.objects.filter(sender=acc) | Transaction.objects.filter(receiver=acc))
        lines = [
            f"- {t.created:%Y-%m-%d} {t.sender.iban} -> {t.receiver.iban}: {t.amount} EUR, note: {t.note}"
            for t in txs.order_by("-created")[:10]
        ]
        return "\n".join(lines) or "no transactions"
    if name == "get_balance":
        return f"{acc.balance_eur} EUR, {acc.balance_usd} USD"
    if name == "send_money":
        # VULN-12b (LLM06 Excessive Agency): the bot can move money with no
        # confirmation from the user and no limit on the amount
        try:
            tx = send_money(user, args["to"], Decimal(args["amount"]), note="sent by LedgerBot")
        except TransferError as e:
            return f"transfer failed: {e}"
        return f"sent {tx.amount} EUR to {tx.receiver.iban}"
    return "unknown tool"


def chat(user, message, llm=None, max_steps=5):
    llm = llm or MockLLM()
    # VULN-12 (LLM01 Prompt Injection): transaction notes are written by
    # whoever sent the money, but they go into the same context as the
    # system prompt and the user's request, with nothing marking them as data
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    actions = []
    for _ in range(max_steps):
        step = llm.next_step(messages)
        if "reply" in step:
            return {"reply": step["reply"], "actions": actions}
        result = _run_tool(user, step["tool"], step["args"])
        args_key = f'{step["args"].get("to")}:{step["args"].get("amount")}' if step["tool"] == "send_money" else None
        messages.append({"role": "tool", "name": step["tool"], "args_key": args_key, "content": result})
        actions.append({"tool": step["tool"], "args": step["args"], "result": result})
    return {"reply": "Sorry, that took too many steps.", "actions": actions}
