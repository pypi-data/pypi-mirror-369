"""
Enhanced LLM caller with intelligent context management capabilities.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .llm_caller import LLMCaller
from .context_analyzer import ContextAnalyzer
from .model_upshifter import ModelUpshifter
from .file_processor import FileProcessor
from .content_chunker import ContentChunker
from .context_strategy import ContextStrategy, ContextOverflowStrategy
from .interaction_logger import InteractionLogger
from ..models.request import LLMRequest, FileAttachment
from ..models.response import LLMResponse, ResponseStatus
from ..exceptions import (
    ContextOverflowError, FileProcessingError, ModelUpshiftError,
    ChunkingError, InteractionLoggingError, ErrorRecoveryStrategy
)

logger = logging.getLogger(__name__)


class EnhancedLLMCaller(LLMCaller):
    """Enhanced LLM caller with intelligent context management."""
    
    def __init__(self,
                 context_analyzer: Optional[ContextAnalyzer] = None,
                 model_upshifter: Optional[ModelUpshifter] = None,
                 file_processor: Optional[FileProcessor] = None,
                 content_chunker: Optional[ContentChunker] = None,
                 context_strategy: Optional[ContextStrategy] = None,
                 interaction_logger: Optional[InteractionLogger] = None,
                 enable_context_management: bool = True,
                 enable_file_processing: bool = True,
                 enable_interaction_logging: bool = True,
                 **kwargs):
        """
        Initialize the enhanced LLM caller.
        
        Args:
            context_analyzer: Context analysis component
            model_upshifter: Model upshifting component
            file_processor: File processing component
            content_chunker: Content chunking component
            context_strategy: Context overflow strategy manager
            interaction_logger: Interaction logging component
            enable_context_management: Whether to enable context management
            enable_file_processing: Whether to enable file processing
            enable_interaction_logging: Whether to enable interaction logging
            **kwargs: Additional arguments passed to base LLMCaller
        """
        super().__init__(**kwargs)
        
        # Initialize components
        self.context_analyzer = context_analyzer or ContextAnalyzer()
        self.model_upshifter = model_upshifter or ModelUpshifter()
        self.file_processor = file_processor or FileProcessor()
        self.content_chunker = content_chunker or ContentChunker()
        self.context_strategy = context_strategy or ContextStrategy()
        self.interaction_logger = interaction_logger or InteractionLogger() if enable_interaction_logging else None
        
        # Feature flags
        self.enable_context_management = enable_context_management
        self.enable_file_processing = enable_file_processing
        self.enable_interaction_logging = enable_interaction_logging
        
        # Enhanced statistics
        self.enhanced_stats = {
            "context_overflows": 0,
            "upshifts_performed": 0,
            "chunks_created": 0,
            "files_processed": 0,
            "context_management_time": 0.0,
            "graceful_degradations": 0,
            "feature_fallbacks": 0
        }
        
        # Graceful degradation settings
        self.graceful_degradation = True
        self.fallback_to_basic_caller = True
    
    def call(self, request: LLMRequest) -> Union[LLMResponse, List[LLMResponse]]:
        """
        Enhanced LLM call with context management.
        
        Args:
            request: LLM request configuration
            
        Returns:
            LLM response or list of responses (for chunked requests)
        """
        start_time = time.time()
        request_id = None
        
        try:
            # Log the request
            if self.interaction_logger:
                request_id = self.interaction_logger.log_request(request)
            
            # Process file attachments if enabled
            if self.enable_file_processing and request.file_attachments:
                request = self._process_file_attachments(request)
            
            # Analyze context requirements if enabled
            if self.enable_context_management:
                context_start = time.time()
                processed_requests = self._handle_context_management(request)
                self.enhanced_stats["context_management_time"] += time.time() - context_start
            else:
                processed_requests = [request]
            
            # Execute the request(s)
            if len(processed_requests) == 1:
                # Single request
                response = super().call(processed_requests[0])
                
                # Log the response
                if self.interaction_logger and request_id:
                    self.interaction_logger.log_response(response, request_id)
                
                return response
            else:
                # Multiple requests (chunked)
                responses = []
                for i, chunk_request in enumerate(processed_requests):
                    chunk_request_id = None
                    try:
                        # Log chunk request
                        if self.interaction_logger:
                            chunk_request_id = self.interaction_logger.log_request(
                                chunk_request, f"{request_id}_chunk_{i}"
                            )
                        
                        # Execute chunk
                        chunk_response = super().call(chunk_request)
                        responses.append(chunk_response)
                        
                        # Log chunk response
                        if self.interaction_logger and chunk_request_id:
                            self.interaction_logger.log_response(chunk_response, chunk_request_id)
                    
                    except Exception as e:
                        logger.error(f"Error processing chunk {i}: {e}")
                        # Create error response for this chunk
                        error_response = LLMResponse(
                            prompt_key=chunk_request.prompt_key,
                            model=chunk_request.model,
                            status=ResponseStatus.ERROR,
                            error_message=str(e),
                            execution_time=time.time() - start_time,
                            request_metadata=chunk_request.metadata
                        )
                        responses.append(error_response)
                        
                        if self.interaction_logger and chunk_request_id:
                            self.interaction_logger.log_response(error_response, chunk_request_id, str(e))
                
                # Reassemble responses if all chunks succeeded
                if all(r.is_success for r in responses):
                    try:
                        combined_response = self.content_chunker.reassemble_responses(
                            responses, request
                        )
                        
                        # Log the combined response
                        if self.interaction_logger and request_id:
                            self.interaction_logger.log_response(combined_response, request_id)
                        
                        return combined_response
                    except Exception as e:
                        logger.error(f"Error reassembling responses: {e}")
                        # Return individual responses if reassembly fails
                        return responses
                else:
                    # Return individual responses if any failed
                    return responses
        
        except Exception as e:
            logger.error(f"Error in enhanced LLM call: {e}")
            
            # Create error response
            error_response = LLMResponse(
                prompt_key=request.prompt_key,
                model=request.model,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                execution_time=time.time() - start_time,
                request_metadata=request.metadata
            )
            
            # Log the error
            if self.interaction_logger and request_id:
                self.interaction_logger.log_response(error_response, request_id, str(e))
            
            return error_response
    
    def _process_file_attachments(self, request: LLMRequest) -> LLMRequest:
        """Process file attachments and add them to the request with graceful degradation."""
        if not request.file_attachments:
            return request
        
        processed_files = []
        failed_files = []
        
        for attachment in request.file_attachments:
            try:
                # Process the file
                processed_file = self.file_processor.create_processed_file(
                    attachment.file_path,
                    request.model,
                    attachment.content_type
                )
                
                processed_files.append(processed_file)
                self.enhanced_stats["files_processed"] += 1
                
                logger.info(f"Processed file: {attachment.file_path} ({processed_file.token_count} tokens)")
                
            except Exception as e:
                logger.error(f"Error processing file {attachment.file_path}: {e}")
                failed_files.append((attachment.file_path, str(e)))
                
                if self.graceful_degradation:
                    # Try graceful degradation strategies
                    recovery_success = self._attempt_file_recovery(attachment, request.model)
                    if recovery_success:
                        processed_files.append(recovery_success)
                        self.enhanced_stats["graceful_degradations"] += 1
                    else:
                        # Continue without this file
                        self.enhanced_stats["feature_fallbacks"] += 1
                        continue
                else:
                    # Re-raise if graceful degradation is disabled
                    raise FileProcessingError(
                        f"Failed to process file {attachment.file_path}: {e}",
                        attachment.file_path,
                        attachment.content_type,
                        recoverable=True
                    )
        
        # Create updated request with processed files
        updated_request = request.model_copy()
        updated_request.processed_files = processed_files
        
        # Add warnings about failed files to metadata
        if failed_files and self.graceful_degradation:
            if not updated_request.metadata:
                updated_request.metadata = {}
            updated_request.metadata["file_processing_warnings"] = [
                f"Failed to process {path}: {error}" for path, error in failed_files
            ]
        
        return updated_request
    
    def _attempt_file_recovery(self, attachment: FileAttachment, model: str):
        """Attempt to recover from file processing errors."""
        try:
            # Try basic text extraction as fallback
            if attachment.content_type and attachment.content_type.startswith('text/'):
                with open(attachment.file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                from ..models.request import ProcessedFile
                return ProcessedFile(
                    original_path=attachment.file_path,
                    content=content[:10000],  # Limit to 10k chars for safety
                    content_type=attachment.content_type,
                    token_count=self.context_analyzer.token_estimator.estimate_text_tokens(content[:10000], model),
                    processing_method="fallback_text_extraction",
                    warnings=["Used fallback text extraction due to processing error"]
                )
        except Exception as e:
            logger.debug(f"File recovery also failed for {attachment.file_path}: {e}")
        
        return None
    
    def _handle_context_management(self, request: LLMRequest) -> List[LLMRequest]:
        """Handle context analysis and overflow management with graceful degradation."""
        try:
            # Analyze context requirements
            context_analysis = self.context_analyzer.analyze_request(request)
            
            # Update request with analysis
            updated_request = request.model_copy()
            updated_request.context_analysis = context_analysis
            
            # Check if context overflow handling is needed
            if context_analysis.requires_upshift or context_analysis.requires_chunking:
                self.enhanced_stats["context_overflows"] += 1
                
                # Determine if vision is required
                requires_vision = any(
                    self.file_processor._is_image_file(Path(att.file_path))
                    for att in request.file_attachments
                ) if request.file_attachments else False
                
                # Apply context strategy with error handling
                try:
                    strategy_result = self.context_strategy.handle_context_overflow(
                        updated_request,
                        context_analysis.total_tokens,
                        context_analysis.model_capacity or 4096,
                        requires_vision
                    )
                    
                    if strategy_result.success:
                        if strategy_result.action_taken == "upshift":
                            self.enhanced_stats["upshifts_performed"] += 1
                            logger.info(f"Upshifted model: {strategy_result.upshift_result.original_model} -> "
                                      f"{strategy_result.upshift_result.selected_model}")
                        elif strategy_result.action_taken == "chunk":
                            self.enhanced_stats["chunks_created"] += len(strategy_result.modified_requests)
                            logger.info(f"Chunked request into {len(strategy_result.modified_requests)} parts")
                        
                        return strategy_result.modified_requests
                    else:
                        logger.warning(f"Context overflow handling failed: {strategy_result.warnings}")
                        
                        if self.graceful_degradation:
                            # Try fallback strategies
                            fallback_requests = self._attempt_context_fallback(updated_request, context_analysis)
                            if fallback_requests:
                                self.enhanced_stats["graceful_degradations"] += 1
                                return fallback_requests
                        
                        # If graceful degradation is disabled or failed, raise error
                        if not self.graceful_degradation:
                            raise ContextOverflowError(
                                f"Context overflow: {context_analysis.total_tokens} tokens exceeds "
                                f"{context_analysis.model_capacity} token limit",
                                context_analysis.total_tokens,
                                context_analysis.model_capacity or 4096,
                                request.model
                            )
                
                except Exception as e:
                    if self.graceful_degradation:
                        logger.error(f"Context strategy failed, attempting fallback: {e}")
                        fallback_requests = self._attempt_context_fallback(updated_request, context_analysis)
                        if fallback_requests:
                            self.enhanced_stats["graceful_degradations"] += 1
                            return fallback_requests
                        else:
                            # Last resort: continue with original request and warn
                            logger.warning("All context management strategies failed, proceeding with original request")
                            self.enhanced_stats["feature_fallbacks"] += 1
                            return [updated_request]
                    else:
                        raise
            
            return [updated_request]
            
        except Exception as e:
            if self.graceful_degradation:
                logger.error(f"Context analysis failed, falling back to basic processing: {e}")
                self.enhanced_stats["feature_fallbacks"] += 1
                return [request]  # Return original request
            else:
                raise
    
    def _attempt_context_fallback(self, request: LLMRequest, context_analysis) -> List[LLMRequest]:
        """Attempt fallback strategies for context overflow."""
        try:
            # Try simple content reduction
            if hasattr(request, 'substitutions') and request.substitutions:
                # Find the largest substitution and try to truncate it
                largest_key = None
                largest_size = 0
                
                for key, value in request.substitutions.items():
                    if isinstance(value, str) and len(value) > largest_size:
                        largest_size = len(value)
                        largest_key = key
                
                if largest_key and largest_size > 1000:
                    # Create a truncated version
                    fallback_request = request.model_copy()
                    original_value = fallback_request.substitutions[largest_key]
                    
                    # Truncate to roughly fit within model limits
                    max_chars = (context_analysis.model_capacity or 4096) * 3  # Rough chars per token
                    truncated_value = original_value[:max_chars] + "\n\n[Content truncated for context limits]"
                    
                    fallback_request.substitutions[largest_key] = truncated_value
                    
                    # Add warning to metadata
                    if not fallback_request.metadata:
                        fallback_request.metadata = {}
                    fallback_request.metadata["content_truncated"] = {
                        "field": largest_key,
                        "original_length": len(original_value),
                        "truncated_length": len(truncated_value)
                    }
                    
                    logger.info(f"Truncated content in field '{largest_key}' to fit context limits")
                    return [fallback_request]
            
        except Exception as e:
            logger.debug(f"Context fallback strategy failed: {e}")
        
        return None
    
    def call_with_files(self, 
                       request: LLMRequest,
                       file_paths: List[Union[str, Path]]) -> Union[LLMResponse, List[LLMResponse]]:
        """
        Convenience method to call with file attachments.
        
        Args:
            request: Base LLM request
            file_paths: List of file paths to attach
            
        Returns:
            LLM response or list of responses
        """
        # Create file attachments
        attachments = []
        for file_path in file_paths:
            path_obj = Path(file_path)
            if path_obj.exists():
                attachments.append(FileAttachment(
                    file_path=str(path_obj),
                    content_type=self.file_processor._detect_content_type(path_obj)
                ))
            else:
                logger.warning(f"File not found: {file_path}")
        
        # Update request with attachments
        enhanced_request = request.model_copy()
        enhanced_request.file_attachments = attachments
        
        return self.call(enhanced_request)
    
    def estimate_request_cost(self, request: LLMRequest) -> Dict[str, Any]:
        """
        Estimate the cost and complexity of a request.
        
        Args:
            request: LLM request to analyze
            
        Returns:
            Cost estimation details
        """
        # Analyze context
        context_analysis = self.context_analyzer.analyze_request(request)
        
        # Get strategy recommendations
        strategy_recommendations = self.context_strategy.get_strategy_recommendations(
            request, context_analysis.total_tokens
        )
        
        # Estimate file processing time
        file_processing_time = 0.0
        if request.file_attachments:
            for attachment in request.file_attachments:
                file_processing_time += self.file_processor.estimate_processing_time(
                    attachment.file_path
                )
        
        return {
            "context_analysis": {
                "total_tokens": context_analysis.total_tokens,
                "text_tokens": context_analysis.text_tokens,
                "file_tokens": context_analysis.file_tokens,
                "requires_upshift": context_analysis.requires_upshift,
                "requires_chunking": context_analysis.requires_chunking
            },
            "strategy_recommendations": strategy_recommendations,
            "estimated_file_processing_time": file_processing_time,
            "estimated_chunks": max(1, context_analysis.total_tokens // 4000) if context_analysis.requires_chunking else 1
        }
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics including context management metrics."""
        base_stats = self.get_statistics()
        
        # Add enhanced statistics
        enhanced_stats = {
            **base_stats,
            **self.enhanced_stats
        }
        
        # Add component statistics
        if self.interaction_logger:
            enhanced_stats["logging_stats"] = self.interaction_logger.get_statistics()
        
        enhanced_stats["upshift_stats"] = self.model_upshifter.analyze_upshift_patterns()
        
        return enhanced_stats
    
    def configure_context_strategy(self, 
                                 default_strategy: ContextOverflowStrategy,
                                 model_strategies: Optional[Dict[str, ContextOverflowStrategy]] = None,
                                 max_cost_multiplier: float = 3.0) -> None:
        """
        Configure context overflow strategy.
        
        Args:
            default_strategy: Default strategy to use
            model_strategies: Per-model strategy overrides
            max_cost_multiplier: Maximum cost multiplier for upshifting
        """
        self.context_strategy.default_strategy = default_strategy
        self.context_strategy.max_cost_multiplier = max_cost_multiplier
        
        if model_strategies:
            for model, strategy in model_strategies.items():
                self.context_strategy.set_model_strategy(model, strategy)
        
        logger.info(f"Configured context strategy: {default_strategy.value}")
    
    def add_custom_model_capacity(self, model_name: str, max_tokens: int, provider: str, 
                                cost_multiplier: float = 1.0, supports_vision: bool = False) -> None:
        """
        Add custom model capacity information.
        
        Args:
            model_name: Name of the model
            max_tokens: Maximum context tokens
            provider: Provider name
            cost_multiplier: Cost multiplier relative to base
            supports_vision: Whether model supports vision
        """
        from .model_capacity_registry import ModelCapacity
        
        capacity = ModelCapacity(
            model_name=model_name,
            max_context_tokens=max_tokens,
            provider=provider,
            cost_multiplier=cost_multiplier,
            supports_vision=supports_vision
        )
        
        self.model_upshifter.add_custom_model(model_name, capacity)
        logger.info(f"Added custom model capacity: {model_name} ({max_tokens} tokens)")
    
    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent interactions from the logger."""
        if self.interaction_logger:
            return self.interaction_logger.get_recent_interactions(count)
        return []
    
    def clear_interaction_logs(self) -> bool:
        """Clear interaction logs."""
        if self.interaction_logger:
            return self.interaction_logger.clear_logs()
        return False
    
    def call_with_fallback(self, request: LLMRequest) -> Union[LLMResponse, List[LLMResponse]]:
        """
        Call with complete fallback to basic LLMCaller if enhanced features fail.
        
        This method provides the highest level of graceful degradation by falling
        back to the basic LLMCaller if all enhanced features fail.
        """
        try:
            return self.call(request)
        except Exception as e:
            if self.fallback_to_basic_caller:
                logger.warning(f"Enhanced features failed, falling back to basic caller: {e}")
                self.enhanced_stats["feature_fallbacks"] += 1
                
                # Use basic LLMCaller as ultimate fallback
                basic_caller = LLMCaller(
                    retry_strategy=self.retry_strategy,
                    json_parser=self.json_parser,
                    default_model_params=self.default_model_params
                )
                
                return basic_caller.call(request)
            else:
                raise
    
    def set_graceful_degradation(self, 
                               enabled: bool, 
                               fallback_to_basic: bool = True) -> None:
        """
        Configure graceful degradation settings.
        
        Args:
            enabled: Whether to enable graceful degradation
            fallback_to_basic: Whether to fallback to basic LLMCaller as last resort
        """
        self.graceful_degradation = enabled
        self.fallback_to_basic_caller = fallback_to_basic
        
        logger.info(f"Graceful degradation: {enabled}, Basic fallback: {fallback_to_basic}")
    
    def get_degradation_report(self) -> Dict[str, Any]:
        """Get report on graceful degradation events."""
        return {
            "graceful_degradations": self.enhanced_stats["graceful_degradations"],
            "feature_fallbacks": self.enhanced_stats["feature_fallbacks"],
            "degradation_rate": (
                (self.enhanced_stats["graceful_degradations"] + self.enhanced_stats["feature_fallbacks"]) 
                / max(1, self.stats["total_calls"])
            ) * 100,
            "most_common_failures": {
                "context_overflows": self.enhanced_stats["context_overflows"],
                "file_processing_errors": self.enhanced_stats["files_processed"] - 
                                        len([f for f in getattr(self, '_processed_files', [])]),
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown the enhanced caller and cleanup resources."""
        if self.interaction_logger:
            self.interaction_logger.shutdown()
        
        logger.info("Enhanced LLM caller shutdown complete")