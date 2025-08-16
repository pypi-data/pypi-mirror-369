"""
Content chunking utilities for handling oversized LLM requests.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
import re

from ..models.request import LLMRequest
from ..models.response import LLMResponse
from .token_estimator import TokenEstimator

logger = logging.getLogger(__name__)


@dataclass
class ChunkInfo:
    """Information about a content chunk."""
    chunk_id: int
    content: str
    token_count: int
    start_position: int
    end_position: int
    overlap_tokens: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChunkingResult:
    """Result of content chunking operation."""
    success: bool
    chunks: List[ChunkInfo] = None
    total_chunks: int = 0
    total_tokens: int = 0
    overlap_tokens: int = 0
    chunking_method: str = ""
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []
        if self.warnings is None:
            self.warnings = []


class ContentChunker:
    """Handles intelligent content splitting for oversized requests."""
    
    def __init__(self, 
                 token_estimator: Optional[TokenEstimator] = None,
                 default_overlap_tokens: int = 100,
                 min_chunk_tokens: int = 500):
        """
        Initialize the content chunker.
        
        Args:
            token_estimator: Token estimator for content analysis
            default_overlap_tokens: Default overlap between chunks
            min_chunk_tokens: Minimum tokens per chunk
        """
        self.token_estimator = token_estimator or TokenEstimator()
        self.default_overlap_tokens = default_overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens
    
    def chunk_content(self, 
                     content: str, 
                     max_tokens: int,
                     model: str,
                     overlap_tokens: Optional[int] = None,
                     preserve_structure: bool = True) -> ChunkingResult:
        """
        Split content into chunks that fit within token limits.
        
        Args:
            content: Content to chunk
            max_tokens: Maximum tokens per chunk
            model: Model name for token estimation
            overlap_tokens: Overlap between chunks (uses default if None)
            preserve_structure: Whether to preserve document structure
            
        Returns:
            ChunkingResult with chunks and metadata
        """
        if overlap_tokens is None:
            overlap_tokens = self.default_overlap_tokens
        
        # Validate inputs
        if max_tokens <= overlap_tokens:
            return ChunkingResult(
                success=False,
                warnings=["max_tokens must be greater than overlap_tokens"]
            )
        
        if max_tokens < self.min_chunk_tokens:
            return ChunkingResult(
                success=False,
                warnings=[f"max_tokens ({max_tokens}) is less than minimum chunk size ({self.min_chunk_tokens})"]
            )
        
        # Check if content needs chunking
        total_tokens = self.token_estimator.estimate_text_tokens(content, model)
        if total_tokens <= max_tokens:
            # Content fits in one chunk
            return ChunkingResult(
                success=True,
                chunks=[ChunkInfo(
                    chunk_id=0,
                    content=content,
                    token_count=total_tokens,
                    start_position=0,
                    end_position=len(content)
                )],
                total_chunks=1,
                total_tokens=total_tokens,
                chunking_method="no_chunking_needed"
            )
        
        # Choose chunking strategy
        if preserve_structure:
            result = self._chunk_by_structure(content, max_tokens, model, overlap_tokens)
        else:
            result = self._chunk_by_tokens(content, max_tokens, model, overlap_tokens)
        
        # Validate result
        if result.success:
            result.total_chunks = len(result.chunks)
            result.total_tokens = sum(chunk.token_count for chunk in result.chunks)
            result.overlap_tokens = overlap_tokens
        
        return result
    
    def _chunk_by_structure(self, 
                           content: str, 
                           max_tokens: int, 
                           model: str, 
                           overlap_tokens: int) -> ChunkingResult:
        """Chunk content while preserving document structure."""
        # Try different structural boundaries in order of preference
        boundaries = [
            (r'\n\n\n+', "triple_newline"),  # Section breaks
            (r'\n\n', "double_newline"),     # Paragraph breaks
            (r'\n', "single_newline"),       # Line breaks
            (r'\.(?:\s|$)', "sentence"),     # Sentence breaks
            (r'\s+', "word"),                # Word breaks
        ]
        
        for pattern, method_name in boundaries:
            try:
                result = self._chunk_by_pattern(content, pattern, max_tokens, model, overlap_tokens)
                if result.success:
                    result.chunking_method = f"structure_{method_name}"
                    return result
            except Exception as e:
                logger.warning(f"Chunking by {method_name} failed: {e}")
                continue
        
        # Fallback to character-based chunking
        return self._chunk_by_characters(content, max_tokens, model, overlap_tokens)
    
    def _chunk_by_pattern(self, 
                         content: str, 
                         pattern: str, 
                         max_tokens: int, 
                         model: str, 
                         overlap_tokens: int) -> ChunkingResult:
        """Chunk content by splitting on a regex pattern."""
        # Split content by pattern
        parts = re.split(pattern, content)
        if len(parts) <= 1:
            raise ValueError(f"Pattern '{pattern}' did not split content")
        
        chunks = []
        current_chunk = ""
        current_position = 0
        chunk_id = 0
        
        for i, part in enumerate(parts):
            # Calculate what the chunk would be with this part added
            test_chunk = current_chunk + part
            if i < len(parts) - 1:
                # Add back the separator (except for last part)
                separator = re.search(pattern, content[current_position + len(current_chunk):])
                if separator:
                    test_chunk += separator.group()
            
            test_tokens = self.token_estimator.estimate_text_tokens(test_chunk, model)
            
            if test_tokens <= max_tokens or not current_chunk:
                # Add to current chunk
                current_chunk = test_chunk
            else:
                # Current chunk is full, save it and start new one
                if current_chunk:
                    chunk_tokens = self.token_estimator.estimate_text_tokens(current_chunk, model)
                    chunks.append(ChunkInfo(
                        chunk_id=chunk_id,
                        content=current_chunk,
                        token_count=chunk_tokens,
                        start_position=current_position,
                        end_position=current_position + len(current_chunk),
                        overlap_tokens=overlap_tokens if chunk_id > 0 else 0
                    ))
                    chunk_id += 1
                
                # Start new chunk with overlap from previous chunk
                if chunks and overlap_tokens > 0:
                    overlap_content = self._get_overlap_content(current_chunk, overlap_tokens, model)
                    current_chunk = overlap_content + part
                    current_position = current_position + len(chunks[-1].content) - len(overlap_content)
                else:
                    current_chunk = part
                    current_position = current_position + len(chunks[-1].content) if chunks else 0
        
        # Add final chunk
        if current_chunk:
            chunk_tokens = self.token_estimator.estimate_text_tokens(current_chunk, model)
            chunks.append(ChunkInfo(
                chunk_id=chunk_id,
                content=current_chunk,
                token_count=chunk_tokens,
                start_position=current_position,
                end_position=current_position + len(current_chunk),
                overlap_tokens=overlap_tokens if chunk_id > 0 else 0
            ))
        
        return ChunkingResult(
            success=True,
            chunks=chunks,
            chunking_method="pattern_based"
        )
    
    def _chunk_by_tokens(self, 
                        content: str, 
                        max_tokens: int, 
                        model: str, 
                        overlap_tokens: int) -> ChunkingResult:
        """Chunk content by token count without preserving structure."""
        # Estimate characters per token for this model
        sample_text = content[:1000] if len(content) > 1000 else content
        sample_tokens = self.token_estimator.estimate_text_tokens(sample_text, model)
        chars_per_token = len(sample_text) / sample_tokens if sample_tokens > 0 else 4.0
        
        # Calculate approximate chunk size in characters
        target_chars = int(max_tokens * chars_per_token * 0.9)  # 90% to be safe
        overlap_chars = int(overlap_tokens * chars_per_token)
        
        chunks = []
        position = 0
        chunk_id = 0
        
        while position < len(content):
            # Calculate chunk end position
            chunk_end = min(position + target_chars, len(content))
            
            # Try to find a good break point near the target
            if chunk_end < len(content):
                # Look for word boundary within last 10% of chunk
                search_start = max(position, chunk_end - int(target_chars * 0.1))
                word_boundary = content.rfind(' ', search_start, chunk_end)
                if word_boundary > position:
                    chunk_end = word_boundary
            
            chunk_content = content[position:chunk_end]
            
            # Verify token count and adjust if necessary
            chunk_tokens = self.token_estimator.estimate_text_tokens(chunk_content, model)
            
            # If chunk is too large, reduce it
            while chunk_tokens > max_tokens and len(chunk_content) > 100:
                chunk_end = int(chunk_end * 0.9)
                chunk_content = content[position:chunk_end]
                chunk_tokens = self.token_estimator.estimate_text_tokens(chunk_content, model)
            
            chunks.append(ChunkInfo(
                chunk_id=chunk_id,
                content=chunk_content,
                token_count=chunk_tokens,
                start_position=position,
                end_position=chunk_end,
                overlap_tokens=overlap_tokens if chunk_id > 0 else 0
            ))
            
            # Move to next chunk with overlap
            if chunk_end >= len(content):
                break
            
            position = chunk_end - overlap_chars
            if position <= chunks[-1].start_position:
                position = chunk_end  # Avoid infinite loop
            
            chunk_id += 1
        
        return ChunkingResult(
            success=True,
            chunks=chunks,
            chunking_method="token_based"
        )
    
    def _chunk_by_characters(self, 
                           content: str, 
                           max_tokens: int, 
                           model: str, 
                           overlap_tokens: int) -> ChunkingResult:
        """Fallback chunking by character count."""
        # Estimate characters per token
        chars_per_token = 4.0  # Conservative estimate
        target_chars = int(max_tokens * chars_per_token * 0.8)  # 80% to be very safe
        overlap_chars = int(overlap_tokens * chars_per_token)
        
        chunks = []
        position = 0
        chunk_id = 0
        
        while position < len(content):
            chunk_end = min(position + target_chars, len(content))
            chunk_content = content[position:chunk_end]
            
            chunk_tokens = self.token_estimator.estimate_text_tokens(chunk_content, model)
            
            chunks.append(ChunkInfo(
                chunk_id=chunk_id,
                content=chunk_content,
                token_count=chunk_tokens,
                start_position=position,
                end_position=chunk_end,
                overlap_tokens=overlap_tokens if chunk_id > 0 else 0
            ))
            
            if chunk_end >= len(content):
                break
            
            position = chunk_end - overlap_chars
            chunk_id += 1
        
        return ChunkingResult(
            success=True,
            chunks=chunks,
            chunking_method="character_based",
            warnings=["Used character-based chunking as fallback"]
        )
    
    def _get_overlap_content(self, content: str, overlap_tokens: int, model: str) -> str:
        """Extract overlap content from the end of a chunk."""
        if overlap_tokens <= 0:
            return ""
        
        # Estimate characters for overlap
        chars_per_token = 4.0
        target_chars = int(overlap_tokens * chars_per_token)
        
        if len(content) <= target_chars:
            return content
        
        # Try to find a good break point
        start_pos = len(content) - target_chars
        
        # Look for sentence boundary
        sentence_break = content.rfind('. ', start_pos)
        if sentence_break > start_pos - target_chars // 2:
            return content[sentence_break + 2:]
        
        # Look for word boundary
        word_break = content.rfind(' ', start_pos)
        if word_break > start_pos - target_chars // 2:
            return content[word_break + 1:]
        
        # Use character position
        return content[start_pos:]
    
    def chunk_request(self, 
                     request: LLMRequest, 
                     max_tokens: int,
                     content_field: str = "substitutions") -> List[LLMRequest]:
        """
        Create chunked requests from an oversized request.
        
        Args:
            request: Original LLM request
            max_tokens: Maximum tokens per chunk
            content_field: Field containing the content to chunk
            
        Returns:
            List of chunked requests
        """
        # Extract content to chunk
        if content_field == "substitutions":
            # Find the largest substitution value to chunk
            content_to_chunk = ""
            chunk_key = None
            
            for key, value in request.substitutions.items():
                if isinstance(value, str) and len(value) > len(content_to_chunk):
                    content_to_chunk = value
                    chunk_key = key
            
            if not content_to_chunk or not chunk_key:
                logger.warning("No suitable content found to chunk in substitutions")
                return [request]
        
        else:
            logger.error(f"Unsupported content_field: {content_field}")
            return [request]
        
        # Chunk the content
        chunking_result = self.chunk_content(
            content_to_chunk, 
            max_tokens, 
            request.model,
            preserve_structure=True
        )
        
        if not chunking_result.success:
            logger.error(f"Failed to chunk content: {chunking_result.warnings}")
            return [request]
        
        # Create chunked requests
        chunked_requests = []
        
        for chunk in chunking_result.chunks:
            # Create a copy of the original request
            chunked_request = request.model_copy()
            
            # Replace the chunked content
            chunked_request.substitutions[chunk_key] = chunk.content
            
            # Add chunk metadata
            if not chunked_request.metadata:
                chunked_request.metadata = {}
            
            chunked_request.metadata.update({
                "chunked": True,
                "chunk_id": chunk.chunk_id,
                "total_chunks": chunking_result.total_chunks,
                "chunk_tokens": chunk.token_count,
                "chunking_method": chunking_result.chunking_method,
                "original_content_length": len(content_to_chunk)
            })
            
            chunked_requests.append(chunked_request)
        
        return chunked_requests
    
    def reassemble_responses(self, 
                           responses: List[LLMResponse], 
                           original_request: LLMRequest,
                           reassembly_strategy: str = "concatenate") -> LLMResponse:
        """
        Combine multiple chunked responses into a single response.
        
        Args:
            responses: List of responses from chunked requests
            original_request: Original request before chunking
            reassembly_strategy: How to combine responses
            
        Returns:
            Combined LLM response
        """
        if not responses:
            raise ValueError("No responses to reassemble")
        
        if len(responses) == 1:
            return responses[0]
        
        # Sort responses by chunk_id if available
        sorted_responses = []
        for response in responses:
            chunk_id = response.metadata.get("chunk_id", 0) if response.metadata else 0
            sorted_responses.append((chunk_id, response))
        
        sorted_responses.sort(key=lambda x: x[0])
        responses = [resp for _, resp in sorted_responses]
        
        # Combine based on strategy
        if reassembly_strategy == "concatenate":
            combined_content = self._concatenate_responses(responses)
        elif reassembly_strategy == "merge_structured":
            combined_content = self._merge_structured_responses(responses)
        elif reassembly_strategy == "summarize":
            combined_content = self._summarize_responses(responses)
        else:
            combined_content = self._concatenate_responses(responses)
        
        # Create combined response
        first_response = responses[0]
        combined_response = LLMResponse(
            content=combined_content,
            model=first_response.model,
            usage=self._combine_usage(responses),
            metadata={
                "reassembled": True,
                "chunk_count": len(responses),
                "reassembly_strategy": reassembly_strategy,
                "original_request_id": id(original_request)
            }
        )
        
        return combined_response
    
    def _concatenate_responses(self, responses: List[LLMResponse]) -> str:
        """Concatenate response contents with separators."""
        contents = []
        for i, response in enumerate(responses):
            if i > 0:
                contents.append(f"\n--- Chunk {i + 1} ---\n")
            contents.append(response.content)
        
        return "".join(contents)
    
    def _merge_structured_responses(self, responses: List[LLMResponse]) -> str:
        """Merge responses by removing redundant separators and overlaps."""
        contents = []
        
        for i, response in enumerate(responses):
            content = response.content
            
            # Remove overlap with previous chunk if detected
            if i > 0 and contents:
                # Simple overlap detection: check if start of current content
                # matches end of previous content
                prev_content = contents[-1]
                overlap_found = False
                
                # Check for overlap up to 200 characters
                for overlap_len in range(min(200, len(content), len(prev_content)), 10, -1):
                    if prev_content[-overlap_len:] == content[:overlap_len]:
                        content = content[overlap_len:]
                        overlap_found = True
                        break
                
                if not overlap_found and len(contents) > 0:
                    # Add separator if no overlap found
                    contents.append("\n\n")
            
            contents.append(content)
        
        return "".join(contents)
    
    def _summarize_responses(self, responses: List[LLMResponse]) -> str:
        """Create a summary of all responses."""
        summary_parts = [
            f"Combined response from {len(responses)} chunks:\n"
        ]
        
        for i, response in enumerate(responses):
            content_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
            summary_parts.append(f"Chunk {i + 1}: {content_preview}")
        
        return "\n\n".join(summary_parts)
    
    def _combine_usage(self, responses: List[LLMResponse]) -> Optional[Dict[str, Any]]:
        """Combine usage statistics from multiple responses."""
        if not responses or not any(r.usage for r in responses):
            return None
        
        combined_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        for response in responses:
            if response.usage:
                for key in combined_usage:
                    if key in response.usage:
                        combined_usage[key] += response.usage[key]
        
        return combined_usage