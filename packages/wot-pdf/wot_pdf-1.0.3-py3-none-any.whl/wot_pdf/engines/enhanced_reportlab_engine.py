#!/usr/bin/env python3
"""
🎯 ENHANCED REPORTLAB ENGINE - PROFESSIONAL THEMES
==================================================
⚡ Advanced ReportLab engine with Typst-quality themes
🔷 Professional styling matching Typst output quality
📊 Hybrid approach for maximum compatibility and beauty

FEATURES:
- Professional color schemes from Typst themes
- Advanced typography with custom fonts
- Template-specific styling and layouts
- Code highlighting and professional formatting
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Table, TableStyle, Image, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.colors import HexColor, black, blue, red, green, gray, white
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.platypus.tableofcontents import TableOfContents
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class EnhancedReportLabEngine:
    """
    Enhanced ReportLab PDF engine with professional Typst-quality themes
    """
    
    # PROFESSIONAL THEME DEFINITIONS (matching Typst themes)
    PROFESSIONAL_THEMES = {
        'modern_blue': {
            'name': '🔵 Modern Blue Professional',
            'primary_color': '#2563eb',
            'secondary_color': '#1e40af', 
            'accent_color': '#3b82f6',
            'text_color': '#1f2937',
            'background_color': '#f8fafc',
            'code_bg': '#f1f5f9'
        },
        'elegant_forest': {
            'name': '🌲 Elegant Forest',
            'primary_color': '#059669',
            'secondary_color': '#047857',
            'accent_color': '#10b981', 
            'text_color': '#1f2937',
            'background_color': '#f0fdf4',
            'code_bg': '#ecfdf5'
        },
        'warm_autumn': {
            'name': '🍂 Warm Autumn',
            'primary_color': '#dc2626',
            'secondary_color': '#b91c1c',
            'accent_color': '#ef4444',
            'text_color': '#1f2937', 
            'background_color': '#fef2f2',
            'code_bg': '#fee2e2'
        },
        'royal_purple': {
            'name': '👑 Royal Purple',
            'primary_color': '#7c3aed',
            'secondary_color': '#6d28d9',
            'accent_color': '#8b5cf6',
            'text_color': '#1f2937',
            'background_color': '#faf5ff',
            'code_bg': '#f3e8ff'
        },
        'corporate_gray': {
            'name': '🏢 Corporate Gray',
            'primary_color': '#374151',
            'secondary_color': '#1f2937',
            'accent_color': '#6b7280',
            'text_color': '#111827',
            'background_color': '#f9fafb',
            'code_bg': '#f3f4f6'
        }
    }
    
    # TEMPLATE CONFIGURATIONS
    TEMPLATE_CONFIGS = {
        'technical': {
            'theme': 'modern_blue',
            'features': ['code_highlighting', 'api_docs', 'diagrams'],
            'font_size': 11,
            'line_spacing': 1.2
        },
        'academic': {
            'theme': 'elegant_forest', 
            'features': ['citations', 'bibliography', 'equations'],
            'font_size': 12,
            'line_spacing': 1.4
        },
        'corporate': {
            'theme': 'corporate_gray',
            'features': ['executive_summary', 'charts', 'branding'], 
            'font_size': 11,
            'line_spacing': 1.3
        },
        'educational': {
            'theme': 'warm_autumn',
            'features': ['exercises', 'examples', 'highlights'],
            'font_size': 12,
            'line_spacing': 1.3
        },
        'minimal': {
            'theme': 'corporate_gray',
            'features': ['clean_typography', 'basic_formatting'],
            'font_size': 11,
            'line_spacing': 1.2
        }
    }
    
    def __init__(self):
        """Initialize enhanced ReportLab engine"""
        self.logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required but not installed")
        
        self.styles = getSampleStyleSheet()
        self.theme = None
        self.template_config = None
        
    def _setup_professional_styles(self, template: str = "technical"):
        """Setup professional paragraph styles with Typst-quality themes"""
        
        # Get template configuration
        self.template_config = self.TEMPLATE_CONFIGS.get(template, self.TEMPLATE_CONFIGS['technical'])
        theme_name = self.template_config['theme']
        self.theme = self.PROFESSIONAL_THEMES[theme_name]
        
        # Clear existing custom styles
        custom_styles = ['ProfTitle', 'ProfSubtitle', 'ProfCode', 'ProfQuote', 'ProfCaption']
        for i in range(1, 7):
            custom_styles.append(f'ProfHeading{i}')
        
        for style_name in custom_styles:
            if style_name in self.styles:
                del self.styles[style_name]
        
        # Professional title style
        self.styles.add(ParagraphStyle(
            name='ProfTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor(self.theme['primary_color']),
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Professional subtitle
        self.styles.add(ParagraphStyle(
            name='ProfSubtitle', 
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor(self.theme['secondary_color']),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Professional headings with theme colors
        heading_sizes = [18, 16, 14, 13, 12, 11]
        for i, size in enumerate(heading_sizes, 1):
            self.styles.add(ParagraphStyle(
                name=f'ProfHeading{i}',
                parent=self.styles['Normal'],
                fontSize=size,
                textColor=HexColor(self.theme['primary_color']),
                fontName='Helvetica-Bold',
                spaceAfter=12,
                spaceBefore=20 if i <= 2 else 16,
                leftIndent=0
            ))
        
        # Professional code style
        self.styles.add(ParagraphStyle(
            name='ProfCode',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=HexColor(self.theme['text_color']),
            backColor=HexColor(self.theme['code_bg']),
            fontName='Courier',
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=20,
            rightIndent=20,
            borderColor=HexColor(self.theme['accent_color']),
            borderWidth=1,
            borderPadding=8
        ))
        
        # Professional quote style
        self.styles.add(ParagraphStyle(
            name='ProfQuote',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor(self.theme['secondary_color']),
            fontName='Helvetica-Oblique',
            leftIndent=30,
            rightIndent=30,
            spaceAfter=12,
            spaceBefore=12,
            borderColor=HexColor(self.theme['accent_color']),
            borderWidth=0,
            borderPadding=0,
            leftBorderWidth=3,  # Left border for quote
            leftBorderColor=HexColor(self.theme['accent_color']),
            leftBorderPadding=15
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='ProfCaption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor(self.theme['secondary_color']),
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=6
        ))
    
    def _create_professional_header_footer(self, canvas, doc, title: str, author: str):
        """Create professional header and footer"""
        canvas.saveState()
        
        # Header
        if hasattr(doc, 'page') and doc.page > 1:  # Skip header on first page
            header_text = title[:50] + "..." if len(title) > 50 else title
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(HexColor(self.theme['secondary_color']))
            canvas.drawString(50, A4[1] - 30, header_text)
            
            # Header line
            canvas.setStrokeColor(HexColor(self.theme['accent_color']))
            canvas.setLineWidth(0.5)
            canvas.line(50, A4[1] - 35, A4[0] - 50, A4[1] - 35)
        
        # Footer
        canvas.setFont('Helvetica', 9) 
        canvas.setFillColor(HexColor(self.theme['secondary_color']))
        
        # Page number
        canvas.drawRightString(A4[0] - 50, 30, f"Page {doc.page}")
        
        # Author/date
        footer_left = f"{author} • {datetime.now().strftime('%Y-%m-%d')}"
        canvas.drawString(50, 30, footer_left)
        
        # Footer line
        canvas.setStrokeColor(HexColor(self.theme['accent_color']))
        canvas.setLineWidth(0.5)
        canvas.line(50, 45, A4[0] - 50, 45)
        
        canvas.restoreState()
    
    def generate(self,
                 content: str,
                 output_file: Path,
                 template: str = "technical",
                 title: Optional[str] = None,
                 author: Optional[str] = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Generate professional PDF with enhanced styling
        """
        try:
            # Setup professional styles
            self._setup_professional_styles(template)
            
            # Create document with professional styling
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=60,
                title=title or "Document",
                author=author or "WOT-PDF"
            )
            
            # Create story (content elements)
            story = []
            
            # Add title page if title provided
            if title:
                story.append(Paragraph(title, self.styles['ProfTitle']))
                if author:
                    story.append(Paragraph(f"by {author}", self.styles['ProfSubtitle']))
                story.append(Spacer(1, 40))
                story.append(PageBreak())
            
            # Process markdown content
            story.extend(self._process_markdown_content(content))
            
            # Build PDF with professional header/footer
            def add_header_footer(canvas, doc):
                self._create_professional_header_footer(canvas, doc, title or "Document", author or "WOT-PDF")
            
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            # Get file size
            file_size = output_file.stat().st_size if output_file.exists() else 0
            
            self.logger.info(f"✅ Enhanced ReportLab PDF generated: {output_file} ({file_size/1024:.1f} KB)")
            
            return {
                "success": True,
                "output_file": str(output_file),
                "file_size_bytes": file_size,
                "template": template,
                "theme": self.theme['name'],
                "engine": "enhanced_reportlab"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced ReportLab generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "enhanced_reportlab"
            }
    
    def _process_markdown_content(self, content: str) -> List[Any]:
        """Process markdown content into ReportLab story elements"""
        story = []
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ').strip()
                if header_text and level <= 6:
                    story.append(Paragraph(header_text, self.styles[f'ProfHeading{level}']))
                    story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Code blocks
            if line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    # Escape HTML entities and special characters
                    code_text = (code_text
                                .replace('&', '&amp;')
                                .replace('<', '&lt;')
                                .replace('>', '&gt;')
                                .replace('"', '&quot;')
                                .replace("'", '&#39;'))
                    
                    # Handle very long code blocks
                    if len(code_text) > 2000:
                        code_text = code_text[:1997] + "..."
                    
                    try:
                        story.append(Paragraph(f'<font name="Courier">{code_text}</font>', self.styles['ProfCode']))
                    except Exception as e:
                        # Fallback: add as plain text without formatting
                        self.logger.warning(f"Code block formatting failed, using plain text: {e}")
                        story.append(Paragraph(f'CODE BLOCK:\n{code_text[:500]}...', self.styles['Normal']))
                    
                    story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Block quotes
            if line.startswith('>'):
                quote_text = line.lstrip('> ').strip()
                story.append(Paragraph(quote_text, self.styles['ProfQuote']))
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Lists
            if line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', line):
                list_items = []
                while i < len(lines) and lines[i].strip() and (
                    lines[i].strip().startswith(('- ', '* ', '+ ')) or 
                    re.match(r'^\d+\.\s', lines[i].strip())
                ):
                    item_text = re.sub(r'^[-*+]\s|\d+\.\s', '', lines[i].strip())
                    list_items.append(f'• {item_text}')
                    i += 1
                
                for item in list_items:
                    story.append(Paragraph(item, self.styles['Normal']))
                    story.append(Spacer(1, 3))
                story.append(Spacer(1, 6))
                continue
            
            # Table detection (simple markdown tables)
            if '|' in line and line.count('|') >= 2:
                # This looks like a table row, handle it simply
                # Escape basic characters but preserve table structure
                table_text = (line.replace('&', '&amp;')
                                 .replace('<', '&lt;')
                                 .replace('>', '&gt;'))
                # Don't process as complex inline formatting
                try:
                    story.append(Paragraph(table_text, self.styles['Normal']))
                except Exception as e:
                    # Fallback: completely clean text
                    clean_text = line.replace('<', '').replace('>', '').replace('&', '').replace('|', ' | ')
                    story.append(Paragraph(clean_text, self.styles['Normal']))
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Regular paragraph
            para_text = self._process_inline_formatting(line)
            
            # Final safety check for paragraph creation
            try:
                story.append(Paragraph(para_text, self.styles['Normal']))
            except Exception as e:
                # Fallback: completely clean text without any formatting
                self.logger.warning(f"Paragraph formatting failed, using plain text: {e}")
                clean_text = (line.replace('<', '')
                                 .replace('>', '')
                                 .replace('&', '')
                                 .replace('|', ' | '))
                story.append(Paragraph(clean_text, self.styles['Normal']))
            
            story.append(Spacer(1, 6))
            i += 1
        
        return story
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process inline markdown formatting with proper HTML escaping"""
        
        # First escape HTML entities in the entire text
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Process markdown formatting with escaped content
        # Bold - use simple replacement to avoid regex issues
        import re
        
        # Process inline code first (most restrictive)
        def escape_code_content(match):
            code_content = match.group(1)
            # Double-escape for code content to prevent XML parsing issues
            escaped = (code_content.replace('&', '&amp;')
                                  .replace('<', '&lt;')
                                  .replace('>', '&gt;')
                                  .replace('"', '&quot;')
                                  .replace("'", '&#39;'))
            return f'<font name="Courier">{escaped}</font>'
        
        # Apply inline code processing
        text = re.sub(r'`([^`]+)`', escape_code_content, text)
        
        # Now re-enable HTML tags for formatting (after code is processed)
        text = (text.replace('&lt;b&gt;', '<b>')
                   .replace('&lt;/b&gt;', '</b>')
                   .replace('&lt;i&gt;', '<i>')
                   .replace('&lt;/i&gt;', '</i>')
                   .replace('&lt;u&gt;', '<u>')
                   .replace('&lt;/u&gt;', '</u>')
                   .replace('&lt;font name="Courier"&gt;', '<font name="Courier">'))
        
        # Bold formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        
        # Italic formatting 
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        
        # Links (basic)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'<u>\1</u>', text)
        
        return text


# Create alias for backward compatibility
ReportLabEngine = EnhancedReportLabEngine

if __name__ == "__main__":
    # Quick test
    engine = EnhancedReportLabEngine()
    test_content = """
# Test Professional Document

This is a **professional** document with *enhanced* styling.

## Code Example

```python
def hello_world():
    print("Hello, professional world!")
```

> This is a professional quote with beautiful styling.

## Features

- Professional color themes
- Enhanced typography  
- Beautiful code highlighting
- Modern layout design

The enhanced ReportLab engine provides Typst-quality output!
"""
    
    result = engine.generate(
        content=test_content,
        output_file=Path("test_enhanced.pdf"),
        template="technical", 
        title="Enhanced ReportLab Test",
        author="WOT-PDF Team"
    )
    
    print(f"Test result: {result}")
