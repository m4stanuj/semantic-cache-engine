"""
Semantic Cache Engine - Core Module
Drop-in LLM response cache using ChromaDB vector similarity.
"""
import hashlib
import time
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SemanticCache:
    """
    A semantic similarity cache for LLM responses.
    
    Uses sentence-transformers to embed queries and ChromaDB
    to find semantically similar previous queries. If a match
    exceeds the similarity threshold, returns the cached response
    instead of making a new API call.
    
    Args:
        collection_name: ChromaDB collection name
        similarity_threshold: Minimum cosine similarity for cache hit (0-1)
        max_entries: Maximum cache entries before LRU eviction
        ttl_seconds: Time-to-live for cache entries
        persist_dir: Directory for ChromaDB persistence (None = in-memory)
        embedding_model: Sentence-transformers model name
    """
    
    def __init__(
        self,
        collection_name: str = "llm_cache",
        similarity_threshold: float = 0.92,
        max_entries: int = 10000,
        ttl_seconds: int = 3600,
        persist_dir: Optional[str] = "./cache_db",
        embedding_model: str = "all-mpnet-base-v2",
    ):
        if chromadb is None:
            raise ImportError("pip install chromadb")
        if SentenceTransformer is None:
            raise ImportError("pip install sentence-transformers")
        
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
        
        # Initialize embedding model
        self._model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        if persist_dir:
            self._client = chromadb.PersistentClient(path=persist_dir)
        else:
            self._client = chromadb.Client()
        
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    
    def get(self, query: str) -> Optional[str]:
        """
        Look up a semantically similar cached response.
        
        Returns the cached response if similarity >= threshold,
        otherwise returns None (cache miss).
        """
        if self._collection.count() == 0:
            self.stats["misses"] += 1
            return None
        
        embedding = self._model.encode(query).tolist()
        
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
        
        if not results["documents"][0]:
            self.stats["misses"] += 1
            return None
        
        distance = results["distances"][0][0]
        similarity = 1 - distance  # cosine distance to similarity
        
        if similarity >= self.similarity_threshold:
            metadata = results["metadatas"][0][0]
            
            # Check TTL
            cached_at = metadata.get("cached_at", 0)
            if time.time() - cached_at > self.ttl_seconds:
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return results["documents"][0][0]
        
        self.stats["misses"] += 1
        return None
    
    def put(self, query: str, response: str):
        """Store a query-response pair in the cache."""
        # Evict if at capacity
        if self._collection.count() >= self.max_entries:
            self._evict_oldest()
        
        embedding = self._model.encode(query).tolist()
        doc_id = hashlib.md5(query.encode()).hexdigest()
        
        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[response],
            metadatas=[{
                "query": query[:500],
                "cached_at": time.time(),
                "query_length": len(query),
                "response_length": len(response),
            }],
        )
    
    def _evict_oldest(self):
        """Remove the oldest entry from the cache."""
        all_data = self._collection.get(include=["metadatas"])
        if all_data["ids"]:
            oldest_id = min(
                zip(all_data["ids"], all_data["metadatas"]),
                key=lambda x: x[1].get("cached_at", 0),
            )[0]
            self._collection.delete(ids=[oldest_id])
            self.stats["evictions"] += 1
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return (self.stats["hits"] / total) * 100
    
    def clear(self):
        """Clear all cached entries."""
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            metadata={"hnsw:space": "cosine"},
        )
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def __repr__(self):
        return (
            f"SemanticCache(entries={self._collection.count()}, "
            f"hit_rate={self.hit_rate:.1f}%, "
            f"threshold={self.similarity_threshold})"
        )


def cache_wrap(cache_instance: SemanticCache):
    """
    Decorator for caching LLM function calls.
    
    Usage:
        cache = SemanticCache()
        
        @cache_wrap(cache)
        def ask_llm(prompt: str) -> str:
            return openai.chat(prompt)
    """
    def decorator(func):
        def wrapper(query: str, *args, **kwargs):
            cached = cache_instance.get(query)
            if cached is not None:
                return cached
            response = func(query, *args, **kwargs)
            cache_instance.put(query, response)
            return response
        return wrapper
    return decorator
