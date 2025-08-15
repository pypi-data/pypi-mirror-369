"""Main CLI entry point for LitAI."""

import asyncio
import os
import shlex
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from typing import Any

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style
from pyfiglet import Figlet
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

from litai.commands.config import handle_config_command
from litai.commands.context_commands import (
    handle_context_add,
    handle_context_clear,
    handle_context_modify,
    handle_context_remove,
    handle_context_show,
    show_context_add_help,
    show_context_modify_help,
    show_context_remove_help,
)
from litai.commands.synthesize import handle_synthesize_command
from litai.commands.tokens import format_session_summary_compact, handle_tokens_command
from litai.config import Config
from litai.context_manager import SessionContext
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler
from litai.output_formatter import OutputFormatter
from litai.paper_resolver import resolve_paper_references
from litai.semantic_scholar import SemanticScholarClient
from litai.token_tracker import TokenTracker
from litai.utils.log_context import operation_context
from litai.utils.log_events import Events
from litai.utils.logger import get_logger, setup_logging

# Define a neutral theme that works well on both dark and light terminals
# Strategy: Use terminal defaults + bold/dim for hierarchy, colors only for important alerts
custom_theme = Theme(
    {
        # Core semantic colors - only for important states
        "success": "green",  # Terminal's green (adapts to background)
        "warning": "yellow",  # Terminal's yellow (visible on both)
        "error": "red",  # Terminal's red (for errors only)
        
        # Text hierarchy using weight/style instead of color
        "primary": "bold",  # Important text uses bold
        "secondary": "default",  # Normal text uses terminal default
        "dim_text": "dim",  # Less important text uses dim
        
        # Specific UI elements
        "heading": "bold",  # Headers use bold for emphasis
        "command": "bold cyan",  # Commands in cyan (good contrast on both)
        "info": "dim",  # Informational text is dimmed
        "accent": "bold",  # Accents use bold instead of color
        "number": "bold",  # Numbers stand out with bold
        
        # Collection-specific (minimal color use)
        "command.collection": "bold",  # Collection commands use bold
        "command.analysis": "bold",  # Analysis commands use bold
    },
)

console = Console(theme=custom_theme)
logger = get_logger(__name__)
output = OutputFormatter(console)

# Global search results storage (for /add command)
_search_results: list[Paper] = []

# Search metadata for cumulative search tracking
_search_metadata: dict[str, list] = {
    "queries": [],  # List of search queries performed
    "timestamps": [],  # When each search was done
    "counts": [],  # Papers found per search
}


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool) -> None:
    """LitAI - AI-powered academic paper synthesis tool."""
    import uuid
    
    setup_logging(debug=debug)

    # Generate unique session ID for tracking
    session_id = str(uuid.uuid4())[:8]
    
    with operation_context("cli_session", session_id=session_id, debug=debug):
        logger.info(Events.APP_STARTED, debug=debug)

        # Initialize configuration and database
        config = Config()
        db = Database(config)

        # Generate personalized time-based greeting

        now = datetime.now()
        hour = now.hour

        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        elif hour < 21:
            greeting = "Good evening"
        else:
            greeting = "Good night"

        # Get research snapshot data
        paper_count = db.count_papers()
        papers = db.list_papers(limit=100) if paper_count > 0 else []

        # Count read papers (those with key_points extraction)
        read_count = 0
        last_read_paper = None
        for paper in papers:
            if db.get_extraction(paper.paper_id, "key_points") is not None:
                read_count += 1
                if last_read_paper is None or (
                    paper.added_at and paper.added_at > last_read_paper.added_at
                ):
                    last_read_paper = paper

        # Count papers with notes
        notes_count = len(db.list_papers_with_notes())

        # Get last synthesis activity
        last_synthesis = db.get_last_synthesis_time()

        # Build personalized greeting
        from rich.columns import Columns
        from rich.panel import Panel

        # larry3d, isometric1, smkeyboard, epic, slant, ogre, crawford
        fig = Figlet(font="larry3d")
        console.print("\n")
        console.print(fig.renderText("LitAI"), style="bold")

        console.print(f"\n[heading]{greeting}! Welcome back to LitAI[/heading]\n")

        if paper_count > 0:
            # Left column - research snapshot
            snapshot_lines = [
                "[bold]▚ Your research collection:[/bold]",
                f"  • [info]{paper_count}[/info] papers collected",
                f"  • [accent]{read_count}[/accent] papers analyzed",
            ]

            if notes_count > 0:
                snapshot_lines.append(
                    f"  • [number]{notes_count}[/number] papers with notes",
                )

            if last_synthesis:
                time_diff = datetime.now() - last_synthesis
                if time_diff.days > 0:
                    time_str = (
                        f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                    )
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    minutes = time_diff.seconds // 60
                    time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                snapshot_lines.append(f"  • Last synthesis: [dim]{time_str}[/dim]")

            if last_read_paper:
                snapshot_lines.append(
                    f'  • Recently read: [dim]"{last_read_paper.title[:40]}..."[/dim]',
                )

            # Right column - natural language examples
            commands_lines = [
                "[bold]Continue your research:[/bold]",
                '"Find more papers about transformers"',
                '"What are the key insights from my recent papers?"',
                '"Compare the methods across my collection"',
                '"Show papers where I\'ve added notes"',
            ]

            # Add empty line if needed to match left column height
            if len(snapshot_lines) > len(commands_lines):
                commands_lines.append("")

            # Create columns with minimal spacing
            left_panel = Panel(
                "\n".join(snapshot_lines), border_style="none", padding=(0, 1, 0, 0),
            )
            right_panel = Panel(
                "\n".join(commands_lines), border_style="none", padding=(0, 0, 0, 1),
            )

            columns = Columns(
                [left_panel, right_panel], equal=False, expand=False, padding=(0, 2),
            )
            console.print(columns)

            console.print(
                "\n[dim_text]» Ask questions naturally and let AI handle the commands, or run them yourself[/dim_text]",
            )
            console.print(
                "[dim_text]   Need ideas? Try [command]/synthesize --examples[/command] for synthesis example questions[/dim_text]",
            )
            console.print(
                "[dim_text]   See [command]/help[/command] for all commands or use [command]--help[/command] flag with any command[/dim_text]",
            )

            # Show vi mode status if enabled
            if config.get_vi_mode():
                console.print(
                    "[dim_text]   Vi mode is enabled • Press ESC to enter normal mode[/dim_text]",
                )

            console.print()  # Add blank line
        else:
            # For new users, show research workflow with natural language first
            console.print("[bold]Start your research workflow (run these in order):[/bold]")
            console.print(
                '1. "Find papers about attention mechanisms" [dim_text](searches for papers)[/dim_text]',
            )
            console.print(
                "2. \"Add 'Attention Is All You Need' to my collection\" [dim_text](saves found papers)[/dim_text]",
            )
            console.print(
                '3. "What are the key insights from the BERT paper?" [dim_text](analyzes saved papers)[/dim_text]',
            )
            console.print(
                '4. "How do Vision Transformer\'s methods compare to other papers?" [dim_text](synthesizes across collection)[/dim_text]',
            )
            console.print(
                "\n[dim_text]Or use commands directly: [command]/find[/command], [command]/add[/command], [command]/synthesize[/command][/dim_text]",
            )
            console.print(
                "[dim_text]Need help? • [command]/help[/command] shows all commands • Use [command]--help[/command] flag with any command[/dim_text]",
            )

        chat_loop(db)


class CommandCompleter(Completer):
    """Custom completer for LitAI commands."""

    def __init__(self) -> None:
        # Controls autocomplete for commands
        self.commands = {
            "/find": "Search for papers",
            "/add": "Add paper to collection",
            "/papers": "List and manage papers in your collection",
            "/remove": "Remove paper(s) from collection",
            "/synthesize": "Synthesize insights from papers in context",
            "/note": "Manage notes for a paper",
            "/tag": "Manage tags for a paper",
            "/import": "Import papers from BibTeX file",
            "/prompt": "Manage your personal research background and preferences",
            "/cadd": "Add papers to context",
            "/cremove": "Remove papers from context",
            "/cshow": "Show current context",
            "/cclear": "Clear all context",
            "/cmodify": "Modify paper context type",
            "/help": "Show all commands",
            "/clear": "Clear console, chat history, and context",
            "/config": "Manage model & system configuration",
            "/tokens": "View token usage ",
        }

    def get_completions(self, document: Any, complete_event: Any) -> Any:
        """Get completions for the current input."""
        text = document.text_before_cursor
        
        # Commands that support --help flag
        help_enabled_commands = [
            "/find", "/papers", "/add", "/remove", 
            "/synthesize", "/note", "/tag", "/prompt", "/config", "/tokens",
            "/cadd", "/cremove", "/cshow", "/cclear", "/cmodify", "/clear",
        ]

        # Flag completion for /find command
        if text.startswith("/find "):
            remaining = text[6:].strip()  # Remove "/find "
            if remaining.startswith("-"):
                # Suggest flags
                flags = ["--recent", "--help"]
                for flag in flags:
                    if flag.startswith(remaining):
                        yield Completion(
                            f"/find {flag}",
                            start_position=-len(text),
                            display=flag,
                            display_meta="Show recent results" if flag == "--recent" else "Show help",
                        )
            return

        # Flag completion for /papers command
        if text.startswith("/papers "):
            remaining = text[8:].strip()  # Remove "/papers "
            if remaining.startswith("-"):
                # Suggest flags
                flag_options = [
                    ("--tags", "Show all tags"),
                    ("--notes", "Show papers with notes"),
                    ("--help", "Show help"),
                ]
                for flag, desc in flag_options:
                    if flag.startswith(remaining):
                        yield Completion(
                            f"/papers {flag}",
                            start_position=-len(text),
                            display=flag,
                            display_meta=desc,
                        )
            return
        
        # Flag completion for /synthesize command
        if text.startswith("/synthesize "):
            remaining = text[12:].strip()  # Remove "/synthesize "
            if remaining.startswith("-"):
                # Suggest flags
                flag_options = [
                    ("--examples", "Show example synthesis questions"),
                    ("--help", "Show help"),
                ]
                for flag, desc in flag_options:
                    if flag.startswith(remaining):
                        yield Completion(
                            f"/synthesize {flag}",
                            start_position=-len(text),
                            display=flag,
                            display_meta=desc,
                        )
            return
            
        # Generic --help flag completion for other commands
        for cmd in help_enabled_commands:
            if cmd in ["/find", "/papers", "/synthesize"]:  # Skip commands with custom handling
                continue
            if text.startswith(f"{cmd} "):
                remaining = text[len(cmd)+1:].strip()
                if remaining.startswith("-") and "--help".startswith(remaining):
                        yield Completion(
                            f"{cmd} --help",
                            start_position=-len(text),
                            display="--help",
                            display_meta="Show help",
                        )
                return

        # Path completion for /import
        if text.startswith("/import "):
            path = text[8:]  # Remove "/import "
            original_path = path  # Keep original for completion
            path = os.path.expanduser(path)  # Handle ~/
            
            if path and not path.endswith('/'):
                dir_path = os.path.dirname(path) or "."
                prefix = os.path.basename(path)
            else:
                dir_path = path or "."
                prefix = ""
            
            try:
                for name in os.listdir(os.path.expanduser(dir_path)):
                    if name.startswith(prefix):
                        full = os.path.join(dir_path, name)
                        if os.path.isdir(full):
                            name += "/"
                        elif not name.endswith(('.pdf', '.bib')):
                            continue
                        
                        # Build the completion text (without /import prefix)
                        if original_path.endswith('/'):
                            completion = original_path + name
                        else:
                            completion = os.path.join(os.path.dirname(original_path), name) if os.path.dirname(original_path) else name
                        
                        # The key fix: prepend "/import " to the completion
                        full_completion = "/import " + completion
                        
                        yield Completion(
                            full_completion,
                            start_position=-len(text),  # Replace entire text including "/import "
                            display=name,
                        )
            except Exception:
                pass
            return

        # Only complete if user started typing a command
        if not text.startswith("/"):
            return

        # Get matching commands
        for cmd, description in self.commands.items():
            if cmd.startswith(text):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta=description,
                )


