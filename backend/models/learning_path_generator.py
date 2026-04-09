"""
Learning Path Generator Module
================================
Generates personalized learning paths using DAG-based prerequisite ordering.
Uses networkx for topological sorting and graph algorithms.

Features:
    - Directed Acyclic Graph (DAG) of skill prerequisites
    - Topological sort for optimal learning order
    - Difficulty progression (Beginner → Intermediate → Advanced)
    - Estimated time per skill
    - Market justification for each recommendation
    - Curated learning resources

References:
    - Zhang & Liu (2024) — AI-Driven Career Recommendation Systems
"""

import networkx as nx
from backend.nlp.skill_normalizer import get_normalizer
from backend.models.market_analyzer import get_market_analyzer


class LearningPathGenerator:
    """
    Generates personalized learning paths using graph-based algorithms.
    """

    def __init__(self):
        self.normalizer = get_normalizer()
        self.market = get_market_analyzer()
        self.skill_graph = self._build_skill_graph()

    def _build_skill_graph(self):
        """
        Build a Directed Acyclic Graph (DAG) from skill prerequisites.
        Edges: prerequisite → skill (must learn prereq before skill)
        """
        G = nx.DiGraph()

        for skill_name in self.normalizer.get_all_canonical_skills():
            G.add_node(skill_name)
            prereqs = self.normalizer.get_skill_prerequisites(skill_name)
            for prereq in prereqs:
                if prereq in self.normalizer.skill_details:
                    G.add_edge(prereq, skill_name)

        return G

    def generate_path(self, missing_skills, user_skills=None, target_role=None):
        """
        Generate an optimal learning path for missing skills.

        Args:
            missing_skills: List of skills the user needs to learn
            user_skills: List of skills the user already has
            target_role: Target job role (for context)

        Returns:
            List of learning steps in optimal order
        """
        if not missing_skills:
            return []

        user_skills = set(user_skills or [])
        market_scores = self.market.get_skill_demand_scores()

        # Step 1: Build subgraph of relevant skills + prerequisites
        relevant_skills = set(missing_skills)
        for skill in missing_skills:
            prereqs = self._get_all_prerequisites(skill)
            # Only include prereqs that user doesn't already have
            for p in prereqs:
                if p not in user_skills:
                    relevant_skills.add(p)

        # Step 2: Topological sort for optimal order
        subgraph = self.skill_graph.subgraph(
            [s for s in relevant_skills if s in self.skill_graph]
        )

        try:
            ordered_skills = list(nx.topological_sort(subgraph))
        except nx.NetworkXError:
            # If cycle exists, fallback to difficulty-based ordering
            ordered_skills = sorted(
                relevant_skills,
                key=lambda s: {"beginner": 0, "intermediate": 1, "advanced": 2}.get(
                    self.normalizer.get_skill_difficulty(s), 1
                )
            )

        # Step 3: Build learning path with details
        path = []
        cumulative_hours = 0

        for i, skill in enumerate(ordered_skills):
            if skill in user_skills:
                continue  # Skip skills user already knows

            info = self.normalizer.get_skill_info(skill) or {}
            hours = self.normalizer.get_estimated_hours(skill)
            difficulty = self.normalizer.get_skill_difficulty(skill)
            market_weight = market_scores.get(skill, self.normalizer.get_market_weight(skill))
            category = self.normalizer.get_skill_category(skill)
            prereqs = self.normalizer.get_skill_prerequisites(skill)

            cumulative_hours += hours

            # Generate resource links
            resources = self._generate_resources(skill)

            # Market justification
            justification = self._generate_market_justification(
                skill, market_weight, target_role
            )

            step = {
                "step": len(path) + 1,
                "skill": skill,
                "category": category,
                "difficulty": difficulty,
                "estimated_hours": hours,
                "cumulative_hours": cumulative_hours,
                "estimated_weeks": round(hours / 15, 1),  # ~15hrs/week
                "market_demand_score": round(market_weight, 1),
                "prerequisites": prereqs,
                "prerequisites_met": all(p in user_skills for p in prereqs),
                "is_critical_gap": skill in missing_skills,
                "resources": resources,
                "market_justification": justification
            }

            path.append(step)

        return path

    def _get_all_prerequisites(self, skill, visited=None):
        """Recursively get all prerequisites including transitive deps."""
        if visited is None:
            visited = set()

        if skill in visited:
            return set()

        visited.add(skill)
        direct_prereqs = self.normalizer.get_skill_prerequisites(skill)
        all_prereqs = set(direct_prereqs)

        for prereq in direct_prereqs:
            all_prereqs.update(self._get_all_prerequisites(prereq, visited))

        return all_prereqs

    def _generate_resources(self, skill):
        """Generate curated learning resource links for a skill."""
        skill_query = skill.replace(" ", "+")
        return {
            "course": f"https://www.coursera.org/search?query={skill_query}",
            "youtube": f"https://www.youtube.com/results?search_query={skill_query}+tutorial",
            "documentation": f"https://www.google.com/search?q={skill_query}+official+documentation",
            "practice": f"https://www.hackerrank.com/domains?q={skill_query}"
        }

    def _generate_market_justification(self, skill, market_weight, target_role=None):
        """Generate market-backed justification for learning a skill."""
        demand_level = (
            "Very High" if market_weight >= 8 else
            "High" if market_weight >= 6 else
            "Medium" if market_weight >= 4 else
            "Low"
        )

        justification = f"{skill.title()} has {demand_level.lower()} market demand (score: {market_weight}/10)."

        if target_role:
            role_analysis = self.market.get_role_analysis(target_role)
            top_skills = [s["skill"] for s in role_analysis.get("top_skills", [])]
            if skill in top_skills:
                justification += f" It's a top required skill for {target_role} roles."

        return justification

    def get_path_summary(self, path):
        """Get summary statistics for a learning path."""
        if not path:
            return {}

        total_hours = sum(step["estimated_hours"] for step in path)
        difficulties = [step["difficulty"] for step in path]

        return {
            "total_skills": len(path),
            "total_estimated_hours": total_hours,
            "total_estimated_weeks": round(total_hours / 15, 1),
            "difficulty_breakdown": {
                "beginner": difficulties.count("beginner"),
                "intermediate": difficulties.count("intermediate"),
                "advanced": difficulties.count("advanced")
            },
            "categories_covered": list(set(step["category"] for step in path)),
            "critical_gaps": sum(1 for step in path if step["is_critical_gap"]),
            "prerequisite_steps": sum(1 for step in path if not step["is_critical_gap"])
        }

    def generate_timeline(self, path, hours_per_week=15):
        """
        Generate a week-by-week timeline from the learning path.
        """
        timeline = []
        current_week = 1
        accumulated_hours = 0

        for step in path:
            hours = step["estimated_hours"]
            start_week = current_week
            weeks_needed = max(1, round(hours / hours_per_week))
            end_week = start_week + weeks_needed - 1

            timeline.append({
                "skill": step["skill"],
                "start_week": start_week,
                "end_week": end_week,
                "hours": hours,
                "difficulty": step["difficulty"]
            })

            current_week = end_week + 1

        return timeline


# ====================================
# SINGLETON
# ====================================
_generator = None

def get_path_generator():
    global _generator
    if _generator is None:
        _generator = LearningPathGenerator()
    return _generator
