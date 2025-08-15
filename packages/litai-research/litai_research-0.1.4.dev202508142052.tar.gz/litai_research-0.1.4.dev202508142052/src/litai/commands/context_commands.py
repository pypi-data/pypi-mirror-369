"""Context management commands for LitAI."""

from rich.console import Console
from rich.table import Table

from litai.context_manager import SessionContext
from litai.database import Database
from litai.extraction import PaperExtractor
from litai.llm import LLMClient
from litai.paper_resolver import resolve_paper_references
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

async def handle_context_add(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
    extractor: PaperExtractor,
) -> str:
    """
    Handle /cadd command.
    Usage: /cadd <paper reference> [full-text|abstract|notes]
    
    Examples:
        /cadd 1 full-text
        /cadd "BERT paper" notes
        /cadd "attention is all you need" abstract
    """
    logger.info("context_add_command", args=args)
    
    # Check for --help flag
    if args and args.strip() == "--help":
        return show_context_add_help()
    
    if not args:
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
    
    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
    
    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"
    
    # Get the paper
    paper = db.get_paper(paper_id)
    if not paper:
        return f"[red]Paper not found in database: {paper_id}[/red]"
    
    # Check if already in context
    if session_context.has_paper(paper_id):
        # Paper already in context, add new context type
        entry = session_context.papers[paper_id]
        if context_type in entry.context_types:
            return f"[yellow]Paper already has {context_type} in context[/yellow]"
    
    # Extract content based on context type
    content = ""
    if context_type == "full_text":
        # Get full text extraction
        extraction = db.get_extraction(paper_id, "full_text")
        if extraction:
            content = extraction.content
        else:
            # Try to extract if not cached
            try:
                content = await extractor.extract_full_text(paper)
            except Exception as e:
                logger.error("extraction_failed", paper_id=paper_id, error=str(e))
                content = paper.abstract  # Fallback to abstract
    elif context_type == "notes":
        extraction = db.get_extraction(paper_id, "key_points")
        if extraction:
            content = extraction.content
        else:
            content = "No notes available. Using abstract."
            content += f"\n\n{paper.abstract}"
    else:  # abstract
        content = paper.abstract
    
    # Add to session context
    session_context.add_paper(
        paper_id=paper_id,
        paper_title=paper.title,
        context_type=context_type,
        content=content,
    )
    
    console.print(f"[green]✓ Added '{paper.title[:60]}...' ({context_type})[/green]")
    return ""

