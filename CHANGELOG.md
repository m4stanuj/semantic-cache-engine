# Changelog

All notable changes to Semantic Cache Engine are documented here.

## [1.4.0] — 2026-04-05

### Added
- **Batch embedding mode** — 3x faster initial cache population
- TTL extension on cache hits (configurable, default: extend by 50%)
- Cache analytics endpoint: hit rate, avg latency, storage usage

### Fixed
- Cosine similarity calculation edge case with zero-norm vectors
- ChromaDB connection leak when cache exceeds `max_entries`

## [1.3.0] — 2026-02-18

### Added
- Redis-compatible API layer for drop-in replacement
- Namespace isolation — separate cache spaces per application
- LRU eviction policy as alternative to TTL-based expiry

### Changed
- Default embedding model upgraded from `all-MiniLM-L6-v2` to `all-mpnet-base-v2` (+4% recall)

## [1.2.0] — 2025-12-01

### Added
- Async API support for high-concurrency applications
- Cache warming from CSV/JSON seed files
- Prometheus-compatible metrics export

### Fixed
- Memory spike when processing embeddings for queries >4096 tokens

## [1.1.0] — 2025-09-15

### Added
- ChromaDB persistence — cache survives application restarts
- Configurable similarity threshold (default: 0.92)
- Decorator API (`@cache.wrap`) for zero-config integration

### Changed
- Migrated from FAISS to ChromaDB for better persistence support

## [1.0.0] — 2025-06-20

### Added
- Initial release — extracted from M4STCLAW v2 core
- In-memory vector cache with sentence-transformers
- Basic TTL expiry and max entry limits
- 40-60% API cost reduction in production benchmarks
