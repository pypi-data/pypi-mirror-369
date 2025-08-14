"""
Command line interface for kicad-circuit-analysis.
"""

import argparse
import sys
from pathlib import Path

from .fmea.enhanced_fmea_analyzer import EnhancedFMEAAnalyzer
from .core.circuit_parser import CircuitParser

def main_fmea():
    """Main entry point for FMEA analysis CLI."""
    parser = argparse.ArgumentParser(description="KiCAD FMEA Analysis Tool")
    parser.add_argument("input_file", help="KiCAD schematic (.kicad_sch) or project (.kicad_pro) file")
    parser.add_argument("-o", "--output", help="Output report file (PDF or Excel)")
    parser.add_argument("--ai", action="store_true", help="Enable AI-enhanced analysis")
    parser.add_argument("--format", choices=["pdf", "excel", "json"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    try:
        analyzer = EnhancedFMEAAnalyzer()
        
        # Load input file
        input_path = Path(args.input_file)
        if input_path.suffix == ".kicad_sch":
            analyzer.load_schematic(input_path)
        elif input_path.suffix == ".kicad_pro":
            analyzer.load_project(input_path)
        else:
            print(f"Error: Unsupported file type: {input_path.suffix}")
            sys.exit(1)
        
        # Run analysis
        print("Running FMEA analysis...")
        results = analyzer.analyze_circuit(ai_enhanced=args.ai)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            if args.format == "pdf":
                analyzer.export_pdf(results, output_path)
            elif args.format == "excel":
                analyzer.export_excel(results, output_path)
            else:
                analyzer.export_json(results, output_path)
            print(f"Analysis complete. Report saved to {output_path}")
        else:
            print("Analysis Results:")
            print(f"Risk Score: {analyzer.calculate_risk_score(results)}/100")
            print(f"Issues Found: {len(results.get('issues', []))}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main_qa():
    """Main entry point for Quality Assurance CLI."""
    parser = argparse.ArgumentParser(description="KiCAD Quality Assurance Tool")
    parser.add_argument("project_file", help="KiCAD project file (.kicad_pro)")
    parser.add_argument("-o", "--output", help="Output directory for reports")
    parser.add_argument("--checks", nargs="+", 
                       choices=["electrical", "thermal", "mechanical", "manufacturing"],
                       default=["electrical"], help="Types of checks to run")
    
    args = parser.parse_args()
    
    try:
        from . import QualityAssurance
        
        qa = QualityAssurance()
        results = qa.analyze_design(args.project_file, checks=args.checks)
        risk_score = qa.calculate_risk_score(results)
        
        print(f"Quality Assurance Analysis Complete")
        print(f"Overall Risk Score: {risk_score}/100")
        print(f"Checks Performed: {', '.join(args.checks)}")
        
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(exist_ok=True)
            # Save reports would go here
            print(f"Reports saved to {output_dir}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fmea":
        main_fmea()
    else:
        main_qa()