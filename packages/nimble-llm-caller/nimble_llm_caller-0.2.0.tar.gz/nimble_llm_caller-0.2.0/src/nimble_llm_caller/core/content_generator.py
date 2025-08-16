"""
High-level content generator that orchestrates prompt management, LLM calls, and document assembly.
"""

import logging
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .llm_caller import LLMCaller
from .prompt_manager import PromptManager
from .document_assembler import DocumentAssembler
from ..models.request import LLMRequest, BatchRequest, RepromptRequest, ResponseFormat
from ..models.response import LLMResponse, BatchResponse, DocumentResponse
from ..utils.retry_strategy import RetryStrategy

logger = logging.getLogger(__name__)


class LLMContentGenerator:
    """
    High-level content generator that orchestrates the entire LLM workflow.
    
    This is the main interface for users of the package.
    """
    
    def __init__(
        self,
        prompt_file_path: Optional[str] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        default_model: str = "gpt-4o",
        output_dir: Optional[str] = None,
        template_dir: Optional[str] = None
    ):
        """
        Initialize the content generator.
        
        Args:
            prompt_file_path: Path to JSON file containing prompts
            retry_strategy: Strategy for handling retries
            default_model: Default model to use for calls
            output_dir: Directory for saving outputs
            template_dir: Directory containing document templates
        """
        self.default_model = default_model
        self.output_dir = Path(output_dir) if output_dir else Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.llm_caller = LLMCaller(retry_strategy=retry_strategy)
        self.prompt_manager = PromptManager(prompt_file_path, template_dir)
        self.document_assembler = DocumentAssembler(template_dir)
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_results = []
        
        logger.info(f"Initialized LLMContentGenerator with session ID: {self.session_id}")
    
    def call_single(
        self,
        prompt_key: str,
        model: Optional[str] = None,
        substitutions: Optional[Dict[str, Any]] = None,
        response_format: ResponseFormat = ResponseFormat.TEXT,
        model_params: Optional[Dict[str, Any]] = None,
        save_response: bool = True
    ) -> LLMResponse:
        """
        Make a single LLM call with a prompt.
        
        Args:
            prompt_key: Key of the prompt to use
            model: Model to use (defaults to default_model)
            substitutions: Variables to substitute in prompt
            response_format: Expected response format
            model_params: Model-specific parameters
            save_response: Whether to save response to file
            
        Returns:
            LLM response
        """
        model = model or self.default_model
        substitutions = substitutions or {}
        model_params = model_params or {}
        
        # Prepare the prompt
        prompt_config = self.prompt_manager.prepare_prompt(prompt_key, substitutions)
        if not prompt_config:
            raise ValueError(f"Could not prepare prompt: {prompt_key}")
        
        # Create request
        request = LLMRequest(
            prompt_key=prompt_key,
            model=model,
            substitutions=substitutions,
            response_format=response_format,
            model_params=model_params,
            metadata=prompt_config
        )
        
        # Make the call
        response = self.llm_caller.call(request)
        
        # Save response if requested
        if save_response:
            self._save_response(response)
        
        # Add to session results
        self.session_results.append(response)
        
        return response
    
    def call_batch(
        self,
        prompt_keys: List[str],
        models: Optional[List[str]] = None,
        shared_substitutions: Optional[Dict[str, Any]] = None,
        individual_substitutions: Optional[Dict[str, Dict[str, Any]]] = None,
        response_format: ResponseFormat = ResponseFormat.TEXT,
        parallel: bool = True,
        max_concurrent: int = 5,
        save_responses: bool = True
    ) -> BatchResponse:
        """
        Make multiple LLM calls in batch.
        
        Args:
            prompt_keys: List of prompt keys to use
            models: List of models to use (cycles through if fewer than prompts)
            shared_substitutions: Substitutions applied to all prompts
            individual_substitutions: Per-prompt substitutions
            response_format: Expected response format
            parallel: Whether to execute in parallel
            max_concurrent: Maximum concurrent requests
            save_responses: Whether to save responses to files
            
        Returns:
            Batch response with all individual responses
        """
        models = models or [self.default_model]
        shared_substitutions = shared_substitutions or {}
        individual_substitutions = individual_substitutions or {}
        
        # Create individual requests
        requests = []
        for i, prompt_key in enumerate(prompt_keys):
            model = models[i % len(models)]  # Cycle through models
            
            # Merge substitutions
            substitutions = shared_substitutions.copy()
            if prompt_key in individual_substitutions:
                substitutions.update(individual_substitutions[prompt_key])
            
            # Prepare prompt
            prompt_config = self.prompt_manager.prepare_prompt(prompt_key, substitutions)
            if not prompt_config:
                logger.warning(f"Could not prepare prompt: {prompt_key}")
                continue
            
            request = LLMRequest(
                prompt_key=prompt_key,
                model=model,
                substitutions=substitutions,
                response_format=response_format,
                metadata=prompt_config
            )
            requests.append(request)
        
        # Execute requests
        batch_response = BatchResponse(responses=[], total_requests=len(requests))
        batch_response.start_time = datetime.now()
        
        if parallel and len(requests) > 1:
            responses = self._execute_parallel(requests, max_concurrent)
        else:
            responses = self._execute_sequential(requests)
        
        batch_response.responses = responses
        batch_response.finalize()
        
        # Save responses if requested
        if save_responses:
            for response in responses:
                self._save_response(response)
        
        # Add to session results
        self.session_results.extend(responses)
        
        logger.info(f"Completed batch of {len(requests)} requests with "
                   f"{batch_response.success_rate:.1f}% success rate")
        
        return batch_response
    
    def reprompt(
        self,
        base_prompt_key: str,
        previous_results: List[Union[LLMResponse, Dict[str, Any]]],
        model: Optional[str] = None,
        context_key: str = "previous_context",
        combine_strategy: str = "append",
        additional_substitutions: Optional[Dict[str, Any]] = None,
        save_response: bool = True
    ) -> LLMResponse:
        """
        Make a reprompt call using previous results as context.
        
        Args:
            base_prompt_key: Base prompt to use
            previous_results: Results from previous calls
            model: Model to use
            context_key: Key to use for previous results in substitutions
            combine_strategy: How to combine previous results
            additional_substitutions: Additional substitutions
            save_response: Whether to save response
            
        Returns:
            LLM response
        """
        model = model or self.default_model
        additional_substitutions = additional_substitutions or {}
        
        # Convert responses to dictionaries
        results_data = []
        for result in previous_results:
            if isinstance(result, LLMResponse):
                results_data.append({
                    "prompt_key": result.prompt_key,
                    "content": result.content,
                    "parsed_content": result.parsed_content
                })
            else:
                results_data.append(result)
        
        # Create base request
        base_request = LLMRequest(
            prompt_key=base_prompt_key,
            model=model,
            substitutions=additional_substitutions
        )
        
        # Create reprompt request
        reprompt_request = RepromptRequest(
            base_request=base_request,
            previous_results=results_data,
            context_key=context_key,
            combine_strategy=combine_strategy
        )
        
        # Convert to standard request and execute
        request = reprompt_request.to_llm_request()
        
        # Prepare the prompt with context
        prompt_config = self.prompt_manager.prepare_prompt(
            request.prompt_key, 
            request.substitutions
        )
        if not prompt_config:
            raise ValueError(f"Could not prepare prompt: {request.prompt_key}")
        
        request.metadata = prompt_config
        
        # Make the call
        response = self.llm_caller.call(request)
        
        # Save response if requested
        if save_response:
            self._save_response(response)
        
        # Add to session results
        self.session_results.append(response)
        
        return response
    
    def assemble_document(
        self,
        responses: Union[BatchResponse, List[LLMResponse]],
        format: str = "markdown",
        template: Optional[str] = None,
        output_filename: Optional[str] = None,
        custom_sections: Optional[Dict[str, str]] = None
    ) -> DocumentResponse:
        """
        Assemble responses into a formatted document.
        
        Args:
            responses: Batch response or list of responses
            format: Output format (markdown, latex, text)
            template: Template file to use
            output_filename: Filename for output (auto-generated if None)
            custom_sections: Additional sections to include
            
        Returns:
            Document response
        """
        # Extract responses list
        if isinstance(responses, BatchResponse):
            response_list = responses.get_successful_responses()
        else:
            response_list = responses
        
        # Prepare content for assembly
        content_sections = {}
        source_keys = []
        
        for response in response_list:
            if response.has_content:
                content_sections[response.prompt_key] = response.content
                source_keys.append(response.prompt_key)
        
        # Add custom sections
        if custom_sections:
            content_sections.update(custom_sections)
        
        # Assemble document
        document_content = self.document_assembler.assemble(
            content_sections,
            format=format,
            template=template
        )
        
        # Create document response
        doc_response = DocumentResponse(
            document_content=document_content,
            format=format,
            source_responses=source_keys,
            template_used=template
        )
        
        # Save document if filename provided
        if output_filename:
            output_path = self.output_dir / output_filename
            doc_response.save_to_file(str(output_path))
            logger.info(f"Saved document to: {output_path}")
        
        return doc_response
    
    def _execute_parallel(
        self, 
        requests: List[LLMRequest], 
        max_concurrent: int
    ) -> List[LLMResponse]:
        """Execute requests in parallel using thread pool."""
        responses = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(self.llm_caller.call, request): request 
                for request in requests
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_request):
                try:
                    response = future.result()
                    responses.append(response)
                except Exception as e:
                    request = future_to_request[future]
                    logger.error(f"Request failed: {request.prompt_key}: {e}")
                    # Create error response
                    error_response = LLMResponse(
                        prompt_key=request.prompt_key,
                        model=request.model,
                        status="error",
                        error_message=str(e)
                    )
                    responses.append(error_response)
        
        return responses
    
    def _execute_sequential(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """Execute requests sequentially."""
        responses = []
        
        for request in requests:
            try:
                response = self.llm_caller.call(request)
                responses.append(response)
            except Exception as e:
                logger.error(f"Request failed: {request.prompt_key}: {e}")
                error_response = LLMResponse(
                    prompt_key=request.prompt_key,
                    model=request.model,
                    status="error",
                    error_message=str(e)
                )
                responses.append(error_response)
        
        return responses
    
    def _save_response(self, response: LLMResponse):
        """Save a response to file."""
        # Create session directory
        session_dir = self.output_dir / f"session_{self.session_id}"
        session_dir.mkdir(exist_ok=True)
        
        # Save raw content
        if response.content:
            content_file = session_dir / f"{response.prompt_key}_raw.txt"
            content_file.write_text(response.content, encoding='utf-8')
        
        # Save parsed content as JSON
        if response.parsed_content:
            import json
            parsed_file = session_dir / f"{response.prompt_key}_parsed.json"
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(response.parsed_content, f, indent=2, ensure_ascii=False)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics for the current session."""
        successful_responses = [r for r in self.session_results if r.is_success]
        
        return {
            "session_id": self.session_id,
            "total_requests": len(self.session_results),
            "successful_requests": len(successful_responses),
            "success_rate": len(successful_responses) / len(self.session_results) * 100 if self.session_results else 0,
            "llm_caller_stats": self.llm_caller.get_statistics(),
            "prompt_stats": self.prompt_manager.get_prompt_statistics()
        }
    
    def save_session_report(self, filename: Optional[str] = None):
        """Save a comprehensive session report."""
        if not filename:
            filename = f"session_report_{self.session_id}.json"
        
        report = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_results[0].timestamp.isoformat() if self.session_results else None,
                "end_time": self.session_results[-1].timestamp.isoformat() if self.session_results else None
            },
            "statistics": self.get_session_statistics(),
            "responses": [
                {
                    "prompt_key": r.prompt_key,
                    "model": r.model,
                    "status": r.status,
                    "execution_time": r.execution_time,
                    "has_content": r.has_content,
                    "content_preview": r.get_content_preview()
                }
                for r in self.session_results
            ]
        }
        
        report_path = self.output_dir / filename
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved session report to: {report_path}")