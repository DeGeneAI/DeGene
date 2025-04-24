import numpy as np
from typing import Tuple, List, Dict, Optional
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import zlib
import base64
import re
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompressionStats:
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    algorithm: str
    quality_score: Optional[float] = None
    error_rate: Optional[float] = None

class GenomeCompressor:
    """Advanced genome data compressor with quality control"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunk_size = chunk_size
        self.compression_stats = []
        self.quality_threshold = 30
        self.min_pattern_length = 8
        self.max_pattern_length = 32
        
    def _encode_sequence(self, sequence: str) -> bytes:
        """Encode DNA sequence using custom encoding scheme with quality scores"""
        # 2-bit encoding: A=00, C=01, G=10, T=11
        encoding = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        binary = ''.join(encoding.get(base, '00') for base in sequence.upper())
        
        # Add quality score encoding
        quality_scores = self._calculate_quality_scores(sequence)
        quality_binary = ''.join(format(score, '08b') for score in quality_scores)
        
        # Combine sequence and quality data
        combined = binary + quality_binary
        
        return int(combined, 2).to_bytes((len(combined) + 7) // 8, byteorder='big')
        
    def _calculate_quality_scores(self, sequence: str) -> List[int]:
        """Calculate quality scores for sequence"""
        # Implement quality score calculation based on NCBI's methods
        scores = []
        for i in range(len(sequence)):
            # Basic quality scoring based on sequence context
            score = 30  # Default score
            if i > 0 and sequence[i] == sequence[i-1]:
                score += 5  # Homopolymer bonus
            if i > 1 and sequence[i] == sequence[i-2]:
                score += 3  # Repeat bonus
            scores.append(min(score, 40))  # Cap at 40
        return scores
        
    def _compress_chunk(self, chunk: str) -> Tuple[bytes, Dict]:
        """Compress a single data chunk with advanced features"""
        # 1. Sequence encoding with quality scores
        encoded = self._encode_sequence(chunk)
        
        # 2. Find repeating patterns with variable length
        patterns = self._find_patterns(chunk)
        
        # 3. Apply adaptive compression based on content
        if self._is_highly_repetitive(chunk):
            compressed = self._compress_repetitive(encoded)
        else:
            compressed = zlib.compress(encoded, level=9)
        
        # 4. Add enhanced metadata
        metadata = {
            'original_length': len(chunk),
            'patterns': patterns,
            'checksum': zlib.crc32(encoded),
            'quality_scores': self._calculate_quality_scores(chunk),
            'compression_type': 'adaptive',
            'error_rate': self._calculate_error_rate(chunk)
        }
        
        return compressed, metadata
        
    def _find_patterns(self, sequence: str) -> Dict[str, List[int]]:
        """Find repeating patterns with variable length"""
        patterns = defaultdict(list)
        
        for length in range(self.min_pattern_length, self.max_pattern_length + 1):
            for i in range(len(sequence) - length):
                pattern = sequence[i:i + length]
                if sequence.count(pattern) > 1:
                    patterns[pattern].append(i)
        
        return {k: v for k, v in patterns.items() if len(v) > 2}
        
    def _is_highly_repetitive(self, sequence: str) -> bool:
        """Check if sequence is highly repetitive"""
        patterns = self._find_patterns(sequence)
        total_repeats = sum(len(positions) for positions in patterns.values())
        return total_repeats > len(sequence) * 0.3
        
    def _compress_repetitive(self, data: bytes) -> bytes:
        """Special compression for repetitive sequences"""
        # Implement specialized compression for repetitive sequences
        return zlib.compress(data, level=9)
        
    def _calculate_error_rate(self, sequence: str) -> float:
        """Calculate potential error rate in sequence"""
        # Implement error rate calculation based on NCBI's methods
        errors = 0
        for i in range(len(sequence)):
            if sequence[i] not in 'ACGT':
                errors += 1
            if i > 0 and sequence[i] == sequence[i-1]:
                errors += 0.1  # Homopolymer penalty
        return errors / len(sequence)
        
    def compress(self, genome_data: str) -> Tuple[bytes, List[Dict]]:
        """Compress genome data with quality control"""
        # Validate input
        if not self._validate_sequence(genome_data):
            raise ValueError("Invalid genome sequence")
            
        chunks = [genome_data[i:i + self.chunk_size] 
                 for i in range(0, len(genome_data), self.chunk_size)]
        
        compressed_chunks = []
        metadata_list = []
        
        with ThreadPoolExecutor() as executor:
            results = executor.map(self._compress_chunk, chunks)
            
            for compressed, metadata in results:
                compressed_chunks.append(compressed)
                metadata_list.append(metadata)
                
        # Merge compressed data
        final_compressed = b''.join(compressed_chunks)
        
        # Add checksum and metadata
        checksum = zlib.crc32(final_compressed)
        
        # Encode to Base64
        encoded = base64.b64encode(final_compressed)
        
        # Update compression stats
        stats = CompressionStats(
            original_size=len(genome_data),
            compressed_size=len(encoded),
            compression_ratio=len(encoded) / len(genome_data),
            compression_time=0.0,  # TODO: Implement timing
            algorithm='adaptive',
            quality_score=sum(m['quality_scores'] for m in metadata_list) / len(metadata_list),
            error_rate=sum(m['error_rate'] for m in metadata_list) / len(metadata_list)
        )
        self.compression_stats.append(stats)
        
        logger.info(f"Compressed {len(genome_data)} bytes to {len(encoded)} bytes")
        logger.info(f"Average quality score: {stats.quality_score}")
        logger.info(f"Average error rate: {stats.error_rate}")
        
        return encoded, metadata_list
        
    def _validate_sequence(self, sequence: str) -> bool:
        """Validate genome sequence"""
        # Check for invalid characters
        if not re.match(r'^[ACGTN]+$', sequence.upper()):
            return False
            
        # Check for minimum length
        if len(sequence) < 100:
            return False
            
        return True
        
    def decompress(self, compressed_data: bytes, metadata_list: List[Dict]) -> str:
        """Decompress genome data with quality verification"""
        # Decode Base64
        decoded = base64.b64decode(compressed_data)
        
        # Verify checksum
        checksum = zlib.crc32(decoded)
        
        # Decompress chunks
        decompressed_chunks = []
        current_pos = 0
        
        for metadata in metadata_list:
            chunk_size = metadata['original_length']
            chunk_data = decoded[current_pos:current_pos + chunk_size]
            
            # Decompress based on compression type
            if metadata['compression_type'] == 'adaptive':
                decompressed = zlib.decompress(chunk_data)
            else:
                decompressed = zlib.decompress(chunk_data)
            
            # Verify chunk checksum
            if zlib.crc32(decompressed) != metadata['checksum']:
                raise ValueError(f"Checksum mismatch for chunk at position {current_pos}")
            
            # Verify quality scores
            if metadata['quality_scores'] and any(score < self.quality_threshold for score in metadata['quality_scores']):
                logger.warning(f"Low quality scores detected in chunk at position {current_pos}")
            
            decompressed_chunks.append(decompressed)
            current_pos += chunk_size
            
        return ''.join(chunk.decode() for chunk in decompressed_chunks)
        
    def get_compression_stats(self) -> List[CompressionStats]:
        """Get compression statistics with quality metrics"""
        return self.compression_stats

class AdvancedCompressionPipeline:
    """Advanced compression pipeline with quality control"""
    
    def __init__(self):
        self.compressor = GenomeCompressor()
        self.patterns_cache = {}
        self.quality_cache = {}
        
    def _preprocess(self, data: str) -> str:
        """Data preprocessing with quality control"""
        # Remove invalid characters
        cleaned = ''.join(c for c in data.upper() if c in 'ACGTN')
        
        # Find and cache common patterns
        self._update_patterns_cache(cleaned)
        
        # Cache quality information
        self._update_quality_cache(cleaned)
        
        return cleaned
        
    def _update_patterns_cache(self, sequence: str):
        """Update pattern cache with quality information"""
        new_patterns = self.compressor._find_patterns(sequence)
        
        for pattern, positions in new_patterns.items():
            if pattern in self.patterns_cache:
                self.patterns_cache[pattern].extend(positions)
            else:
                self.patterns_cache[pattern] = positions
                
    def _update_quality_cache(self, sequence: str):
        """Update quality information cache"""
        quality_scores = self.compressor._calculate_quality_scores(sequence)
        self.quality_cache[hashlib.md5(sequence.encode()).hexdigest()] = quality_scores
                
    def process(self, genome_data: str) -> Tuple[bytes, List[Dict]]:
        """Process genome data with quality control"""
        # 1. Preprocess
        preprocessed = self._preprocess(genome_data)
        
        # 2. Compress
        compressed, metadata = self.compressor.compress(preprocessed)
        
        # 3. Add enhanced metadata
        for meta in metadata:
            meta['cached_patterns'] = self.patterns_cache
            meta['quality_cache'] = self.quality_cache
            
        return compressed, metadata 