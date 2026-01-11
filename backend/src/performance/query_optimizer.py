from loguru import logger
import time
from typing import List, Dict, Any, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class QueryOptimizer:
    """
    Utility for analyzing and optimizing Cypher queries in Memgraph/Neo4j.
    Focuses on maintaining the sub-300ms latency target.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter
        self.latency_threshold_ms = 300.0

    def explain_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes EXPLAIN on a Cypher query to get the execution plan without running it.
        """
        explain_query = f"EXPLAIN {query}"
        try:
            return self.adapter.run_query(explain_query, parameters)
        except Exception as e:
            logger.error(f"Failed to explain query: {e}")
            return []

    def profile_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes PROFILE on a Cypher query to get detailed execution statistics.
        Note: This actually runs the query.
        """
        profile_query = f"PROFILE {query}"
        start_time = time.time()
        try:
            results = self.adapter.run_query(profile_query, parameters)
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                "results": results,
                "duration_ms": duration_ms,
                "is_slow": duration_ms > self.latency_threshold_ms
            }
        except Exception as e:
            logger.error(f"Failed to profile query: {e}")
            return {"error": str(e)}

    def analyze_slow_queries(self, queries: List[str], sample_params: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Analyzes a set of queries and identifies those exceeding the latency threshold.
        """
        analysis_report = []
        for i, query in enumerate(queries):
            params = sample_params[i] if sample_params and i < len(sample_params) else {}
            profile = self.profile_query(query, params)
            
            if profile.get("is_slow"):
                # Run EXPLAIN to get the plan for the slow query
                plan = self.explain_query(query, params)
                analysis_report.append({
                    "query": query,
                    "duration_ms": profile["duration_ms"],
                    "plan": plan,
                    "recommendations": self._generate_recommendations(plan)
                })
        
        return analysis_report

    def _generate_recommendations(self, plan: List[Dict[str, Any]]) -> List[str]:
        """
        Generates basic optimization recommendations based on the execution plan.
        """
        recommendations = []
        plan_str = str(plan).lower()
        
        if "allnodescan" in plan_str:
            recommendations.append("Full node scan detected. Consider adding an index on the filtering property.")
        if "expandall" in plan_str:
            recommendations.append("Large expansion detected. Consider limiting hops or adding relationship type filters.")
        if "cartesianproduct" in plan_str:
            recommendations.append("Cartesian product detected. Check for missing joins or MATCH patterns.")
            
        if not recommendations:
            recommendations.append("No obvious issues found in plan. Consider index tuning or hardware scaling.")
            
        return recommendations

