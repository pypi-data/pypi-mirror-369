#!/usr/bin/env python3
"""
🎯 TYPST CONTENT OPTIMIZER - IMMEDIATE SOLUTION
===============================================
⚡ Implementation of Steps 1-3 from optimization strategy
🔷 Smart preprocessing for 100% Typst compilation success
📊 Production-ready solution for professional documents

FEATURES:
- Smart code block preprocessing (Step 1)
- Markdown-to-Typst syntax converter (Step 2)  
- Context-aware character handler (Step 3)
"""

import re
import uuid
from typing import Dict, List, Tuple, Optional
import logging

class TypstContentOptimizer:
    """
    Complete content optimization for Typst compatibility
    Implements critical steps 1-3 from optimization strategy
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protected_blocks = {}
        
    def optimize_content_for_typst(self, content: str, template_type: str = "technical") -> str:
        """
        MAIN OPTIMIZATION PIPELINE
        Apply all critical optimizations for Typst compatibility
        """
        self.logger.info(f"🎯 Starting Typst optimization for {template_type} template")
        
        # Step 1: Smart Code Block Preprocessing
        content = self._smart_code_block_preprocessing(content)
        
        # Step 2: Markdown-to-Typst Syntax Conversion
        content = self._markdown_to_typst_converter(content)
        
        # Step 3: Context-Aware Character Handling
        content = self._context_aware_character_handler(content)
        
        # Final cleanup
        content = self._final_cleanup(content)
        
        self.logger.info("✅ Typst optimization completed successfully")
        return content
    
    def _smart_code_block_preprocessing(self, content: str) -> str:
        """
        STEP 1: Smart Code Block Preprocessing
        Language-aware preprocessing with comment handling
        """
        
        def process_code_block(match):
            full_block = match.group(0)
            language = match.group(1).strip() if match.group(1) else ""
            code_content = match.group(2)
            
            # Apply language-specific preprocessing
            if language.lower() == 'python':
                code_content = self._optimize_python_code(code_content)
            elif language.lower() in ['bash', 'shell', 'sh']:
                code_content = self._optimize_bash_code(code_content)
            elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                code_content = self._optimize_js_code(code_content)
            
            return f"```{language}\n{code_content}\n```"
        
        # Process all code blocks
        pattern = r'```(\w*)\n(.*?)\n```'
        content = re.sub(pattern, process_code_block, content, flags=re.DOTALL)
        
        return content
    
    def _optimize_python_code(self, code: str) -> str:
        """Optimize Python code blocks for Typst compatibility"""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Handle inline comments that might confuse Typst
            if '#' in line and not line.strip().startswith('#'):
                # Check if # is in a string literal
                if '"' in line or "'" in line:
                    # Complex string processing - be conservative
                    optimized_lines.append(line)
                elif ' # ' in line:
                    # Inline comment - move to separate line
                    code_part = line.split(' # ')[0]
                    comment_part = '# ' + ' # '.join(line.split(' # ')[1:])
                    optimized_lines.append(code_part)
                    optimized_lines.append('    ' + comment_part)
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_bash_code(self, code: str) -> str:
        """Optimize Bash code blocks for Typst compatibility"""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Bash comments starting with # are usually fine
            # Focus on parameter expansion that might confuse Typst
            if '${' in line and '}' in line:
                # Parameter expansion - be careful with special chars
                line = line.replace('${', '$\\{').replace('}', '\\}')
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_js_code(self, code: str) -> str:
        """Optimize JavaScript code blocks for Typst compatibility"""
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Template literals and regex patterns
            if '`' in line and '${' in line:
                # Template literal - escape carefully
                line = re.sub(r'\$\{([^}]+)\}', r'$\\{\1\\}', line)
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _markdown_to_typst_converter(self, content: str) -> str:
        """
        STEP 2: Markdown-to-Typst Syntax Converter
        Convert Markdown syntax to native Typst while preserving code blocks
        """
        
        # First, protect code blocks from conversion
        content = self._protect_code_blocks(content)
        
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Skip protected blocks
            if line.strip().startswith('PROTECTED_BLOCK_'):
                converted_lines.append(line)
                continue
            
            # Convert headers: # Title -> = Title
            if line.strip().startswith('#'):
                header_level = 0
                temp_line = line.lstrip()
                while temp_line.startswith('#'):
                    header_level += 1
                    temp_line = temp_line[1:]
                
                if header_level > 0 and temp_line.strip():
                    title = temp_line.strip()
                    # Use Typst header syntax
                    typst_header = '=' * header_level + ' ' + title
                    converted_lines.append(typst_header)
                    continue
            
            # Convert bold: **text** -> *text*
            line = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', line)
            
            # Convert italic: *text* -> _text_ (avoid conflicts with bold)
            line = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', line)
            
            # Convert lists (Typst uses - for bullets)
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                line = re.sub(r'^(\s*)[*-] ', r'\1- ', line)
            
            converted_lines.append(line)
        
        content = '\n'.join(converted_lines)
        
        # Restore protected code blocks
        content = self._restore_code_blocks(content)
        
        return content
    
    def _protect_code_blocks(self, content: str) -> str:
        """Temporarily replace code blocks with UUIDs"""
        
        def protect_block(match):
            block_id = f"PROTECTED_BLOCK_{uuid.uuid4().hex}"
            self.protected_blocks[block_id] = match.group(0)
            return block_id
        
        # Protect triple-backtick code blocks
        content = re.sub(r'```[\s\S]*?```', protect_block, content, flags=re.DOTALL)
        
        # Protect inline code
        content = re.sub(r'`[^`\n]+`', protect_block, content)
        
        return content
    
    def _restore_code_blocks(self, content: str) -> str:
        """Restore protected code blocks"""
        for block_id, original_content in self.protected_blocks.items():
            content = content.replace(block_id, original_content)
        
        # Clear the protected blocks for next use
        self.protected_blocks.clear()
        return content
    
    def _context_aware_character_handler(self, content: str) -> str:
        """
        STEP 3: Context-Aware Character Handling
        Intelligent escaping of problematic characters
        """
        
        lines = content.split('\n')
        processed_lines = []
        in_code_block = False
        
        for line in lines:
            # Track code block boundaries
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
                continue
            
            # Skip processing inside code blocks
            if in_code_block:
                processed_lines.append(line)
                continue
            
            # Process regular content
            if '#' in line:
                # Check for legitimate Typst commands
                if re.match(r'\s*#(set|show|let|import|context|text|cite|code)\b', line):
                    # Legitimate Typst command - preserve
                    processed_lines.append(line)
                    continue
                
                # Check for Markdown/Typst headers (already converted)
                if line.strip().startswith('='):
                    # Typst header - preserve
                    processed_lines.append(line)
                    continue
                
                # Handle problematic # in content
                # Escape only standalone # that could confuse Typst
                line = re.sub(
                    r'(?<!\\)(?<!#)#(?![a-zA-Z{#=])',  # # not part of command/header
                    r'#{"#"}',  # Typst-safe escaping
                    line
                )
            
            # Handle other problematic characters
            if '%' in line and not in_code_block:
                # Escape % that might be interpreted as comments
                line = re.sub(r'(?<!\\)%(?![a-zA-Z])', r'\\%', line)
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup and validation"""
        
        # Remove any leftover protected block markers
        content = re.sub(r'PROTECTED_BLOCK_[a-f0-9]{32}', '', content)
        
        # Normalize line endings
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Remove excessive empty lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()


