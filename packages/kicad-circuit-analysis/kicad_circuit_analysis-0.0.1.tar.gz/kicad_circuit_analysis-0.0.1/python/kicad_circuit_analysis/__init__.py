"""
KiCAD Circuit Analysis - Professional Quality Assurance and FMEA Analysis

A comprehensive Python library for quality assurance and failure mode analysis 
of KiCAD circuit designs with AI-powered insights and professional reporting.

Example usage:
    import kicad_circuit_analysis as kca
    
    # FMEA Analysis
    analyzer = kca.FMEAAnalyzer()
    analyzer.load_schematic('circuit.kicad_sch')
    report = analyzer.run_comprehensive_fmea(ai_enhanced=True)
    
    # Quality Assurance
    qa = kca.QualityAssurance()
    results = qa.analyze_design('project.kicad_pro')
"""

from .fmea.simple_fmea import SimpleFMEAAnalyzer as FMEAAnalyzer
from .fmea.simple_fmea import SimpleFMEAAnalyzer as EnhancedFMEAAnalyzer

__version__ = "0.0.1"
__author__ = "Circuit-Synth Team"
__email__ = "contact@circuit-synth.com"

# Main API classes
class QualityAssurance:
    """Main quality assurance interface."""
    
    def __init__(self):
        self.fmea_analyzer = EnhancedFMEAAnalyzer()
    
    def load_project(self, project_path):
        """Load a KiCAD project for analysis."""
        return self.fmea_analyzer.load_project(project_path)
    
    def analyze_design(self, project_path, checks=None, ai_insights=True):
        """Run comprehensive design analysis."""
        self.fmea_analyzer.load_project(project_path)
        return self.fmea_analyzer.analyze_circuit(ai_enhanced=ai_insights)
    
    def calculate_risk_score(self, analysis_results):
        """Calculate overall design risk score."""
        return self.fmea_analyzer.calculate_risk_score(analysis_results)

# Export key classes
__all__ = [
    "FMEAAnalyzer",
    "EnhancedFMEAAnalyzer", 
    "QualityAssurance",
]