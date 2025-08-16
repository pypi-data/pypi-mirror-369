import re
from typing import List, Dict, Any, Optional
import pandas as pd


class QueryProcessor:
    """Process and categorize natural language queries for intelligent handling."""
    
    def __init__(self):
        """Initialize the query processor."""
        self.query_patterns = {
            'visualization': [
                r'\b(plot|chart|graph|visualize|show|display|create)\b',
                r'\b(bar|line|scatter|histogram|box|heatmap|pie)\s+(chart|plot|graph)\b',
                r'\b(visualization|chart|plot)\b'
            ],
            'aggregation': [
                r'\b(count|sum|average|mean|median|min|max|total)\b',
                r'\b(group\s+by|aggregate|pivot|summary)\b',
                r'\b(how\s+many|what\s+is\s+the|find\s+the)\b'
            ],
            'filtering': [
                r'\b(filter|where|select|find|show\s+only|exclude)\b',
                r'\b(greater\s+than|less\s+than|equal\s+to|between)\b',
                r'\b(top|bottom|highest|lowest|best|worst)\b'
            ],
            'sorting': [
                r'\b(sort|order|arrange|rank|ascending|descending)\b',
                r'\b(alphabetical|numerical|chronological)\b'
            ],
            'data_quality': [
                r'\b(null|missing|duplicate|unique|clean|validate)\b',
                r'\b(data\s+quality|integrity|consistency)\b'
            ],
            'statistics': [
                r'\b(correlation|variance|standard\s+deviation|distribution)\b',
                r'\b(statistical|analysis|insights|patterns)\b'
            ]
        }
        
        self.query_suggestions = {
            'visualization': [
                "Try asking for specific chart types like 'bar chart', 'line chart', or 'scatter plot'",
                "Specify what you want to visualize, e.g., 'Show revenue by country as a bar chart'"
            ],
            'aggregation': [
                "Be specific about what you want to count or sum",
                "Try 'Group by category and show the total sales'"
            ],
            'filtering': [
                "Specify the conditions clearly, e.g., 'Show only rows where revenue > 1000'",
                "Use 'top 10' or 'highest 5' for ranking queries"
            ]
        }

    def categorize_query(self, query: str) -> Dict[str, Any]:
        """Categorize a query and provide suggestions."""
        query_lower = query.lower()
        categories = {}
        
        for category, patterns in self.query_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                categories[category] = {
                    'confidence': len(matches) / len(patterns),
                    'patterns_matched': matches,
                    'suggestions': self.query_suggestions.get(category, [])
                }
        
        return {
            'query': query,
            'categories': categories,
            'primary_category': max(categories.keys(), key=lambda k: categories[k]['confidence']) if categories else None,
            'total_categories': len(categories)
        }

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities like column names, values, and conditions from the query."""
        entities = {
            'columns': [],
            'values': [],
            'conditions': [],
            'numbers': [],
            'dates': []
        }
        
        # Extract potential column names (words that might be column names)
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', query)
        entities['columns'] = [word for word in words if len(word) > 2]
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query)
        entities['numbers'] = [float(num) if '.' in num else int(num) for num in numbers]
        
        # Extract date patterns
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{2}/\d{2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b'  # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, query, re.IGNORECASE)
            entities['dates'].extend(dates)
        
        # Extract conditions
        condition_patterns = [
            r'\b(greater\s+than|less\s+than|equal\s+to|between)\b',
            r'\b(top|bottom|highest|lowest)\b',
            r'\b(where|filter|select)\b'
        ]
        
        for pattern in condition_patterns:
            conditions = re.findall(pattern, query, re.IGNORECASE)
            entities['conditions'].extend(conditions)
        
        return entities

    def suggest_improvements(self, query: str) -> List[str]:
        """Suggest improvements for the query."""
        suggestions = []
        query_lower = query.lower()
        
        # Check for vague terms
        vague_terms = {
            'show': 'Be more specific about what you want to see',
            'analyze': 'Specify what kind of analysis you want',
            'data': 'Mention specific columns or metrics',
            'information': 'Ask for specific information'
        }
        
        for term, suggestion in vague_terms.items():
            if term in query_lower:
                suggestions.append(suggestion)
        
        # Check for missing context
        if 'chart' in query_lower and not any(word in query_lower for word in ['bar', 'line', 'scatter', 'histogram']):
            suggestions.append("Specify the chart type (bar, line, scatter, etc.)")
        
        if 'top' in query_lower and not any(word in query_lower for word in ['5', '10', '20', 'number']):
            suggestions.append("Specify how many top results you want (e.g., 'top 10')")
        
        return suggestions

    def validate_query(self, query: str, available_columns: List[str]) -> Dict[str, Any]:
        """Validate if the query can be executed with available columns."""
        entities = self.extract_entities(query)
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'missing_columns': [],
            'suggestions': []
        }
        
        # Check if mentioned columns exist
        for col in entities['columns']:
            if col not in available_columns:
                validation['missing_columns'].append(col)
                validation['warnings'].append(f"Column '{col}' not found in the dataset")
        
        if validation['missing_columns']:
            validation['is_valid'] = False
            validation['suggestions'].append("Check the available columns and use correct column names")
        
        # Check for empty query
        if not query.strip():
            validation['is_valid'] = False
            validation['errors'].append("Query cannot be empty")
        
        # Check for very long queries
        if len(query) > 500:
            validation['warnings'].append("Query is very long. Consider breaking it into smaller parts")
        
        return validation

    def get_query_examples(self, category: Optional[str] = None) -> List[str]:
        """Get example queries for different categories."""
        examples = {
            'visualization': [
                "Create a bar chart showing total revenue by country",
                "Plot a line chart of sales over time",
                "Show a scatter plot of price vs. quantity",
                "Generate a histogram of customer ages"
            ],
            'aggregation': [
                "What is the total revenue by product category?",
                "Count the number of customers by region",
                "Show the average price for each brand",
                "What is the sum of sales for each month?"
            ],
            'filtering': [
                "Show only products with price > $100",
                "Filter to customers from New York",
                "Display top 10 products by revenue",
                "Show orders placed in 2023"
            ],
            'sorting': [
                "Sort products by price in descending order",
                "Arrange customers by total purchases",
                "Order sales by date chronologically"
            ]
        }
        
        if category and category in examples:
            return examples[category]
        elif category:
            return [f"No examples available for category: {category}"]
        else:
            all_examples = []
            for cat_examples in examples.values():
                all_examples.extend(cat_examples)
            return all_examples
