"""Context management for papers in conversation."""

from dataclasses import dataclass, field

from litai.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ContextEntry:
    """Represents a paper in the context with multiple extraction types."""
    paper_id: str
    paper_title: str
    context_types: set[str] = field(default_factory=set)
    extracted_content: dict[str, str] = field(default_factory=dict)
    
    def add_context_type(self, context_type: str, content: str) -> None:
        """Add a context type with its content."""
        self.context_types.add(context_type)
        self.extracted_content[context_type] = content
        logger.info("context_type_added", paper_id=self.paper_id, context_type=context_type)
    
    def remove_context_type(self, context_type: str) -> None:
        """Remove a specific context type."""
        self.context_types.discard(context_type)
        self.extracted_content.pop(context_type, None)
        logger.info("context_type_removed", paper_id=self.paper_id, context_type=context_type)
    
    def get_combined_context(self) -> str:
        """Get ALL context types combined for synthesis."""
        parts = []
        for ctype in sorted(self.context_types):
            if ctype in self.extracted_content:
                parts.append(f'=== {ctype.upper()} ===\n{self.extracted_content[ctype]}')
        return '\n\n'.join(parts)

class SessionContext:
    """Manages papers and their context for the current session."""
    
    def __init__(self) -> None:
        self.papers: dict[str, ContextEntry] = {}
        logger.info("session_context_initialized")
    
    def add_paper(self, paper_id: str, paper_title: str, context_type: str, content: str) -> None:
        """Add a paper with a specific context type."""
        if paper_id not in self.papers:
            self.papers[paper_id] = ContextEntry(paper_id, paper_title)
            logger.info("paper_added_to_context", paper_id=paper_id, title=paper_title)
        self.papers[paper_id].add_context_type(context_type, content)
    
    def remove_paper(self, paper_id: str, context_type: str | None = None) -> None:
        """Remove a paper or specific context type."""
        if paper_id in self.papers:
            if context_type:
                self.papers[paper_id].remove_context_type(context_type)
                if not self.papers[paper_id].context_types:
                    del self.papers[paper_id]
                    logger.info("paper_removed_from_context", paper_id=paper_id)
            else:
                del self.papers[paper_id]
                logger.info("paper_removed_from_context", paper_id=paper_id)
    
    def clear(self) -> None:
        """Clear all context."""
        self.papers.clear()
        logger.info("context_cleared")
    
    def get_all_context(self) -> str:
        """Get combined context from all papers for synthesis."""
        if not self.papers:
            return ""
        
        combined = []
        for _paper_id, entry in self.papers.items():
            combined.append(f"Paper: {entry.paper_title}")
            combined.append(entry.get_combined_context())
            combined.append("")  # Blank line between papers
        
        return '\n'.join(combined)
    
    def get_paper_count(self) -> int:
        """Get number of papers in context."""
        return len(self.papers)
    
    def has_paper(self, paper_id: str) -> bool:
        """Check if a paper is in context."""
        return paper_id in self.papers
    
    def get_all_papers(self) -> dict[str, set[str]]:
        """Get all papers with their context types."""
        return {paper_id: entry.context_types for paper_id, entry in self.papers.items()}