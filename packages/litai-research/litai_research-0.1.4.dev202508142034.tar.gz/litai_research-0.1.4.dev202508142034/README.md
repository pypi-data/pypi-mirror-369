# LitAI

AI-powered literature review assistant that understands your research questions and automatically finds papers, extracts insights, and synthesizes findings - all through natural conversation.

## Meet Pearl

Pearl is your intelligent research assistant within LitAI. Created to help researchers synthesize academic literature, Pearl specializes in addressing real-time research questions - from debugging experiments to contextualizing results - providing actionable insights from existing work to inform your next steps.

## Why LitAI?

LitAI accelerates your research by turning hours of paper reading into minutes of focused insights:

- **Find relevant papers fast**: Natural language search across millions of papers
- **Extract key insights**: AI reads papers and pulls out claims with evidence
- **Synthesize findings**: Ask questions across multiple papers and get cited answers
- **Build your collection**: Manage PDFs locally with automatic downloads from ArXiv

Perfect for:
- Literature reviews for research papers
- Understanding a new field quickly  
- Finding solutions to technical problems
- Discovering contradictions in existing work
- Building comprehensive reading lists

💡 **Tip**: Use the `/synthesize --examples` command to see synthesis example questions organized by phase - from debugging experiments to contextualizing results.

## Installation

### Prerequisites
- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

