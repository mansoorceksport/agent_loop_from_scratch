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
- **So: model for judgment, code for guarantees.** If a business rule must hold
  every single time, enforce it in code — don't write it in a tool description
  and hope.

## Run it

```bash
pip install -r requirements.txt
echo "OLLAMA_API_KEY=your_key_here" > .env
python main.py
```

Uses Ollama Cloud. Swap the model string in `main.py` for any tool-capable model.