async def handle_context_remove(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """
    Handle /cremove command.
    Usage: /cremove <paper reference> [context_type]
    
    Examples:
        /cremove 1
        /cremove "BERT paper" notes
        /cremove "attention paper"
    """
    logger.info("context_remove_command", args=args)
    
    # Check for --help flag
    if args and args.strip() == "--help":
        return show_context_remove_help()
    
    if not args:
        return "[red]Usage: /cremove <paper reference> [context_type][/red]"
    
    # Parse context type if provided
    context_type = None
    paper_ref = args
    
    # Check if removing specific context type
    for ct in ["full-text", "full_text", "abstract", "notes"]:
        if args.endswith(f" {ct}"):
            context_type = ct.replace("-", "_")
            paper_ref = args[:-len(f" {ct}")].strip()
            break
    
    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
    
    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"
    
    # Check if paper is in context
    if not session_context.has_paper(paper_id):
        return f"[yellow]Paper not in context: {paper_ref}[/yellow]"
    
    # Get paper title for display
    paper = db.get_paper(paper_id)
    paper_title = paper.title if paper else paper_id
    
    # Remove from context
    session_context.remove_paper(paper_id, context_type)
    
    if context_type:
        console.print(f"[yellow]✓ Removed {context_type} from '{paper_title[:60]}...'[/yellow]")
    else:
        console.print(f"[yellow]✓ Removed '{paper_title[:60]}...' from context[/yellow]")
    
    return ""

def handle_context_show(session_context: SessionContext, args: str = "") -> str:
    """
    Handle /cshow command.
    Displays current context as a table.
    """
    from litai.output_formatter import OutputFormatter
    output = OutputFormatter(console)
    
    logger.info("context_show_command_start")
    
    # Check for --help flag
    if args and args.strip() == "--help":
        return show_context_show_help()
    
    if not session_context.papers:
        logger.info("context_show_empty")
        return "[info]No papers in context. Use /cadd to add papers.[/info]"
    
    # Create table
    paper_count = session_context.get_paper_count()
    logger.info("context_show_displaying", paper_count=paper_count)
    
    # Use output.section for consistent formatting
    output.section(f"Current Context ({paper_count} papers)", "📋", "bold cyan")
    
    table = Table(show_header=True)
    table.add_column("Paper", style="bold")
    table.add_column("Context Types", style="cyan")
    
    # Build list for LLM context
    paper_summaries = []
    
    for _paper_id, entry in session_context.papers.items():
        title = entry.paper_title[:80] + "..." if len(entry.paper_title) > 80 else entry.paper_title
        context_types = ", ".join(sorted(entry.context_types))
        table.add_row(title, context_types)
        
        # Add to summary for LLM
        paper_summaries.append(f'"{entry.paper_title}" ({context_types})')
    
    console.print(table)
    logger.info("context_show_success", paper_count=paper_count)
    
    # Return summary for LLM context
    if paper_summaries:
        return f"Current context has {paper_count} papers:\n" + "\n".join(paper_summaries)
    return ""

def handle_context_clear(session_context: SessionContext, args: str = "") -> str:
    """
    Handle /cclear command.
    Clears all context.
    """
    logger.info("context_clear_command_start")
    
    # Check for --help flag
    if args and args.strip() == "--help":
        return show_context_clear_help()
    
    if not session_context.papers:
        logger.info("context_clear_already_empty")
        return "[info]Context is already empty.[/info]"
    
    paper_count = session_context.get_paper_count()
    logger.info("context_clear_clearing", paper_count=paper_count)
    session_context.clear()
    
    logger.info("context_clear_success", cleared_count=paper_count)
    return f"[green]✓ Cleared {paper_count} papers from context[/green]"

async def handle_context_modify(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
    extractor: PaperExtractor,
) -> str:
    """
    Handle /cmodify command.
    Changes one context type to another while preserving other context types.
    Usage: /cmodify <paper reference> <old_context_type> <new_context_type>
    
    Examples:
        /cmodify 1 notes abstract
        /cmodify "BERT paper" full-text notes
    """
    logger.info("context_modify_command", args=args)
    
    # Check for --help flag
    if args and args.strip() == "--help":
        return show_context_modify_help()
    
    if not args:
        return "[red]Usage: /cmodify <paper reference> <old_context_type> <new_context_type>[/red]"
    
    # Parse arguments: paper_ref old_type new_type
    parts = args.strip().split()
    if len(parts) < 3:
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
        return f"[red]Invalid old context type: {old_context_type}. Must be: {', '.join(valid_types)}[/red]"
    if new_context_type not in valid_types:
        return f"[red]Invalid new context type: {new_context_type}. Must be: {', '.join(valid_types)}[/red]"
    
    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)
    
    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"
    
    if not session_context.has_paper(paper_id):
        return f"[yellow]Paper not in context: {paper_ref}[/yellow]"
    
    # Check if the old context type exists
    entry = session_context.papers[paper_id]
    if old_context_type not in entry.context_types:
        return f"[yellow]Paper doesn't have {old_context_type} context type. Current types: {', '.join(sorted(entry.context_types))}[/yellow]"
    
    # Check if new context type already exists
    if new_context_type in entry.context_types:
        return f"[yellow]Paper already has {new_context_type} context type[/yellow]"
    
    # Get the paper
    paper = db.get_paper(paper_id)
    if not paper:
        return "[red]Paper not found in database[/red]"
    
    # Extract content for new type
    content = ""
    if new_context_type == "full_text":
        extraction = db.get_extraction(paper_id, "full_text")
        if extraction:
            content = extraction.content
        else:
            # Try to extract if not cached
            try:
                content = await extractor.extract_full_text(paper)
            except Exception as e:
                logger.error("extraction_failed", paper_id=paper_id, error=str(e))
                content = paper.abstract  # Fallback to abstract
    elif new_context_type == "notes":
        extraction = db.get_extraction(paper_id, "key_points")
        if extraction:
            content = extraction.content
        else:
            content = "No notes available. Using abstract."
            content += f"\n\n{paper.abstract}"
    else:  # abstract
        content = paper.abstract
    
    # Remove old context type and add new one
    entry.remove_context_type(old_context_type)
    entry.add_context_type(new_context_type, content)
    
    console.print(f"[green]✓ Modified '{paper.title[:60]}...' from {old_context_type} to {new_context_type}[/green]")
    return ""


# Help display functions
def show_context_add_help() -> str:
    """Display help for /cadd command."""
    lines = [
        "",
        "[bold cyan]Context Add Command Help[/bold cyan]",
        "",
        "[bold]Usage:[/bold] /cadd <paper reference> [context_type]",
        "",
        "[bold]Description:[/bold]",
        "  Add papers to your working context for synthesis.",
        "  Papers in context are used by /synthesize for analysis.",
        "",
        "[bold]Arguments:[/bold]",
        "  [command]paper reference[/command]  Paper number from /papers or natural language reference",
        "  [command]context_type[/command]     Type of content to add (default: full-text)",
        "",
        "[bold]Context Types:[/bold]",
        "  [green]full-text[/green]    Complete paper content (most detailed)",
        "  [green]abstract[/green]     Just the abstract (fastest)",
        "  [green]notes[/green]        Your personal notes on the paper",
        "",
        "[bold]Examples:[/bold]",
        "  [command]/cadd 1[/command]                          # Add paper 1 with full text",
        "  [command]/cadd 3 abstract[/command]                 # Add paper 3's abstract only",
        "  [command]/cadd \"BERT paper\" notes[/command]         # Add BERT paper's notes",
        "  [command]/cadd \"attention is all\" full-text[/command] # Add by title search",
        "",
        "[bold]Tips:[/bold]",
        "  • Use /cshow to see papers currently in context",
        "  • Add multiple context types for the same paper",
        "  • Natural language references are matched using AI",
        "",
    ]
    return "\n".join(lines)


