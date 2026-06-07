# Using claude-mem with UI UX Pro Max

[claude-mem](https://github.com/thedotmack/claude-mem) is a persistent memory plugin for Claude Code that compresses and stores session observations, making them available in future sessions. Paired with UI UX Pro Max, it preserves your design decisions, generated design systems, and UI/UX reasoning across sessions — so Claude doesn't start from scratch each time.

## Why they work well together

UI UX Pro Max generates detailed design systems (colors, typography, style patterns, anti-patterns) for your project. Without a memory layer, these decisions vanish when the session ends. With claude-mem:

- Generated design systems are stored as semantic observations
- Style decisions ("we chose Glassmorphism for the SaaS dashboard") persist across restarts
- Anti-patterns flagged for your product type are remembered
- Stack-specific guidelines are carried over between sessions

## Installation

Install both tools independently:

```bash
# Install UI UX Pro Max
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill

# Install claude-mem
npx claude-mem install
```

Restart Claude Code after installing claude-mem for hooks to activate.

## Recommended workflow

### 1. Generate and persist your design system

Use the `--persist` flag to write the design system to files:

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" \
  --design-system --persist -p "MyApp"
```

This creates `design-system/MASTER.md` — a file claude-mem will observe and reference in future sessions.

### 2. Let claude-mem capture design decisions

As you work, claude-mem automatically stores observations from your session. Design-related decisions are captured as they happen — no manual steps required.

### 3. Retrieve context in new sessions

When you start a new session, claude-mem injects relevant past observations. You can also query memory directly:

```
Search memory for: UI design decisions for MyApp
```

Or use the mem-search skill (if installed via claude-mem):

```
/mem-search glassmorphism dashboard decisions
```

### 4. Reference persisted design files

Always include your design system files in context for consistent output:

```
I am building the Checkout page.
Read design-system/MASTER.md first.
Also check design-system/pages/checkout.md if it exists.
Now generate the checkout form component.
```

## Privacy

claude-mem supports `<private>` tags. If you want to prevent specific design notes from being stored:

```
<private>Client API keys and internal pricing data</private>
```

Content inside `<private>` tags is excluded from memory storage.

## Web viewer

claude-mem provides a web viewer at `http://localhost:37777` where you can browse all stored design observations, search by query, and review the full session history for your project.

## Further reading

- [claude-mem documentation](https://docs.claude-mem.ai/)
- [UI UX Pro Max — Persist Design System](../README.md#persist-design-system-master--overrides-pattern)
- [claude-mem search tools](https://docs.claude-mem.ai/usage/search-tools)