def chat_loop(db: Database) -> None:
    """Main interactive chat loop."""
    global _search_results

    # Initialize config once for all commands
    config = Config()
    session_context = SessionContext()
    
    # Initialize token tracker for usage monitoring
    token_tracker = TokenTracker(config)

    # Create minimal style for better readability
    style = Style.from_dict(
        {
            # Ensure completion menu has good contrast
            "completion-menu.completion": "",  # Use terminal defaults
            "completion-menu.completion.current": "reverse",  # Invert colors for selection
            "completion-menu.meta.completion": "fg:ansibrightblack",  # Dimmed description
            "completion-menu.meta.completion.current": "reverse",  # Invert for selection
        },
    )

    # Create command completer and prompt session
    completer = CommandCompleter()
    session: PromptSession = PromptSession(
        completer=completer,
        complete_while_typing=False,  # Only show completions on Tab
        mouse_support=True,
        # Ensure completions appear below the input
        reserve_space_for_menu=0,  # Don't reserve space, show inline
        complete_style=CompleteStyle.MULTI_COLUMN,
        style=style,
        vi_mode=config.get_vi_mode(),  # Enable vi mode based on config
    )

    # Create natural language handler with command mappings
    command_handlers: dict[str, Callable[..., Any]] = {
        "find_papers": find_papers,
        "add_paper": add_paper,
        "list_papers": list_papers,
        "remove_paper": remove_paper,
        "show_search_results": show_search_results,
        "handle_tag_command": handle_tag_command,
        "list_tags": list_tags,
        "handle_context_add": handle_context_add,
        "handle_context_remove": handle_context_remove,
        "handle_context_modify": handle_context_modify,
        "handle_context_show": handle_context_show,
        "handle_synthesize": handle_synthesize_command,
    }

    nl_handler = NaturalLanguageHandler(db, command_handlers, _search_results, config, session_context, token_tracker)

    try:
        while True:
            try:
                prompt_text = HTML("<ansiblue><b>pearl▸</b></ansiblue> ")

                # Use prompt_toolkit for rich input
                user_input = session.prompt(
                    prompt_text,
                    default="",
                )

                # Skip empty lines
                if not user_input.strip():
                    continue

                # Log user input
                logger.info("user_input", input=user_input)

                if user_input.lower() in ["exit", "quit", "q"]:
                    logger.info("user_exit", method=user_input.lower())
                    console.print("[warning]Goodbye![/warning]")
                    break


                if user_input.startswith("/"):
                    handle_command(user_input, db, config, session_context, token_tracker, nl_handler)
                elif user_input.lower() == "clear":
                    handle_clear_command("", nl_handler, session_context)
                else:
                    # Handle natural language query
                    import uuid
                    nl_request_id = str(uuid.uuid4())[:8]
                    with operation_context("natural_language_query", request_id=nl_request_id, query=user_input):
                        asyncio.run(nl_handler.handle_query(user_input))

            except KeyboardInterrupt:
                console.print("\n[warning]Tip: Use 'exit' to quit.[/warning]")
            except Exception as e:
                logger.exception("Unexpected error in chat loop")
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
    finally:
        # Show session summary on exit
        try:
            session_summary = token_tracker.get_session_summary()
            if session_summary["total"] > 0:
                summary_text = format_session_summary_compact(session_summary)
                console.print(f"\n[dim_text]{summary_text}[/dim_text]")
        except Exception:
            # Don't let token summary errors break exit
            pass
        
        # Cleanup the NL handler when exiting
        with suppress(Exception):
            asyncio.run(nl_handler.close())

        # Cleanup the Semantic Scholar client
        try:
            from litai.semantic_scholar import SemanticScholarClient

            asyncio.run(SemanticScholarClient.shutdown())
        except Exception:
            # Ignore errors during cleanup
            pass


# Context command wrappers to handle LLMClient and extraction dependencies
async def handle_context_add_wrapper(args: str, db: Database, session_context: SessionContext, config: Config, token_tracker: TokenTracker | None = None) -> None:
    """Wrapper for handle_context_add that creates LLMClient."""
    await logger.ainfo("handle_context_add_wrapper_start", args=args)
    
    # Check for --help flag first (before creating LLMClient)
    if args and args.strip() == "--help":
        console.print(show_context_add_help())
        return
    
    llm_client = LLMClient(config, token_tracker=token_tracker)
    try:
        # For now, we'll handle extraction logic here since we don't have PaperExtractor
        result = await handle_context_add_simple(args, db, session_context, llm_client)
        if result:
            console.print(result)
        await logger.ainfo("handle_context_add_wrapper_complete")
    except Exception as e:
        await logger.aerror("handle_context_add_wrapper_error", error=str(e))
        console.print(f"[red]Error adding to context: {str(e)}[/red]")
    finally:
        await llm_client.close()

async def handle_context_remove_wrapper(args: str, db: Database, session_context: SessionContext, config: Config, token_tracker: TokenTracker | None = None) -> None:
    """Wrapper for handle_context_remove that creates LLMClient."""
    await logger.ainfo("handle_context_remove_wrapper_start", args=args)
    
    # Check for --help flag first (before creating LLMClient)
    if args and args.strip() == "--help":
        console.print(show_context_remove_help())
        return
    
    llm_client = LLMClient(config, token_tracker=token_tracker)
    try:
        result = await handle_context_remove(args, db, session_context, llm_client)
        if result:
            console.print(result)
        await logger.ainfo("handle_context_remove_wrapper_complete")
    except Exception as e:
        await logger.aerror("handle_context_remove_wrapper_error", error=str(e))
        console.print(f"[red]Error removing from context: {str(e)}[/red]")
    finally:
        await llm_client.close()

async def handle_context_modify_wrapper(args: str, db: Database, session_context: SessionContext, config: Config, token_tracker: TokenTracker | None = None) -> None:
    """Wrapper for handle_context_modify that creates LLMClient."""
    await logger.ainfo("handle_context_modify_wrapper_start", args=args)
    
    # Check for --help flag first (before creating LLMClient)
    if args and args.strip() == "--help":
        console.print(show_context_modify_help())
        return
    
    llm_client = LLMClient(config, token_tracker=token_tracker)
    try:
        # For now, we'll handle extraction logic here since we don't have PaperExtractor
        result = await handle_context_modify_simple(args, db, session_context, llm_client)
        if result:
            console.print(result)
        await logger.ainfo("handle_context_modify_wrapper_complete")
    except Exception as e:
        await logger.aerror("handle_context_modify_wrapper_error", error=str(e))
        console.print(f"[red]Error modifying context: {str(e)}[/red]")
    finally:
        await llm_client.close()

