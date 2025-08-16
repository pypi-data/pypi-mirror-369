#!/usr/bin/env python3
"""
🎯 INTELLIGENT ENGINE ROUTER - DEFINITIVE SOLUTION
==================================================
⚡ Smart content analysis and engine selection
🔷 Automatic routing to optimal PDF generation engine
📊 Typst for clean content, ReportLab for complex content

BREAKTHROUGH APPROACH:
- Stop fighting Typst's limitations
- Use each engine for what it does best
- Automatic decision making based on content complexity
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class EngineType(Enum):
    TYPST = "typst"
    REPORTLAB = "reportlab"
    AUTO = "auto"

@dataclass
class ContentAnalysis:
    """Results of content complexity analysis"""
    complexity_score: int
    code_block_count: int
    programming_languages: List[str]
    special_char_density: float
    has_math_formulas: bool
    has_tables: bool
    recommended_engine: EngineType
    confidence: float
    analysis_details: Dict[str, any]

class IntelligentEngineRouter:
    """
    Analyzes content complexity and routes to optimal engine
    """
    
    def __init__(self):
        self.complexity_weights = {
            'code_blocks': 25,          # Heavy penalty for code blocks
            'programming_languages': 15, # Penalty per unique language
            'special_chars': 20,        # Penalty for special characters
            'python_comments': 30,      # Heavy penalty for Python # comments
            'regex_patterns': 25,       # Heavy penalty for regex patterns
            'math_operators': 10,       # Penalty for math operators
            'markdown_complexity': 5,   # Light penalty for complex markdown
        }
        
        # Thresholds for engine selection (documentation-friendly)
        self.typst_threshold = 300      # Increased for documentation
        self.reportlab_threshold = 800  # Much higher threshold for ReportLab
        # Between thresholds = Content-dependent decision
        
        # Special handling for documentation
        self.documentation_indicators = [
            'installation', 'guide', 'tutorial', 'documentation', 'readme',
            'getting started', 'quick start', 'overview', 'introduction'
        ]
    
    def analyze_content(self, content: str) -> ContentAnalysis:
        """
        Comprehensive content analysis for engine selection
        """
        
        # Initialize analysis
        analysis_details = {}
        complexity_score = 0
        
        # 1. Code Block Analysis
        code_analysis = self._analyze_code_blocks(content)
        complexity_score += code_analysis['score']
        analysis_details['code_blocks'] = code_analysis
        
        # 2. Programming Language Analysis
        lang_analysis = self._analyze_languages(content)
        complexity_score += lang_analysis['score']
        analysis_details['languages'] = lang_analysis
        
        # 3. Special Character Analysis  
        char_analysis = self._analyze_special_characters(content)
        complexity_score += char_analysis['score']
        analysis_details['special_chars'] = char_analysis
        
        # 4. Python Comment Analysis (Critical for Typst)
        comment_analysis = self._analyze_python_comments(content)
        complexity_score += comment_analysis['score']
        analysis_details['python_comments'] = comment_analysis
        
        # 5. Regex Pattern Analysis
        regex_analysis = self._analyze_regex_patterns(content)
        complexity_score += regex_analysis['score']
        analysis_details['regex_patterns'] = regex_analysis
        
        # 6. Math Formula Analysis
        math_analysis = self._analyze_math_content(content)
        complexity_score += math_analysis['score']
        analysis_details['math_content'] = math_analysis
        
        # 7. Table Analysis
        table_analysis = self._analyze_tables(content)
        complexity_score += table_analysis['score']
        analysis_details['tables'] = table_analysis
        
        # 8. Overall Markdown Complexity
        markdown_analysis = self._analyze_markdown_complexity(content)
        complexity_score += markdown_analysis['score']
        analysis_details['markdown_complexity'] = markdown_analysis
        
        # Engine Recommendation with content context
        recommended_engine, confidence = self._recommend_engine(complexity_score, analysis_details, content)
        
        return ContentAnalysis(
            complexity_score=complexity_score,
            code_block_count=code_analysis['count'],
            programming_languages=lang_analysis['languages'],
            special_char_density=char_analysis['density'],
            has_math_formulas=math_analysis['has_formulas'],
            has_tables=table_analysis['has_tables'],
            recommended_engine=recommended_engine,
            confidence=confidence,
            analysis_details=analysis_details
        )
    
    def recommend_engine(self, content: str) -> Dict[str, Any]:
        """Compatibility method that returns engine recommendation as dict"""
        analysis = self.analyze_content(content)
        
        return {
            'engine': analysis.recommended_engine.value,
            'confidence': analysis.confidence,
            'complexity_score': analysis.complexity_score,
            'analysis_details': analysis.analysis_details
        }
    
    def _analyze_code_blocks(self, content: str) -> Dict:
        """Analyze code blocks and their complexity"""
        
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        
        analysis = {
            'count': len(code_blocks),
            'languages': [],
            'total_lines': 0,
            'score': 0
        }
        
        for lang, code in code_blocks:
            if lang:
                analysis['languages'].append(lang.lower())
            
            lines = len(code.split('\n'))
            analysis['total_lines'] += lines
            
            # Score based on content complexity
            if '#' in code and lang.lower() == 'python':
                analysis['score'] += self.complexity_weights['code_blocks'] * 1.5  # Extra penalty
            else:
                analysis['score'] += self.complexity_weights['code_blocks']
        
        return analysis
    
    def _analyze_languages(self, content: str) -> Dict:
        """Analyze programming languages used"""
        
        languages = set()
        code_blocks = re.findall(r'```(\w+)', content)
        
        for lang in code_blocks:
            if lang:
                languages.add(lang.lower())
        
        # Higher penalty for more languages (complexity indicator)
        score = len(languages) * self.complexity_weights['programming_languages']
        
        return {
            'languages': list(languages),
            'count': len(languages),
            'score': score
        }
    
    def _analyze_special_characters(self, content: str) -> Dict:
        """Analyze density of characters that confuse Typst"""
        
        # Characters that commonly cause Typst issues
        special_chars = ['#', '%', '$', '{', '}', '\\', '`', '*']
        
        total_chars = len(content)
        special_count = sum(content.count(char) for char in special_chars)
        density = special_count / total_chars if total_chars > 0 else 0
        
        # Score based on density
        score = int(density * 1000 * self.complexity_weights['special_chars'] / 20)
        
        return {
            'density': density,
            'special_count': special_count,
            'score': score
        }
    
    def _analyze_python_comments(self, content: str) -> Dict:
        """Analyze Python comments that break Typst"""
        
        python_comment_patterns = [
            r'```python.*?# [A-Z].*?```',  # Python blocks with comments
            r'def \w+\(.*?\):.*?# .*?\n',   # Function definitions with comments
            r'\s+# [A-Z].*?\n',             # Indented comments
        ]
        
        comment_count = 0
        for pattern in python_comment_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            comment_count += len(matches)
        
        # High penalty for Python comments (Typst killer)
        score = comment_count * self.complexity_weights['python_comments']
        
        return {
            'comment_count': comment_count,
            'score': score,
            'high_risk': comment_count > 3  # More than 3 = very risky for Typst
        }
    
    def _analyze_regex_patterns(self, content: str) -> Dict:
        """Analyze regex patterns that confuse Typst"""
        
        regex_patterns = [
            r'r["\'].*?```.*?["\']',      # Raw strings with backticks
            r'["\'].*?\\n.*?["\']',       # Strings with newlines
            r'pattern\s*=.*?["\'].*?["\']', # Pattern assignments
        ]
        
        pattern_count = 0
        for pattern in regex_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            pattern_count += len(matches)
        
        score = pattern_count * self.complexity_weights['regex_patterns']
        
        return {
            'pattern_count': pattern_count,
            'score': score
        }
    
    def _analyze_math_content(self, content: str) -> Dict:
        """Analyze mathematical content"""
        
        math_indicators = [
            r'\$.*?\$',           # Inline math
            r'\$\$.*?\$\$',       # Block math
            r'\\[a-z]+\{',       # LaTeX commands
            r'\*\s*\d+',         # Math operations
        ]
        
        math_count = 0
        for pattern in math_indicators:
            matches = re.findall(pattern, content, re.DOTALL)
            math_count += len(matches)
        
        # Math operations in code can confuse Typst
        math_in_code = len(re.findall(r'```.*?\*.*?```', content, re.DOTALL))
        
        score = math_count * self.complexity_weights['math_operators']
        if math_in_code > 0:
            score += math_in_code * 15  # Extra penalty for math in code
        
        return {
            'math_count': math_count,
            'math_in_code': math_in_code,
            'has_formulas': math_count > 0,
            'score': score
        }
    
    def _analyze_tables(self, content: str) -> Dict:
        """Analyze table complexity"""
        
        table_patterns = [
            r'\|.*?\|.*?\n',      # Markdown tables
            r'<table>.*?</table>', # HTML tables
        ]
        
        table_count = 0
        for pattern in table_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            table_count += len(matches)
        
        return {
            'table_count': table_count,
            'has_tables': table_count > 0,
            'score': table_count * 5  # Light penalty - tables usually work fine
        }
    
    def _analyze_markdown_complexity(self, content: str) -> Dict:
        """Analyze overall Markdown complexity"""
        
        complexity_indicators = [
            (r'!\[.*?\]\(.*?\)', 'images'),
            (r'\[.*?\]\(.*?\)', 'links'),
            (r'^#{1,6}\s', 'headers'),
            (r'^\s*[-*+]\s', 'lists'),
            (r'>\s', 'quotes'),
        ]
        
        total_complexity = 0
        details = {}
        
        for pattern, name in complexity_indicators:
            count = len(re.findall(pattern, content, re.MULTILINE))
            details[name] = count
            total_complexity += count
        
        score = min(total_complexity * self.complexity_weights['markdown_complexity'], 50)  # Cap at 50
        
        return {
            'total_elements': total_complexity,
            'details': details,
            'score': score
        }
    
    def _recommend_engine(self, complexity_score: int, analysis_details: Dict, content: str = "") -> Tuple[EngineType, float]:
        """Recommend optimal engine based on analysis"""
        
        # Check for documentation patterns first
        content_lower = content.lower()
        is_documentation = any(indicator in content_lower for indicator in self.documentation_indicators)
        
        # Critical decision factors
        python_comments = analysis_details.get('python_comments', {})
        code_blocks = analysis_details.get('code_blocks', {})
        regex_patterns = analysis_details.get('regex_patterns', {})
        
        # Documentation bias - prefer Typst for better typography
        if is_documentation:
            # More lenient thresholds for documentation
            doc_reportlab_threshold = 2000  # Much higher threshold for documentation
            
            if complexity_score >= doc_reportlab_threshold:
                return EngineType.REPORTLAB, 0.80
            else:
                # Prefer Typst for documentation typography
                return EngineType.TYPST, 0.80
        
        # Immediate ReportLab triggers (Typst killers)
        if python_comments.get('high_risk', False):
            return EngineType.REPORTLAB, 0.95
        
        if code_blocks.get('count', 0) > 8:  # Increased from 5 to 8
            return EngineType.REPORTLAB, 0.90
        
        if regex_patterns.get('pattern_count', 0) > 3:  # Increased from 2 to 3
            return EngineType.REPORTLAB, 0.85
        
        # Score-based decision
        if complexity_score <= self.typst_threshold:
            confidence = 0.8 + (self.typst_threshold - complexity_score) / self.typst_threshold * 0.2
            return EngineType.TYPST, min(confidence, 0.95)
        
        elif complexity_score >= self.reportlab_threshold:
            confidence = 0.8 + min((complexity_score - self.reportlab_threshold) / 200 * 0.2, 0.2)
            return EngineType.REPORTLAB, min(confidence, 0.95)
        
        else:
            # Middle ground - prefer Typst for quality (changed from ReportLab)
            return EngineType.TYPST, 0.65
    
    def get_recommendation_summary(self, analysis: ContentAnalysis) -> str:
        """Generate human-readable recommendation summary"""
        
        summary = f"""
