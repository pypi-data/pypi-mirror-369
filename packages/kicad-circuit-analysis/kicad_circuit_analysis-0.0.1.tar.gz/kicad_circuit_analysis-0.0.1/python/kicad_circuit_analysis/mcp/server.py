"""
MCP Server for KiCAD Circuit Analysis

Provides Model Context Protocol interface for AI agent integration
with circuit quality assurance and FMEA analysis capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from ..fmea.simple_fmea import SimpleFMEAAnalyzer as EnhancedFMEAAnalyzer

# Configure logging to stderr (never stdout for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("kicad-circuit-analysis")

# Global analyzer instances
_fmea_analyzer: Optional[EnhancedFMEAAnalyzer] = None

@mcp.tool()
async def initialize_analyzer() -> str:
    """
    Initialize the FMEA analyzer and circuit parser.
    
    Returns:
        Success message
    """
    global _fmea_analyzer
    try:
        _fmea_analyzer = EnhancedFMEAAnalyzer()
        return "Initialized circuit analysis tools successfully"
    except Exception as e:
        logger.error(f"Error initializing analyzer: {e}")
        return f"Error initializing analyzer: {e}"

@mcp.tool()
async def load_schematic(filepath: str) -> str:
    """
    Load a KiCAD schematic file for analysis.
    
    Args:
        filepath: Path to the .kicad_sch file
        
    Returns:
        Success message with circuit info
    """
    if not _fmea_analyzer:
        await initialize_analyzer()
    
    try:
        result = _fmea_analyzer.load_schematic(filepath)
        return f"Loaded schematic: {filepath}"
    except Exception as e:
        logger.error(f"Error loading schematic {filepath}: {e}")
        return f"Error loading schematic: {e}"

@mcp.tool()
async def load_project(project_path: str) -> str:
    """
    Load a KiCAD project for comprehensive analysis.
    
    Args:
        project_path: Path to the .kicad_pro file
        
    Returns:
        Success message with project info
    """
    if not _fmea_analyzer:
        await initialize_analyzer()
    
    try:
        result = _fmea_analyzer.load_project(project_path)
        return f"Loaded project: {project_path}"
    except Exception as e:
        logger.error(f"Error loading project {project_path}: {e}")
        return f"Error loading project: {e}"

@mcp.tool()
async def run_fmea_analysis(ai_enhanced: bool = True) -> str:
    """
    Run comprehensive FMEA analysis on loaded circuit.
    
    Args:
        ai_enhanced: Enable AI-enhanced analysis for better insights
        
    Returns:
        FMEA analysis summary
    """
    if not _fmea_analyzer:
        return "Error: No analyzer initialized. Use initialize_analyzer() first"
    
    try:
        results = _fmea_analyzer.analyze_circuit(ai_enhanced=ai_enhanced)
        
        # Format results
        risk_score = _fmea_analyzer.calculate_risk_score(results)
        issues = results.get('issues', [])
        
        summary = f"FMEA Analysis Complete:\n"
        summary += f"  Risk Score: {risk_score}/100\n"
        summary += f"  Issues Found: {len(issues)}\n"
        
        if issues:
            summary += f"  Top Issues:\n"
            for issue in issues[:3]:  # Show top 3 issues
                summary += f"    - {issue.get('description', 'Unknown issue')}\n"
        
        return summary
    except Exception as e:
        logger.error(f"Error running FMEA analysis: {e}")
        return f"Error running FMEA analysis: {e}"

@mcp.tool()
async def analyze_component_risks(component_ref: str) -> str:
    """
    Analyze failure risks for a specific component.
    
    Args:
        component_ref: Component reference (e.g., "U1", "R1")
        
    Returns:
        Component risk analysis
    """
    if not _fmea_analyzer:
        return "Error: No analyzer initialized"
    
    try:
        risks = _fmea_analyzer.analyze_component_risks(component_ref)
        
        if not risks:
            return f"No specific risks identified for component {component_ref}"
        
        result = f"Risk Analysis for {component_ref}:\n"
        for risk in risks:
            result += f"  - {risk.get('failure_mode', 'Unknown')}: "
            result += f"{risk.get('severity', 'N/A')} severity\n"
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing component {component_ref}: {e}")
        return f"Error analyzing component: {e}"

@mcp.tool()
async def calculate_overall_risk() -> str:
    """
    Calculate overall design risk score.
    
    Returns:
        Risk score and assessment
    """
    if not _fmea_analyzer:
        return "Error: No analyzer initialized"
    
    try:
        # This would run a quick analysis if not already done
        results = _fmea_analyzer.get_cached_results() or _fmea_analyzer.analyze_circuit()
        risk_score = _fmea_analyzer.calculate_risk_score(results)
        
        if risk_score < 30:
            assessment = "Low Risk - Good design quality"
        elif risk_score < 60:
            assessment = "Medium Risk - Some concerns to address"
        else:
            assessment = "High Risk - Significant issues need attention"
        
        return f"Overall Risk Score: {risk_score}/100\nAssessment: {assessment}"
    except Exception as e:
        logger.error(f"Error calculating risk: {e}")
        return f"Error calculating risk: {e}"

@mcp.tool()
async def get_design_recommendations() -> str:
    """
    Get AI-powered design improvement recommendations.
    
    Returns:
        List of design recommendations
    """
    if not _fmea_analyzer:
        return "Error: No analyzer initialized"
    
    try:
        recommendations = _fmea_analyzer.get_recommendations()
        
        if not recommendations:
            return "No specific recommendations at this time"
        
        result = "Design Recommendations:\n"
        for i, rec in enumerate(recommendations[:5], 1):  # Top 5
            result += f"  {i}. {rec}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return f"Error getting recommendations: {e}"

def create_server() -> FastMCP:
    """Create and return the MCP server instance.""" 
    return mcp

def main():
    """Main entry point for MCP server."""
    import asyncio
    mcp.run()

if __name__ == "__main__":
    main()