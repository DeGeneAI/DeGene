from typing import List, Dict
from dataclasses import dataclass
import hashlib
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import entropy
from collections import Counter

@dataclass
class GeneExpression:
    gene_id: str
    expression_level: float
    tissue_specificity: Dict[str, float]
    regulatory_elements: List[str]
    predicted_function: str

class ExpressionAnalyzer:
    """Advanced gene expression analysis tools"""
    
    def __init__(self):
        self.model = self._build_expression_model()
        
    def _build_expression_model(self):
        """Build gene expression prediction model"""
        model = RandomForestClassifier(n_estimators=100)
        return model
        
    def predict_gene_expression(self, gene_sequence: str) -> GeneExpression:
        """Predict gene expression patterns"""
        # Extract features
        features = self._extract_expression_features(gene_sequence)
        
        # Predict expression level
        expression_level = self.model.predict([features])[0]
        
        # Predict tissue specificity
        tissue_specificity = self._predict_tissue_specificity(gene_sequence)
        
        # Predict regulatory elements
        regulatory_elements = self._find_regulatory_elements(gene_sequence)
        
        # Predict function
        predicted_function = self._predict_gene_function(gene_sequence)
        
        return GeneExpression(
            gene_id=f"gene_{hashlib.md5(gene_sequence.encode()).hexdigest()[:8]}",
            expression_level=float(expression_level),
            tissue_specificity=tissue_specificity,
            regulatory_elements=regulatory_elements,
            predicted_function=predicted_function
        )
        
    def _extract_expression_features(self, sequence: str) -> List[float]:
        """Extract features for expression prediction"""
        features = []
        
        # GC content
        features.append(self._calculate_gc_content(sequence))
        
        # CpG content
        cpg_count = sequence.count('CG')
        features.append(cpg_count / len(sequence))
        
        # Sequence complexity
        features.append(self._calculate_sequence_complexity(sequence))
        
        # Promoter strength
        features.append(self._calculate_promoter_strength(sequence))
        
        return features
        
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content"""
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0.0
        
    def _calculate_sequence_complexity(self, sequence: str) -> float:
        """Calculate sequence complexity using entropy"""
        base_counts = Counter(sequence)
        total = sum(base_counts.values())
        probabilities = [count/total for count in base_counts.values()]
        return entropy(probabilities)
        
    def _calculate_promoter_strength(self, sequence: str) -> float:
        """Calculate promoter strength"""
        score = 0.0
        
        # Check for TATA box
        if 'TATAAA' in sequence:
            score += 0.3
            
        # Check for GC-rich regions
        gc_content = self._calculate_gc_content(sequence)
        if gc_content > 0.6:
            score += 0.2
            
        # Check for transcription factor binding sites
        tf_sites = self._find_transcription_factor_sites(sequence)
        score += len(tf_sites) * 0.1
        
        return score
        
    def _predict_tissue_specificity(self, sequence: str) -> Dict[str, float]:
        """Predict tissue specificity"""
        # Implement tissue specificity prediction
        return {
            'liver': 0.8,
            'brain': 0.6,
            'heart': 0.4
        }
        
    def _find_regulatory_elements(self, sequence: str) -> List[str]:
        """Find regulatory elements"""
        elements = []
        
        # Check for common regulatory elements
        if 'TATAAA' in sequence:
            elements.append('TATA_box')
        if 'CCAAT' in sequence:
            elements.append('CAAT_box')
        if 'GGGCGG' in sequence:
            elements.append('GC_box')
            
        return elements
        
    def _predict_gene_function(self, sequence: str) -> str:
        """Predict gene function"""
        # Implement function prediction
        return "transcription_factor" 