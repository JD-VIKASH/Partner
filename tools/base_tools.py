from langchain_core.tools import tool
from ddgs import DDGS

@tool("Search")
def Search(query: str) -> str:
    """Useful for searching the web for real-time information, current events, or things you don't know."""
    print(f"\n🔮 [Frieren is casting the 'Search' spell for: '{query}'...]")
    try:
        results = DDGS().text(query, max_results=3)
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Error during search: {e}"

@tool("Create")
def Create(content: str) -> str:
    """Useful for drafting or creating a document's content in memory."""
    print(f"\n🔮 [Frieren is casting the 'Create' spell to draft a document...]")
    return "Document content created. You can now use the 'Save' spell to save it to a file if needed."

@tool("Save")
def Save(filename: str, content: str) -> str:
    """Useful for saving text, research notes, or code to a file. Requires filename and content."""
    print(f"\n🔮 [Frieren is casting the 'Save' spell, inscribing knowledge into '{filename}'...]")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {e}"

@tool("Spidy_Web")
def Spidy_Web(filename: str, html_content: str) -> str:
    """Useful for creating a basic website. Ensure html_content contains full valid HTML."""
    print(f"\n🔮 [Frieren is casting the 'Spidy Web' spell, weaving an HTML construct into '{filename}'...]")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        return f"Successfully created website at {filename}"
    except Exception as e:
        return f"Error creating website: {e}"

@tool("ConsolidateMemory")
def ConsolidateMemory() -> str:
    """Useful for organizing and compressing the user's memories into high-quality consolidated facts. Run this when asked to clean up or optimize memory."""
    from memory.consolidation import MemoryConsolidator
    print(f"\n🔮 [Frieren is casting the 'ConsolidateMemory' spell...]")
    consolidator = MemoryConsolidator()
    consolidator.run_full_consolidation()
    return "Memory consolidation complete. Redundant memories have been archived."

def get_base_tools():
    return [Search, Create, Save, Spidy_Web, ConsolidateMemory]
