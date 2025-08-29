# Choice of LLMs

One of the first questions operators ask is: **“How much is this going to cost me?”**

The answer: *it’s entirely up to you.*

ADIF-MCP doesn’t ship with, or require, a specific Large Language Model (LLM).
Instead, it provides a **standard interface** so you (or developers) can connect whatever model fits your needs, budget, and shack setup:

- **Free / Local Models**
  - Run open-source LLMs (like LLaMA-3, Mistral, or Mixtral) on your own PC, NUC, or server.
  - Tools like [Ollama](https://ollama.ai/) make this easy to run offline, with zero cloud cost.
  - Great for experimenters, DIYers, or anyone who prefers not to rely on the internet.

- **Commercial Cloud Models**
  - Use providers like OpenAI (ChatGPT), Anthropic (Claude), or Google (Gemini).
  - These are “plug and play” with powerful reasoning and large context windows.
  - Costs vary, but many have free tiers and low-cost options for light use.

- **Hybrid Setups**
  - Some operators may use a small free local model for day-to-day queries,
    and keep a stronger paid model in reserve for heavy lifting (e.g., log analysis or award prep).

---

### In short
- **Operators** can choose *free local* if cost is the priority.
- **Developers** can choose *best-in-class paid models* if capability is the priority.
- **Everyone** gets the same MCP backbone — the choice of LLM is up to you.

Just like antennas or radios, there’s no one “right” answer:
**your shack, your choice.**
