# Agent Loop From Scratch

A minimal AI agent loop written by hand in Python — no LangChain, no framework.
I built this to understand what an "agent" actually is, instead of letting a
framework hide it.

## What it does

You type a message. The model can call tools. If it calls a tool, the code runs
it, feeds the result back, and asks the model again — looping until the model
answers in plain text. That loop is the whole idea behind every agent framework.

Tools included as examples:
- `current_time` — returns the real current time (Asia/Jakarta)
- `current_balance` — returns a fake balance
- `congrats_on_balance` — congratulates the user

## The core loop

```python
while response.message.tool_calls:
    response = tool_call_func(response.message.tool_calls)
```

Run every tool the model asked for, send the results back, ask again. Stop when
there are no more tool calls.

## What I learned building it

- **Only the assistant's own reply carries the model's memory.** Storing just
  the user turns is not enough — the model needs its own past messages too.
- **You must append the whole message object, not just the text.** The
  `tool_calls` field has to survive, or the tool result has nothing to attach to.
- **A prompt is a suggestion, not a guarantee.** The model reused a stale time
  even after I told it not to. It also skipped a rule I buried in a tool
  description.

## Where do you put a rule? Three tiers of reliability

I tested one rule — "if the balance is above 500,000, congratulate the user" —
in three different places. The results surprised me.

1. **In the tool description (static).** The model reads it once, at the start,
   before it even has the balance. Reliability: weak. It often skipped the rule,
   because when it read the rule it had no number to act on.

2. **In the tool result (runtime).** Instead of describing the rule up front, I
   returned it *with the data* — the balance and the instruction arrive together,
   at the exact moment the rule becomes true. Reliability jumped to 10/10 in my
   tests. Same words, better placement: the model acts on instructions that sit
   next to fresh, relevant data far more reliably than ones it skimmed earlier.

3. **In code (deterministic).** The code checks the number and calls the tool
   itself. Reliability: 100%, always, forever. The model never gets a vote.

The lesson: **tier 2 raises the odds, tier 3 gives a guarantee.** 10/10 in a test
is not 10/10 forever — change the model, the temperature, or the length of the
conversation and the number drops.

## How I decide which tier to use

One question: **if this rule fails once, does someone get hurt?**

- **Yes** (money, security, a booked slot) → enforce it in code. Tier 3.
- **No** (tone, a nice-to-have nudge like congratulating a high balance) → a rule
  in the tool result is the right tool. Tier 2. You can't hard-code judgment, and
  you don't need to.

**Model for judgment, code for guarantees.**

## Run it

```bash
uv sync
echo "OLLAMA_API_KEY=your_key_here" > .env
echo "MONGO_DB_URI=your_mongo_uri_here" >> .env
uv run agent-loop
```

Uses Ollama Cloud and MongoDB Atlas. Swap the model string in `main.py` for any tool-capable model.

## What I added: a tool with a parameter

`balance_by_date` is the first tool here that takes an argument — a date string —
and returns the balance for that date. Adding one parameter meant handling
everything that can go wrong with it, so this tool has three layers of defense:

- **Format validation in code.** The date must be `YYYY-MM-DD`. I check it with
  `date.fromisoformat` before touching the data, so an impossible date like
  `2026-02-30` is rejected too — not just a wrong shape.
- **Self-healing retry.** When the model sends the wrong format, the tool doesn't
  just fail — it returns the correct format as an instruction. The model reads
  that, fixes the date, and calls the tool again on its own. No human in the loop.
- **Honest handling of missing dates.** A valid date with no record gets a plain
  "no record for that date" and asks the user to confirm — it never invents a
  balance.

I keep the format rule in *both* the system prompt and the code on purpose. The
system prompt is nearly free and gets it right most of the time; the code layer
costs an extra round-trip but never leaks. Cheap probabilistic layer first,
deterministic layer last. That's defense in depth.