# Simplified versions that don't use PaperExtractor
async def handle_context_add_simple(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """Simplified version of handle_context_add without PaperExtractor."""
    await logger.ainfo("context_add_command_start", args=args)
    
    if not args:
        await logger.awarning("context_add_command_no_args")
        return "[red]Usage: /cadd <paper reference> [full-text|abstract|notes][/red]"
    
    # Parse context type if provided (default to full-text)
    context_type = "full_text"
    paper_ref = args
    
    # Check if context type is specified
    for ct in ["full-text", "full_text", "abstract", "notes"]:
        if args.endswith(f" {ct}"):
            context_type = ct.replace("-", "_")
            paper_ref = args[:-len(f" {ct}")].strip()
            break
    
    await logger.ainfo("context_add_parsed", paper_ref=paper_ref, context_type=context_type)
    
    # Resolve paper reference to a single paper ID
    await logger.ainfo("context_add_resolving_paper", paper_ref=paper_ref)
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
    
    if not paper_id:
        await logger.awarning("context_add_paper_not_found", paper_ref=paper_ref)
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"
    
    await logger.ainfo("context_add_paper_resolved", paper_id=paper_id)
    
    # Get the paper
    paper = db.get_paper(paper_id)
    if not paper:
        await logger.aerror("context_add_paper_not_in_db", paper_id=paper_id)
        return f"[red]Paper not found in database: {paper_id}[/red]"
    
    # Check if already in context
    if session_context.has_paper(paper_id):
        # Paper already in context, add new context type
        entry = session_context.papers[paper_id]
        if context_type in entry.context_types:
            await logger.awarning("context_add_duplicate_type", paper_id=paper_id, context_type=context_type)
            return f"[yellow]Paper already has {context_type} in context[/yellow]"
        await logger.ainfo("context_add_existing_paper", paper_id=paper_id, existing_types=list(entry.context_types))
    
    # Extract content based on context type (simplified without PaperExtractor)
    await logger.ainfo("context_add_extracting_content", paper_id=paper_id, context_type=context_type)
    content = ""
    if context_type == "full_text":
        # Get full text extraction
        extraction = db.get_extraction(paper_id, "full_text")
        if extraction:
            content = extraction.content
            await logger.ainfo("context_add_used_full_text_extraction", paper_id=paper_id)
        else:
            # Fallback to abstract since we don't have PaperExtractor
            content = paper.abstract
            await logger.ainfo("context_add_fallback_to_abstract", paper_id=paper_id)
    elif context_type == "notes":
        extraction = db.get_extraction(paper_id, "key_points")
        if extraction:
            content = extraction.content
            await logger.ainfo("context_add_used_notes_extraction", paper_id=paper_id)
        else:
            content = "No notes available. Using abstract."
            content += f"\n\n{paper.abstract}"
            await logger.ainfo("context_add_fallback_notes_to_abstract", paper_id=paper_id)
    else:  # abstract
        content = paper.abstract
        await logger.ainfo("context_add_using_abstract", paper_id=paper_id)
    
    # Add to session context
    session_context.add_paper(
        paper_id=paper_id,
        paper_title=paper.title,
        context_type=context_type,
        content=content,
    )
    
    await logger.ainfo("context_add_success", paper_id=paper_id, paper_title=paper.title, context_type=context_type)
    console.print(f"[green]✓ Added '{paper.title[:60]}...' ({context_type})[/green]")
    return ""

async def handle_context_modify_simple(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """Simplified version of handle_context_modify without PaperExtractor."""
    await logger.ainfo("context_modify_command_start", args=args)
    
    if not args:
        await logger.awarning("context_modify_command_no_args")
        return "[red]Usage: /cmodify <paper reference> <old_context_type> <new_context_type>[/red]"
    
    # Parse arguments: paper_ref old_type new_type
    parts = args.strip().split()
    if len(parts) < 3:
        await logger.awarning("context_modify_command_insufficient_args")
        return "[red]Usage: /cmodify <paper reference> <old_context_type> <new_context_type>[/red]"
    
    # Handle quoted paper references
    if args.startswith('"'):
        # Find the closing quote
        end_quote = args.find('"', 1)
        if end_quote == -1:
            return "[red]Missing closing quote for paper reference[/red]"
        paper_ref = args[1:end_quote]
        remaining = args[end_quote + 1:].strip().split()
        if len(remaining) < 2:
            return "[red]Must specify both old and new context types[/red]"
        old_context_type = remaining[0].replace("-", "_")
        new_context_type = remaining[1].replace("-", "_")
    else:
        # Last two parts are context types, everything else is paper ref
        paper_ref = " ".join(parts[:-2])
        old_context_type = parts[-2].replace("-", "_")
        new_context_type = parts[-1].replace("-", "_")
    
    # Validate context types
    valid_types = ["full_text", "abstract", "notes"]
    if old_context_type not in valid_types:
        await logger.awarning("context_modify_invalid_old_type", old_context_type=old_context_type)
        return f"[red]Invalid old context type: {old_context_type}. Must be: {', '.join(valid_types)}[/red]"
    if new_context_type not in valid_types:
        await logger.awarning("context_modify_invalid_new_type", new_context_type=new_context_type)
        return f"[red]Invalid new context type: {new_context_type}. Must be: {', '.join(valid_types)}[/red]"
    
    await logger.ainfo("context_modify_parsed", paper_ref=paper_ref, old_context_type=old_context_type, new_context_type=new_context_type)
    
    # Resolve paper reference to a single paper ID
    await logger.ainfo("context_modify_resolving_paper", paper_ref=paper_ref)
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
    
    if not paper_id:
        await logger.awarning("context_modify_paper_not_found", paper_ref=paper_ref)
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"
    
    await logger.ainfo("context_modify_paper_resolved", paper_id=paper_id)
    
    if not session_context.has_paper(paper_id):
        await logger.awarning("context_modify_paper_not_in_context", paper_id=paper_id)
        return f"[yellow]Paper not in context: {paper_ref}[/yellow]"
    
    # Check if the old context type exists
    entry = session_context.papers[paper_id]
    if old_context_type not in entry.context_types:
        await logger.awarning("context_modify_old_type_not_found", paper_id=paper_id, old_context_type=old_context_type)
        return f"[yellow]Paper doesn't have {old_context_type} context type. Current types: {', '.join(sorted(entry.context_types))}[/yellow]"
    
    # Check if new context type already exists
    if new_context_type in entry.context_types:
        await logger.awarning("context_modify_new_type_exists", paper_id=paper_id, new_context_type=new_context_type)
        return f"[yellow]Paper already has {new_context_type} context type[/yellow]"
    
    # Get the paper
    paper = db.get_paper(paper_id)
    if not paper:
        await logger.aerror("context_modify_paper_not_in_db", paper_id=paper_id)
        return "[red]Paper not found in database[/red]"
    
    # Extract content for new type (simplified)
    await logger.ainfo("context_modify_extracting_content", paper_id=paper_id, new_context_type=new_context_type)
    content = ""
    if new_context_type == "full_text":
        extraction = db.get_extraction(paper_id, "full_text")
        content = extraction.content if extraction else paper.abstract
        await logger.ainfo("context_modify_used_full_text", paper_id=paper_id, has_extraction=bool(extraction))
    elif new_context_type == "notes":
        extraction = db.get_extraction(paper_id, "key_points")
        content = extraction.content if extraction else f"No notes. Abstract:\n{paper.abstract}"
        await logger.ainfo("context_modify_used_notes", paper_id=paper_id, has_extraction=bool(extraction))
    else:
        content = paper.abstract
        await logger.ainfo("context_modify_using_abstract", paper_id=paper_id)
    
    # Remove old context type and add new one (preserving other context types)
    await logger.ainfo("context_modify_updating_types", paper_id=paper_id, old_context_type=old_context_type, new_context_type=new_context_type)
    entry.remove_context_type(old_context_type)
    entry.add_context_type(new_context_type, content)
    
    await logger.ainfo("context_modify_success", paper_id=paper_id, paper_title=paper.title, old_context_type=old_context_type, new_context_type=new_context_type)
    console.print(f"[green]✓ Modified '{paper.title[:60]}...' from {old_context_type} to {new_context_type}[/green]")
    return ""


def handle_clear_command(
    args: str,
    nl_handler: Any | None = None,
    session_context: SessionContext | None = None,
) -> None:
    """Handle the /clear command with enhanced functionality.
    
    Args:
        args: Command arguments (e.g., "--help")
        nl_handler: Natural language handler to reset conversation
        session_context: Session context to clear papers
    """
    logger.info("clear_command_start", args=args)
    
    # Check for help flag
    if args and args.strip() == "--help":
        console.print("\n[bold]Clear Command[/bold]")
        console.print("Clears console, chat history, and session context for a fresh start.\n")
        console.print("Usage:")
        console.print("  /clear        - Clear everything (default)")
        console.print("  /clear --help - Show this help message")
        return
    
    # Clear console
    console.clear()
    
    # Reset natural language conversation if handler is available
    if nl_handler:
        nl_handler.reset_conversation()
        logger.info("clear_command_reset_conversation")
    
    # Clear session context if available
    cleared_count = 0
    if session_context and session_context.papers:
        cleared_count = session_context.get_paper_count()
        session_context.clear()
        logger.info("clear_command_cleared_context", paper_count=cleared_count)
    
    # Show confirmation message
    if cleared_count > 0:
        console.print(f"[green]✓ Cleared console, chat history, and {cleared_count} papers from context[/green]")
    else:
        console.print("[green]✓ Cleared console and chat history[/green]")
    
    logger.info("clear_command_success", papers_cleared=cleared_count)


def handle_command(command: str, db: Database, config: Config | None = None, session_context: SessionContext | None = None, token_tracker: TokenTracker | None = None, nl_handler: Any | None = None) -> None:
    """Handle slash commands."""
    import uuid
    
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Generate unique request ID for command tracking
    request_id = str(uuid.uuid4())[:8]
    
    with operation_context("command_execution", command=cmd, request_id=request_id, args=args):
        logger.info("command_executed", command=cmd, args=args)

    if cmd == "/help":
        show_help()
    elif cmd == "/find":
        # Parse flags for /find command
        if args and args.strip() == "--help":
            show_find_help()
            return
        if args and args.strip() == "--recent":
            show_search_results()
            return
        if args and args.strip() == "--clear":
            clear_search_results()
            return
        
        # Parse arguments using shlex to handle flags
        try:
            parsed_args = shlex.split(args) if args else []
        except ValueError:
            output.error("Invalid command syntax. Use quotes for complex queries.")
            return
            
        # Extract flags and query
        append = False
        query_parts = []
        
        for arg in parsed_args:
            if arg == "--append":
                append = True
            else:
                query_parts.append(arg)
        
        if not query_parts:
            output.error("Please provide a search query. Usage: /find <query> [--append] or /find --recent or /find --help")
            return
            
        query = " ".join(query_parts)
        asyncio.run(find_papers(query, append=append))
    elif cmd == "/add":
        add_paper(args, db)
    elif cmd == "/papers":
        handle_papers_command(args, db)
    elif cmd == "/remove":
        remove_paper(args, db)
    elif cmd == "/synthesize":
        if config and session_context:
            handle_synthesize_command(args, db, session_context, config, token_tracker)
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/note" or cmd == "/note":
        asyncio.run(handle_note_command(args, db))
    elif cmd == "/tag":
        asyncio.run(handle_tag_command(args, db))
    elif cmd == "/import":
        handle_import_command(args, db, config)
    elif cmd == "/clear":
        handle_clear_command(args, nl_handler, session_context)
    elif cmd == "/config":
        if config:
            handle_config_command(args, config)
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/tokens":
        if config:
            handle_tokens_command(args, config, token_tracker)
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/prompt":
        if config:
            handle_prompt_command(args, config)
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/cadd":
        if config and session_context:
            asyncio.run(handle_context_add_wrapper(args, db, session_context, config, token_tracker))
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/cremove":
        if config and session_context:
            asyncio.run(handle_context_remove_wrapper(args, db, session_context, config, token_tracker))
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/cshow":
        if session_context:
            result = handle_context_show(session_context)
            if result:
                console.print(result)
        else:
            console.print("[red]Session context not available[/red]")
    elif cmd == "/cclear":
        if session_context:
            result = handle_context_clear(session_context)
            if result:
                console.print(result)
        else:
            console.print("[red]Session context not available[/red]")
    elif cmd == "/cmodify":
        if config and session_context:
            asyncio.run(handle_context_modify_wrapper(args, db, session_context, config, token_tracker))
        else:
            console.print("[red]Configuration not available[/red]")
    else:
        logger.warning("unknown_command", command=cmd, args=args)
        console.print(f"[error]Unknown command: {cmd}[/error]")
        console.print("Type '/help' for available commands.")


async def find_papers(query: str, append: bool = False) -> str:
    """Search for papers using Semantic Scholar.

    Args:
        query: The search query
        append: If True, append to existing results instead of replacing them

    Returns:
        A summary string describing the search results for LLM context.
    """
    global _search_results, _search_metadata

    try:
        await logger.ainfo("find_papers_start", query=query)
        from litai.ui.status_manager import get_status_manager
        status = get_status_manager()
        status.start(f"[blue]Searching for papers matching '{query}'...[/blue]")

        async with SemanticScholarClient() as client:
            papers = await client.search(query, limit=10)

        if not papers:
            await logger.ainfo("find_papers_no_results", query=query)
            status.stop()
            output.error(f"No papers found matching '{query}'")
            return f"No papers found matching '{query}'"

        # Initialize variables for all paths
        new_papers = []
        duplicates_count = 0
        
        # Handle append vs replace logic
        if append and _search_results:
            # Get existing paper IDs for deduplication
            existing_ids = {p.paper_id for p in _search_results}
            new_papers = [p for p in papers if p.paper_id not in existing_ids]
            duplicates_count = len(papers) - len(new_papers)
            
            # Check if we would exceed maximum papers
            if len(_search_results) + len(new_papers) > 100:
                max_new_papers = 100 - len(_search_results)
                new_papers = new_papers[:max_new_papers]
                output.error(f"Maximum 100 papers allowed. Adding {len(new_papers)} papers, {len(papers) - len(new_papers)} excluded due to limit.")
            
            _search_results.extend(new_papers)
            
            # Track search metadata
            _search_metadata["queries"].append(query)
            _search_metadata["timestamps"].append(datetime.now())
            _search_metadata["counts"].append(len(new_papers))
            
            result_count = len(new_papers)
            total_count = len(_search_results)
            
            await logger.ainfo("find_papers_append_success", query=query, result_count=result_count, 
                       duplicates=duplicates_count, total_count=total_count)
            
            if duplicates_count > 0:
                status.stop()
                output.search_complete(result_count)
                console.print(f"[dim]({duplicates_count} duplicates removed, {total_count} total)[/dim]")
            else:
                status.stop()
                output.search_complete(result_count)
                console.print(f"[dim]({total_count} total)[/dim]")
        else:
            # Replace mode (default)
            _search_results = papers
            new_papers = papers  # For display purposes
            
            # Reset search metadata and add first entry
            _search_metadata = {
                "queries": [query],
                "timestamps": [datetime.now()],
                "counts": [len(papers)],
            }
            
            result_count = len(papers)
            await logger.ainfo("find_papers_success", query=query, result_count=result_count)
            status.stop()
            output.search_complete(result_count)

        # Create a table for results
        table = Table(show_header=True)
        table.add_column("No.", style="number", width=4)
        table.add_column("Title", style="bold")
        table.add_column(
            "Authors", style="dim_text", width=25,
        )  # Increased width to prevent wrapping
        table.add_column("Year", style="dim_text", width=6)
        table.add_column("Citations", style="dim_text", width=10)

        # Show the papers that were actually added
        display_papers = new_papers
        for i, paper in enumerate(display_papers, 1):
            # Truncate title if too long
            title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

            # Format authors
            if len(paper.authors) > 2:
                authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
            else:
                authors = ", ".join(paper.authors)

            table.add_row(
                str(i),
                title,
                authors,
                str(paper.year) if paper.year else "N/A",
                str(paper.citation_count),
            )

        console.print(table)
        console.print(
            "\n[warning]⊹ Tip: Use /add <number> to add a paper to your collection[/warning]",
        )

        # Return summary for LLM
        paper_summaries = []
        for i, paper in enumerate(display_papers, 1):
            authors_str = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors_str += " et al."
            paper_summaries.append(
                f'{i}. "{paper.title}" by {authors_str} ({paper.year}, {paper.citation_count} citations)',
            )

        if append and _search_results:
            total_papers = len(_search_results)
            added_papers = len(new_papers)
            message = f"Added {added_papers} new papers to collection (total: {total_papers})"
            if duplicates_count > 0:
                message += f", {duplicates_count} duplicates removed"
            message += f" for query '{query}'"
            if added_papers > 0:
                message += ":\n" + "\n".join(paper_summaries)
            return message
        return f"Found {len(papers)} papers matching '{query}':\n" + "\n".join(
            paper_summaries,
        )

    except Exception as e:
        status.stop()
        output.error(f"Search failed: {e}")
        await logger.aexception("Search failed", query=query)
        return f"Search failed: {str(e)}"


def clear_search_results() -> None:
    """Clear all accumulated search results and metadata."""
    global _search_results, _search_metadata
    
    logger.info("clear_search_results_start")
    
    if not _search_results:
        logger.info("clear_search_results_empty")
        console.print("[warning]No search results to clear.[/warning]")
        return
    
    count = len(_search_results)
    _search_results = []
    _search_metadata = {
        "queries": [],
        "timestamps": [],
        "counts": [],
    }
    
    logger.info("clear_search_results_success", cleared_count=count)
    console.print(f"[green]Cleared {count} accumulated search results.[/green]")


def show_search_results() -> None:
    """Show the currently cached search results."""
    global _search_results, _search_metadata

    logger.info("show_results_start")

    if not _search_results:
        logger.info("show_results_empty")
        console.print(
            "[warning]Warning: No search results cached. Use [command]/find[/command] to search for papers.[/warning]",
        )
        return

    logger.info("show_results_success", result_count=len(_search_results))
    
    # Show search history if we have metadata
    if _search_metadata.get("queries"):
        num_searches = len(_search_metadata["queries"])
        total_papers = len(_search_results)
        
        output.section(f"Cached Search Results ({total_papers} papers from {num_searches} searches)", "🔍", "bold cyan")
        console.print("[bold]Search History:[/bold]")
        
        for i, (query, timestamp, count) in enumerate(
            zip(_search_metadata["queries"], _search_metadata["timestamps"], _search_metadata["counts"], strict=False), 1,
        ):
            # Calculate duplicates for display (all but first search might have duplicates)
            if i == 1:
                duplicate_info = ""
            else:
                # This is an approximation - we can't know exact duplicates from past searches
                duplicate_info = " (some duplicates removed)" if count < 10 else ""
            
            time_str = timestamp.strftime("%H:%M")
            console.print(f"  {i}. \"{query}\" → {count} papers{duplicate_info} [{time_str}]")
        console.print("")
    else:
        # Fallback for backward compatibility
        total_papers = len(_search_results)
        output.section(f"Cached Search Results ({total_papers} papers)", "🔍", "bold cyan")

    # Create a table for cached results
    table = Table(show_header=True)
    table.add_column("No.", style="number", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Authors", style="dim_text", width=25)
    table.add_column("Year", style="dim_text", width=6)
    table.add_column("Citations", style="dim_text", width=10)

    for i, paper in enumerate(_search_results, 1):
        # Truncate title if too long
        title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

        # Format authors
        if len(paper.authors) > 2:
            authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
        else:
            authors = ", ".join(paper.authors)

        table.add_row(
            str(i),
            title,
            authors,
            str(paper.year) if paper.year else "N/A",
            str(paper.citation_count),
        )

    console.print(table)
    console.print(
        "\n[warning]⊹ Tip: Use /add <number> to add a paper to your collection[/warning]",
    )


def remove_paper(args: str, db: Database) -> None:
    """Remove paper(s) from the collection."""
    logger.info("remove_paper_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("remove")
        return

    papers = db.list_papers()
    if not papers:
        logger.warning("remove_paper_no_papers")
        console.print(
            "[yellow]Warning: No papers in your collection to remove.[/yellow]",
        )
        return

    try:
        if not args.strip():
            # Empty input - remove all papers
            console.print(
                f"[yellow]Remove all {len(papers)} papers from collection?[/yellow]",
            )
            confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
            if confirm.lower() != "yes":
                console.print("[red]Cancelled[/red]")
                return

            paper_indices = list(range(len(papers)))
            skip_second_confirmation = True  # Flag to skip the second confirmation
        else:
            # Parse comma-delimited paper numbers and ranges (e.g., "1,3,5-10,15")
            paper_indices = []
            skip_second_confirmation = False  # Flag to enable second confirmation
            for part in args.split(","):
                part = part.strip()
                if not part:
                    continue
                
                # Check if it's a range (e.g., "5-10")
                if "-" in part:
                    try:
                        start_str, end_str = part.split("-", 1)
                        start = int(start_str.strip())
                        end = int(end_str.strip())
                        
                        # Validate range bounds
                        if start < 1 or end > len(papers):
                            console.print(
                                f"[red]Invalid range: {part}. Must be between 1 and {len(papers)}[/red]",
                            )
                            return
                        if start > end:
                            console.print(
                                f"[red]Invalid range: {part}. Start must be less than or equal to end[/red]",
                            )
                            return
                        
                        # Add all papers in range (inclusive)
                        for i in range(start, end + 1):
                            if i - 1 not in paper_indices:  # Avoid duplicates
                                paper_indices.append(i - 1)
                    except ValueError:
                        console.print(f"[error]Invalid range format: '{part}'[/error]")
                        return
                else:
                    # Single number
                    try:
                        paper_num = int(part)
                        if paper_num < 1 or paper_num > len(papers):
                            console.print(
                                f"[red]Invalid paper number: {paper_num}. Must be between 1 and {len(papers)}[/red]",
                            )
                            return
                        if paper_num - 1 not in paper_indices:  # Avoid duplicates
                            paper_indices.append(paper_num - 1)
                    except ValueError:
                        console.print(f"[error]Invalid number: '{part}'[/error]")
                        return

        # Show papers to be removed and get confirmation (skip if already confirmed)
        if not skip_second_confirmation:
            if len(paper_indices) > 1:
                console.print(
                    f"\n[yellow]Are you sure you want to remove {len(paper_indices)} papers?[/yellow]",
                )
                for idx in paper_indices[:5]:  # Show first 5
                    paper = papers[idx]
                    console.print(f"  • {paper.title[:60]}...")
                if len(paper_indices) > 5:
                    console.print(f"  ... and {len(paper_indices) - 5} more")
            else:
                paper = papers[paper_indices[0]]
                console.print(
                    "\n[yellow]Are you sure you want to remove this paper?[/yellow]",
                )
                console.print(f"Title: {paper.title}")
                console.print(f"Authors: {', '.join(paper.authors[:3])}")
                if len(paper.authors) > 3:
                    console.print(f"... and {len(paper.authors) - 3} more")

            confirmation = Prompt.ask(
                "\nConfirm removal?", choices=["yes", "y", "no", "n"], default="no",
            )

            if confirmation not in ["yes", "y"]:
                console.print("[red]Cancelled[/red]")
                return

        # Proceed with removal
        removed_count = 0
        failed_count = 0

        for idx in paper_indices:
            paper = papers[idx]
            success = db.delete_paper(paper.paper_id)
            if success:
                logger.info(
                    "remove_paper_success", paper_id=paper.paper_id, title=paper.title,
                )
                removed_count += 1
                if len(paper_indices) == 1:
                    console.print(
                        f"[green]✓ Removed from collection: '{paper.title}'[/green]",
                    )
            else:
                logger.error(
                    "remove_paper_failed", paper_id=paper.paper_id, title=paper.title,
                )
                failed_count += 1

        # Summary
        if len(paper_indices) > 1:
            console.print(f"\n[green]✓ Removed {removed_count} papers[/green]")
            if failed_count:
                console.print(f"[red]Failed to remove {failed_count} papers[/red]")

        console.print(
            "\n[yellow]⊹ Tip: Use /papers to see your updated collection[/yellow]",
        )

    except Exception as e:
        console.print(f"[red]Error removing papers: {e}[/red]")
        logger.exception("Failed to remove papers", args=args)


def add_paper(args: str, db: Database) -> None:
    """Add a paper from search results to the collection."""
    global _search_results

    logger.info("add_paper_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("add")
        return

    if not _search_results:
        logger.warning("add_paper_no_results")
        console.print(
            "[warning]Warning: No search results available. Use [command]/find[/command] first to search for papers.[/warning]",
        )
        return

    # Parse tags if provided with --tags option
    tags_to_add = []
    actual_args = args
    if "--tags" in args:
        parts = args.split("--tags")
        actual_args = parts[0].strip()
        if len(parts) > 1:
            tag_str = parts[1].strip()
            tags_to_add = [t.strip() for t in tag_str.split(",") if t.strip()]

    try:
        if not actual_args:
            # Empty input - add all papers
            console.print(
                f"[yellow]Add all {len(_search_results)} papers to collection?[/yellow]",
            )
            confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
            if confirm.lower() != "yes":
                console.print("[red]Cancelled[/red]")
                return

            paper_indices = list(range(len(_search_results)))
        else:
            # Parse comma-delimited paper numbers and ranges (e.g., "1,3,5-10,15")
            paper_indices = []
            for part in actual_args.split(","):
                part = part.strip()
                if not part:
                    continue
                
                # Check if it's a range (e.g., "5-10")
                if "-" in part:
                    try:
                        start_str, end_str = part.split("-", 1)
                        start = int(start_str.strip())
                        end = int(end_str.strip())
                        
                        # Validate range bounds
                        if start < 1 or end > len(_search_results):
                            console.print(
                                f"[error]Invalid range: {part}. Must be between 1 and {len(_search_results)}[/error]",
                            )
                            return
                        if start > end:
                            console.print(
                                f"[error]Invalid range: {part}. Start must be less than or equal to end[/error]",
                            )
                            return
                        
                        # Add all papers in range (inclusive)
                        for i in range(start, end + 1):
                            if i - 1 not in paper_indices:  # Avoid duplicates
                                paper_indices.append(i - 1)
                    except ValueError:
                        console.print(f"[error]Invalid range format: '{part}'[/error]")
                        return
                else:
                    # Single number
                    try:
                        paper_num = int(part)
                        if paper_num < 1 or paper_num > len(_search_results):
                            console.print(
                                f"[error]Invalid paper number: {paper_num}. Must be between 1 and {len(_search_results)}[/error]",
                            )
                            return
                        if paper_num - 1 not in paper_indices:  # Avoid duplicates
                            paper_indices.append(paper_num - 1)
                    except ValueError:
                        console.print(f"[error]Invalid number: '{part}'[/error]")
                        return

        # Add papers
        added_count = 0
        duplicate_count = 0
        
        # Get existing citation keys to avoid duplicates
        existing_papers = db.list_papers(limit=1000)
        existing_keys = {p.citation_key for p in existing_papers if p.citation_key}

        for idx in paper_indices:
            paper = _search_results[idx]
            existing = db.get_paper(paper.paper_id)

            if existing:
                logger.info(
                    "add_paper_duplicate", paper_id=paper.paper_id, title=paper.title,
                )
                duplicate_count += 1
                continue

            # Generate citation key before adding
            paper.citation_key = paper.generate_citation_key(existing_keys)
            existing_keys.add(paper.citation_key)
            
            success = db.add_paper(paper)
            if success:
                logger.info(
                    "add_paper_success", paper_id=paper.paper_id, title=paper.title,
                )
                added_count += 1
                output.success(f"Added: '{paper.title}'")

                # Add tags if provided
                if tags_to_add:
                    db.add_tags_to_paper(paper.paper_id, tags_to_add)
                    console.print(f"  Tagged with: {output.format_tags(tags_to_add)}")
            else:
                logger.error(
                    "add_paper_failed", paper_id=paper.paper_id, title=paper.title,
                )
                output.error(f"Failed to add: '{paper.title}'")

        # Summary
        console.print(f"[success]✓ Added {added_count} papers[/success]")
        if duplicate_count:
            console.print(f"[warning]Skipped {duplicate_count} duplicates[/warning]")

        # Show tip
        if added_count > 0:
            console.print(
                "\n[warning]⊹ Tip: Use /papers to see your collection or /synthesize to analyze papers[/warning]",
            )

    except Exception as e:
        console.print(f"[error]Error adding papers: {e}[/error]")
        logger.exception("Failed to add papers", args=args)


def list_papers(db: Database, page: int = 1, tag_filter: str | None = None) -> str:
    """List all papers in the collection with pagination.

    Args:
        db: Database instance
        page: Page number (1-indexed)
        tag_filter: Optional tag name to filter by

    Returns:
        A summary string describing the papers in the collection for LLM context.
    """
    # Column configuration mapping
    column_config: dict[str, dict[str, Any]] = {
        # Core identification
        "no": {"name": "No.", "style": "secondary", "width": 4},
        "title": {"name": "Title", "style": "bold", "ratio": 4},
        # Authors and venue
        "authors": {
            "name": "Authors",
            "style": "dim_text",
            "width": 25,
            "no_wrap": True,
        },
        "venue": {"name": "Venue", "style": "dim_text", "ratio": 2},
        # Temporal and metrics
        "year": {"name": "Year", "style": "dim_text", "width": 6},
        "citations": {"name": "Citations", "style": "dim_text", "width": 6},
        "added_at": {"name": "Added", "style": "dim_text", "width": 10},
        # Status indicators
        "notes": {"name": "Notes", "style": "info", "width": 5},
        "tags": {"name": "Tags", "style": "cyan", "ratio": 2},
        # Content fields
        "abstract": {
            "name": "Abstract",
            "style": "dim_text",
            "ratio": 3,
            "truncate": 100,
        },
        "tldr": {"name": "TL;DR", "style": "dim_text", "ratio": 2},
        # Identifiers
        "doi": {"name": "DOI", "style": "dim_text", "width": 15, "no_wrap": True},
        "arxiv_id": {"name": "ArXiv", "style": "dim_text", "width": 12},
        "citation_key": {"name": "Cite Key", "style": "dim_text", "width": 15},
    }

    page_size = 20  # Papers per page
    offset = (page - 1) * page_size

    logger.info("list_papers_start", page=page, offset=offset, tag_filter=tag_filter)

    # If tag filter, we need to get filtered papers
    if tag_filter:
        # Get all papers with the tag (no pagination for tag search)
        all_tagged_papers = db.list_papers(limit=1000, offset=0, tag=tag_filter)
        total_count = len(all_tagged_papers)

        if total_count == 0:
            logger.info("list_papers_empty_tag", tag=tag_filter)
            console.print(
                f"[warning]No papers found with tag '{tag_filter}'. Use [command]/papers --tags[/command] to see available tags.[/warning]",
            )
            return f"No papers found with tag '{tag_filter}'."

        # Calculate total pages for tagged papers
        total_pages = (total_count + page_size - 1) // page_size

        # Validate page number
        if page < 1 or page > total_pages:
            console.print(
                f"[error]Invalid page number. Please choose between 1 and {total_pages}[/error]",
            )
            return f"Invalid page number. Total pages: {total_pages}"

        # Get papers for current page from the filtered list
        start_idx = offset
        end_idx = min(start_idx + page_size, total_count)
        papers = all_tagged_papers[start_idx:end_idx]
    else:
        # Get total count first to check if collection is empty
        total_count = db.count_papers()

        if total_count == 0:
            logger.info("list_papers_empty")
            console.print(
                "[warning]Warning: No papers in your collection yet. Use [command]/find[/command] to search for papers.[/warning]",
            )
            return "Your collection is empty. No papers found."

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size

        # Validate page number
        if page < 1 or page > total_pages:
            console.print(
                f"[error]Invalid page number. Please choose between 1 and {total_pages}[/error]",
            )
            return f"Invalid page number. Total pages: {total_pages}"

        # Get papers for current page
        papers = db.list_papers(limit=page_size, offset=offset)
    logger.info(
        "list_papers_success",
        paper_count=len(papers),
        total_count=total_count,
        page=page,
        total_pages=total_pages,
    )

    # Show section header
    if tag_filter:
        output.section(
            f"Papers tagged #{tag_filter} ({total_count} papers)", "🏷️", "bold cyan",
        )
    else:
        output.section(f"Your Collection ({total_count} papers)", "⧉", "bold secondary")
    if total_pages > 1:
        console.print(f"[dim_text]Page {page} of {total_pages}[/dim_text]\n")

    # Get configured columns
    config = Config()
    configured_columns = config.get_list_columns()

    # Build table with configured columns only
    table = Table(show_header=True, expand=True)
    for col_key in configured_columns:
        if col_key not in column_config:
            logger.warning(f"Unknown column configured: {col_key}")
            continue

        col_info = column_config[col_key]
        table.add_column(
            col_info["name"],
            style=col_info.get("style", ""),
            width=col_info.get("width"),
            ratio=col_info.get("ratio"),
            no_wrap=col_info.get("no_wrap", False),
        )

    for i, paper in enumerate(papers):
        # Calculate the actual paper number accounting for pagination
        paper_num = offset + i + 1

        # Build row data based on configured columns
        row_data = []
        for col_key in configured_columns:
            if col_key == "no":
                row_data.append(str(paper_num))
            elif col_key == "title":
                title = (
                    paper.title[:120] + "..." if len(paper.title) > 120 else paper.title
                )
                row_data.append(title)
            elif col_key == "authors":
                if len(paper.authors) > 2:
                    authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
                else:
                    authors = ", ".join(paper.authors)
                row_data.append(authors)
            elif col_key == "year":
                row_data.append(str(paper.year) if paper.year else "N/A")
            elif col_key == "citations":
                row_data.append(str(paper.citation_count))
            elif col_key == "notes":
                has_notes = db.get_note(paper.paper_id) is not None
                row_data.append("✓" if has_notes else "")
            elif col_key == "tags":
                if paper.tags:
                    tags_display = ", ".join([f"#{tag}" for tag in paper.tags[:3]])
                    if len(paper.tags) > 3:
                        tags_display += f" +{len(paper.tags) - 3}"
                    row_data.append(tags_display)
                else:
                    row_data.append("")
            elif col_key == "venue":
                row_data.append(paper.venue if paper.venue else "N/A")
            elif col_key == "abstract":
                truncate_len = int(column_config[col_key].get("truncate", 100))
                abstract = (
                    paper.abstract[:truncate_len] + "..."
                    if paper.abstract and len(paper.abstract) > truncate_len
                    else paper.abstract or ""
                )
                row_data.append(abstract)
            elif col_key == "tldr":
                row_data.append(paper.tldr if paper.tldr else "")
            elif col_key == "doi":
                row_data.append(paper.doi if paper.doi else "")
            elif col_key == "arxiv_id":
                row_data.append(paper.arxiv_id if paper.arxiv_id else "")
            elif col_key == "citation_key":
                row_data.append(paper.citation_key if paper.citation_key else "")
            elif col_key == "added_at":
                row_data.append(paper.added_at.strftime("%Y-%m-%d"))
            else:
                row_data.append("")  # Unknown column

        table.add_row(*row_data)

    console.print(table)

    # Show pagination info
    if total_pages > 1:
        console.print(
            f"\n[dim_text]Page {page} of {total_pages} • Papers {offset + 1}-{offset + len(papers)} of {total_count}[/dim_text]",
        )

        # Show navigation hints
        nav_hints = []
        if page > 1:
            nav_hints.append("/papers 1 (first page)")
            nav_hints.append(f"/papers {page - 1} (previous)")
        if page < total_pages:
            nav_hints.append(f"/papers {page + 1} (next)")
            nav_hints.append(f"/papers {total_pages} (last page)")

        if nav_hints:
            console.print(f"[dim_text]Navigate: {' • '.join(nav_hints)}[/dim_text]")

    output.tip(
        "Use /synthesize to extract key points or analyze across papers",
    )

    # Return summary for LLM
    paper_summaries = []
    for i, paper in enumerate(papers[:10], 1):  # Include top 10 for LLM context
        authors_str = ", ".join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors_str += " et al."
        paper_summaries.append(f'{i}. "{paper.title}" by {authors_str} ({paper.year})')

    result = f"Found {total_count} papers in your collection."
    if paper_summaries:
        result += " Top papers:\n" + "\n".join(paper_summaries)
    return result


def show_papers_help() -> None:
    """Show help for the /papers command."""
    output.section("Papers Command Help", "⧉", "bold secondary")
    
    console.print("[bold]Usage:[/bold] /papers [page_number] [--tags] [--notes] [--help]\n")
    
    console.print("[bold]Description:[/bold]")
    console.print("  List and manage papers in your collection with various filters\n")
    
    console.print("[bold]Options:[/bold]")
    console.print("  [command]page_number[/command]  Page number for pagination (default: 1)")
    console.print("  [command]--tags[/command]        Show all tags with paper counts")
    console.print("  [command]--notes[/command]       Show papers that have notes")
    console.print("  [command]--help[/command]        Show this help message\n")
    
    console.print("[bold]Examples:[/bold]")
    console.print("  [command]/papers[/command]           # List first page of papers")
    console.print("  [command]/papers 2[/command]         # Show page 2 of papers")
    console.print("  [command]/papers --tags[/command]    # Show all tags")
    console.print("  [command]/papers --notes[/command]   # Show papers with notes")


def handle_papers_command(args: str, db: Database) -> None:
    """Handle the /papers command with various flags."""
    if not args:
        # No arguments - show first page
        list_papers(db, page=1)
        return
    
    args = args.strip()
    
    # Check for flags
    if args == "--help":
        show_papers_help()
        return
    if args == "--tags":
        list_tags(db)
        return
    if args == "--notes":
        list_papers_with_notes(db)
        return
    
    # Try to parse as page number
    try:
        page = int(args)
        list_papers(db, page=page)
    except ValueError:
        # Check if it's a tag filter (backward compatibility)
        if args.startswith("--tag "):
            tag_parts = args[6:].strip().split(maxsplit=1)
            if tag_parts:
                tag_filter = tag_parts[0]
                page = 1
                if len(tag_parts) > 1:
                    with suppress(ValueError):
                        page = int(tag_parts[1])
                list_papers(db, page=page, tag_filter=tag_filter)
            else:
                output.error("Please provide a tag name. Usage: /papers --tag <tag_name>")
        else:
            output.error(f"Invalid argument: {args}. Use /papers --help for usage.")

def show_examples(command: str = "") -> None:
    """Show usage examples for different commands."""
    logger.info("show_examples", command=command)

    # If a specific command is provided, show examples for that command
    if command:
        command = command.strip().lower()
        if command.startswith("/"):
            command = command[1:]  # Remove leading slash

        examples = get_command_examples()
        if command in examples:
            console.print(f"\n[bold]Examples for /{command}:[/bold]\n")
            console.print(examples[command])
        else:
            console.print(f"[red]No examples found for '{command}'[/red]")
            console.print("Use '/examples' without arguments to see all examples.")
        return

    # Show all examples
    console.print("\n[bold]Usage Examples:[/bold]\n")

    examples = get_command_examples()
    for cmd, example_text in examples.items():
        console.print(f"[bold cyan]/{cmd}[/bold cyan]")
        console.print(example_text)
        console.print()  # Add spacing between examples


def get_command_examples() -> dict[str, str]:
    """Get example usage for each command."""
    return {
        "config": """[dim]Manage LitAI configuration:[/dim]
  /config show                    [dim]# Display current configuration[/dim]
  /config set <key> <value>       [dim]# Set a configuration value[/dim]
  /config reset [key]             [dim]# Reset to defaults[/dim]

[dim]Change AI Model (defaults to GPT-5):[/dim]
  /config set llm.provider openai         [dim]# Uses GPT-5 by default[/dim]
  
[dim]Small/Large Model Configuration:[/dim]
  /config set llm.small_model gpt-5-mini  [dim]# Fast model for quick tasks[/dim]
  /config set llm.large_model gpt-5       [dim]# Powerful model for complex tasks[/dim]

[dim]Display settings:[/dim]
  /config set display.list_columns title,authors,tags,notes
  /config set display.list_columns no,title,year,tldr  
  /config reset display.list_columns   [dim]# Reset to default columns[/dim]

[dim]Tool approval settings:[/dim]
  /config set tool_approval true   [dim]# Enable tool approval prompts (all modes)[/dim]
  /config set tool_approval false  [dim]# Auto-approve all tools (all modes)[/dim]

[dim]Reset configuration:[/dim]
  /config reset                   [dim]# Reset all configuration[/dim]
  /config reset llm.small_model   [dim]# Reset small model to default[/dim]
  /config reset llm.large_model   [dim]# Reset large model to default[/dim]

[dim]Available columns:[/dim]
  no, title, authors, year, citations, notes, tags,
  venue, abstract, tldr, doi, arxiv_id, citation_key, added_at
  
[dim]Default columns:[/dim]
  no,title,authors,year,citations,notes,tags,venue
  
[dim]Set your OpenAI API key:[/dim]
  export OPENAI_API_KEY=sk-...    [dim]# Get from platform.openai.com/api-keys[/dim]
  
[dim]Tip: After changing model, restart LitAI for changes to take effect[/dim]""",
        "find": """[dim]Search for papers on a specific topic:[/dim]
  [blue]/find attention mechanisms[/blue]
  [blue]/find transformer architecture[/blue]
  [blue]/find "deep learning optimization"[/blue]
  [blue]/find COVID-19 wastewater surveillance[/blue]""",
        "add": """[dim]Add paper(s) from search results:[/dim]
  /add            [dim]# Add all papers from search results (prompts for confirmation)[/dim]
  /add 1          [dim]# Add the first paper from search results[/dim]
  /add 3          [dim]# Add the third paper[/dim]
  /add 1,3,5      [dim]# Add multiple papers (comma-delimited)[/dim]
  /add 1-10       [dim]# Add papers 1 through 10 (range)[/dim]
  /add 1-5,8,10-15 [dim]# Mix ranges and individual papers[/dim]
  
[dim]Note: You must use [blue]/find[/blue] first to get search results[/dim]""",
        "list": """[dim]List papers in your collection with pagination:[/dim]
  /list           [dim]# Shows page 1 of your collection (20 papers per page)[/dim]
  /list 2         [dim]# Shows page 2 of your collection[/dim]
  /list 5         [dim]# Shows page 5 of your collection[/dim]""",
        "remove": """[dim]Remove paper(s) from your collection:[/dim]
  /remove         [dim]# Remove all papers from your collection (prompts for confirmation)[/dim]
  /remove 1       [dim]# Remove the first paper from your collection[/dim]
  /remove 5       [dim]# Remove the fifth paper[/dim]
  /remove 1,3,5   [dim]# Remove multiple papers (comma-delimited)[/dim]
  /remove 1-10    [dim]# Remove papers 1 through 10 (range)[/dim]
  /remove 1-5,8,10-15 [dim]# Mix ranges and individual papers[/dim]
  
[dim]Note: Use /list first to see paper numbers[/dim]
[dim]You will be asked to confirm before deletion[/dim]""",
        "synthesize": """[dim]Synthesize insights from papers in your context:[/dim]
  /synthesize <question>       [dim]# Ask a synthesis question[/dim]
  /synthesize --examples       [dim]# Show example synthesis questions[/dim]
  /synthesize --help          [dim]# Show this help message[/dim]

[dim]Usage:[/dim]
  • First add papers to context with /cadd
  • Then ask synthesis questions about them
  • Use --examples to see common research questions

[dim]Example workflow:[/dim]
  /cadd "BERT paper" full_text
  /cadd "GPT-3 paper" notes  
  /synthesize How do these models handle context?

[dim]For example questions:[/dim]
  /synthesize --examples""",
        "examples": """[dim]Show examples for specific commands:[/dim]
  /examples               [dim]# Show all examples[/dim]
  /examples synthesize    [dim]# Show examples for /synthesize[/dim]
  /examples find          [dim]# Show examples for [blue]/find[/blue][/dim]""",
        "note": """[dim]Manage personal notes for papers:[/dim]
  /note 1                 [dim]# Open note for paper 1 in your editor[/dim]
  /note "attention is all" [dim]# Open note using fuzzy paper reference[/dim]
  /note 1 view           [dim]# Display note in terminal[/dim]
  /note 1 append "TODO: Implement algorithm from section 3"
  /note 1 clear          [dim]# Delete note (asks for confirmation)[/dim]
  
[dim]Tips:[/dim]
  - Notes are written in Markdown format
  - Set your preferred editor with: export EDITOR=vim
  - Use /papers --notes to see all papers with notes""",
        "prompt": """[dim]Manage your personal research context:[/dim]
  /prompt                [dim]# Edit your research context (opens in editor)[/dim]
  /prompt view          [dim]# Display your current research context[/dim]
  /prompt append "Also interested in hardware-aware NAS"
  /prompt clear         [dim]# Delete your research context (asks for confirmation)[/dim]
  
[dim]Your research context helps LitAI:[/dim]
  - Understand your expertise level
  - Focus on relevant aspects of papers
  - Tailor synthesis to your interests
  - Remember your preferences""",
        "tag": """[dim]Manage tags for papers in your collection:[/dim]
  /tag 1 -a ml,deep-learning              [dim]# Add tags to paper 1[/dim]
  /tag "attention paper" -a transformers  [dim]# Add tag using fuzzy paper reference[/dim]
  /tag 2 -r outdated                      [dim]# Remove tag from paper 2[/dim]
  /tag "BERT paper" -r old                 [dim]# Remove tag using fuzzy paper reference[/dim]
  /tag 3 -l                               [dim]# List tags for paper 3[/dim]
  /tag 1                                  [dim]# View tags for paper 1[/dim]
  /tag "transformer paper"                [dim]# View tags using paper reference[/dim]
  
[dim]Tips:[/dim]
  - Use paper numbers or natural language references (in quotes)
  - Tags help organize your collection
  - Use /papers --tags to see all tags
  - Tags are case-insensitive and normalized""",
    }




def handle_prompt_command(args: str, config: Config) -> None:
    """Handle /prompt commands for managing user research context."""
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("prompt")
        return
    
    args_parts = args.strip().split(maxsplit=1)
    subcommand = args_parts[0] if args_parts else "edit"

    if subcommand == "edit":
        edit_user_prompt(config)
    elif subcommand == "view":
        view_user_prompt(config)
    elif subcommand == "append":
        if len(args_parts) < 2:
            console.print("[red]Usage: /prompt append <text>[/red]")
            return
        append_to_user_prompt(args_parts[1], config)
    elif subcommand == "clear":
        clear_user_prompt(config)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
        console.print("Available subcommands: edit, view, append, clear")


def edit_user_prompt(config: Config) -> None:
    """Open user prompt in external editor."""
    import os
    import tempfile
    from pathlib import Path

    logger.info("edit_user_prompt_start")

    # Get existing prompt
    prompt_path = config.user_prompt_path
    existing_prompt = ""
    if prompt_path.exists():
        try:
            existing_prompt = prompt_path.read_text().strip()
            logger.info("edit_user_prompt_existing", length=len(existing_prompt))
        except Exception as e:
            logger.error("edit_user_prompt_read_error", error=str(e))
            output.error(f"Failed to read existing prompt: {e}")
            return

    # Create temp file with content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_user_prompt.md", prefix="litai_", delete=False,
    ) as tmp:
        # Write header and template/existing content
        tmp.write("# LitAI User Prompt\n")
        tmp.write("<!-- This prompt will be added to every conversation -->\n\n")

        if existing_prompt:
            tmp.write(existing_prompt)
        else:
            # Provide template
            tmp.write("## Research Context\n")
            tmp.write("<!-- Describe your research area and current focus -->\n\n")
            tmp.write("## Background & Expertise\n")
            tmp.write(
                "<!-- Your academic/professional background relevant to your research -->\n\n",
            )
            tmp.write("## Specific Interests\n")
            tmp.write(
                "<!-- Particular topics, methods, or problems you're investigating -->\n\n",
            )
            tmp.write("## Preferences\n")
            tmp.write(
                "<!-- How you prefer information to be presented or synthesized -->\n",
            )

        tmp_path = tmp.name

    # Use the new editor system with fallback
    from litai.editor import open_in_editor_with_fallback
    
    # Open editor with fallback support
    success, error_msg = open_in_editor_with_fallback(Path(tmp_path), config)
    
    if not success:
        os.unlink(tmp_path)
        logger.error("edit_user_prompt_editor_failed", error=error_msg)
        output.error(f"Failed to open editor: {error_msg}")
        output.error("You can configure an editor with: /config set editor <name>")
        return

    # Read back the content
    try:
        with open(tmp_path) as f:
            new_content = f.read()

        # Remove header lines
        lines = new_content.split("\n")
        content_lines = []
        skip_next = False
        for line in lines:
            if line.startswith("# LitAI User Prompt"):
                skip_next = True
                continue
            if skip_next and line.startswith("<!--"):
                skip_next = False
                continue
            content_lines.append(line)

        # Join and clean up
        final_content = "\n".join(content_lines).strip()

        if final_content:
            # Save to file
            prompt_path.write_text(final_content)
            logger.info("edit_user_prompt_saved", length=len(final_content))
            console.print("[green]✓ User prompt saved successfully[/green]")
        else:
            logger.info("edit_user_prompt_empty")
            console.print("[yellow]No content saved (file was empty)[/yellow]")

    except Exception as e:
        logger.error("edit_user_prompt_save_error", error=str(e))
        output.error(f"Failed to save prompt: {e}")
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


def view_user_prompt(config: Config) -> None:
    """Display current user prompt."""
    logger.info("view_user_prompt_start")

    prompt_path = config.user_prompt_path
    if not prompt_path.exists():
        console.print(
            "[info]No user prompt set. Use /prompt edit to create one.[/info]",
        )
        return

    try:
        content = prompt_path.read_text().strip()
        if not content:
            console.print("[info]User prompt file is empty.[/info]")
            return

        output.section("Your Research Context", "📝", "bold blue")
        console.print(content)
        console.print("\n[dim]Use /prompt edit to modify[/dim]")

    except Exception as e:
        logger.error("view_user_prompt_error", error=str(e))
        output.error(f"Failed to read user prompt: {e}")


def append_to_user_prompt(text: str, config: Config) -> None:
    """Append text to existing user prompt."""
    logger.info("append_to_user_prompt_start", text_length=len(text))

    prompt_path = config.user_prompt_path

    try:
        # Read existing content
        existing = ""
        if prompt_path.exists():
            existing = prompt_path.read_text()

        # Append new text
        if existing and not existing.endswith("\n"):
            existing += "\n"

        new_content = existing + text + "\n"
        prompt_path.write_text(new_content)

        logger.info("append_to_user_prompt_success")
        console.print("[green]✓ Text appended to user prompt[/green]")

    except Exception as e:
        logger.error("append_to_user_prompt_error", error=str(e))
        output.error(f"Failed to append to prompt: {e}")


def clear_user_prompt(config: Config) -> None:
    """Delete user prompt file."""
    logger.info("clear_user_prompt_start")

    prompt_path = config.user_prompt_path
    if not prompt_path.exists():
        console.print("[info]No user prompt to clear.[/info]")
        return

    # Confirm deletion
    console.print("[yellow]This will permanently delete your user prompt.[/yellow]")
    confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")

    if confirm.lower() != "yes":
        console.print("[red]Cancelled[/red]")
        return

    try:
        prompt_path.unlink()
        logger.info("clear_user_prompt_success")
        console.print("[green]✓ User prompt cleared[/green]")
    except Exception as e:
        logger.error("clear_user_prompt_error", error=str(e))
        output.error(f"Failed to clear prompt: {e}")


def show_help() -> None:
    """Display a quick reference of all available commands."""
    logger.info("show_help")

    console.print("\n[bold]Available Commands:[/bold]\n")
    
    # Core commands
    console.print("[bold cyan]Paper Discovery:[/bold cyan]")
    console.print("  [blue]/find[/blue]        Search for papers")
    console.print("  [blue]/papers[/blue]      List papers in collection")
    console.print()
    
    console.print("[bold cyan]Collection Management:[/bold cyan]")
    console.print("  [green]/add[/green]         Add papers from search")
    console.print("  [red]/remove[/red]      Remove papers from collection")
    console.print("  [yellow]/note[/yellow]        Add notes to papers")
    console.print("  [magenta]/tag[/magenta]         Tag papers")
    console.print("  [dim]/import[/dim]      Import from BibTeX")
    console.print()
    
    console.print("[bold cyan]Context Management:[/bold cyan]")
    console.print("  [cyan]/cadd[/cyan]        Add papers to context")
    console.print("  [cyan]/cremove[/cyan]     Remove papers from context")
    console.print("  [cyan]/cshow[/cyan]       Show current context")
    console.print("  [cyan]/cclear[/cyan]      Clear all context")
    console.print("  [cyan]/cmodify[/cyan]     Modify paper context type")
    console.print()
    
    console.print("[bold cyan]Analysis:[/bold cyan]")
    console.print("  [blue]/synthesize[/blue]  Synthesize insights from papers")
    console.print()
    
    console.print("[bold cyan]System:[/bold cyan]")
    console.print("  [dim]/prompt[/dim]      Manage the user prompt")
    console.print("  [dim]/config[/dim]      Model & system configuration")
    console.print("  [dim]/tokens[/dim]      Token usage ")
    console.print("  [dim]/clear[/dim]       Clear console, chat history, and context")
    console.print("  [dim]/exit[/dim]        Exit LitAI")
    console.print()
    
    console.print("[dim]💡 Type any command with [bold]--help[/bold] for detailed usage and examples[/dim]")
    console.print("[dim]   Example: [italic]/find --help[/italic][/dim]\n")
    
    console.print("[dim]📜 To scroll up: Use [bold]Option/Command + ↑[/bold] arrow[/dim]")


def show_command_help(command: str) -> None:
    """Display help information for a specific command."""
    logger.info("show_command_help", command=command)
    
    # Get command examples
    examples = get_command_examples()
    
    # Special case for commands with custom help formatting
    if command == "find":
        show_find_help()
        return
    if command == "papers":
        show_papers_help()
        return
    
    # Generic help display for other commands
    if command in examples:
        console.print(f"\n[bold]/{command} Command Usage[/bold]\n")
        console.print(examples[command])
        console.print()
    else:
        console.print(f"\n[yellow]No help available for /{command}[/yellow]\n")


def show_find_help() -> None:
    """Display help information for the /find command."""
    logger.info("show_find_help")
    
    console.print("\n[bold]/find Command Usage[/bold]\n")
    
    console.print("Search for papers on Semantic Scholar with flexible result management.\n")
    
    console.print("[bold]Usage:[/bold]")
    console.print("[blue]/find <query>[/blue] — Search and replace current results (default)")
    console.print("[blue]/find <query> --append[/blue] — Add to existing search results")
    console.print("[blue]/find --clear[/blue] — Clear all accumulated search results")
    console.print("[blue]/find --recent[/blue] — Show cached results from previous searches")
    console.print("[blue]/find --help[/blue] — Show this help message\n")
    
    console.print("[bold]Examples:[/bold]")
    console.print("  [dim]/find \"transformer architecture\"[/dim]")
    console.print("  [dim]/find \"attention is all you need\" --append[/dim]")
    console.print("  [dim]/find \"BERT pretraining\" --append[/dim]")
    console.print("  [dim]/find --recent  # Shows all 3 searches combined[/dim]\n")
    
    console.print("[bold]Tips:[/bold]")
    console.print("  • Use --append to build comprehensive paper collections")
    console.print("  • Duplicates are automatically removed when appending")
    console.print("  • Maximum 100 papers can be accumulated")
    console.print("  • Use quotes for exact phrases: /find \"exact phrase\"")
    console.print("  • After searching, use /add <number> to add papers to your collection\n")


def show_synthesis_help() -> None:
    """Display help information for synthesis mode commands."""
    logger.info("show_synthesis_help")
    
    console.print("\n[bold cyan]◈ Synthesis Mode Commands[/bold cyan]\n")
    
    console.print("[bold]Slash Commands:[/bold]")
    console.print("  [blue]/papers[/blue]      List all papers in your collection")
    console.print("  [blue]/selected[/blue]    Show papers selected in current session")
    console.print("  [blue]/context[/blue]     Change context depth (abstracts, notes, sections, full_text)")
    console.print("  [blue]/clear[/blue]       Clear session (keeping selected papers)")
    console.print("  [blue]/help[/blue]        Show this help")
    console.print("  [blue]/exit[/blue]        Exit synthesis mode\n")
    
    console.print("[bold]Natural Language Commands:[/bold]")
    console.print("  Just ask questions naturally! Examples:")
    console.print("  • \"What are the main findings about attention mechanisms?\"")
    console.print("  • \"How do these papers approach optimization?\"")
    console.print("  • \"Compare the methods across my papers\"")
    console.print("  • \"Go deeper on the evaluation metrics\"\n")
    
    console.print("[bold]Context Depths:[/bold]")
    console.print("  [green]abstracts[/green]     Quick overview from paper abstracts")
    console.print("  [green]notes[/green]         Your personal notes on papers")
    console.print("  [green]sections[/green]      Specific sections from papers")
    console.print("  [green]full_text[/green]     Complete paper content (slower)\n")
    
    console.print("[bold]Workflow Tips:[/bold]")
    console.print("  1. Ask a question - I'll find relevant papers automatically")
    console.print("  2. Say \"go deeper\" for more detailed analysis")
    console.print("  3. Use /context to change detail level")
    console.print("  4. Build on previous answers with follow-up questions")
    console.print("  5. Use /selected to see which papers I'm working with\n")




async def handle_note_command(args: str, db: Database) -> None:
    """Handle /note command for managing user notes."""
    await logger.ainfo("handle_note_command_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("note")
        return

    if not args.strip():
        await logger.awarning("handle_note_command_no_args")
        output.error("Usage: /note <paper_number|\"paper reference\"> [view|append|clear]")
        console.print("[dim]Examples:[/dim]")
        console.print("  /note 1         # Edit note for paper 1")
        console.print("  /note 1 view    # View note for paper 1")
        console.print('  /note 1 append "Additional thoughts"')
        console.print("  /note 1 clear   # Delete note for paper 1")
        console.print('  /note "attention paper"  # Edit note for paper with natural language')
        console.print('  /note "transformer" view  # View note using paper reference')
        return

    # Use shlex to properly parse quoted strings
    try:
        parts = shlex.split(args.strip())
    except ValueError as e:
        output.error(f"Invalid command syntax: {e}")
        console.print('[dim]Tip: Use quotes for paper references with spaces, e.g., /note "attention paper"[/dim]')
        return
    
    if not parts:
        output.error("Usage: /note <paper_number|\"paper reference\"> [view|append|clear]")
        return
    
    paper = None
    paper_ref = parts[0]
    
    # First check if it's a paper number
    try:
        paper_num = int(paper_ref)
        papers = db.list_papers()
        if paper_num < 1 or paper_num > len(papers):
            await logger.awarning(
                "handle_note_command_invalid_number",
                paper_num=paper_num,
                max_num=len(papers),
            )
            output.error(f"Invalid paper number. Choose 1-{len(papers)}")
            return
        paper = papers[paper_num - 1]
        await logger.ainfo(
            "handle_note_command_paper_selected",
            paper_num=paper_num,
            paper_id=paper.paper_id,
        )
    except ValueError:
        # Not a number, try to resolve as natural language reference
        config = Config()
        llm_client = LLMClient(config)
        try:
            resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
            if paper_id:
                paper = db.get_paper(paper_id)
                if paper:
                    console.print(f"[dim]Resolved to: {paper.title}[/dim]")
                    await logger.ainfo(
                        "handle_note_command_resolved",
                        paper_id=paper_id,
                        title=paper.title,
                    )
                else:
                    await logger.awarning("handle_note_command_parse_error", input=paper_ref)
                    output.error(f"Could not resolve paper reference: '{paper_ref}'")
                    return
            else:
                await logger.awarning("handle_note_command_parse_error", input=paper_ref)
                output.error(f"Could not resolve paper reference: '{paper_ref}'")
                console.print('[dim]Tip: Try being more specific or use /papers to see paper numbers[/dim]')
                return
        finally:
            await llm_client.close()

    # Determine action
    action = parts[1].lower() if len(parts) > 1 else "edit"
    await logger.ainfo("handle_note_command_action", action=action)

    # Validate action
    valid_actions = ["edit", "view", "append", "clear"]
    if action not in valid_actions:
        await logger.awarning("handle_note_command_invalid_action", action=action)
        output.error(f"Invalid action: '{action}'. Valid actions: view, append, clear")
        return

    if action == "edit":
        await edit_note(paper, db)
    elif action == "view":
        view_note(paper, db)
    elif action == "append":
        if len(parts) < 3:
            await logger.awarning("handle_note_command_append_no_text")
            output.error("Usage: /note <number> append <text>")
            return
        append_to_note(paper, parts[2], db)
    elif action == "clear":
        clear_note(paper, db)


async def edit_note(paper: Paper, db: Database) -> None:
    """Open note in external editor."""
    import os
    import tempfile
    from pathlib import Path

    await logger.ainfo("edit_note_start", paper_id=paper.paper_id, title=paper.title)

    # Get existing note
    existing_note = db.get_note(paper.paper_id) or ""
    await logger.ainfo(
        "edit_note_existing",
        has_existing=bool(existing_note),
        length=len(existing_note),
    )

    # Create temp file with content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=f"_{paper.paper_id}.md", prefix="litai_note_", delete=False,
    ) as tmp:
        # Write header and existing content
        tmp.write(f"# Notes: {paper.title}\n")
        tmp.write(f"<!-- Paper: {paper.paper_id} -->\n")
        tmp.write("<!-- Do not edit the above lines -->\n\n")

        if existing_note:
            tmp.write(existing_note)
        else:
            # Provide template
            tmp.write("## Key Insights\n\n")
            tmp.write("## Questions\n\n")
            tmp.write("## Implementation Ideas\n\n")
            tmp.write("## Related Work\n\n")

        tmp_path = tmp.name

    try:
        # Use the new editor system with fallback
        from litai.config import Config
        from litai.editor import open_in_editor_with_fallback
        
        # Create config instance to get editor settings
        config = Config()
        
        # Open editor with fallback support
        console.print("[info]Opening note in editor...[/info]")
        success, error_msg = open_in_editor_with_fallback(Path(tmp_path), config)
        
        if not success:
            await logger.aerror("edit_note_editor_failed", error=error_msg)
            output.error(f"Failed to open editor: {error_msg}")
            output.error("You can configure an editor with: /config set editor <name>")
            return

        # Read updated content
        with open(tmp_path) as f:
            content = f.read()

        # Remove header lines
        lines = content.split("\n")
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "<!-- Do not edit the above lines -->":
                content_start = i + 1
                break

        final_content = "\n".join(lines[content_start:]).strip()

        # Save to database
        if final_content:
            success = db.add_note(paper.paper_id, final_content)
            await logger.ainfo(
                "edit_note_saved",
                paper_id=paper.paper_id,
                length=len(final_content),
                success=success,
            )
            output.success(f"Notes saved for '{paper.title}'")
        else:
            await logger.ainfo("edit_note_empty", paper_id=paper.paper_id)
            console.print("[warning]Empty note not saved[/warning]")

    except Exception as e:
        await logger.aexception("edit_note_failed", paper_id=paper.paper_id)
        output.error(f"Failed to edit note: {e}")
    finally:
        # Cleanup
        with suppress(Exception):
            os.unlink(tmp_path)


def view_note(paper: Paper, db: Database) -> None:
    """Display note in terminal."""
    logger.info("view_note_start", paper_id=paper.paper_id, title=paper.title)

    note = db.get_note(paper.paper_id)
    if not note:
        logger.info("view_note_not_found", paper_id=paper.paper_id)
        console.print(f"[warning]No notes found for '{paper.title}'[/warning]")
        return

    logger.info("view_note_found", paper_id=paper.paper_id, length=len(note))

    output.section(f"Notes: {paper.title}", "📝", "bold blue")
    from rich.markdown import Markdown

    console.print(Markdown(note))


def append_to_note(paper: Paper, text: str, db: Database) -> None:
    """Append text to an existing note."""
    logger.info("append_note_start", paper_id=paper.paper_id, text_length=len(text))

    existing_note = db.get_note(paper.paper_id) or ""

    # Add newlines if the existing note doesn't end with them
    if existing_note and not existing_note.endswith("\n"):
        existing_note += "\n\n"

    new_content = existing_note + text
    success = db.add_note(paper.paper_id, new_content)
    logger.info(
        "append_note_complete",
        paper_id=paper.paper_id,
        new_length=len(new_content),
        success=success,
    )
    output.success(f"Text appended to notes for '{paper.title}'")


def clear_note(paper: Paper, db: Database) -> None:
    """Delete note with confirmation."""
    logger.info("clear_note_start", paper_id=paper.paper_id)

    if not db.get_note(paper.paper_id):
        logger.info("clear_note_not_found", paper_id=paper.paper_id)
        console.print(f"[warning]No notes found for '{paper.title}'[/warning]")
        return

    confirm = Prompt.ask(
        f"[warning]Are you sure you want to delete notes for '{paper.title}'?[/warning]",
        choices=["yes", "no"],
        default="no",
    )

    if confirm == "yes":
        success = db.delete_note(paper.paper_id)
        logger.info("clear_note_result", paper_id=paper.paper_id, success=success)
        if success:
            output.success(f"Notes deleted for '{paper.title}'")
        else:
            output.error("Failed to delete notes")
    else:
        logger.info("clear_note_cancelled", paper_id=paper.paper_id)


def list_papers_with_notes(db: Database) -> None:
    """List all papers that have notes attached."""
    logger.info("list_notes_start")

    papers_with_notes = db.list_papers_with_notes()
    logger.info("list_notes_found", count=len(papers_with_notes))

    if not papers_with_notes:
        console.print(
            "[info]No papers have notes yet. Use /note <paper_number> to add notes.[/info]",
        )
        return

    output.section(
        f"Papers with Notes ({len(papers_with_notes)} total)", "📚", "bold blue",
    )

    # Get full paper list to find paper numbers
    all_papers = db.list_papers()
    paper_id_to_num = {p.paper_id: i + 1 for i, p in enumerate(all_papers)}

    for paper, preview, updated_at in papers_with_notes:
        paper_num = paper_id_to_num.get(paper.paper_id, "?")
        console.print(
            f"\n[number]{paper_num}[/number]. [primary]{paper.title}[/primary] ({paper.year})",
        )
        console.print(
            f"   [dim_text]Last updated: {updated_at.strftime('%Y-%m-%d %H:%M')}[/dim_text]",
        )
        console.print(f"   [italic]Preview: {preview}[/italic]")






async def handle_tag_command(args: str, db: Database) -> None:
    """Handle tag management for a paper."""
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("tag")
        return
    
    # Use shlex to properly parse quoted strings
    try:
        parts = shlex.split(args.strip()) if args.strip() else []
    except ValueError as e:
        output.error(f"Invalid command syntax: {e}")
        console.print('[dim]Tip: Use quotes for paper references with spaces[/dim]')
        return
    
    if not parts:
        output.error(
            'Please provide a paper number or reference. Usage: /tag <paper_number|"paper reference"> [-a|-r|-l tags]',
        )
        console.print("[dim]Examples:[/dim]")
        console.print("  /tag 1 -a ml,deep-learning    # Add tags to paper 1")
        console.print('  /tag "attention paper" -a transformers  # Add tag using paper reference')
        console.print("  /tag 2 -r outdated            # Remove tag from paper 2")
        console.print("  /tag 3 -l                     # List tags for paper 3")
        return

    paper = None
    paper_ref = parts[0]
    
    # First check if it's a paper number
    try:
        paper_num = int(paper_ref)
        papers = db.list_papers(limit=100)
        if paper_num < 1 or paper_num > len(papers):
            output.error(f"Invalid paper number. Please choose between 1 and {len(papers)}")
            return
        paper = papers[paper_num - 1]
        await logger.ainfo(
            "handle_tag_command_paper_selected",
            paper_num=paper_num,
            paper_id=paper.paper_id,
        )
    except ValueError:
        # Not a number, try to resolve as natural language reference
        config = Config()
        llm_client = LLMClient(config)
        try:
            resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
            if paper_id:
                paper = db.get_paper(paper_id)
                if paper:
                    console.print(f"[dim]Resolved to: {paper.title}[/dim]")
                    await logger.ainfo(
                        "handle_tag_command_resolved",
                        paper_id=paper_id,
                        title=paper.title,
                    )
                    # Update paper_num for display purposes
                    papers = db.list_papers(limit=100)
                    for i, p in enumerate(papers):
                        if p.paper_id == paper.paper_id:
                            paper_num = i + 1
                            break
                else:
                    await logger.awarning("handle_tag_command_parse_error", input=paper_ref)
                    output.error(f"Could not resolve paper reference: '{paper_ref}'")
                    return
            else:
                await logger.awarning("handle_tag_command_parse_error", input=paper_ref)
                output.error(f"Could not resolve paper reference: '{paper_ref}'")
                console.print('[dim]Tip: Try being more specific or use /papers to see paper numbers[/dim]')
                return
        finally:
            await llm_client.close()

    current_tags = db.get_paper_tags(paper.paper_id)

    # Parse the command options
    if len(parts) == 1:
        # No options provided, show current tags
        if current_tags:
            output.section(f"Tags for: {paper.title}", "🏷️", "bold cyan")
            console.print("Current tags: " + output.format_tags(current_tags))
            console.print(
                "\n[dim]Use -a to add tags, -r to remove tags, -l to list tags[/dim]",
            )
        else:
            console.print(f"[info]No tags for: {paper.title}[/info]")
            console.print("[dim]Use /tag <paper> -a <tags> to add tags[/dim]")
        return

    # Parse the action and tags
    action = parts[1]
    if action == "-a":
        # Add tags
        if len(parts) < 3:
            output.error(
                "Please provide tags to add. Usage: /tag <paper> -a tag1,tag2",
            )
            return
        
        tag_str = " ".join(parts[2:])  # Join remaining parts as tag string
        new_tags = [t.strip() for t in tag_str.split(",") if t.strip()]
        db.add_tags_to_paper(paper.paper_id, new_tags)

        output.success(f"Added {len(new_tags)} tag(s) to '{paper.title}'")
        updated_tags = db.get_paper_tags(paper.paper_id)
        console.print("Updated tags: " + output.format_tags(updated_tags))

    elif action == "-r":
        # Remove tags
        if len(parts) < 3:
            output.error(
                "Please provide tags to remove. Usage: /tag <paper> -r tag1,tag2",
            )
            return
        
        tag_str = " ".join(parts[2:])  # Join remaining parts as tag string
        tags_to_remove = [t.strip() for t in tag_str.split(",") if t.strip()]
        removed_count = 0
        for tag in tags_to_remove:
            if db.remove_tag_from_paper(paper.paper_id, tag):
                removed_count += 1

        if removed_count > 0:
            output.success(f"Removed {removed_count} tag(s) from '{paper.title}'")
            updated_tags = db.get_paper_tags(paper.paper_id)
            if updated_tags:
                console.print("Remaining tags: " + output.format_tags(updated_tags))
            else:
                console.print("[dim]Paper now has no tags[/dim]")
        else:
            output.error("No matching tags found to remove")

    elif action == "-l":
        # List all current tags
        if current_tags:
            output.section(f"Tags for: {paper.title}", "🏷️", "bold cyan")
            for tag in sorted(current_tags):
                console.print(f"  {output.format_tag(tag)}")
        else:
            console.print(f"[info]No tags for: {paper.title}[/info]")
    else:
        output.error(
            "Invalid option. Use -a to add tags, -r to remove tags, or -l to list tags",
        )


def list_tags(db: Database) -> None:
    """List all tags in the database with paper counts."""
    tags_with_counts = db.list_all_tags()

    if not tags_with_counts:
        console.print(
            "[info]No tags in the database yet. Use /tag <number> -a <tags> to add tags to papers.[/info]",
        )
        return

    output.section(f"All Tags ({len(tags_with_counts)} total)", "🏷️", "bold cyan")

    # Create a table for tags
    table = Table(show_header=True)
    table.add_column("Tag", style="cyan")
    table.add_column("Papers", style="number", justify="right")
    table.add_column("Created", style="dim_text")

    for tag, count in tags_with_counts:
        table.add_row(
            output.format_tag(tag.name), str(count), tag.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print(
        "\n[dim]Use /papers --tag <tag_name> to see papers with a specific tag[/dim]",
    )


def handle_import_command(args: str, db: Database, config: Config | None) -> None:
    """Handle BibTeX import command."""
    from pathlib import Path

    from litai.importers.bibtex import parse_bibtex_file

    if not args:
        output.error(
            "Please provide a BibTeX file path. Usage: /import <path/to/file.bib> [--dry-run]",
        )
        return

    # Parse arguments
    parts = args.split()
    file_path = Path(parts[0]).expanduser()
    dry_run = "--dry-run" in parts

    # Check if file exists
    if not file_path.exists():
        output.error(f"File not found: {file_path}")
        return

    if file_path.suffix.lower() not in [".bib", ".bibtex"]:
        output.error("File must have .bib or .bibtex extension")
        return

    try:
        # Parse the BibTeX file
        output.section("Importing BibTeX", "📚", "bold cyan")
        console.print(f"[info]Parsing {file_path}...[/info]")

        papers = parse_bibtex_file(file_path)

        if not papers:
            output.error("No valid entries found in BibTeX file")
            return

        console.print(f"[success]Found {len(papers)} valid entries[/success]")

        if dry_run:
            console.print("\n[warning]DRY RUN - No changes will be made[/warning]\n")

        # Process each paper
        imported = 0
        skipped = 0

        for i, paper in enumerate(papers, 1):
            # Check if paper already exists
            existing = None

            # Check by paper_id
            existing = db.get_paper(paper.paper_id)

            # Check by DOI if we have one
            if not existing and paper.doi:
                papers_with_doi = db.list_papers(limit=1000)
                for p in papers_with_doi:
                    if p.doi == paper.doi:
                        existing = p
                        break

            # Check by arXiv ID if we have one
            if not existing and paper.arxiv_id:
                papers_with_arxiv = db.list_papers(limit=1000)
                for p in papers_with_arxiv:
                    if p.arxiv_id == paper.arxiv_id:
                        existing = p
                        break

            if existing:
                skipped += 1
                if existing.citation_key != paper.citation_key and paper.citation_key:
                    # Update citation key if different
                    if not dry_run:
                        # TODO: Add update_paper_citation_key method to database
                        pass
                    console.print(
                        f"[dim][{i}/{len(papers)}] Skipped (exists): {paper.title[:60]}...[/dim]",
                    )
            else:
                if not dry_run:
                    success = db.add_paper(paper)
                    if success:
                        imported += 1
                        console.print(
                            f"[success][{i}/{len(papers)}] Added: {paper.title[:60]}...[/success]",
                        )
                    else:
                        skipped += 1
                        console.print(
                            f"[warning][{i}/{len(papers)}] Failed to add: {paper.title[:60]}...[/warning]",
                        )
                else:
                    imported += 1
                    console.print(
                        f"[info][{i}/{len(papers)}] Would add: {paper.title[:60]}...[/info]",
                    )

        # Summary
        console.print("\n[success]Import complete![/success]")
        console.print(f"  • Imported: {imported} papers")
        console.print(f"  • Skipped: {skipped} papers (duplicates)")

    except Exception as e:
        logger.error("Import failed", error=str(e))
        output.error(f"Import failed: {str(e)}")


if __name__ == "__main__":
    main()
