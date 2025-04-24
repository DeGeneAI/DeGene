from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GenomeAnnotation:
    gene_id: str
    start: int
    end: int
    strand: str
    type: str
    description: Optional[str] = None
    quality_score: Optional[float] = None

@dataclass
class VariantCall:
    position: int
    reference: str
    alternate: str
    quality: float
    frequency: float
    type: str
    impact: Optional[str] = None

class GenomeAnalyzer:
    """Core genome analysis tools"""
    
    def __init__(self):
        self.variant_cache = {}
        self.annotation_cache = {}
        
    def find_genes(self, sequence: str) -> List[GenomeAnnotation]:
        """Find genes in genome sequence"""
        genes = []
        current_gene = None
        
        for i in range(len(sequence) - 2):
            codon = sequence[i:i+3]
            
            # Check for start codon
            if codon == 'ATG' and current_gene is None:
                current_gene = {
                    'start': i,
                    'strand': '+',
                    'type': 'protein_coding'
                }
                
            # Check for stop codon
            elif codon in ['TAA', 'TAG', 'TGA'] and current_gene is not None:
                current_gene['end'] = i + 3
                current_gene['gene_id'] = f"gene_{len(genes)}"
                
                # Calculate quality score
                quality = self._calculate_gene_quality(sequence[current_gene['start']:current_gene['end']])
                current_gene['quality_score'] = quality
                
                genes.append(GenomeAnnotation(**current_gene))
                current_gene = None
                
        return genes
        
    def _calculate_gene_quality(self, gene_sequence: str) -> float:
        """Calculate gene quality score"""
        score = 0.0
        
        # Check for proper start/stop
        if gene_sequence.startswith('ATG'):
            score += 0.3
            
        if gene_sequence.endswith(('TAA', 'TAG', 'TGA')):
            score += 0.3
            
        # Check for proper length (multiple of 3)
        if len(gene_sequence) % 3 == 0:
            score += 0.2
            
        # Check for GC content
        gc_content = (gene_sequence.count('G') + gene_sequence.count('C')) / len(gene_sequence)
        if 0.4 <= gc_content <= 0.6:
            score += 0.2
            
        return score
        
    def find_variants(self, reference: str, sample: str) -> List[VariantCall]:
        """Find variants between reference and sample sequences"""
        variants = []
        
        # Align sequences
        alignment = self._align_sequences(reference, sample)
        
        for pos, (ref_base, sample_base) in enumerate(alignment):
            if ref_base != sample_base and ref_base != '-' and sample_base != '-':
                # Calculate variant quality
                quality = self._calculate_variant_quality(pos, ref_base, sample_base, alignment)
                
                # Determine variant type
                variant_type = self._determine_variant_type(ref_base, sample_base)
                
                # Calculate frequency
                frequency = self._calculate_variant_frequency(sample_base, alignment)
                
                variant = VariantCall(
                    position=pos,
                    reference=ref_base,
                    alternate=sample_base,
                    quality=quality,
                    frequency=frequency,
                    type=variant_type,
                    impact=self._predict_variant_impact(pos, ref_base, sample_base)
                )
                
                variants.append(variant)
                
        return variants
        
    def _align_sequences(self, seq1: str, seq2: str) -> List[Tuple[str, str]]:
        """Align two sequences using basic algorithm"""
        alignment = []
        i = j = 0
        
        while i < len(seq1) or j < len(seq2):
            if i < len(seq1) and j < len(seq2):
                alignment.append((seq1[i], seq2[j]))
                i += 1
                j += 1
            elif i < len(seq1):
                alignment.append((seq1[i], '-'))
                i += 1
            else:
                alignment.append(('-', seq2[j]))
                j += 1
                
        return alignment
        
    def _calculate_variant_quality(self, pos: int, ref: str, alt: str, alignment: List[Tuple[str, str]]) -> float:
        """Calculate variant quality score"""
        score = 0.0
        
        # Check surrounding bases
        context = ''.join(b for b, _ in alignment[max(0, pos-2):pos+3])
        if len(context) == 5:
            score += 0.3
            
        # Check for homopolymer
        if ref == alt:
            score += 0.2
            
        # Check for transition/transversion
        if (ref in 'AG' and alt in 'CT') or (ref in 'CT' and alt in 'AG'):
            score += 0.2
            
        return score
        
    def _determine_variant_type(self, ref: str, alt: str) -> str:
        """Determine variant type"""
        if len(ref) == len(alt):
            return 'SNP'
        elif len(ref) > len(alt):
            return 'DEL'
        else:
            return 'INS'
            
    def _calculate_variant_frequency(self, alt: str, alignment: List[Tuple[str, str]]) -> float:
        """Calculate variant frequency"""
        alt_count = sum(1 for _, b in alignment if b == alt)
        total = len(alignment)
        return alt_count / total if total > 0 else 0.0
        
    def _predict_variant_impact(self, pos: int, ref: str, alt: str) -> Optional[str]:
        """Predict variant impact"""
        if len(ref) != len(alt):
            return 'HIGH'
            
        # Check if in coding region
        if pos % 3 == 0:  # First position of codon
            return 'MODERATE'
        elif pos % 3 == 2:  # Third position of codon
            return 'LOW'
        else:
            return 'MODIFIER' 