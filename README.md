# OpenJupy (OpenUp)

> **Bridge the gap between production Jupyter and AI-native workflows.**

OpenJupy is a high-performance middleware layer designed to integrate `jupyter-mcp-server` (Datalayer) with the **OpenCode** environment. It enriches standard Jupyter execution outputs with "Smart Tips," "Interactive Heal Suggestions," and "Next-Step Guidance" to turn standard notebooks into a collaborative AI laboratory.

---

## 🚀 Key Features

### 1. Smart Error Recovery ("Self-Healing")
When a code cell fails, OpenJupy intercepts the Python traceback and provides:
- **`claude_tip`**: A plain-English explanation of why the crash happened.
- **`suggested_action`**: A ready-to-run terminal command (e.g., `uv add pandas`) to fix the environment instantly.
- **Traceback Mapping**: Structured error data that allows the AI to pinpoint the exact line of failure.

### 2. Context-Aware Guidance
The middleware inspects your active Python namespace and proactively suggests the next steps:
- **DataFrame detection**: Automatically suggests `df.head()` or `df.describe()`.
- **Plotting assistance**: Validates that visualizations are correctly rendered and accessible.
- **Variable tracking**: Keeps the AI informed of defined variables to prevent redundant imports.

### 3. Real-Time Collaboration (RTC)
Watch the AI work live in your browser (`localhost:8888`) while it operates from OpenCode. You can manually edit a cell in the browser, and the AI will "see" your changes in the next turn.

---

## 🛠 Setup & Installation

### 1. Environment Preparation
Set your persistent Jupyter token in your `~/.zshrc`:
```bash
export JUPYTER_TOKEN="your-secret-password"
```

### 2. Start the Engine
From your project root (e.g., your complex data pipeline directory):
```bash
uv tool run --from jupyterlab jupyter lab --port 8888 --IdentityProvider.token "your-secret-password"
```

### 3. Configure OpenCode
Add the `jupyter` MCP to your `opencode.json` and the `data-scientist` agent to your `oh-my-opencode.json` (see `agent-config/` for snippets).

---

## 💡 Use Cases

### 🔬 The "Pipeline Laboratory" (Best for Complex Projects)
Test extensive, multi-stage data pipelines function-by-function.
- **Problem**: Running a 10-minute extraction script only to have it crash on a simple plotting error in phase 5.
- **OpenUp Solution**: Run the extraction once. The state is kept in the persistent kernel. Debug and fix the plotting phase in seconds without re-loading the data.

### 📊 Autonomous EDA (Exploratory Data Analysis)
Drop a CSV into a directory and ask the **Data Scientist** agent to analyze it.
- OpenUp will guide the agent to perform a systematic EDA, suggesting schema checks and distribution plots based on the data it "sees" in the namespace.

### 🧪 API Development & Testing
Test live API endpoints or database connections interactively.
- Define your connection objects in one turn and use them to test multiple query variations across several chat turns without re-authenticating.

---

## 📖 Further Reading
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md): Detailed configuration guide.
- [WALKTHROUGH_DATA_PIPELINES.md](WALKTHROUGH_DATA_PIPELINES.md): Step-by-step guide for debugging large Python projects.
- [IMPLEMENTATION_PLAN.md](OpenJupy/IMPLEMENTATION_PLAN.md): Technical roadmap and project architecture.
