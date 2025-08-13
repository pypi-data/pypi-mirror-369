"""
Test file for email_cleaner UDF
Generated from spec hash: e52aaa1b
Generated on: 2025-07-19T16:54:44.537954
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
import sys
from pathlib import Path

# Add the current directory to path so we can import the UDF
sys.path.insert(0, str(Path(__file__).parent))

try:
    from email_cleaner_udf import email_cleaner_udf
except ImportError as e:
    pytest.skip(f"Could not import {e}", allow_module_level=True)


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .appName("test_email_cleaner") \
        .master("local[2]") \
        .getOrCreate()


class TestEmailCleanerUDF:
    """Test cases for email_cleaner_udf."""
    
    def test_basic_functionality(self, spark):
        """Test basic UDF functionality."""
        # Create test data
        test_data = [
            ("test_input_1",),
            ("test_input_2",),
            ("",),
            (None,),
        ]
        
        df = spark.createDataFrame(test_data, ["input"])
        
        # Apply UDF
        result_df = df.withColumn("cleaned", email_cleaner_udf(df.input))
        
        # Collect results
        results = result_df.collect()
        
        # Basic assertions
        assert len(results) == len(test_data)
        assert results[0]["cleaned"] is not None  # Modify based on expected behavior
    
    def test_empty_input(self, spark):
        """Test UDF with empty input."""
        test_data = [("",), (None,)]
        df = spark.createDataFrame(test_data, ["input"])
        
        result_df = df.withColumn("cleaned", email_cleaner_udf(df.input))
        results = result_df.collect()
        
        # Add your specific assertions here
        assert len(results) == 2
    
    def test_edge_cases(self, spark):
        """Test UDF with edge cases."""
        # Add specific test cases based on your spec
        test_data = [
            ("very_long_input_" * 100,),
            ("special!@#$%chars",),
            ("unicode_测试",),
        ]
        
        df = spark.createDataFrame(test_data, ["input"])
        result_df = df.withColumn("cleaned", email_cleaner_udf(df.input))
        
        # Should not raise exceptions
        results = result_df.collect()
        assert len(results) == len(test_data)


if __name__ == "__main__":
    # Simple test runner
    spark = SparkSession.builder \
        .appName("test_email_cleaner") \
        .master("local[2]") \
        .getOrCreate()
    
    test_instance = TestEmailCleanerUDF()
    
    print("Running basic functionality test...")
    test_instance.test_basic_functionality(spark)
    
    print("Running empty input test...")
    test_instance.test_empty_input(spark)
    
    print("Running edge cases test...")
    test_instance.test_edge_cases(spark)
    
    print("All tests passed!")
    spark.stop()
