import pytest
import numpy as np
from src.genomics.compression import GenomeCompressor, AdvancedCompressionPipeline

@pytest.fixture
def sample_genome_data():
    """Generate test genome data"""
    bases = ['A', 'C', 'G', 'T']
    return ''.join(np.random.choice(bases) for _ in range(1000))

@pytest.fixture
def compressor():
    """Create compressor instance"""
    return GenomeCompressor(chunk_size=100)

@pytest.fixture
def pipeline():
    """Create compression pipeline instance"""
    return AdvancedCompressionPipeline()

def test_encode_sequence(compressor, sample_genome_data):
    """Test sequence encoding"""
    encoded = compressor._encode_sequence(sample_genome_data)
    assert isinstance(encoded, bytes)
    assert len(encoded) <= len(sample_genome_data) / 4 + 1

def test_find_patterns(compressor):
    """Test pattern finding"""
    sequence = "ACGTACGTACGTACGT"
    patterns = compressor._find_patterns(sequence)
    assert isinstance(patterns, dict)
    assert "ACGT" in ''.join(patterns.keys())

def test_compress_decompress(compressor, sample_genome_data):
    """Test compression and decompression"""
    # Compression
    compressed, metadata = compressor.compress(sample_genome_data)
    assert isinstance(compressed, bytes)
    assert isinstance(metadata, list)
    
    # Decompression
    decompressed = compressor.decompress(compressed, metadata)
    assert isinstance(decompressed, str)
    assert len(decompressed) == len(sample_genome_data)

def test_compression_pipeline(pipeline, sample_genome_data):
    """Test compression pipeline"""
    # Process data
    compressed, metadata = pipeline.process(sample_genome_data)
    
    # Verify results
    assert isinstance(compressed, bytes)
    assert isinstance(metadata, list)
    assert 'cached_patterns' in metadata[0]

def test_invalid_input(compressor):
    """Test invalid input"""
    with pytest.raises(ValueError):
        compressor.compress("")
        
    with pytest.raises(ValueError):
        compressor.compress("123")  # Non-ACGT characters

def test_compression_stats(compressor, sample_genome_data):
    """Test compression statistics"""
    compressed, _ = compressor.compress(sample_genome_data)
    stats = compressor.get_compression_stats()
    
    assert isinstance(stats, list)
    if stats:
        assert stats[0].original_size > 0
        assert stats[0].compressed_size > 0
        assert 0 < stats[0].compression_ratio <= 1

def test_large_sequence(compressor):
    """Test large sequence compression"""
    large_sequence = 'ACGT' * 1000  # 4000 bp
    compressed, metadata = compressor.compress(large_sequence)
    
    assert len(compressed) < len(large_sequence)
    assert len(metadata) > 1  # Should be split into multiple chunks

def test_pattern_cache(pipeline):
    """Test pattern caching"""
    sequence1 = "ACGTACGT" * 10
    sequence2 = "ACGTACGT" * 5
    
    # Process first sequence
    pipeline.process(sequence1)
    cache_size_1 = len(pipeline.patterns_cache)
    
    # Process second sequence
    pipeline.process(sequence2)
    cache_size_2 = len(pipeline.patterns_cache)
    
    assert cache_size_2 >= cache_size_1
    assert "ACGTACGT" in ''.join(pipeline.patterns_cache.keys()) 