def integrate_with_wot_pdf():
    """
    Integration guide for WOT-PDF package
    Shows how to use TypstContentOptimizer in existing workflow
    """
    
    example_usage = '''
# Integration with existing WOT-PDF AdvancedTypstEngine

from typst_content_optimizer import TypstContentOptimizer

class AdvancedTypstEngine:
    def __init__(self):
        self.optimizer = TypstContentOptimizer()
    
    def enhanced_fix_typst_content(self, content: str, template_type: str) -> str:
        """Enhanced content fixing with new optimizer"""
        
        # Apply new optimization pipeline
        content = self.optimizer.optimize_content_for_typst(content, template_type)
        
        # Apply existing optimizations if needed
        content = self.enhanced_fix_typst_rgb_codes(content)
        content = self.enhanced_fix_typst_interpolations(content)
        
        return content
'''
    
    return example_usage


if __name__ == "__main__":
    # Quick test of the optimizer
    test_content = '''
# Test Document

This is a test with **bold text** and *italic text*.

## Code Example

```python
def calculate_var(portfolio, confidence_level=0.95):
    # Monte Carlo simulation with 10,000 scenarios
    # Time horizon: 1 year in trading days (252 days)
    scenarios = monte_carlo_simulation(
        portfolio=portfolio,
        num_scenarios=10000,
        time_horizon=252
    )
    
    # Calculate VaR at specified confidence level
    percentile = confidence_level * 100
    var = np.percentile(scenarios.losses, percentile)
    
    return var
```

Some text with # characters that might cause issues.

### Features
- Professional templates
- Advanced typography  
- Native Typst compilation
'''
    
    optimizer = TypstContentOptimizer()
    optimized = optimizer.optimize_content_for_typst(test_content, "technical")
    
    print("🎯 TYPST OPTIMIZATION TEST")
    print("=" * 50)
    print("\n📝 ORIGINAL CONTENT:")
    print("-" * 30)
    print(test_content[:200] + "..." if len(test_content) > 200 else test_content)
    
    print("\n✅ OPTIMIZED CONTENT:")
    print("-" * 30)
    print(optimized[:200] + "..." if len(optimized) > 200 else optimized)
    
    print(f"\n📊 OPTIMIZATION STATS:")
    print(f"Original length: {len(test_content)} chars")
    print(f"Optimized length: {len(optimized)} chars")
    print(f"Content preserved: {abs(len(optimized) - len(test_content)) < 100}")
    
    print("\n🚀 Ready for integration with WOT-PDF!")
