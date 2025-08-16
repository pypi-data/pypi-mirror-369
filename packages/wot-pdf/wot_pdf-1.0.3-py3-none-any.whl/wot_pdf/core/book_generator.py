"""
🎯 Book Generator - Enhanced with Typst Optimization
===================================================
Convert directories of markdown files into professional books
Integrated with Future-Proofing and Typst Content Optimization
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .generator import PDFGenerator

# Import optimization systems
try:
    from .typst_content_optimizer import TypstContentOptimizer
    CONTENT_OPTIMIZER_AVAILABLE = True
except ImportError:
    CONTENT_OPTIMIZER_AVAILABLE = False
    logging.warning("Typst Content Optimizer not available")

try:
    from .future_proofing_system import FutureProofingSystem
    FUTURE_PROOFING_AVAILABLE = True
except ImportError:
    FUTURE_PROOFING_AVAILABLE = False
    logging.warning("Future-Proofing System not available")

class BookGenerator:
    """
    Enhanced book generator with Typst optimization and future-proofing
    """
    
    def __init__(self, pdf_generator: Optional[PDFGenerator] = None):
        """
        Initialize enhanced book generator
        
        Args:
            pdf_generator: PDF generator instance (optional)
        """
        self.pdf_generator = pdf_generator or PDFGenerator()
        self.logger = logging.getLogger(__name__)
        
        # Initialize optimization systems
        if CONTENT_OPTIMIZER_AVAILABLE:
            self.content_optimizer = TypstContentOptimizer()
            self.logger.info("🎯 Typst Content Optimizer enabled")
        else:
            self.content_optimizer = None
            
        if FUTURE_PROOFING_AVAILABLE:
            self.future_proofing = FutureProofingSystem()
            self.logger.info("🛡️ Future-Proofing System enabled")
        else:
            self.future_proofing = None
    
    def generate_book(self,
                      input_dir: Path,
                      output_file: Path,
                      template: str = "technical",
                      title: Optional[str] = None,
                      author: Optional[str] = None,
                      recursive: bool = True,
                      file_pattern: str = "*.md",
                      **kwargs) -> Dict[str, Any]:
        """
        Enhanced book generation with Typst optimization and future-proofing
        
        Args:
            input_dir: Directory containing markdown files
            output_file: Output PDF file path
            template: Template name
            title: Book title (auto-generated if None)
            author: Book author
            recursive: Search subdirectories
            file_pattern: File pattern to match
            **kwargs: Additional template parameters
            
        Returns:
            Generation result with optimization details
        """
        try:
            input_path = Path(input_dir)
            if not input_path.exists():
                raise FileNotFoundError(f"Input directory not found: {input_path}")
            
            # Find markdown files
            markdown_files = self._find_markdown_files(input_path, recursive, file_pattern)
            
            if not markdown_files:
                raise ValueError(f"No markdown files found in {input_path}")
            
            self.logger.info(f"Found {len(markdown_files)} markdown files")
            
            # Combine files into single content
            combined_content = self._combine_files(markdown_files)
            
            # STEP 1: Apply Typst Content Optimization
            optimization_info = {"applied": False, "issues": []}
            if self.content_optimizer:
                self.logger.info("🎯 Applying Typst content optimization...")
                try:
                    optimized_content = self.content_optimizer.optimize_content_for_typst(
                        combined_content, template
                    )
                    combined_content = optimized_content
                    optimization_info["applied"] = True
                    self.logger.info("✅ Typst optimization applied successfully")
                except Exception as e:
                    self.logger.warning(f"⚠️ Typst optimization failed: {e}")
                    optimization_info["error"] = str(e)
            
            # STEP 2: Apply Future-Proofing Security
            security_info = {"applied": False, "issues": []}
            if self.future_proofing:
                self.logger.info("🛡️ Applying future-proofing protection...")
                try:
                    processed_content, issues = self.future_proofing.process_content_safely(
                        combined_content, f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    combined_content = processed_content
                    security_info["applied"] = True
                    security_info["issues"] = issues
                    if issues:
                        self.logger.info(f"🛡️ Resolved {len(issues)} security/compatibility issues")
                except Exception as e:
                    self.logger.warning(f"⚠️ Future-proofing failed: {e}")
                    security_info["error"] = str(e)
            
            # Generate metadata
            book_title = title or self._generate_title(input_path)
            book_author = author or "Generated by WOT-PDF"
            
            # Generate PDF
            result = self.pdf_generator.generate(
                input_content=combined_content,
                output_file=output_file,
                template=template,
                title=book_title,
                author=book_author,
                **kwargs
            )
            
            # Add book-specific metadata
            if result.get("success"):
                result.update({
                    "book_title": book_title,
                    "book_author": book_author,
                    "source_files": len(markdown_files),
                    "source_directory": str(input_path),
                    "optimization_applied": optimization_info,
                    "security_protection": security_info,
                    "enhanced_features": {
                        "typst_optimization": optimization_info["applied"],
                        "future_proofing": security_info["applied"],
                        "total_issues_resolved": len(security_info.get("issues", []))
                    }
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Book generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_directory": str(input_dir)
            }
    
    def _find_markdown_files(self, 
                           directory: Path, 
                           recursive: bool, 
                           pattern: str) -> List[Path]:
        """Find markdown files in directory"""
        files = []
        
        if recursive:
            # Recursive search
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    files.append(file_path)
        else:
            # Non-recursive search
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    files.append(file_path)
        
        # Sort files for consistent ordering
        return sorted(files)
    
    def _combine_files(self, files: List[Path]) -> str:
        """Combine multiple markdown files with automatic chapter numbering"""
        combined_lines = []
        chapter_num = 1
        
        for file_path in files:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Process content to add chapter numbering
                content_lines = content.split('\n')
                processed_lines = []
                
                for line in content_lines:
                    # Add chapter number to main headers (# Header)
                    if line.strip().startswith('# ') and not line.strip().startswith('## '):
                        header_text = line.strip()[2:].strip()
                        # Add chapter number
                        numbered_header = f"# {chapter_num}. {header_text}"
                        processed_lines.append(numbered_header)
                        chapter_num += 1
                    else:
                        processed_lines.append(line)
                
                # Add processed content
                combined_lines.append("")
                combined_lines.extend(processed_lines)
                combined_lines.append("")
                combined_lines.append("---")  # Section separator
                combined_lines.append("")
                
            except Exception as e:
                self.logger.warning(f"Failed to read {file_path}: {e}")
                combined_lines.append(f"<!-- Error reading {file_path.name}: {e} -->")
                combined_lines.append("")
        
        return "\n".join(combined_lines)
    
    def _generate_title(self, input_dir: Path) -> str:
        """Generate book title from directory name"""
        dir_name = input_dir.name
        
        # Clean up directory name
        title = dir_name.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Add "Guide" or "Manual" suffix if not present
        if not any(suffix in title.lower() for suffix in ['guide', 'manual', 'book', 'documentation']):
            title += " Guide"
        
        return title
