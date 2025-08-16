import pytest
import pandas as pd
import numpy as np
import askpandas as ap
from askpandas.core.dataframe import AskDataFrame
from askpandas.utils.helpers import validate_dataframe, get_dataframe_summary
from askpandas.visualization.charts import create_bar_chart, create_line_chart


class TestAskDataFrame:
    """Test cases for AskDataFrame class."""
    
    def setup_method(self):
        """Set up test data."""
        self.sample_data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        }
        self.df = AskDataFrame(self.sample_data)
    
    def test_dataframe_creation_from_dict(self):
        """Test DataFrame creation from dictionary."""
        assert isinstance(self.df.df, pd.DataFrame)
        assert self.df.df.shape == (3, 3)
        assert list(self.df.df.columns) == ['name', 'age', 'salary']
    
    def test_dataframe_creation_from_pandas(self):
        """Test DataFrame creation from pandas DataFrame."""
        pd_df = pd.DataFrame(self.sample_data)
        ap_df = AskDataFrame(pd_df)
        assert isinstance(ap_df.df, pd.DataFrame)
        assert ap_df.df.equals(pd_df)
    
    def test_dataframe_creation_from_list(self):
        """Test DataFrame creation from list of dictionaries."""
        list_data = [
            {'name': 'Alice', 'age': 25},
            {'name': 'Bob', 'age': 30}
        ]
        ap_df = AskDataFrame(list_data)
        assert isinstance(ap_df.df, pd.DataFrame)
        assert ap_df.df.shape == (2, 2)
    
    def test_info_method(self):
        """Test the info method."""
        info = self.df.info()
        assert isinstance(info, str)
        assert 'Shape: (3, 3)' in info
        assert 'Columns: [\'name\', \'age\', \'salary\']' in info
    
    def test_describe_method(self):
        """Test the describe method."""
        desc = self.df.describe()
        assert isinstance(desc, pd.DataFrame)
        assert 'age' in desc.columns
        assert 'salary' in desc.columns
    
    def test_head_method(self):
        """Test the head method."""
        head = self.df.head(2)
        assert isinstance(head, pd.DataFrame)
        assert head.shape == (2, 3)
    
    def test_tail_method(self):
        """Test the tail method."""
        tail = self.df.tail(2)
        assert isinstance(tail, pd.DataFrame)
        assert tail.shape == (2, 3)
    
    def test_shape_method(self):
        """Test the shape method."""
        shape = self.df.shape()
        assert shape == (3, 3)
    
    def test_columns_method(self):
        """Test the columns method."""
        columns = self.df.columns()
        assert columns == ['name', 'age', 'salary']
    
    def test_dtypes_method(self):
        """Test the dtypes method."""
        dtypes = self.df.dtypes()
        assert isinstance(dtypes, dict)
        assert 'name' in dtypes
        assert 'age' in dtypes
    
    def test_isnull_method(self):
        """Test the isnull method."""
        null_mask = self.df.isnull()
        assert isinstance(null_mask, pd.DataFrame)
        assert null_mask.shape == (3, 3)
    
    def test_dropna_method(self):
        """Test the dropna method."""
        # Add some null values
        df_with_nulls = AskDataFrame({
            'name': ['Alice', 'Bob', None],
            'age': [25, None, 35],
            'salary': [50000, 60000, 70000]
        })
        cleaned_df = df_with_nulls.dropna()
        assert isinstance(cleaned_df, AskDataFrame)
        assert cleaned_df.df.shape[0] <= df_with_nulls.df.shape[0]
    
    def test_sort_values_method(self):
        """Test the sort_values method."""
        sorted_df = self.df.sort_values('age', ascending=False)
        assert isinstance(sorted_df, AskDataFrame)
        assert sorted_df.df.iloc[0]['age'] == 35
    
    def test_groupby_method(self):
        """Test the groupby method."""
        # Add department column for grouping
        df_with_dept = AskDataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'department': ['HR', 'IT', 'HR'],
            'salary': [50000, 60000, 70000]
        })
        grouped = df_with_dept.groupby('department')
        assert hasattr(grouped, 'groups')
    
    def test_query_method(self):
        """Test the query method."""
        filtered_df = self.df.query('age > 25')
        assert isinstance(filtered_df, AskDataFrame)
        assert filtered_df.df.shape[0] == 2
    
    def test_select_dtypes_method(self):
        """Test the select_dtypes method."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        assert isinstance(numeric_df, AskDataFrame)
        assert 'age' in numeric_df.df.columns
        assert 'salary' in numeric_df.df.columns
        assert 'name' not in numeric_df.df.columns
    
    def test_clean_columns_method(self):
        """Test the clean_columns method."""
        df_with_special_chars = AskDataFrame({
            'First Name': ['Alice'],
            'Last Name': ['Smith'],
            'Age (Years)': [25]
        })
        cleaned_df = df_with_special_chars.clean_columns()
        assert 'first_name' in cleaned_df.df.columns
        assert 'last_name' in cleaned_df.df.columns
        assert 'age_years' in cleaned_df.df.columns
    
    def test_to_csv_method(self):
        """Test the to_csv method."""
        result = self.df.to_csv("test_output.csv")
        assert "DataFrame saved to test_output.csv" in result
        
        # Clean up
        import os
        if os.path.exists("test_output.csv"):
            os.remove("test_output.csv")
    
    def test_get_summary_stats_method(self):
        """Test the get_summary_stats method."""
        stats = self.df.get_summary_stats()
        assert isinstance(stats, dict)
        assert 'shape' in stats
        assert 'columns' in stats
        assert 'numeric_columns' in stats
        assert 'categorical_columns' in stats
    
    def test_get_column_info_method(self):
        """Test the get_column_info method."""
        col_info = self.df.get_column_info('age')
        assert isinstance(col_info, dict)
        assert col_info['name'] == 'age'
        assert col_info['dtype'] == 'int64'
        assert 'min' in col_info
        assert 'max' in col_info
    
    def test_indexing(self):
        """Test DataFrame indexing."""
        # Test single column selection
        name_col = self.df['name']
        assert isinstance(name_col, pd.Series)
        
        # Test multiple column selection
        subset = self.df[['name', 'age']]
        assert isinstance(subset, AskDataFrame)
        assert subset.df.shape == (3, 2)
    
    def test_length(self):
        """Test the length of DataFrame."""
        assert len(self.df) == 3
    
    def test_string_representation(self):
        """Test string representation methods."""
        repr_str = repr(self.df)
        str_str = str(self.df)
        assert "AskDataFrame" in repr_str
        assert "shape=(3, 3)" in repr_str
        assert repr_str == str_str


class TestHelpers:
    """Test cases for utility helper functions."""
    
    def test_validate_dataframe(self):
        """Test validate_dataframe function."""
        # Test with dictionary
        df = validate_dataframe({'a': [1, 2], 'b': [3, 4]})
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 2)
        
        # Test with pandas DataFrame
        pd_df = pd.DataFrame({'a': [1, 2]})
        df = validate_dataframe(pd_df)
        assert isinstance(df, pd.DataFrame)
        assert df.equals(pd_df)
    
    def test_get_dataframe_summary(self):
        """Test get_dataframe_summary function."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': ['x', 'y', 'z']
        })
        summary = get_dataframe_summary(df)
        assert isinstance(summary, dict)
        assert 'shape' in summary
        assert 'columns' in summary
        assert 'dtypes' in summary
        assert 'memory_usage' in summary


