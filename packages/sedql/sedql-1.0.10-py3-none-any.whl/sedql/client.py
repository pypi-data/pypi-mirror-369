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
        self.config_path = config_path or str(Path.cwd() / "sed.config.json")
        self._ensure_sed_installed()
        self._check_ai_environment()
    
    def _ensure_sed_installed(self):
        """Check if SED CLI is available - works on all platforms"""
        # Try global sedql command first (works on all platforms)
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
        
        # Try npm exec as last resort
        try:
            result = subprocess.run(["npm", "exec", "sedql", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._sed_command = ["npm", "exec", "sedql"]
                return
        except FileNotFoundError:
            pass
        
        raise SEDError("SED CLI not found. Install with: npm install -g sed-cli")
    
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
            if self.config_path and self.config_path != str(Path.cwd() / "sed.config.json"):
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
                "timestamp": self._get_timestamp(),
                "cli_version": "TypeScript CLI v1.0.10"
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
        Query with AI integration using user-provided AI services or environment variables
        
        Args:
            query_params: Dictionary containing:
                - natural_language: The query string
                - ai_client: User's AI client instance (optional if using environment)
                - ai_model: AI model to use (optional)
                - ai_service: AI service to use ('openai', 'anthropic', or 'custom')
                - business_context: Business context (optional)
                - verbose: Show detailed output (optional)
                
        Returns:
            AI-enhanced query results with full SED features
        """
        natural_language = query_params.get("natural_language")
        ai_client = query_params.get("ai_client")
        ai_service = query_params.get("ai_service", "auto")
        
        if not natural_language:
            raise SEDError("natural_language is required in query_params")
        
        # Auto-detect AI service if not specified
        if ai_service == "auto":
            if ai_client:
                ai_service = "custom"
            elif self.ai_environment["openai"]["available"]:
                ai_service = "openai"
            elif self.ai_environment["anthropic"]["available"]:
                ai_service = "anthropic"
            else:
                ai_service = "none"
        
        # Handle different AI service scenarios
        if ai_service == "openai" and self.ai_environment["openai"]["available"]:
            # Use OpenAI from environment
            import openai
            ai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            ai_model = query_params.get("ai_model", "gpt-4")
            
        elif ai_service == "anthropic" and self.ai_environment["anthropic"]["available"]:
            # Use Anthropic from environment
            import anthropic
            ai_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            ai_model = query_params.get("ai_model", "claude-3-sonnet-20240229")
            
        elif ai_service == "custom" and ai_client:
            # Use user-provided AI client
            ai_model = query_params.get("ai_model", "user-specified")
            
        else:
            # No AI service available
            raise SEDError(
                f"No AI service available for '{ai_service}'. "
                f"Available services: {self.get_ai_environment_status()['available_services']}. "
                f"Set environment variables or provide ai_client parameter."
            )
        
        # Get business context from SED
        business_context = self._get_business_context()
        
        # Execute query with full TypeScript processing
        query_result = self.query(natural_language, verbose=query_params.get("verbose", False))
        
        # Enhance with AI service
        ai_enhancement = self._enhance_with_user_ai(
            ai_client, 
                    natural_language, 
                    query_result,
            business_context,
            ai_model
                )
        
        # Return comprehensive AI-enhanced response
        return {
            "query_result": query_result,
            "ai_enhancement": ai_enhancement,
            "business_context": business_context,
            "insights": self._extract_insights(query_result),
            "risk_assessment": query_result.get("risk_assessment", {}),
            "metadata": {
                "ai_model": ai_model,
                "ai_service": ai_service,
                "ai_enhanced": True,
                "ai_provider": "environment" if ai_service in ["openai", "anthropic"] else "user-provided",
                "timestamp": self._get_timestamp()
            }
        }
    
    def _enhance_with_user_ai(self, ai_client: Any, query: str, result: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
        """
        Enhance results using user-provided AI client
        
        This method works with any AI service the user provides:
        - OpenAI client
        - Anthropic client  
        - Custom AI service
        - Any other AI provider
        """
        try:
            # Detect AI client type and enhance accordingly
            client_type = self._detect_ai_client_type(ai_client)
            
            if client_type == "openai":
                return self._enhance_with_openai(ai_client, query, result, context, model)
            elif client_type == "anthropic":
                return self._enhance_with_anthropic(ai_client, query, result, context, model)
            else:
                # Generic enhancement for custom AI services
                return self._enhance_with_generic_ai(ai_client, query, result, context, model)
                
        except Exception as e:
            return {
                "ai_processed": False,
                "error": f"AI enhancement failed: {str(e)}",
                "client_type": "unknown",
                "message": "Check your AI client configuration and try again"
            }
    
    def _detect_ai_client_type(self, ai_client: Any) -> str:
        """Detect the type of AI client provided by the user"""
        try:
            # Check for OpenAI client
            if hasattr(ai_client, 'chat') and hasattr(ai_client.chat, 'completions'):
                return "openai"
            # Check for Anthropic client
            elif hasattr(ai_client, 'messages') and hasattr(ai_client.messages, 'create'):
                return "anthropic"
            # Check for custom client with standard interface
            elif hasattr(ai_client, 'generate') or hasattr(ai_client, 'query'):
                return "custom"
            else:
                return "unknown"
        except:
            return "unknown"
    
    def _enhance_with_openai(self, ai_client: Any, query: str, result: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Enhance results using OpenAI client"""
        try:
            # Create a prompt that leverages SED's business context
            system_prompt = f"""You are a data analyst with access to a database through SED (Semantic Entities Designs).

Business Context: {context}

Your role is to:
1. Understand the user's query
2. Provide insights based on the query results
3. Suggest additional analysis if relevant
4. Explain findings in business terms

Current Query: {query}
Query Results: {result}

Provide a business-focused analysis and insights."""
            
            response = ai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please analyze this data and provide business insights."}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "ai_processed": True,
                "client_type": "openai",
                "model": model,
                "enhancement_type": "business_analysis",
                "ai_response": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            return {
                "ai_processed": False,
                "client_type": "openai",
                "error": f"OpenAI enhancement failed: {str(e)}"
            }
    
    def _enhance_with_anthropic(self, ai_client: Any, query: str, result: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Enhance results using Anthropic client"""
        try:
            system_prompt = f"""You are a data analyst with access to a database through SED (Semantic Entities Designs).

Business Context: {context}

Your role is to:
1. Understand the user's query
2. Provide insights based on the query results
3. Suggest additional analysis if relevant
4. Explain findings in business terms

Current Query: {query}
Query Results: {result}

Provide a business-focused analysis and insights."""
            
            response = ai_client.messages.create(
                model=model,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "Please analyze this data and provide business insights."}
                ]
            )
            
            return {
                "ai_processed": True,
                "client_type": "anthropic",
                "model": model,
                "enhancement_type": "business_analysis",
                "ai_response": response.content[0].text,
                "usage": getattr(response, 'usage', None)
            }
            
        except Exception as e:
            return {
                "ai_processed": False,
                "client_type": "anthropic",
                "error": f"Anthropic enhancement failed: {str(e)}"
            }
    
    def _enhance_with_generic_ai(self, ai_client: Any, query: str, result: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Enhance results using generic AI client interface"""
        try:
            # Try common AI client methods
            if hasattr(ai_client, 'generate'):
                ai_response = ai_client.generate(
                    prompt=f"Analyze this data: {query}\nResults: {result}\nContext: {context}",
                    max_tokens=1000
                )
            elif hasattr(ai_client, 'query'):
                ai_response = ai_client.query(
                    query=f"Analyze this data: {query}\nResults: {result}\nContext: {context}"
                )
            else:
                # Last resort: try to call the client directly
                ai_response = ai_client(
                    f"Analyze this data: {query}\nResults: {result}\nContext: {context}"
                )
            
            return {
                "ai_processed": True,
                "client_type": "custom",
                "model": model,
                "enhancement_type": "business_analysis",
                "ai_response": str(ai_response),
                "note": "Using custom AI client interface"
            }
            
        except Exception as e:
            return {
                "ai_processed": False,
                "client_type": "custom",
                "error": f"Custom AI enhancement failed: {str(e)}",
                "message": "Ensure your AI client has a compatible interface (generate, query, or callable)"
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
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

    def _check_ai_environment(self):
        """Check for AI API keys in environment variables"""
        self.ai_environment = {
            "openai": {
                "available": bool(os.getenv("OPENAI_API_KEY")),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "message": "Set OPENAI_API_KEY environment variable to use OpenAI"
            },
            "anthropic": {
                "available": bool(os.getenv("ANTHROPIC_API_KEY")),
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "message": "Set ANTHROPIC_API_KEY environment variable to use Anthropic"
            }
        }
        
        # Log available AI services
        available_services = [service for service, config in self.ai_environment.items() if config["available"]]
        if available_services:
            logger.info(f"Detected AI services: {', '.join(available_services)}")
        else:
            logger.info("No AI API keys detected. Set environment variables to use AI features.")
            logger.info("Examples:")
            logger.info("  export OPENAI_API_KEY='your-openai-key'")
            logger.info("  export ANTHROPIC_API_KEY='your-anthropic-key'")
    
    def get_ai_environment_status(self) -> Dict[str, Any]:
        """Get status of available AI services"""
        return {
            "available_services": [service for service, config in self.ai_environment.items() if config["available"]],
            "environment_status": self.ai_environment,
            "setup_instructions": {
                "openai": "export OPENAI_API_KEY='your-openai-api-key'",
                "anthropic": "export ANTHROPIC_API_KEY='your-anthropic-api-key'",
                "custom": "Provide your AI client instance directly to query_with_ai()"
            }
        }

    def query_with_openai(self, query: str, model: str = "gpt-4", verbose: bool = False) -> Dict[str, Any]:
        """
        Convenience method for OpenAI queries using environment variables
        
        Args:
            query: Natural language query
            model: OpenAI model to use
            verbose: Show detailed output
            
        Returns:
            AI-enhanced query results
        """
        if not self.ai_environment["openai"]["available"]:
            raise SEDError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable:\n"
                "  export OPENAI_API_KEY='your-openai-api-key'"
            )
        
        return self.query_with_ai({
            "natural_language": query,
            "ai_service": "openai",
            "ai_model": model,
            "verbose": verbose
        })
    
    def query_with_anthropic(self, query: str, model: str = "claude-3-sonnet-20240229", verbose: bool = False) -> Dict[str, Any]:
        """
        Convenience method for Anthropic queries using environment variables
        
        Args:
            query: Natural language query
            model: Anthropic model to use
            verbose: Show detailed output
            
        Returns:
            AI-enhanced query results
        """
        if not self.ai_environment["anthropic"]["available"]:
            raise SEDError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable:\n"
                "  export ANTHROPIC_API_KEY='your-anthropic-api-key'"
            )
        
        return self.query_with_ai({
            "natural_language": query,
            "ai_service": "anthropic",
            "ai_model": model,
            "verbose": verbose
        })
