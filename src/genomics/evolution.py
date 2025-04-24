from typing import List, Tuple
from dataclasses import dataclass
from collections import Counter
from scipy.stats import entropy
import numpy as np

@dataclass
class EvolutionaryFeature:
    position: int
    conservation_score: float
    selection_pressure: str
    ancestral_state: str
    derived_state: str

class EvolutionAnalyzer:
    """Advanced evolutionary analysis tools"""
    
    def analyze_evolution(self, sequence: str, reference: str) -> List[EvolutionaryFeature]:
        """Analyze evolutionary features"""
        features = []
        
        # Align sequences
        alignment = self._align_sequences(sequence, reference)
        
        for pos, (ref_base, sample_base) in enumerate(alignment):
            if ref_base != sample_base:
                # Calculate conservation score
                conservation = self._calculate_conservation_score(pos, alignment)
                
                # Determine selection pressure
                pressure = self._determine_selection_pressure(ref_base, sample_base)
                
                # Infer ancestral state
                ancestral = self._infer_ancestral_state(pos, alignment)
                
                features.append(EvolutionaryFeature(
                    position=pos,
                    conservation_score=conservation,
                    selection_pressure=pressure,
                    ancestral_state=ancestral,
                    derived_state=sample_base
                ))
                
        return features
        
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
        
    def _calculate_conservation_score(self, pos: int, alignment: List[Tuple[str, str]]) -> float:
        """Calculate conservation score"""
        # Count occurrences of each base
        base_counts = Counter(b for _, b in alignment)
        total = sum(base_counts.values())
        
        # Calculate entropy
        probabilities = [count/total for count in base_counts.values()]
        max_entropy = np.log2(len(base_counts))
        actual_entropy = entropy(probabilities)
        
        # Convert to conservation score
        return 1 - (actual_entropy / max_entropy)
        
    def _determine_selection_pressure(self, ref: str, alt: str) -> str:
        """Determine selection pressure"""
        # Check for synonymous vs non-synonymous changes
        if self._is_synonymous(ref, alt):
            return 'neutral'
        else:
            return 'positive' if self._is_beneficial(ref, alt) else 'negative'
            
    def _is_synonymous(self, ref: str, alt: str) -> bool:
        """Check if mutation is synonymous"""
        # Implement codon table lookup
        codon_table = {
            'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
            'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
            # ... more codons ...
        }
        return codon_table.get(ref, '') == codon_table.get(alt, '')
        
    def _is_beneficial(self, ref: str, alt: str) -> bool:
        """Check if mutation is likely beneficial"""
        # Implement simple scoring system
        score = 0
        
        # Check for conservative changes
        if ref in 'AG' and alt in 'CT':
            score += 1
            
        # Check for hydrophobic to hydrophobic
        if ref in 'AVILMFW' and alt in 'AVILMFW':
            score += 1
            
        return score > 0
        
    def _infer_ancestral_state(self, pos: int, alignment: List[Tuple[str, str]]) -> str:
        """Infer ancestral state using parsimony"""
        # Count base frequencies
        base_counts = Counter(b for _, b in alignment)
        return max(base_counts.items(), key=lambda x: x[1])[0] 