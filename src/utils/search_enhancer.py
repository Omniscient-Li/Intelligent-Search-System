#!/usr/bin/env python3
"""
Search Enhancer Utility
Provides fuzzy search, synonym expansion, and scene recognition for product search
"""

import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SearchContext:
    original_query: str
    expanded_queries: List[str]
    scene: str
    product_type: str
    requirements: List[str]
    synonyms_used: List[str]

class SearchEnhancer:
    """Fuzzy search and query expansion utility"""
    def __init__(self):
        self._init_synonyms()
        self._init_scenes()
        self._init_product_types()

    def _init_synonyms(self):
        self.synonyms = {
            'handle': ['pull', 'knob', 'grip', 'drawer pull', 'cabinet pull'],
            'pull': ['handle', 'knob', 'grip', 'drawer pull', 'cabinet pull'],
            'knob': ['handle', 'pull', 'grip', 'door knob', 'cabinet knob'],
            'cabinet': ['cupboard', 'storage', 'wardrobe'],
            'drawer': ['drawer', 'pull-out', 'slide-out'],
            'door': ['door', 'entry', 'entrance'],
            'kitchen': ['kitchen', 'cooking', 'culinary'],
            'bathroom': ['bathroom', 'washroom', 'toilet'],
            'office': ['office', 'work', 'business'],
            'brass': ['brass', 'bronze', 'gold', 'metallic'],
            'stainless': ['stainless steel', 'steel', 'metal'],
            'modern': ['contemporary', 'sleek', 'minimalist'],
        }

    def _init_scenes(self):
        self.scenes = {
            'kitchen': {
                'keywords': ['kitchen', 'cooking', 'culinary'],
                'requirements': ['oil-resistant', 'easy to clean', 'durable', 'heat-resistant'],
            },
            'bathroom': {
                'keywords': ['bathroom', 'washroom', 'toilet', 'shower'],
                'requirements': ['waterproof', 'rustproof', 'aesthetic', 'durable'],
            },
            'office': {
                'keywords': ['office', 'work', 'business', 'desk'],
                'requirements': ['professional', 'durable', 'practical', 'aesthetic'],
            }
        }

    def _init_product_types(self):
        self.product_types = {
            'drawer_pull': ['drawer pull', 'drawer handle', 'drawer knob'],
            'cabinet_handle': ['cabinet handle', 'cabinet pull', 'cabinet knob'],
            'door_handle': ['door handle', 'door knob', 'door pull'],
            'knob': ['knob', 'round handle', 'circular pull'],
        }

    def enhance_query(self, query: str) -> SearchContext:
        norm_query = self._normalize_query(query)
        scene = self._detect_scene(norm_query)
        product_type = self._detect_product_type(norm_query)
        synonyms_used = self._generate_synonyms(norm_query)
        expanded_queries = self._expand_queries(norm_query, synonyms_used, scene)
        requirements = self._extract_requirements(norm_query, scene)
        return SearchContext(
            original_query=query,
            expanded_queries=expanded_queries,
            scene=scene,
            product_type=product_type,
            requirements=requirements,
            synonyms_used=synonyms_used
        )

    def _normalize_query(self, query: str) -> str:
        query = query.lower().strip()
        query = re.sub(r'\s+', ' ', query)
        return query

    def _detect_scene(self, query: str) -> str:
        for scene, info in self.scenes.items():
            for keyword in info['keywords']:
                if keyword in query:
                    return scene
        return 'kitchen'

    def _detect_product_type(self, query: str) -> str:
        for ptype, keywords in self.product_types.items():
            for keyword in keywords:
                if keyword in query:
                    return ptype
        return 'drawer_pull'

    def _generate_synonyms(self, query: str) -> List[str]:
        synonyms_used = []
        for word in query.split():
            if word in self.synonyms:
                synonyms_used.extend(self.synonyms[word])
        return list(set(synonyms_used))

    def _expand_queries(self, query: str, synonyms: List[str], scene: str) -> List[str]:
        expanded = [query]
        for synonym in synonyms[:5]:
            for word in query.split():
                if word in self.synonyms:
                    for syn in self.synonyms[word][:2]:
                        new_query = query.replace(word, syn)
                        if new_query not in expanded:
                            expanded.append(new_query)
        for keyword in self.scenes.get(scene, {}).get('keywords', [])[:2]:
            scene_query = f"{query} {keyword}"
            if scene_query not in expanded:
                expanded.append(scene_query)
        return expanded[:10]

    def _extract_requirements(self, query: str, scene: str) -> List[str]:
        reqs = list(self.scenes.get(scene, {}).get('requirements', []))
        if 'waterproof' in query:
            reqs.append('waterproof')
        if 'rust' in query:
            reqs.append('rustproof')
        if 'aesthetic' in query:
            reqs.append('aesthetic')
        if 'durable' in query:
            reqs.append('durable')
        if 'easy clean' in query:
            reqs.append('easy to clean')
        return list(set(reqs)) 