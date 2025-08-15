"""
🎯 WOT-PDF Main API
==================
High-level convenience functions for PDF generation
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..core.generator import PDFGenerator
from ..core.book_generator import BookGenerator
from ..core.template_manager import TemplateManager

# Global instances for convenience
_pdf_generator = None
_book_generator = None
_template_manager = None

def get_pdf_generator() -> PDFGenerator:
    """Get or create global PDF generator instance"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFGenerator()
    return _pdf_generator

def get_book_generator() -> BookGenerator:
    """Get or create global book generator instance"""
    global _book_generator
    if _book_generator is None:
        _book_generator = BookGenerator(get_pdf_generator())
    return _book_generator

def get_template_manager() -> TemplateManager:
    """Get or create global template manager instance"""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager

def generate_pdf(input_content: Union[str, Path],
                 output_file: Union[str, Path],
                 template: str = "technical",
                 title: Optional[str] = None,
                 author: Optional[str] = None,
                 **kwargs) -> Dict[str, Any]:
    """
    Generate PDF from markdown content
    
    Args:
        input_content: Markdown content or file path
        output_file: Output PDF file path
        template: Template name (default: "technical")
        title: Document title
        author: Document author
        **kwargs: Additional template parameters
        
    Returns:
        Generation result dictionary
        
    Example:
        >>> result = generate_pdf("# Hello World", "output.pdf")
        >>> print(result["success"])
        True
    """
    generator = get_pdf_generator()
    
    return generator.generate(
        input_content=input_content,
        output_file=Path(output_file),
        template=template,
        title=title,
        author=author,
        **kwargs
    )

def generate_book(input_dir: Union[str, Path],
                  output_file: Union[str, Path],
                  template: str = "technical", 
                  title: Optional[str] = None,
                  author: Optional[str] = None,
                  recursive: bool = True,
                  **kwargs) -> Dict[str, Any]:
    """
    Generate book from directory of markdown files
    
    Args:
        input_dir: Directory containing markdown files
        output_file: Output PDF file path
        template: Template name (default: "technical")
        title: Book title (auto-generated if None)
        author: Book author
        recursive: Search subdirectories for markdown files
        **kwargs: Additional template parameters
        
    Returns:
        Generation result dictionary
        
    Example:
        >>> result = generate_book("./docs/", "book.pdf", template="academic")
        >>> print(f"Generated book with {result['source_files']} files")
    """
    book_gen = get_book_generator()
    
    return book_gen.generate_book(
        input_dir=Path(input_dir),
        output_file=Path(output_file),
        template=template,
        title=title,
        author=author,
        recursive=recursive,
        **kwargs
    )

def list_templates() -> List[Dict[str, Any]]:
    """
    List all available templates
    
    Returns:
        List of template information dictionaries
        
    Example:
        >>> templates = list_templates()
        >>> for template in templates:
        ...     print(f"{template['name']}: {template['description']}")
    """
    manager = get_template_manager()
    return manager.list_templates()

def get_template_info(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific template
    
    Args:
        template_name: Name of the template
        
    Returns:
        Template information dictionary or None if not found
        
    Example:
        >>> info = get_template_info("academic")
        >>> print(info["features"])
        ['citations', 'bibliography', 'equations', 'figures', 'abstract']
    """
    manager = get_template_manager()
    return manager.get_template(template_name)

def search_templates(query: str) -> List[Dict[str, Any]]:
    """
    Search templates by keyword
    
    Args:
        query: Search query
        
    Returns:
        List of matching templates
        
    Example:
        >>> results = search_templates("academic")
        >>> print([t["name"] for t in results])
        ['Academic Paper']
    """
    manager = get_template_manager()
    return manager.search_templates(query)

def validate_template(template_name: str) -> bool:
    """
    Check if template exists
    
    Args:
        template_name: Name of the template
        
    Returns:
        True if template exists, False otherwise
        
    Example:
        >>> validate_template("technical")
        True
        >>> validate_template("nonexistent")
        False
    """
    manager = get_template_manager()
    return manager.validate_template(template_name)

# Convenience aliases
pdf = generate_pdf
book = generate_book
templates = list_templates
