"""Search engine service for the MCP server."""

from typing import Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient, models

from ..config import OpenAIConfig, QdrantConfig, SearchConfig
from ..utils.logging import LoggingConfig
from .components.search_result_models import HybridSearchResult
from .enhanced.cross_document_intelligence import ClusteringStrategy, SimilarityMetric
from .enhanced.topic_search_chain import ChainStrategy, TopicSearchChain
from .hybrid_search import HybridSearchEngine

logger = LoggingConfig.get_logger(__name__)


class SearchEngine:
    """Main search engine that orchestrates query processing and search."""

    def __init__(self):
        """Initialize the search engine."""
        self.client: AsyncQdrantClient | None = None
        self.config: QdrantConfig | None = None
        self.openai_client: AsyncOpenAI | None = None
        self.hybrid_search: HybridSearchEngine | None = None
        self.logger = LoggingConfig.get_logger(__name__)

    async def initialize(
        self,
        config: QdrantConfig,
        openai_config: OpenAIConfig,
        search_config: SearchConfig | None = None,
    ) -> None:
        """Initialize the search engine with configuration."""
        self.config = config
        try:
            # Configure timeout for Qdrant cloud instances
            # Set to 120 seconds to handle large datasets and prevent ReadTimeout errors
            self.client = AsyncQdrantClient(
                url=config.url,
                api_key=config.api_key,
                timeout=120,  # 120 seconds timeout for cloud instances
            )
            self.openai_client = AsyncOpenAI(api_key=openai_config.api_key)

            # Ensure collection exists
            if self.client is None:
                raise RuntimeError("Failed to initialize Qdrant client")

            collections = await self.client.get_collections()
            if not any(
                c.name == config.collection_name for c in collections.collections
            ):
                await self.client.create_collection(
                    collection_name=config.collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # Default size for OpenAI embeddings
                        distance=models.Distance.COSINE,
                    ),
                )

            # Initialize hybrid search (single path; pass through search_config which may be None)
            if self.client and self.openai_client:
                self.hybrid_search = HybridSearchEngine(
                    qdrant_client=self.client,
                    openai_client=self.openai_client,
                    collection_name=config.collection_name,
                    search_config=search_config,
                )

            self.logger.info("Successfully connected to Qdrant", url=config.url)
        except Exception as e:
            self.logger.error(
                "Failed to connect to Qdrant server",
                error=str(e),
                url=config.url,
                hint="Make sure Qdrant is running and accessible at the configured URL",
            )
            raise RuntimeError(
                f"Failed to connect to Qdrant server at {config.url}. "
                "Please ensure Qdrant is running and accessible."
            ) from None  # Suppress the original exception

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.client:
            await self.client.close()
            self.client = None

    async def search(
        self,
        query: str,
        source_types: list[str] | None = None,
        limit: int = 5,
        project_ids: list[str] | None = None,
    ) -> list[HybridSearchResult]:
        """Search for documents using hybrid search.

        Args:
            query: Search query text
            source_types: Optional list of source types to filter by
            limit: Maximum number of results to return
            project_ids: Optional list of project IDs to filter by
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        self.logger.debug(
            "Performing search",
            query=query,
            source_types=source_types,
            limit=limit,
            project_ids=project_ids,
        )

        try:
            results = await self.hybrid_search.search(
                query=query,
                source_types=source_types,
                limit=limit,
                project_ids=project_ids,
            )

            self.logger.info(
                "Search completed",
                query=query,
                result_count=len(results),
                project_ids=project_ids,
            )

            return results
        except Exception as e:
            self.logger.error("Search failed", error=str(e), query=query)
            raise

    async def generate_topic_chain(
        self, query: str, strategy: str = "mixed_exploration", max_links: int = 5
    ) -> TopicSearchChain:
        """🔥 NEW: Generate a topic-driven search chain for progressive discovery.

        Args:
            query: Original search query
            strategy: Chain generation strategy (breadth_first, depth_first, relevance_ranked, mixed_exploration)
            max_links: Maximum number of chain links to generate

        Returns:
            TopicSearchChain with progressive exploration queries
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        # Convert string strategy to enum
        try:
            chain_strategy = ChainStrategy(strategy)
        except ValueError:
            self.logger.warning(
                f"Unknown strategy '{strategy}', using mixed_exploration"
            )
            chain_strategy = ChainStrategy.MIXED_EXPLORATION

        self.logger.debug(
            "Generating topic search chain",
            query=query,
            strategy=strategy,
            max_links=max_links,
        )

        try:
            topic_chain = await self.hybrid_search.generate_topic_search_chain(
                query=query, strategy=chain_strategy, max_links=max_links
            )

            self.logger.info(
                "Topic chain generation completed",
                query=query,
                chain_length=len(topic_chain.chain_links),
                topics_covered=topic_chain.total_topics_covered,
                discovery_potential=f"{topic_chain.estimated_discovery_potential:.2f}",
            )

            return topic_chain
        except Exception as e:
            self.logger.error(
                "Topic chain generation failed", error=str(e), query=query
            )
            raise

    async def execute_topic_chain(
        self,
        topic_chain: TopicSearchChain,
        results_per_link: int = 3,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> dict[str, list[HybridSearchResult]]:
        """🔥 NEW: Execute searches for all links in a topic chain.

        Args:
            topic_chain: The topic search chain to execute
            results_per_link: Number of results per chain link
            source_types: Optional source type filters
            project_ids: Optional project ID filters

        Returns:
            Dictionary mapping queries to search results
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        self.logger.debug(
            "Executing topic chain search",
            original_query=topic_chain.original_query,
            chain_length=len(topic_chain.chain_links),
            results_per_link=results_per_link,
        )

        try:
            chain_results = await self.hybrid_search.execute_topic_chain_search(
                topic_chain=topic_chain,
                results_per_link=results_per_link,
                source_types=source_types,
                project_ids=project_ids,
            )

            total_results = sum(len(results) for results in chain_results.values())
            self.logger.info(
                "Topic chain execution completed",
                original_query=topic_chain.original_query,
                total_queries=len(chain_results),
                total_results=total_results,
            )

            return chain_results
        except Exception as e:
            self.logger.error("Topic chain execution failed", error=str(e))
            raise

    async def search_with_topic_chain(
        self,
        query: str,
        strategy: str = "mixed_exploration",
        max_links: int = 5,
        results_per_link: int = 3,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> dict[str, list[HybridSearchResult]]:
        """🔥 NEW: Combined method to generate and execute a topic search chain.

        Args:
            query: Original search query
            strategy: Chain generation strategy
            max_links: Maximum chain links
            results_per_link: Results per link
            source_types: Optional source filters
            project_ids: Optional project filters

        Returns:
            Dictionary mapping chain queries to their results
        """
        self.logger.debug(
            "Starting topic chain search workflow",
            query=query,
            strategy=strategy,
            max_links=max_links,
            results_per_link=results_per_link,
        )

        try:
            # Generate topic chain
            topic_chain = await self.generate_topic_chain(
                query=query, strategy=strategy, max_links=max_links
            )

            # Execute the chain
            chain_results = await self.execute_topic_chain(
                topic_chain=topic_chain,
                results_per_link=results_per_link,
                source_types=source_types,
                project_ids=project_ids,
            )

            self.logger.info(
                "Topic chain search workflow completed",
                query=query,
                total_queries=len(chain_results),
                total_results=sum(len(results) for results in chain_results.values()),
                discovery_potential=f"{topic_chain.estimated_discovery_potential:.2f}",
            )

            return chain_results
        except Exception as e:
            self.logger.error(
                "Topic chain search workflow failed", error=str(e), query=query
            )
            raise

    # ============================================================================
    # Dynamic Faceted Search Interface Methods
    # ============================================================================

    async def search_with_facets(
        self,
        query: str,
        limit: int = 5,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
        facet_filters: list[dict] | None = None,
    ) -> dict:
        """
        Perform faceted search with dynamic facet generation.

        Returns search results with generated facets for interactive filtering.

        Args:
            query: Search query
            limit: Maximum number of results to return
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by
            facet_filters: Optional list of facet filters to apply

        Returns:
            Dictionary containing:
            - results: List of search results
            - facets: List of generated facets with counts
            - total_results: Total results before facet filtering
            - filtered_count: Results after facet filtering
            - applied_filters: Currently applied facet filters
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # Convert facet filter dictionaries to FacetFilter objects if provided
            filter_objects = []
            if facet_filters:
                from .enhanced.faceted_search import FacetFilter, FacetType

                for filter_dict in facet_filters:
                    try:
                        facet_type = FacetType(filter_dict["facet_type"])
                    except Exception:
                        self.logger.warning(
                            "Invalid facet_type provided; skipping facet filter",
                            facet_type=str(filter_dict.get("facet_type")),
                        )
                        continue

                    # Validate and normalize values
                    values_raw = filter_dict.get("values")
                    if not values_raw:
                        self.logger.warning(
                            "Missing or empty 'values' for facet filter; skipping",
                            facet_type=facet_type.value,
                        )
                        continue
                    if isinstance(values_raw, (set, tuple)):
                        values = list(values_raw)
                    elif isinstance(values_raw, list):
                        values = values_raw
                    else:
                        values = [values_raw]

                    # Validate operator
                    allowed_operators = {"OR", "AND"}
                    operator = str(filter_dict.get("operator", "OR")).upper()
                    if operator not in allowed_operators:
                        self.logger.warning(
                            "Invalid operator for facet filter; defaulting to 'OR'",
                            operator=str(filter_dict.get("operator")),
                        )
                        operator = "OR"

                    filter_objects.append(
                        FacetFilter(
                            facet_type=facet_type,
                            values=values,
                            operator=operator,
                        )
                    )

            faceted_results = await self.hybrid_search.search_with_facets(
                query=query,
                limit=limit,
                source_types=source_types,
                project_ids=project_ids,
                facet_filters=filter_objects,
                generate_facets=True,
            )

            # Convert to MCP-friendly format
            return {
                "results": faceted_results.results,
                "facets": [
                    {
                        "type": facet.facet_type.value,
                        "name": facet.name,
                        "display_name": facet.display_name,
                        "description": facet.description,
                        "values": [
                            {
                                "value": fv.value,
                                "count": fv.count,
                                "display_name": fv.display_name,
                                "description": fv.description,
                            }
                            for fv in facet.get_top_values(10)
                        ],
                    }
                    for facet in faceted_results.facets
                ],
                "total_results": faceted_results.total_results,
                "filtered_count": faceted_results.filtered_count,
                "applied_filters": [
                    {
                        "facet_type": f.facet_type.value,
                        "values": f.values,
                        "operator": f.operator,
                    }
                    for f in faceted_results.applied_filters
                ],
                "generation_time_ms": faceted_results.generation_time_ms,
            }

        except Exception as e:
            self.logger.error("Faceted search failed", error=str(e), query=query)
            raise

    async def get_facet_suggestions(
        self, query: str, current_filters: list[dict] | None = None, limit: int = 20
    ) -> list[dict]:
        """
        Get facet refinement suggestions based on current search.

        Args:
            query: Current search query
            current_filters: Currently applied facet filters
            limit: Number of results to analyze for suggestions

        Returns:
            List of facet refinement suggestions with impact estimates
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # First get current search results
            current_results = await self.hybrid_search.search(
                query=query, limit=limit, source_types=None, project_ids=None
            )

            # Convert filter dictionaries to FacetFilter objects
            filter_objects = []
            if current_filters:
                from .enhanced.faceted_search import FacetFilter, FacetType

                for filter_dict in current_filters:
                    try:
                        facet_type = FacetType(filter_dict["facet_type"])
                    except Exception:
                        self.logger.warning(
                            "Invalid facet_type provided; skipping facet filter",
                            facet_type=str(filter_dict.get("facet_type")),
                        )
                        continue

                    # Validate and normalize values
                    values_raw = filter_dict.get("values")
                    if not values_raw:
                        self.logger.warning(
                            "Missing or empty 'values' for facet filter; skipping",
                            facet_type=facet_type.value,
                        )
                        continue
                    if isinstance(values_raw, (set, tuple)):
                        values = list(values_raw)
                    elif isinstance(values_raw, list):
                        values = values_raw
                    else:
                        values = [values_raw]

                    # Validate operator
                    allowed_operators = {"OR", "AND"}
                    operator = str(filter_dict.get("operator", "OR")).upper()
                    if operator not in allowed_operators:
                        self.logger.warning(
                            "Invalid operator for facet filter; defaulting to 'OR'",
                            operator=str(filter_dict.get("operator")),
                        )
                        operator = "OR"

                    filter_objects.append(
                        FacetFilter(
                            facet_type=facet_type,
                            values=values,
                            operator=operator,
                        )
                    )

            suggestions = self.hybrid_search.suggest_facet_refinements(
                current_results=current_results, current_filters=filter_objects
            )

            return suggestions

        except Exception as e:
            self.logger.error("Facet suggestions failed", error=str(e), query=query)
            raise

    # Cross-Document Intelligence MCP Interface

    async def analyze_document_relationships(
        self,
        query: str,
        limit: int = 20,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze relationships between documents from search results.

        Args:
            query: Search query to get documents for analysis
            limit: Maximum number of documents to analyze
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by

        Returns:
            Comprehensive cross-document relationship analysis
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # Get documents for analysis
            # Honor default conflict limit from config if caller didn't override
            effective_limit = limit
            config = getattr(self, "config", None)
            if limit is None and config is not None:
                default_limit = getattr(config, "conflict_limit_default", None)
                if isinstance(default_limit, int):
                    effective_limit = default_limit

            documents = await self.hybrid_search.search(
                query=query,
                limit=effective_limit,
                source_types=source_types,
                project_ids=project_ids,
            )

            if len(documents) < 2:
                return {
                    "error": "Need at least 2 documents for relationship analysis",
                    "document_count": len(documents),
                }

            # Perform cross-document analysis
            analysis = await self.hybrid_search.analyze_document_relationships(
                documents
            )

            # Add query metadata
            analysis["query_metadata"] = {
                "original_query": query,
                "document_count": len(documents),
                "source_types": source_types,
                "project_ids": project_ids,
            }

            return analysis

        except Exception as e:
            self.logger.error(
                "Document relationship analysis failed", error=str(e), query=query
            )
            raise

    async def find_similar_documents(
        self,
        target_query: str,
        comparison_query: str,
        similarity_metrics: list[str] | None = None,
        max_similar: int = 5,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find documents similar to a target document.

        Args:
            target_query: Query to find the target document
            comparison_query: Query to get documents to compare against
            similarity_metrics: Similarity metrics to use
            max_similar: Maximum number of similar documents to return
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by

        Returns:
            List of similar documents with similarity scores
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # Get target document (first result from target query)
            target_results = await self.hybrid_search.search(
                query=target_query,
                limit=1,
                source_types=source_types,
                project_ids=project_ids,
            )

            if not target_results:
                return []

            target_document = target_results[0]

            # Get comparison documents
            comparison_documents = await self.hybrid_search.search(
                query=comparison_query,
                limit=20,
                source_types=source_types,
                project_ids=project_ids,
            )

            # Convert string metrics to SimilarityMetric enums with validation
            metrics = None
            if similarity_metrics:
                valid_metrics = []
                for metric in similarity_metrics:
                    try:
                        valid_metrics.append(SimilarityMetric(metric))
                    except (ValueError, TypeError):
                        self.logger.warning(
                            "Invalid similarity metric provided; skipping",
                            metric=str(metric),
                        )
                metrics = valid_metrics if valid_metrics else None

            # Find similar documents
            similar_docs = await self.hybrid_search.find_similar_documents(
                target_document=target_document,
                documents=comparison_documents,
                similarity_metrics=metrics,
                max_similar=max_similar,
            )

            return similar_docs

        except Exception as e:
            self.logger.error("Similar documents search failed", error=str(e))
            raise

    async def detect_document_conflicts(
        self,
        query: str,
        limit: int | None = None,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
        *,
        use_llm: bool | None = None,
        max_llm_pairs: int | None = None,
        overall_timeout_s: float | None = None,
        max_pairs_total: int | None = None,
        text_window_chars: int | None = None,
    ) -> dict[str, Any]:
        """
        Detect conflicts between documents.

        Args:
            query: Search query to get documents for conflict analysis
            limit: Maximum number of documents to analyze
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by

        Returns:
            Conflict analysis with detected conflicts and resolution suggestions
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # Get documents for conflict analysis
            effective_limit = limit
            config = getattr(self, "config", None)
            if limit is None and config is not None:
                default_limit = getattr(config, "conflict_limit_default", None)
                if isinstance(default_limit, int):
                    effective_limit = default_limit

            documents = await self.hybrid_search.search(
                query=query,
                limit=effective_limit,
                source_types=source_types,
                project_ids=project_ids,
            )

            if len(documents) < 2:
                return {
                    "conflicts": [],
                    "resolution_suggestions": [],
                    "message": "Need at least 2 documents for conflict detection",
                    "document_count": len(documents),
                }

            # Detect conflicts with optional per-call overrides applied
            detector = self.hybrid_search.cross_document_engine.conflict_detector
            previous_settings = getattr(detector, "_settings", {}) if hasattr(detector, "_settings") else {}
            call_overrides: dict[str, Any] = {}
            if use_llm is not None:
                call_overrides["conflict_use_llm"] = bool(use_llm)
            if isinstance(max_llm_pairs, int):
                call_overrides["conflict_max_llm_pairs"] = max_llm_pairs
            if isinstance(overall_timeout_s, (int, float)):
                call_overrides["conflict_overall_timeout_s"] = float(overall_timeout_s)
            if isinstance(max_pairs_total, int):
                call_overrides["conflict_max_pairs_total"] = max_pairs_total
            if isinstance(text_window_chars, int):
                call_overrides["conflict_text_window_chars"] = text_window_chars

            try:
                if call_overrides:
                    merged = dict(previous_settings)
                    merged.update(call_overrides)
                    detector._settings = merged  # type: ignore[attr-defined]

                conflicts = await self.hybrid_search.detect_document_conflicts(documents)
            finally:
                # Restore original settings to avoid leaking overrides
                try:
                    detector._settings = previous_settings  # type: ignore[attr-defined]
                except Exception:
                    pass

            # Add query metadata and original documents for formatting
            conflicts["query_metadata"] = {
                "original_query": query,
                "document_count": len(documents),
                "source_types": source_types,
                "project_ids": project_ids,
            }

            # Inject detector runtime stats if available for richer structured output
            try:
                detector = self.hybrid_search.cross_document_engine.conflict_detector
                try:
                    raw_stats = detector._last_stats or {}
                except AttributeError:
                    raw_stats = {}
                
                if raw_stats:
                    # Filter to JSON-safe scalar values only
                    safe_stats = {}
                    for key, value in raw_stats.items():
                        if isinstance(value, (str, int, float, bool)) and not key.startswith('partial_'):
                            safe_stats[key] = value
                    
                    if safe_stats:
                        conflicts["query_metadata"]["detector_stats"] = safe_stats
            except (AttributeError, TypeError) as e:
                self.logger.debug("Failed to access detector stats", error=str(e))

            # Store lightweight, JSON-serializable representations of documents
            # to keep payload minimal and avoid non-serializable objects
            safe_documents: list[dict[str, Any]] = []
            for doc in documents:
                try:
                    document_id = getattr(doc, "document_id", None)
                    # Support either attribute or mapping style access
                    if document_id is None and isinstance(doc, dict):
                        document_id = doc.get("document_id") or doc.get("id")

                    title = None
                    if hasattr(doc, "get_display_title") and callable(
                        getattr(doc, "get_display_title")
                    ):
                        try:
                            title = doc.get_display_title()
                        except Exception:
                            title = None
                    if not title:
                        title = getattr(doc, "source_title", None)
                    if not title and isinstance(doc, dict):
                        title = doc.get("source_title") or doc.get("title")

                    source_type = getattr(doc, "source_type", None)
                    if source_type is None and isinstance(doc, dict):
                        source_type = doc.get("source_type")

                    safe_documents.append(
                        {
                            "document_id": document_id or "",
                            "title": title or "Untitled",
                            "source_type": source_type or "unknown",
                        }
                    )
                except Exception:
                    # Skip malformed entries
                    continue

            conflicts["original_documents"] = safe_documents

            return conflicts

        except Exception as e:
            self.logger.error("Conflict detection failed", error=str(e), query=query)
            raise

    async def find_complementary_content(
        self,
        target_query: str,
        context_query: str,
        max_recommendations: int = 5,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Find content that complements a target document.

        Args:
            target_query: Query to find the target document
            context_query: Query to get contextual documents
            max_recommendations: Maximum number of recommendations
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by

        Returns:
            Dict containing complementary recommendations and target document info
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            self.logger.info(
                f"🔍 Step 1: Searching for target document with query: '{target_query}'"
            )
            # Get target document
            target_results = await self.hybrid_search.search(
                query=target_query,
                limit=1,
                source_types=source_types,
                project_ids=project_ids,
            )

            self.logger.info(f"🎯 Target search returned {len(target_results)} results")
            if not target_results:
                self.logger.warning("No target document found!")
                return {
                    "complementary_recommendations": [],
                    "target_document": None,
                    "context_documents_analyzed": 0,
                }

            target_document = target_results[0]
            self.logger.info(f"🎯 Target document: {target_document.source_title}")

            # Adaptive context limit based on recommendations needed
            context_limit = max(
                max_recommendations * 4, 20
            )  # 4x buffer for better selection
            context_limit = min(context_limit, 100)  # Cap at 100 for performance

            self.logger.info(
                f"🔍 Step 2: Searching for context documents with query: '{context_query}' (limit: {context_limit})"
            )
            # Get context documents with adaptive limit
            context_documents = await self.hybrid_search.search(
                query=context_query,
                limit=context_limit,
                source_types=source_types,
                project_ids=project_ids,
            )

            self.logger.info(
                f"📚 Context search returned {len(context_documents)} documents"
            )

            self.logger.info("🔍 Step 3: Finding complementary content...")
            # Find complementary content
            complementary = await self.hybrid_search.find_complementary_content(
                target_document=target_document,
                documents=context_documents,
                max_recommendations=max_recommendations,
            )

            self.logger.info(
                f"✅ Found {len(complementary)} complementary recommendations"
            )

            # Return structured result with target document info (JSON-serializable)
            target_doc_lightweight = {
                "document_id": getattr(target_document, "document_id", "") or "",
                "title": (
                    target_document.get_display_title()
                    if hasattr(target_document, "get_display_title")
                    else (getattr(target_document, "source_title", None) or "Untitled")
                ),
                "source_type": getattr(target_document, "source_type", "unknown") or "unknown",
            }

            # Map recommendations to JSON-safe dictionaries
            safe_recommendations = []
            for rec in complementary:
                try:
                    doc = rec.get("document") if isinstance(rec, dict) else None
                    doc_id = (
                        getattr(doc, "document_id", None)
                        if doc is not None
                        else None
                    ) or rec.get("document_id")
                    title = (
                        getattr(doc, "source_title", None)
                        if doc is not None
                        else None
                    ) or rec.get("title", "Untitled")
                    safe_recommendations.append(
                        {
                            "document_id": doc_id or "",
                            "title": title or "Untitled",
                            "relevance_score": rec.get("relevance_score", 0.0),
                            "reason": rec.get("recommendation_reason", ""),
                            "strategy": rec.get("strategy", "related"),
                        }
                    )
                except Exception:
                    # Skip malformed entries
                    continue

            return {
                "complementary_recommendations": safe_recommendations,
                "target_document": target_doc_lightweight,
                "context_documents_analyzed": len(context_documents),
            }

        except Exception as e:
            self.logger.error("Complementary content search failed", error=str(e))
            raise

    async def cluster_documents(
        self,
        query: str,
        strategy: str = "mixed_features",
        max_clusters: int = 10,
        min_cluster_size: int = 2,
        limit: int = 25,
        source_types: list[str] | None = None,
        project_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Cluster documents based on similarity and relationships.

        Args:
            query: Search query to get documents for clustering
            strategy: Clustering strategy (mixed_features, entity_based, topic_based, project_based)
            max_clusters: Maximum number of clusters to create
            min_cluster_size: Minimum size for a cluster
            limit: Maximum number of documents to cluster
            source_types: Optional list of source types to filter by
            project_ids: Optional list of project IDs to filter by

        Returns:
            Document clusters with metadata and relationships
        """
        if not self.hybrid_search:
            raise RuntimeError("Search engine not initialized")

        try:
            # Get documents for clustering
            documents = await self.hybrid_search.search(
                query=query,
                limit=limit,
                source_types=source_types,
                project_ids=project_ids,
            )

            if len(documents) < min_cluster_size:
                return {
                    "clusters": [],
                    "clustering_metadata": {
                        "message": f"Need at least {min_cluster_size} documents for clustering",
                        "document_count": len(documents),
                    },
                }

            # Adaptive strategy selection
            if strategy == "adaptive" or strategy == "auto":
                strategy = self._select_optimal_strategy(documents)
                self.logger.info(f"Adaptive strategy selected: {strategy}")

            # Convert strategy string to enum with validation/fallback
            try:
                clustering_strategy = ClusteringStrategy(strategy)
            except (ValueError, TypeError):
                self.logger.warning(
                    f"Unsupported clustering strategy '{strategy}', using 'mixed_features'"
                )
                clustering_strategy = ClusteringStrategy.MIXED_FEATURES

            # Cluster documents
            cluster_results = await self.hybrid_search.cluster_documents(
                documents=documents,
                strategy=clustering_strategy,
                max_clusters=max_clusters,
                min_cluster_size=min_cluster_size,
            )

            # Add query metadata (ensure key exists and is a dict)
            if not isinstance(cluster_results.get("clustering_metadata"), dict):
                cluster_results["clustering_metadata"] = {}
            cluster_results["clustering_metadata"].update(
                {
                    "original_query": query,
                    "source_types": source_types,
                    "project_ids": project_ids,
                }
            )

            return cluster_results

        except Exception as e:
            self.logger.error("Document clustering failed", error=str(e), query=query)
            raise

    def _select_optimal_strategy(self, documents: list) -> str:
        """Analyze document characteristics and select optimal clustering strategy."""
        if not documents:
            return "mixed_features"

        # Analyze document characteristics
        analysis = self._analyze_document_characteristics(documents)

        # Strategy scoring system
        strategy_scores = {
            "entity_based": 0,
            "topic_based": 0,
            "project_based": 0,
            "hierarchical": 0,
            "mixed_features": 0,
        }

        # Score based on entity richness
        if analysis["entity_richness"] > 0.7:
            strategy_scores["entity_based"] += 3
            strategy_scores["mixed_features"] += 1
        elif analysis["entity_richness"] > 0.4:
            strategy_scores["entity_based"] += 1
            strategy_scores["mixed_features"] += 2

        # Score based on topic clarity
        if analysis["topic_clarity"] > 0.7:
            strategy_scores["topic_based"] += 3
            strategy_scores["mixed_features"] += 1
        elif analysis["topic_clarity"] > 0.4:
            strategy_scores["topic_based"] += 1
            strategy_scores["mixed_features"] += 2

        # Score based on project distribution
        if analysis["project_distribution"] > 0.6:
            strategy_scores["project_based"] += 3
        elif analysis["project_distribution"] > 0.3:
            strategy_scores["project_based"] += 1
            strategy_scores["mixed_features"] += 1

        # Score based on hierarchical structure
        if analysis["hierarchical_structure"] > 0.6:
            strategy_scores["hierarchical"] += 3
        elif analysis["hierarchical_structure"] > 0.3:
            strategy_scores["hierarchical"] += 1
            strategy_scores["mixed_features"] += 1

        # Score based on source diversity
        if analysis["source_diversity"] > 0.7:
            strategy_scores["mixed_features"] += 2

        # Bonus for mixed_features as a safe default
        strategy_scores["mixed_features"] += 1

        # Select strategy with highest score
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]

        self.logger.info(f"Strategy analysis: {analysis}")
        self.logger.info(f"Strategy scores: {strategy_scores}")
        self.logger.info(f"Selected strategy: {best_strategy}")

        # Validate against ClusteringStrategy enum; fallback to safe default
        try:
            _ = ClusteringStrategy(best_strategy)
        except Exception:
            self.logger.warning(
                f"Unsupported clustering strategy '{best_strategy}', falling back to 'mixed_features'"
            )
            best_strategy = "mixed_features"

        return best_strategy

    def _analyze_document_characteristics(self, documents: list) -> dict[str, float]:
        """Analyze characteristics of documents to inform strategy selection."""
        if not documents:
            return {
                "entity_richness": 0,
                "topic_clarity": 0,
                "project_distribution": 0,
                "hierarchical_structure": 0,
                "source_diversity": 0,
            }

        # Entity analysis
        entity_counts = []
        for doc in documents:
            entities = getattr(doc, "entities", []) or []
            entity_count = len(entities)
            entity_counts.append(entity_count)

        avg_entities = sum(entity_counts) / len(entity_counts) if entity_counts else 0
        entity_richness = min(
            1.0, avg_entities / 5.0
        )  # Normalize to 0-1, assuming 5+ entities is rich

        # Topic analysis
        topic_counts = []
        for doc in documents:
            topics = getattr(doc, "topics", []) or []
            topic_count = len(topics)
            topic_counts.append(topic_count)

        avg_topics = sum(topic_counts) / len(topic_counts) if topic_counts else 0
        topic_clarity = min(
            1.0, avg_topics / 3.0
        )  # Normalize to 0-1, assuming 3+ topics is clear

        # Project distribution analysis
        project_ids = [getattr(doc, "project_id", None) for doc in documents]
        unique_projects = len({p for p in project_ids if p})
        total_docs = len(documents)

        # High project distribution means documents are well-distributed across projects
        if unique_projects > 1:
            project_distribution = min(1.0, unique_projects / (total_docs * 0.5))
        else:
            project_distribution = 0

        # Hierarchical structure analysis
        breadcrumb_counts = []
        for doc in documents:
            breadcrumb = getattr(doc, "breadcrumb_text", "")
            if breadcrumb:
                depth = len(breadcrumb.split(" > "))
                breadcrumb_counts.append(depth)

        if breadcrumb_counts:
            avg_depth = sum(breadcrumb_counts) / len(breadcrumb_counts)
            hierarchical_structure = min(
                1.0, (avg_depth - 1) / 3.0
            )  # Normalize: depth 1 = 0, depth 4+ = 1
        else:
            hierarchical_structure = 0

        # Source diversity analysis
        source_types = [getattr(doc, "source_type", "") for doc in documents]
        unique_sources = len(set(source_types))
        source_diversity = min(
            1.0, unique_sources / 4.0
        )  # Normalize: 4+ source types = max diversity

        return {
            "entity_richness": entity_richness,
            "topic_clarity": topic_clarity,
            "project_distribution": project_distribution,
            "hierarchical_structure": hierarchical_structure,
            "source_diversity": source_diversity,
        }