def show_context_remove_help() -> str:
    """Display help for /cremove command."""
    lines = [
        "",
        "[bold cyan]Context Remove Command Help[/bold cyan]",
        "",
        "[bold]Usage:[/bold] /cremove <paper reference> [context_type]",
        "",
        "[bold]Description:[/bold]",
        "  Remove papers from your working context.",
        "  Optionally remove just specific context types.",
        "",
        "[bold]Arguments:[/bold]",
        "  [command]paper reference[/command]  Paper number from /papers or natural language reference",
        "  [command]context_type[/command]     Optional: specific type to remove",
        "",
        "[bold]Examples:[/bold]",
        "  [command]/cremove 1[/command]                    # Remove all context for paper 1",
        "  [command]/cremove 3 notes[/command]             # Remove only notes for paper 3",
        "  [command]/cremove \"BERT paper\"[/command]        # Remove BERT paper entirely",
        "  [command]/cremove \"transformer\" abstract[/command] # Remove just abstract",
        "",
        "[bold]Tips:[/bold]",
        "  • Use /cshow to see what's in context first",
        "  • Without context_type, removes all types for that paper",
        "  • Use /cclear to remove all papers at once",
        "",
    ]
    return "\n".join(lines)


def show_context_show_help() -> str:
    """Display help for /cshow command."""
    lines = [
        "",
        "[bold cyan]Context Show Command Help[/bold cyan]",
        "",
        "[bold]Usage:[/bold] /cshow",
        "",
        "[bold]Description:[/bold]",
        "  Display all papers currently in your working context.",
        "  Shows which context types are loaded for each paper.",
        "",
        "[bold]Output:[/bold]",
        "  A table showing:",
        "  • Paper titles",
        "  • Context types loaded (full_text, abstract, notes)",
        "  • Total paper count",
        "",
        "[bold]Examples:[/bold]",
        "  [command]/cshow[/command]  # Display current context",
        "",
        "[bold]Tips:[/bold]",
        "  • Empty context shows helpful message",
        "  • Use before /synthesize to verify context",
        "  • Context persists across synthesis sessions",
        "",
    ]
    return "\n".join(lines)


def show_context_clear_help() -> str:
    """Display help for /cclear command."""
    lines = [
        "",
        "[bold cyan]Context Clear Command Help[/bold cyan]",
        "",
        "[bold]Usage:[/bold] /cclear",
        "",
        "[bold]Description:[/bold]",
        "  Clear all papers from your working context.",
        "  Useful for starting fresh synthesis sessions.",
        "",
        "[bold]Examples:[/bold]",
        "  [command]/cclear[/command]  # Remove all papers from context",
        "",
        "[bold]Tips:[/bold]",
        "  • Use /cshow first to see what will be cleared",
        "  • Context is not permanently deleted, just cleared",
        "  • Papers remain in your collection (/papers)",
        "",
    ]
    return "\n".join(lines)


def show_context_modify_help() -> str:
    """Display help for /cmodify command."""
    lines = [
        "",
        "[bold cyan]Context Modify Command Help[/bold cyan]",
        "",
        "[bold]Usage:[/bold] /cmodify <paper reference> <old_type> <new_type>",
        "",
        "[bold]Description:[/bold]",
        "  Change the context type for a paper without removing it.",
        "  Useful for switching between detail levels.",
        "",
        "[bold]Arguments:[/bold]",
        "  [command]paper reference[/command]  Paper number or natural language reference",
        "  [command]old_type[/command]         Current context type to replace",
        "  [command]new_type[/command]         New context type to use",
        "",
        "[bold]Context Types:[/bold]",
        "  [green]full_text[/green] or [green]full-text[/green]  Complete paper content",
        "  [green]abstract[/green]                 Just the abstract",
        "  [green]notes[/green]                    Your personal notes",
        "",
        "[bold]Examples:[/bold]",
        "  [command]/cmodify 1 notes abstract[/command]          # Switch from notes to abstract",
        "  [command]/cmodify \"BERT\" full-text notes[/command]    # Switch from full to notes",
        "  [command]/cmodify 3 abstract full_text[/command]      # Switch to full text",
        "",
        "[bold]Tips:[/bold]",
        "  • Use /cshow to see current context types",
        "  • Both full_text and full-text are accepted",
        "  • Preserves other context types for the same paper",
        "",
    ]
    return "\n".join(lines)