First [install uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
# Install litai globally
uv tool install litai-research

# Alternative: using pipx
pipx install litai-research
```

### Updates
```bash
# Get latest stable updates
uv tool upgrade litai-research

# Alternative: using pipx
pipx upgrade litai-research
```

### Development/Pre-release
For the latest features (may have bugs):
```bash
# Install pre-release version
uv tool install --prerelease=allow litai-research

# Upgrade to latest pre-release
uv tool upgrade --prerelease=allow litai-research

# Alternative: using pipx
pipx install --prerelease litai-research
pipx upgrade --prerelease litai-research
```

## Configuration

### API Key Setup
Set your OpenAI API key as an environment variable:

**For permanent setup (recommended):**

macOS (zsh - default on modern Macs):
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

Linux (bash):
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**For current session only:**
```bash
export OPENAI_API_KEY=sk-...
```
Note: This only lasts until you close your terminal. Use the permanent setup above to avoid re-entering your key.

Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Editor Setup (Optional)
LitAI automatically defaults to `vi` for editing notes and prompts. To use a different editor:

**macOS:**
- **VS Code**: [Install 'code' command](https://code.visualstudio.com/docs/setup/mac) → `/config set editor vscode`
- **Sublime Text**: [Install 'subl' command](https://www.sublimetext.com/docs/command_line.html) → `/config set editor subl`
- **Cursor**: Works automatically → `/config set editor cursor`

**Linux:** Most editors work out of the box → `/config set editor <name>`

After installing editor commands, reload your shell:
```bash
source ~/.zshrc  # macOS (or ~/.bashrc for Linux)
```

**Note:** For best results, use the smartest models as they are better at understanding complex research questions and tool calling. LitAI defaults to GPT-5, the most capable model. You can switch to GPT-5-mini for faster, more affordable processing, or use any other model offered by OpenAI.

**💡 Tip:** You may be eligible for complimentary tokens by sharing data with OpenAI for model improvement. [Learn more about the data sharing program](https://help.openai.com/en/articles/10306912-sharing-feedback-evaluation-and-fine-tuning-data-and-api-inputs-and-outputs-with-openai).

<details>
<summary>Advanced Configuration</summary>

Configure LitAI using the `/config` command:
```bash
# Show current configuration
/config show

# Change model (defaults to gpt-5)
/config set llm.model gpt-5-mini  # Use the faster, more affordable model

# Reset to defaults
/config reset
```

Configuration is stored in `~/.litai/config.json` and persists across sessions.
</details>

## Getting Started

### 1. Launch LitAI
```bash
litai
```

### 2. Set Up Your Research Context (Recommended)
Provide context about your research to get more tailored responses:

```bash
/prompt
```

This opens your default editor with a template where you can describe:
- **Research Context**: Your area of study and current focus
- **Background & Expertise**: Your academic/professional background
- **Specific Interests**: Particular topics, methods, or problems you're investigating  
- **Preferences**: How you prefer information to be presented or synthesized

**Example research context:**
```markdown
## Research Context
I'm a PhD student researching efficient transformer architectures for edge deployment. Currently focusing on knowledge distillation and pruning techniques for large language models.

## Background & Expertise
- Strong background in deep learning and PyTorch
- Experience with model compression techniques
- Familiar with transformer architectures and attention mechanisms

## Specific Interests
- Structured pruning methods that maintain model accuracy
- Hardware-aware neural architecture search
- Quantization techniques for transformers

## Preferences
- When synthesizing papers, please highlight actual compression ratios achieved
- I prefer concrete numbers over vague claims
- Interested in both positive and negative results
```

**Why this matters**: This context gets automatically included in every AI conversation, helping LitAI understand your expertise level and tailor responses accordingly. Without it, LitAI treats every user the same way.

### 3. How LitAI Works

**Natural Language + Commands**: LitAI understands both natural language and slash commands, letting you work how you prefer:

```bash
litai ▸ "Find papers about attention mechanisms"           # Natural language search
litai ▸ "Add the Transformer paper to my collection"       # Natural language add
litai ▸ /papers                                            # View your collection
litai ▸ /note 1                                           # Add personal notes
litai ▸ /tag 1 -a transformers                            # Organize with tags
```

**Context Management**: Build your research context naturally or with commands:
```bash
litai ▸ "Add BERT paper with full text to context"        # Natural language
litai ▸ /cadd "attention paper" abstract                  # Command for specific control
litai ▸ /cshow                                            # Show current context
```

**Synthesis & Analysis**: Analyze papers in your context:
```bash
litai ▸ /cadd "BERT paper" full_text                      # Add to context first
litai ▸ /cadd "GPT paper" full_text                       # Add another paper
litai ▸ /cshow                                            # Check what's in context
litai ▸ /synthesize "What are the key findings?"                     # Ask about context papers
```

**The Workflow:**
1. **Find Papers**: `"Find papers about [topic]"` or `/find <query>`
2. **Build Collection**: `"Add papers 1,2,3"` or `/add <numbers>` to save papers
3. **Add Notes** (optional): `/note <number>` to add your thoughts
4. **Add to Context**: `"Add BERT paper to context"` or `/cadd <paper>` - only papers in context are analyzed
5. **Synthesize**: `/synthesize` to analyze and ask questions about papers in your context

> **Important**: `/synthesize` only works with papers you've added to context. Your collection can have hundreds of papers, but synthesis operates on your focused context.

### 4. Build Your Research Workflow

**For New Research Areas:**
1. `"Find recent papers about [topic]"` → Search for papers
2. `"Add the most cited papers"` → Save to your collection
3. `"Add top 3 papers to context with abstracts"` → Select papers for analysis
4. `/synthesize "What are the main approaches in this field?"` → Synthesize insights

**For Literature Reviews:**
1. Build collection with `/find` + `/add` (accumulate many papers)
2. Add notes (`/note`) and organize with tags (`/tag`)
3. Add specific papers to context: `/cadd <paper> full_text` for detailed analysis
4. `/synthesize "Compare methodologies"` → Analyzes only context papers

> **Key Insight**: Use natural language for exploration, commands for precise control

## Features

### 🔍 Paper Discovery & Management
- **Smart Search**: Natural language queries across millions of papers via Semantic Scholar
- **Intelligent Collection**: Automatic duplicate detection and citation key generation
- **PDF Integration**: Automatic ArXiv downloads with local storage
- **Flexible Organization**: Tags, notes, and configurable paper list views
- **Import Support**: BibTeX file import for existing libraries

### 🤖 AI-Powered Analysis
- **Key Point Extraction**: Automatically extract main claims with evidence
- **Deep Synthesis**: Interactive synthesis with `/synthesize` for collaborative exploration  
- **Context-Aware**: Multiple context depths (abstracts, notes, key points, full text)
- **Agent Notes**: AI-generated insights and summaries for papers
- **Research Context**: Personal research profile for tailored responses

### 💬 Interactive Experience
- **Natural Language Interface**: Chat naturally about your research
- **Command Autocomplete**: Tab completion for all commands and file paths
- **Vi Mode Support**: Optional vi-style keybindings
- **Session Management**: Persistent conversations with paper selections
- **Research Questions**: Built-in prompts to unblock research at any phase

### ⚙️ Advanced Features
- **Configurable Display**: Customize paper list columns and layout
- **Tool Approval System**: Control AI tool usage for all operations
- **Comprehensive Logging**: Debug and track all operations
- **Multi-LLM Support**: OpenAI and Anthropic models with auto-detection

## Command Reference

### Essential Commands
```bash
/find <query>          # Search for papers  
/find <query> --append # Add results to existing search (cumulative search)
/find --clear          # Clear all search results
/find --recent         # Show search history with contribution counts
/add <numbers>         # Add papers from search results
/papers [page]         # List your collection (with pagination)
/synthesize            # Analyze papers in context (must add papers to context first)
/note <number>         # Manage paper notes
/tag <number> -a <tags>  # Add tags to papers
/prompt                # Set up your research context (recommended)
/synthesize --examples # Show synthesis example questions
/help                  # Show all commands
```

### Search Command Options (Cumulative Search)
```bash
/find <query> --append # Add results to previous searches (build comprehensive collections)
/find --clear          # Clear all accumulated search results
/find --recent         # View search history with timestamps and paper counts
```

**Example: Building a comprehensive literature review**
```bash
litai ▸ /find "transformer architectures"              # Initial search
litai ▸ /find "attention mechanisms" --append          # Add more papers
litai ▸ /find "BERT GPT models" --append              # Keep building
litai ▸ /find --recent                                # Review search history
litai ▸ /add 1-15                                     # Add papers 1 through 15 to collection
```

> **Note**: Cumulative search automatically deduplicates papers and limits results to 100 papers maximum

### Papers Command Options
```bash
/papers --tags         # Show all tags with counts
/papers --notes        # Show papers with notes
/papers 2              # Show page 2 of collection
```

### Research Context Commands
```bash
/prompt                # Edit your research context (opens in editor)
/prompt view           # Display your current research context
/prompt append "text"  # Add text to your existing context
/prompt clear          # Delete your research context
```

### Configuration
```bash
/config show           # Display current settings
/config set llm.model gpt-4o-mini
/config set tool_approval false  # Disable approval prompts
/config set display.list_columns title,authors,tags,notes
```

> **Note**: Configuration changes require restarting LitAI to take effect

### Natural Language vs Commands

**Natural Language** - Flexible exploration:
```bash
"Find papers about attention mechanisms"
"Add the top 3 papers to my collection"
"What are the key insights from the BERT paper?"
"Compare methodologies across my papers"
"Add all transformer papers to context with abstracts"
"Remove outdated papers from context"
```

**Slash Commands** - Precise control:
```bash
/find <query>          # Search for papers  
/add <numbers>         # Add papers from search results
/papers [page]         # List your collection
/note <number>         # Add your personal notes
/tag <number> -a <tags>  # Add tags to papers
/cadd <paper> <type>   # Add paper to context
/cshow                 # Show current context
/synthesize <question> # Synthesize insights from papers
```

**Synthesis** (`/synthesize` - works on context papers only):
```bash
# First, add papers to context:
litai ▸ /cadd "transformer paper" full_text
litai ▸ /cadd "BERT paper" abstract
litai ▸ /cshow                            # Shows papers in context

# Then synthesize:
litai ▸ /synthesize "How do these models handle context?"  # Ask synthesis question
litai ▸ /synthesize "What are the key insights?"
litai ▸ /synthesize "How do these approaches compare?"
litai ▸ /synthesize --examples            # Show example questions
```

### Notes System
- **Personal Notes** (`/note` in normal mode): Your own thoughts and observations
- **AI Notes** (request in synthesis mode): Ask AI to generate insights and summaries for papers

## Data Storage

LitAI stores all data locally in `~/.litai/`:
- `litai.db` - SQLite database with paper metadata and extractions
- `pdfs/` - Downloaded PDF files  
- `logs/litai.log` - Application logs for debugging
- `config.json` - User configuration
- `user_prompt.txt` - Personal research context

### Database Management

The LitAI database (`~/.litai/db/litai.db`) is a standard SQLite database that you can explore and manage with any SQLite-compatible tool. We recommend [Beekeeper Studio](https://www.beekeeperstudio.io/) for its user-friendly interface, but you can use any database tool you prefer.

**To open the database in Beekeeper Studio:**

1. Download and install [Beekeeper Studio](https://www.beekeeperstudio.io/)
2. Open Beekeeper Studio and click "New Connection"
3. Select "SQLite" as the database type
4. Click "Browse" and navigate to: `~/.litai/db/litai.db`
   - **macOS tip**: Hidden files (starting with `.`) may not be visible in Finder by default. Press `Command + Shift + .` to show hidden files
5. Click "Connect"

You can now browse tables, run queries, and explore your research data directly.

## FAQ

### Why do paper searches sometimes fail?

Semantic Scholar's public API can experience high load, leading to search failures. If you encounter frequent issues:
- Wait a few minutes and try again
- Consider requesting a free API key for higher rate limits: [Semantic Scholar API Key Form](https://www.semanticscholar.org/product/api#api-key-form)

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Semantic Scholar API](https://www.semanticscholar.org/product/api)
- Powered by OpenAI/Anthropic language models

## Support

- Report issues: [GitHub Issues](https://github.com/harmonbhasin/litai/issues)
- Logs for debugging: `~/.litai/logs/litai.log`