🎯 ENGINE RECOMMENDATION: {analysis.recommended_engine.value.upper()}
📊 Confidence: {analysis.confidence:.1%}
🔢 Complexity Score: {analysis.complexity_score}/100

📋 ANALYSIS SUMMARY:
• Code Blocks: {analysis.code_block_count}
• Languages: {', '.join(analysis.programming_languages) if analysis.programming_languages else 'None'}
• Special Char Density: {analysis.special_char_density:.2%}
• Math Content: {'Yes' if analysis.has_math_formulas else 'No'}
• Tables: {'Yes' if analysis.has_tables else 'No'}

🎯 RECOMMENDATION REASON:
"""
        
        if analysis.recommended_engine == EngineType.TYPST:
            summary += "✅ Content is clean and suitable for Typst's superior typography"
        else:
            summary += "⚠️  Content complexity suggests ReportLab for reliability"
            
            # Add specific reasons
            details = analysis.analysis_details
            reasons = []
            
            if details.get('python_comments', {}).get('high_risk'):
                reasons.append("• High risk Python comments detected")
            
            if details.get('code_blocks', {}).get('count', 0) > 5:
                reasons.append("• Many code blocks present")
                
            if details.get('regex_patterns', {}).get('pattern_count', 0) > 0:
                reasons.append("• Regex patterns that confuse Typst")
            
            if reasons:
                summary += "\n\nSPECIFIC ISSUES:\n" + "\n".join(reasons)
        
        return summary


def demonstrate_intelligent_routing():
    """Demonstrate the intelligent engine router"""
    
    # Test with our problematic book content
    test_content = '''
# WOT-PDF Documentation

This is a comprehensive guide with various content types.

## Simple Content
Regular markdown with **bold** and *italic* text.

## Code Examples

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

## Regex Patterns

```python
mermaid_pattern = r'```mermaid\\n(.*?)\\n```'
```

Some content with # characters and * operations.
'''
    
    router = IntelligentEngineRouter()
    analysis = router.analyze_content(test_content)
    summary = router.get_recommendation_summary(analysis)
    
    print("🎯 INTELLIGENT ENGINE ROUTER DEMONSTRATION")
    print("=" * 60)
    print(summary)
    
    return analysis


if __name__ == "__main__":
    demonstrate_intelligent_routing()