class TestVisualization:
    """Test cases for visualization functions."""
    
    def test_create_bar_chart(self):
        """Test create_bar_chart function."""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': [10, 20, 30]
        })
        fig = create_bar_chart(df, 'category', 'value')
        assert fig is not None
        plt.close(fig)
    
    def test_create_line_chart(self):
        """Test create_line_chart function."""
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [10, 20, 30]
        })
        fig = create_line_chart(df, 'x', 'y')
        assert fig is not None
        plt.close(fig)


class TestLLMIntegration:
    """Test cases for LLM integration."""
    
    @pytest.mark.skipif(
        not ap.OllamaLLM(model_name="mistral").is_available(),
        reason="Ollama is not running locally."
    )
    def test_llm_chat_basic(self):
        """Test basic LLM chat functionality."""
        llm = ap.OllamaLLM(model_name="mistral")
        ap.set_llm(llm)
        df = ap.DataFrame({"country": ["A", "B"], "revenue": [1, 2]})
        result = df.chat("Which country has the highest revenue?")
        assert isinstance(result, str)
        assert len(result.strip()) > 0
    
    @pytest.mark.skipif(
        not ap.OllamaLLM(model_name="mistral").is_available(),
        reason="Ollama is not running locally."
    )
    def test_multi_dataframe_chat(self):
        """Test chat with multiple dataframes."""
        llm = ap.OllamaLLM(model_name="mistral")
        ap.set_llm(llm)
        
        df1 = ap.DataFrame({"id": [1, 2], "name": ["A", "B"]})
        df2 = ap.DataFrame({"id": [1, 2], "value": [100, 200]})
        
        result = ap.chat("Show the names and values", df1, df2)
        assert isinstance(result, str)
        assert len(result.strip()) > 0


class TestConfiguration:
    """Test cases for configuration management."""
    
    def test_config_management(self):
        """Test configuration getter and setter."""
        # Get current config
        config = ap.get_config()
        assert isinstance(config, dict)
        assert 'model_name' in config
        
        # Set new config
        ap.set_config(verbose=True)
        new_config = ap.get_config()
        assert new_config['verbose'] is True


class TestQueryAnalysis:
    """Test cases for query analysis functionality."""
    
    def test_analyze_query(self):
        """Test query analysis."""
        analysis = ap.analyze_query("Show me a bar chart of sales")
        assert isinstance(analysis, dict)
        assert 'categories' in analysis
        assert 'primary_category' in analysis
    
    def test_validate_query(self):
        """Test query validation."""
        columns = ['name', 'age', 'salary']
        validation = ap.validate_query("Show top 5 by salary", columns)
        assert isinstance(validation, dict)
        assert 'is_valid' in validation
    
    def test_get_query_examples(self):
        """Test getting query examples."""
        examples = ap.get_query_examples('visualization')
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        all_examples = ap.get_query_examples()
        assert isinstance(all_examples, list)
        assert len(all_examples) > len(examples)


if __name__ == "__main__":
    pytest.main([__file__])
