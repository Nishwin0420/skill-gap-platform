"""
Graph Machine Learning Engine (Node2Vec/NetworkX)
=================================================
Builds a Knowledge Graph out of the skill ontology.
Calculates shortest paths between known skills and missing skills
to generate mathematically optimal "Bridge Skill" recommendations.

Generates: backend/data/trained_models/skill_graph.pkl
"""

import json
import pickle
import networkx as nx
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = BASE_DIR / "data" / "skill_ontology.json"
MODEL_PATH = BASE_DIR / "data" / "trained_models" / "skill_graph.pkl"

class SkillGraphEngine:
    def __init__(self, graph):
        self.graph = graph
        
    def recommend_bridge_skills(self, user_skills, missing_skills, top_n=3):
        """
        Given the skills a user HAS and the skills they NEED,
        find the shortest path in the graph to recommend intermediate skills.
        """
        user_nodes = [s.lower() for s in user_skills if s.lower() in self.graph.nodes]
        missing_nodes = [s.lower() for s in missing_skills if s.lower() in self.graph.nodes]
        
        if not user_nodes or not missing_nodes:
            return []
            
        recommendations = {}
        
        for target in missing_nodes:
            for source in user_nodes:
                try:
                    # Find shortest path from a known skill to the missing skill
                    path = nx.shortest_path(self.graph, source=source, target=target)
                    # Bridge skills are nodes in between source and target
                    bridges = path[1:-1] 
                    for bridge in bridges:
                        if bridge not in user_nodes and bridge not in missing_nodes:
                            recommendations[bridge] = recommendations.get(bridge, 0) + 1
                except nx.NetworkXNoPath:
                    continue
                    
        # Sort bridge skills by how many paths they appear in (Centrality)
        sorted_bridges = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [b[0] for b in sorted_bridges[:top_n]]


def build_graph():
    print("=" * 50)
    print("[GRAPH] Building Skill Knowledge Graph (NetworkX)")
    print("=" * 50)
    
    if not ONTOLOGY_PATH.exists():
        print(f"ERROR: Ontology not found at {ONTOLOGY_PATH}")
        return
        
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        ontology = json.load(f)
        
    G = nx.Graph()
    
    # Add nodes and edges
    for cat_data in ontology.get("categories", {}).values():
        for key, info in cat_data.get("skills", {}).items():
            canonical = info.get("canonical", key).lower()
            G.add_node(canonical, category=info.get("category", "general"))
            
            # Link prerequisites (edges)
            for prereq in info.get("prerequisites", []):
                prereq_lower = prereq.lower()
                G.add_node(prereq_lower)  # Ensure prereq node exists
                G.add_edge(prereq_lower, canonical, weight=1.0)
                
            # Connect skills in the same category (weak ties)
            for other_key in cat_data.get("skills", {}).keys():
                other_canonical = cat_data["skills"][other_key].get("canonical", other_key).lower()
                if canonical != other_canonical:
                    # Only add weak tie if edge doesn't already exist
                    if not G.has_edge(canonical, other_canonical):
                        G.add_edge(canonical, other_canonical, weight=5.0) # Higher weight = 'longer' path
                        
    print(f"[OK] Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    engine = SkillGraphEngine(G)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(engine, f)
        
    print(f"[OK] Graph Engine saved to: {MODEL_PATH}")

def get_bridge_recommendations(user_skills, missing_skills):
    if not MODEL_PATH.exists():
        return []
        
    with open(MODEL_PATH, "rb") as f:
        engine = pickle.load(f)
        
    return engine.recommend_bridge_skills(user_skills, missing_skills)

if __name__ == "__main__":
    build_graph()
