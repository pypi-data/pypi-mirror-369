"""
Tree-sitter Chunker - Semantic code chunking for LLMs and embeddings.

Simple usage:
    from chunker import chunk_file, chunk_text, chunk_directory

    # Chunk a single file
    chunks = chunk_file("example.py", language="python")

    # Chunk raw text
    chunks = chunk_text(code_text, language="javascript")

    # Chunk entire directory
    results = chunk_directory("src/", language="python")
"""

from ._internal.cache import ASTCache
from .chunker import chunk_text_with_token_limit, count_chunk_tokens
from .chunker_config import ChunkerConfig
from .core import chunk_file
from .exceptions import LanguageNotFoundError, LibraryNotFoundError, ParserError
from .fallback.intelligent_fallback import (
    ChunkingDecision,
    DecisionMetrics,
    IntelligentFallbackChunker,
)
from .incremental import (
    DefaultChangeDetector,
    DefaultChunkCache,
    DefaultIncrementalProcessor,
)
from .languages.base import PluginConfig
from .multi_language import (
    LanguageDetectorImpl,
    MultiLanguageProcessorImpl,
    ProjectAnalyzerImpl,
)
from .optimization import (
    ChunkBoundaryAnalyzer,
    ChunkOptimizer,
    OptimizationConfig,
    OptimizationMetrics,
    OptimizationStrategy,
)
from .parallel import chunk_directory_parallel as chunk_directory
from .parser import (
    ParserConfig,
    clear_cache,
    get_language_info,
    get_parser,
    list_languages,
    return_parser,
)
from .plugin_manager import PluginManager, get_plugin_manager

# Optional advanced query features (may require heavy deps like numpy)
try:
    from .query_advanced import (
        AdvancedQueryIndex,
        NaturalLanguageQueryEngine,
        SmartQueryOptimizer,
    )

    _ADV_QUERY_AVAILABLE = True
except Exception:  # pragma: no cover - keep import lightweight during build tests
    AdvancedQueryIndex = None  # type: ignore
    NaturalLanguageQueryEngine = None  # type: ignore
    SmartQueryOptimizer = None  # type: ignore
    _ADV_QUERY_AVAILABLE = False
from .smart_context import InMemoryContextCache, TreeSitterSmartContextProvider
from .streaming import chunk_file_streaming
from .types import CodeChunk

__version__ = "1.0.1"


# Simple text chunking
def chunk_text(text: str, language: str, **kwargs):
    """Chunk text content directly without file I/O."""
    import tempfile
    from pathlib import Path

    # Write to temporary file and chunk it
    with tempfile.NamedTemporaryFile(
        encoding="utf-8",
        mode="w",
        suffix=".tmp",
        delete=False,
    ) as f:
        f.write(text)
        temp_path = f.name

    try:
        chunks = chunk_file(temp_path, language, **kwargs)
        return chunks
    finally:
        Path(temp_path).unlink(missing_ok=True)


# Convenient exports for common use cases
__all__ = [
    "ASTCache",
    "AdvancedQueryIndex",
    "ChunkBoundaryAnalyzer",
    "ChunkOptimizer",
    "ChunkerConfig",
    "ChunkingDecision",
    "CodeChunk",
    "DecisionMetrics",
    "DefaultChangeDetector",
    "DefaultChunkCache",
    "DefaultIncrementalProcessor",
    "InMemoryContextCache",
    "IntelligentFallbackChunker",
    "LanguageDetectorImpl",
    "LanguageNotFoundError",
    "LibraryNotFoundError",
    "MultiLanguageProcessorImpl",
]

# Extend __all__ with advanced query API only if import succeeded
if _ADV_QUERY_AVAILABLE:
    __all__.extend(
        [
            "AdvancedQueryIndex",
            "NaturalLanguageQueryEngine",
            "SmartQueryOptimizer",
        ],
    )

__all__.extend(
    [
        "OptimizationConfig",
        "OptimizationMetrics",
        "OptimizationStrategy",
        "ParserConfig",
        "ParserError",
        "PluginConfig",
        "PluginManager",
        "ProjectAnalyzerImpl",
        "TreeSitterSmartContextProvider",
        "__version__",
        "chunk_directory",
        "chunk_file",
        "chunk_file_streaming",
        "chunk_text",
        "chunk_text_with_token_limit",
        "clear_cache",
        "count_chunk_tokens",
        "get_language_info",
        "get_parser",
        "get_plugin_manager",
        "list_languages",
        "return_parser",
    ],
)
