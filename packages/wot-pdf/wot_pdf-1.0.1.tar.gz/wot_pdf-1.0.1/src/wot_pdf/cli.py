"""
🎯 WOT-PDF CLI
=============
Command-line interface for WOT-PDF
"""

import click
import logging
from pathlib import Path
from typing import Optional

from .api.main_api import generate_pdf, generate_book, list_templates, get_template_info
from .core.generator import PDFGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

@click.group()
@click.version_option(version="1.0.0", prog_name="wot-pdf")
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(debug):
    """🎯 WOT-PDF - Advanced PDF Generation with Typst & ReportLab"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

@main.command()
@click.option('--input', '-i', required=True, help='Input markdown file')
@click.option('--output', '-o', required=True, help='Output PDF file')
@click.option('--template', '-t', default='technical', 
              type=click.Choice(['academic', 'technical', 'corporate', 'educational', 'minimal']),
              help='Template to use')
@click.option('--title', help='Document title')
@click.option('--author', help='Document author')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate(input, output, template, title, author, verbose):
    """Generate PDF from markdown file"""
    
    if verbose:
        click.echo(f"🚀 Generating PDF...")
        click.echo(f"📄 Input: {input}")
        click.echo(f"📁 Output: {output}")
        click.echo(f"🎨 Template: {template}")
    
    try:
        result = generate_pdf(
            input_content=input,
            output_file=output,
            template=template,
            title=title,
            author=author
        )
        
        if result.get("success"):
            file_size_kb = result.get("file_size_bytes", 0) / 1024
            click.echo(f"✅ PDF generated successfully!")
            click.echo(f"📁 Output: {result['output_file']}")
            click.echo(f"📊 Size: {file_size_kb:.1f} KB")
            click.echo(f"⚙️  Template: {template}")
            click.echo(f"🔧 Engine: {result.get('engine', 'unknown')}")
        else:
            click.echo(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        exit(1)

@main.command()
@click.argument('input_dir')
@click.argument('output_file')
@click.option('--template', '-t', default='technical',
              type=click.Choice(['academic', 'technical', 'corporate', 'educational', 'minimal']),
              help='Template to use')
@click.option('--title', help='Book title (auto-generated if not provided)')
@click.option('--author', help='Book author')
@click.option('--recursive/--no-recursive', default=True, help='Search subdirectories')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def book(input_dir, output_file, template, title, author, recursive, verbose):
    """Generate book from directory of markdown files"""
    
    if verbose:
        click.echo(f"📚 Generating book...")
        click.echo(f"📂 Source: {input_dir}")
        click.echo(f"📁 Output: {output_file}")
        click.echo(f"🎨 Template: {template}")
        click.echo(f"🔍 Recursive: {recursive}")
    
    try:
        result = generate_book(
            input_dir=input_dir,
            output_file=output_file,
            template=template,
            title=title,
            author=author,
            recursive=recursive
        )
        
        if result.get("success"):
            file_size_kb = result.get("file_size_bytes", 0) / 1024
            click.echo(f"✅ Book generated successfully!")
            click.echo(f"📁 Output: {result['output_file']}")
            click.echo(f"📊 Size: {file_size_kb:.1f} KB")
            click.echo(f"📄 Source files: {result.get('source_files', 0)}")
            click.echo(f"⚙️  Template: {template}")
            click.echo(f"🔧 Engine: {result.get('engine', 'unknown')}")
        else:
            click.echo(f"❌ Book generation failed: {result.get('error', 'Unknown error')}")
            exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        exit(1)

@main.command()
def templates():
    """List available templates"""
    click.echo("📚 Available Templates:")
    click.echo()
    
    template_list = list_templates()
    
    for template in template_list:
        click.echo(f"🎨 {template['name']} ({template['name'].lower().replace(' ', '_')})")
        click.echo(f"   {template['description']}")
        
        features = ", ".join(template['features'][:3])
        if len(template['features']) > 3:
            features += f" (+{len(template['features']) - 3} more)"
        click.echo(f"   Features: {features}")
        click.echo()

@main.command()
@click.argument('template_name')
def template_info(template_name):
    """Show detailed information about a template"""
    info = get_template_info(template_name)
    
    if not info:
        click.echo(f"❌ Template '{template_name}' not found")
        click.echo("Use 'wot-pdf templates' to see available templates")
        exit(1)
    
    click.echo(f"🎨 {info['name']}")
    click.echo(f"📝 {info['description']}")
    click.echo()
    click.echo("✨ Features:")
    for feature in info['features']:
        click.echo(f"  • {feature.replace('_', ' ').title()}")
    click.echo()
    click.echo(f"📋 Best for: {info.get('best_for', 'General use')}")
    click.echo(f"🎭 Typography: {info.get('typography', 'Standard')}")
    click.echo(f"📏 Margins: {info.get('margins', 'Standard')}")

@main.command()
@click.option('--output-dir', '-o', default='template_previews', help='Output directory for previews')
def create_previews(output_dir):
    """Generate preview PDFs for all templates"""
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    click.echo("🎨 Creating template previews...")
    
    templates = ['technical', 'corporate', 'academic', 'educational', 'minimal']
    preview_content = """# Template Preview

