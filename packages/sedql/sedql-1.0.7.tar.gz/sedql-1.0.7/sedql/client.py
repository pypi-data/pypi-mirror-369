"""
SED Client - Python wrapper around SED CLI commands
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .exceptions import SEDError, SEDConnectionError, SEDValidationError


class SEDClient:
    """
    Python client for SED (Semantic Entities Designs)
    
    This client wraps the SED CLI tool to provide programmatic access
    to semantic layer functionality with full TypeScript CLI capabilities.
    """
    
    def __init__(self, db_url: str = None, config_path: str = None):
        """
        Initialize SED client
        
        Args:
            db_url: Database connection string (e.g., "postgresql://user:pass@localhost:5432/db")
            config_path: Path to SED config file (optional)
        """
        self.db_url = db_url
        self.config_path = config_path or "sed.config.json"
        self._ensure_sed_installed()
    
    def _ensure_sed_installed(self):
        """Check if SED CLI is available"""
        # Try to find sedql in npm global directory (Windows)
        npm_prefix_path = r"C:\Users\brije\AppData\Roaming\npm"
        sedql_path = os.path.join(npm_prefix_path, "sedql.cmd")
        if os.path.exists(sedql_path):
            self._sed_command = [sedql_path]
            return
        
        # First try global sedql command
        try:
            result = subprocess.run(["sedql", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._sed_command = ["sedql"]
                return
        except FileNotFoundError:
            pass
        
        # Fall back to npx sedql
        try:
            result = subprocess.run(["npx", "sedql", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._sed_command = ["npx", "sedql"]
                return
        except FileNotFoundError:
            pass
        
        raise SEDError("SED CLI not found. Install with: npm install -g @sed/sedql")
    
    def _run_command(self, command: List[str], input_data: str = None) -> Dict[str, Any]:
        """
        Run a SED CLI command and return the result
        
        Args:
            command: List of command arguments
            input_data: Input data to pipe to command (optional)
            
        Returns:
            Command result as dictionary
        """
        try:
            # Add config path if specified
            if self.config_path and self.config_path != "sed.config.json":
                command.extend(["-c", self.config_path])
            
            # Run the command
            if input_data:
                result = subprocess.run(
                    command,
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise SEDError(f"Command failed: {' '.join(command)}\nError: {error_msg}")
            
            # Try to parse JSON output
            try:
                if result.stdout.strip():
                    return json.loads(result.stdout)
                else:
                    return {"success": True, "message": "Command completed successfully"}
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout.strip()}
                
        except subprocess.TimeoutExpired:
            raise SEDError(f"Command timed out: {' '.join(command)}")
        except Exception as e:
            raise SEDError(f"Command execution failed: {str(e)}")
    
    def _get_business_context(self) -> Dict[str, Any]:
        """Get semantic context for AI applications from TypeScript CLI"""
        try:
            return self._run_command(self._sed_command + ["context"])
        except Exception as e:
            return {"error": f"Failed to get business context: {str(e)}"}
    
    def _validate_semantic_layer(self) -> Dict[str, Any]:
        """Validate semantic layer using TypeScript CLI validation"""
        try:
            return self._run_command(self._sed_command + ["validate"])
        except Exception as e:
            return {"error": f"Failed to validate semantic layer: {str(e)}"}
    
    def _get_status_with_rules(self) -> Dict[str, Any]:
        """Get comprehensive status including business rules from TypeScript CLI"""
        try:
            return self._run_command(self._sed_command + ["status"])
        except Exception as e:
            return {"error": f"Failed to get status: {str(e)}"}
    
    def _detect_schema_changes(self, format: str = "json") -> Dict[str, Any]:
        """Detect schema changes using TypeScript CLI with rich analysis"""
        try:
            return self._run_command(self._sed_command + ["detect-changes", "--format", format])
        except Exception as e:
            return {"error": f"Failed to detect changes: {str(e)}"}
    
    def _assess_query_risk(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess query risk using business rules and validation"""
        try:
            # Get business rules status
            rules_status = self._get_status_with_rules()
            
            # Validate the query
            validation = self._validate_semantic_layer()
            
            # Assess risk based on rules and validation
            risk_factors = []
            risk_level = "LOW"
            
            if rules_status.get("rules", {}).get("enabled", 0) == 0:
                risk_factors.append("No business rules enabled")
                risk_level = "HIGH"
            
            if validation.get("errors", []):
                risk_factors.append(f"Validation errors: {len(validation['errors'])}")
                risk_level = "HIGH"
            
            if validation.get("warnings", []):
                risk_factors.append(f"Validation warnings: {len(validation['warnings'])}")
                risk_level = "MEDIUM"
            
            return {
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "business_rules_status": rules_status.get("rules", {}),
                "validation_status": validation
            }
        except Exception as e:
            return {"error": f"Failed to assess risk: {str(e)}", "risk_level": "UNKNOWN"}
    
    def init(self, force: bool = False) -> Dict[str, Any]:
        """
        Initialize SED with database connection
        
        Args:
            force: Overwrite existing config
            
        Returns:
            Initialization result
        """
        command = self._sed_command + ["init"]
        if force:
            command.append("--force")
        
        return self._run_command(command)
    
    def build(self, output_file: str = None) -> Dict[str, Any]:
        """
        Build or rebuild semantic layer
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Build result
        """
        command = self._sed_command + ["build"]
        if output_file:
            command.extend(["-o", output_file])
        
        return self._run_command(command)
    
    def query(self, natural_language_query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Query database using natural language with full TypeScript CLI processing
        
        Args:
            natural_language_query: Natural language query string
            verbose: Show detailed query translation
            
        Returns:
            Query results with business context and validation
        """
        command = self._sed_command + ["query", natural_language_query]
        if verbose:
            command.append("--verbose")
        
        # Execute query with full TypeScript processing
        query_result = self._run_command(command)
        
        # Get additional context and validation
        business_context = self._get_business_context()
        validation = self._validate_semantic_layer()
        risk_assessment = self._assess_query_risk(natural_language_query, business_context)
        
        # Return enriched response
        return {
            "query_result": query_result,
            "business_context": business_context,
            "validation": validation,
            "risk_assessment": risk_assessment,
            "metadata": {
                "query": natural_language_query,
                "timestamp": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip()),
                "cli_version": "TypeScript CLI v1.0.7"
            }
        }
    
    def detect_changes(self, verbose: bool = False, format: str = "summary") -> Dict[str, Any]:
        """
        Detect schema changes in database with rich analysis
        
        Args:
            verbose: Show detailed change information
            format: Output format (json, table, summary)
            
        Returns:
            Change detection results with impact analysis
        """
        command = self._sed_command + ["detect-changes", "--format", format]
        if verbose:
            command.append("--verbose")
        
        changes = self._run_command(command)
        
        # Enhance with additional analysis
        return {
            "changes": changes,
            "analysis": {
                "total_changes": len(changes.get("changes", [])),
                "breaking_changes": len(changes.get("validation", {}).get("breakingChanges", [])),
                "impact_assessment": changes.get("validation", {}).get("impact", "UNKNOWN"),
                "recommendations": self._generate_change_recommendations(changes)
            }
        }
    
    def _generate_change_recommendations(self, changes: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detected changes"""
        recommendations = []
        
        if changes.get("validation", {}).get("breakingChanges"):
            recommendations.append("Review breaking changes before deployment")
        
        if len(changes.get("changes", [])) > 10:
            recommendations.append("Consider staging changes in batches")
        
        if changes.get("validation", {}).get("impact") == "HIGH":
            recommendations.append("Schedule maintenance window for high-impact changes")
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current SED status and configuration with business rules
        
        Returns:
            Comprehensive status information
        """
        return self._get_status_with_rules()
    
    def export_config(self, format: str = "json", output_file: str = None) -> Dict[str, Any]:
        """
        Export semantic layer and configuration
        
        Args:
            format: Export format (json, yaml)
            output_file: Output file path (optional)
            
        Returns:
            Export result
        """
        command = self._sed_command + ["export", "--format", format]
        if output_file:
            command.extend(["-o", output_file])
        
        return self._run_command(command)
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate semantic layer with comprehensive checks
        
        Returns:
            Validation results with detailed analysis
        """
        validation = self._validate_semantic_layer()
        
        # Enhance validation results
        return {
            "validation": validation,
            "summary": {
                "status": "PASS" if not validation.get("errors") else "FAIL",
                "total_checks": len(validation.get("checks", [])),
                "errors": len(validation.get("errors", [])),
                "warnings": len(validation.get("warnings", [])),
                "recommendations": self._generate_validation_recommendations(validation)
            }
        }
    
    def _generate_validation_recommendations(self, validation: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if validation.get("errors"):
            recommendations.append("Fix validation errors before proceeding")
        
        if validation.get("warnings"):
            recommendations.append("Review warnings for potential issues")
        
        if not validation.get("checks"):
            recommendations.append("No validation checks performed")
        
        return recommendations
    
    def query_with_ai(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query with AI integration leveraging full TypeScript CLI capabilities
        
        Args:
            query_params: Dictionary containing:
                - natural_language: The query string
                - ai_model: AI model to use (optional)
                - business_context: Business context (optional)
                - ai_client: AI client instance (optional)
                
        Returns:
            AI-enhanced query results with full SED features
        """
        natural_language = query_params.get("natural_language")
        if not natural_language:
            raise SEDError("natural_language is required in query_params")
        
        # Get business context for AI enhancement
        business_context = self._get_business_context()
        
        # Execute query with full TypeScript processing
        query_result = self.query(natural_language, verbose=query_params.get("verbose", False))
        
        # Enhance with AI-specific processing if client provided
        ai_enhancement = {}
        if query_params.get("ai_client"):
            try:
                ai_enhancement = self._enhance_with_ai(
                    query_params["ai_client"], 
                    natural_language, 
                    query_result,
                    query_params.get("ai_model", "default")
                )
            except Exception as e:
                ai_enhancement = {"error": f"AI enhancement failed: {str(e)}"}
        
        # Return comprehensive AI-enhanced response
        return {
            "query_result": query_result,
            "ai_enhancement": ai_enhancement,
            "business_context": business_context,
            "insights": self._extract_insights(query_result),
            "risk_assessment": query_result.get("risk_assessment", {}),
            "metadata": {
                "ai_model": query_params.get("ai_model", "not_specified"),
                "ai_enhanced": bool(query_params.get("ai_client")),
                "timestamp": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip())
            }
        }
    
    def _enhance_with_ai(self, ai_client: Any, query: str, result: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Enhance results using provided AI client"""
        try:
            # This is a placeholder for AI enhancement logic
            # Users can implement their own AI processing here
            return {
                "ai_processed": True,
                "model": model,
                "enhancement_type": "custom_implementation_required",
                "message": "AI enhancement requires custom implementation using the provided ai_client"
            }
        except Exception as e:
            return {"error": f"AI enhancement failed: {str(e)}"}
    
    def _extract_insights(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from query results"""
        try:
            # Basic insight extraction
            result_data = query_result.get("query_result", {})
            
            insights = {
                "data_points": len(result_data.get("data", [])),
                "execution_time": result_data.get("execution_time", "unknown"),
                "query_complexity": "simple",  # Could be enhanced with actual analysis
                "business_impact": "low"  # Could be enhanced with business rule analysis
            }
            
            return insights
        except Exception as e:
            return {"error": f"Failed to extract insights: {str(e)}"}
    
    def get_semantic_mapping(self) -> Dict[str, Any]:
        """
        Get current semantic mapping with business context
        
        Returns:
            Semantic mapping data with business rules
        """
        try:
            # Get semantic context which includes mapping
            context = self._get_business_context()
            
            # Get business rules status
            rules_status = self._get_status_with_rules()
            
            return {
                "semantic_mapping": context,
                "business_rules": rules_status.get("rules", {}),
                "entities": context.get("entities", []),
                "relationships": context.get("relationships", []),
                "business_domains": context.get("business_domains", [])
            }
        except Exception as e:
            return {"error": f"Failed to get semantic mapping: {str(e)}"}
    
    def close(self):
        """Close any open connections (no-op for CLI wrapper)"""
        pass
