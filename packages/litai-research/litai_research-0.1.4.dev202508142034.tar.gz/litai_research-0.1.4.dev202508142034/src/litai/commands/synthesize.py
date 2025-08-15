"""Synthesis command that uses current context."""

from rich.console import Console

from litai.config import Config
from litai.context_manager import SessionContext
from litai.database import Database
from litai.llm import LLMClient
from litai.token_tracker import TokenTracker
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

async def handle_synthesize(
    query: str,
    session_context: SessionContext,
    db: Database,
    config: Config,
    token_tracker: TokenTracker | None = None,
) -> str:
    """
    Handle /synthesize command using papers in current context.
    
    IMPORTANT: Uses ALL context types for ALL papers in context.
    """
    logger.info("synthesize_command", query=query[:100])
    
    # Check if context is empty
    if not session_context.papers:
        return "[yellow]No papers in context. Use /cadd to add papers first.[/yellow]\n\nExample: /cadd \"attention is all you need\" full_text"
    
    # Get all context
    combined_context = session_context.get_all_context()
    
    # Build synthesis prompt
    prompt = f"""Based on the following papers and their content, please synthesize an answer to this question:

Question: {query}

Papers in Context ({session_context.get_paper_count()} papers):
{combined_context}

Please provide a comprehensive synthesis that:
1. Addresses the question directly
2. Draws from all relevant papers
3. Highlights key insights and connections
4. Notes any contradictions or debates
"""
    
    # Initialize LLM client
    llm_client = LLMClient(config, token_tracker=token_tracker)
    
    try:
        # Get synthesis from LLM (use large model for synthesis)
        response = await llm_client.complete([
            {"role": "system", "content": "You are an expert at synthesizing academic papers."},
            {"role": "user", "content": prompt},
        ], model_size="large", operation_type="synthesis")
        
        synthesis_result = response.get("content", "")
        
        # Format output
        console.print("\n[bold cyan]Synthesis Result[/bold cyan]")
        console.print(f"[dim]Based on {session_context.get_paper_count()} papers in context[/dim]\n")
        console.print(synthesis_result)
        
        return ""  # Already printed
        
    except Exception as e:
        logger.error("synthesis_failed", error=str(e))
        return f"[red]Synthesis failed: {str(e)}[/red]"
    finally:
        await llm_client.close()

def handle_synthesize_command(args: str, db: Database, session_context: SessionContext, config: Config, token_tracker: TokenTracker | None = None) -> None:
    """
    Handle the /synthesize command from CLI.
    """
    if not args.strip():
        console.print("[red]Usage: /synthesize <your question>[/red]")
        console.print("\nExample: /synthesize What are the key innovations in transformer architectures?")
        console.print("\nFor example synthesis questions, use: /synthesize --examples")
        return
    
    # Check for --examples
    if args.strip() == "--examples":
        show_synthesis_examples()
        return
    
    # Check for --help
    if args.strip() == "--help":
        console.print("[bold]Synthesize Command[/bold]")
        console.print("\nSynthesize insights from papers in your current context.")
        console.print("\nUsage: /synthesize <question>")
        console.print("       /synthesize --examples  # Show example synthesis questions")
        console.print("\nNote: You must first add papers to context using /cadd")
        console.print("\nExample workflow:")
        console.print("  1. /cadd \"BERT paper\" full_text")
        console.print("  2. /cadd \"GPT-3 paper\" notes")
        console.print("  3. /synthesize How do these models handle context?")
        return
    
    # Run synthesis
    import asyncio
    asyncio.run(handle_synthesize(args, session_context, db, config, token_tracker))


def show_synthesis_examples() -> None:
    """Display synthesis example questions that users can ask with LitAI."""
    from litai.output_formatter import OutputFormatter
    output = OutputFormatter(console)
    
    console.print("\n[bold heading]SYNTHESIS EXAMPLE QUESTIONS[/bold heading]")
    console.print("[dim_text]Learn to ask better synthesis questions[/dim_text]\n")

    # Experimental Troubleshooting
    output.section("Debugging Experiments", "🔧", "bold cyan")
    console.print("• Why does this baseline perform differently than reported?")
    console.print("• What hyperparameters do papers actually use vs report?")
    console.print('• Which "standard" preprocessing steps vary wildly across papers?')
    console.print("• What's the actual variance in this metric across the literature?")
    console.print("• Do others see this instability/artifact? How do they handle it?\n")

    # Methods & Analysis
    output.section("Methods & Analysis", "📊", "bold cyan")
    console.print("• What statistical tests does this subfield actually use/trust?")
    console.print("• How do people typically visualize this type of data?")
    console.print("• What's the standard ablation set for this method?")
    console.print("• Which evaluation metrics correlate with downstream performance?")
    console.print("• What dataset splits/versions are people actually using?\n")

    # Contextualizing Results
    output.section("Contextualizing Results", "📈", "bold cyan")
    console.print("• Is my improvement within noise bounds of prior work?")
    console.print("• What explains the gap between my results and theirs?")
    console.print("• Which prior results are suspicious outliers?")
    console.print("• Have others tried and failed at this approach?")
    console.print(
        "• What's the real SOTA when you account for compute/data differences?\n",
    )

    # Technical Details
    output.section("Technical Details", "🎯", "bold cyan")
    console.print("• What batch size/learning rate scaling laws apply here?")
    console.print("• Which optimizer quirks matter for this problem?")
    console.print("• What numerical precision issues arise at this scale?")
    console.print("• How long do people actually train these models?")
    console.print("• What early stopping criteria work in practice?\n")

    # Common Research Questions
    output.section("Common Research Questions", "🔍", "bold cyan")
    console.print("• Has someone done this research already?")
    console.print("• What methods do other people use to analyze this problem?")
    console.print("• What are typical issues people run into?")
    console.print("• How do people typically do these analyses?")
    console.print("• Is our result consistent or contradictory with the literature?")
    console.print("• What are known open problems in the field?")
    console.print("• Any key papers I forgot to cite?\n")