This is a preview of the **{template}** template showcasing its unique styling.

## Features Overview

The {template} template provides:

- Professional typography and layout
- Consistent color scheme and branding  
- Optimized for {purpose} documents

## Sample Table

| Feature | Status | Quality |
|---------|--------|---------|
| Typography | ✅ Excellent | A+ |
| Layout | ✅ Professional | A+ |
| Colors | ✅ Consistent | A |

## Sample Quote

> This template demonstrates the high-quality output possible with WOT-PDF's advanced rendering capabilities.

## Code Example

```python
def generate_preview():
    return "Professional PDF generated successfully!"
```

*Preview generated by WOT-PDF*"""

    purposes = {
        'technical': 'technical documentation and API guides',
        'corporate': 'executive reports and business documents', 
        'academic': 'research papers and academic publications',
        'educational': 'learning materials and training guides',
        'minimal': 'simple, clean documents'
    }
    
    for template in templates:
        content = preview_content.format(template=template, purpose=purposes[template])
        output_file = output_path / f"preview_{template}.pdf"
        
        try:
            result = generate_pdf(
                input_content=content,
                output_file=str(output_file),
                template=template,
                title=f"{template.title()} Template Preview"
            )
            
            if result.get("success"):
                size_kb = result.get("file_size_bytes", 0) / 1024
                click.echo(f"  ✅ {template.title()}: {output_file} ({size_kb:.1f} KB)")
            else:
                click.echo(f"  ❌ {template.title()}: Failed")
                
        except Exception as e:
            click.echo(f"  ❌ {template.title()}: Error - {e}")
    
    click.echo(f"\n📁 Previews saved to: {output_path}")

@main.command()
def version():
    """Show version information"""
    from . import get_info
    
    info = get_info()
    click.echo(f"🎯 {info['name']} v{info['version']}")
    click.echo(f"👨‍💻 {info['author']}")
    click.echo(f"📜 License: {info['license']}")
    click.echo()
    click.echo(f"🎨 Templates: {len(info['templates'])}")
    click.echo(f"🔧 Engines: {', '.join(info['engines'])}")

@main.command()
@click.argument('input_file')
@click.option('--output-dir', '-o', default='multi_output', help='Output directory')
@click.option('--templates', '-t', default='technical,corporate,academic', help='Comma-separated template list')
@click.option('--title', help='Document title')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def multi_template(input_file, output_dir, templates, title, verbose):
    """Generate the same document with multiple templates for comparison"""
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    template_list = [t.strip() for t in templates.split(',')]
    input_path = Path(input_file)
    
    if not input_path.exists():
        click.echo(f"❌ Input file not found: {input_file}")
        exit(1)
    
    if verbose:
        click.echo(f"🎨 Generating {len(template_list)} variations...")
        click.echo(f"📄 Input: {input_file}")
        click.echo(f"📁 Output dir: {output_dir}")
        click.echo(f"🎭 Templates: {', '.join(template_list)}")
    
    results = []
    for template in template_list:
        output_file = output_path / f"{input_path.stem}_{template}.pdf"
        
        try:
            result = generate_pdf(
                input_content=str(input_path),
                output_file=str(output_file),
                template=template,
                title=title or f"{input_path.stem.title()} - {template.title()} Style"
            )
            
            if result.get("success"):
                size_kb = result.get("file_size_bytes", 0) / 1024
                engine = result.get("engine", "unknown")
                results.append((template, output_file, size_kb, engine, True))
                if verbose:
                    click.echo(f"  ✅ {template.title()}: {size_kb:.1f} KB ({engine})")
            else:
                results.append((template, output_file, 0, "failed", False))
                click.echo(f"  ❌ {template.title()}: Failed")
                
        except Exception as e:
            results.append((template, output_file, 0, "error", False))
            click.echo(f"  ❌ {template.title()}: Error - {e}")
    
    # Summary
    successful = sum(1 for r in results if r[4])
    click.echo(f"\n📊 Summary: {successful}/{len(template_list)} templates successful")
    click.echo(f"📁 Files saved to: {output_path}")
    
    if verbose and successful > 0:
        click.echo("\n📋 Generated files:")
        for template, file_path, size, engine, success in results:
            if success:
                click.echo(f"  • {file_path} ({size:.1f} KB, {engine})")

if __name__ == '__main__':
    main()
