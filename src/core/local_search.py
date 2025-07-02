#!/usr/bin/env python3
"""
Local Semantic Search Module
Provides semantic search functionality based on local data
"""

import os
import time
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import calculate_similarity_score, safe_str

class LocalSearch:
    """Local Semantic Search Class"""
    
    def __init__(self):
        """Initialize local search"""
        self.model = None
        self.index = None
        self.dataframe = None
        self._load_local_data()
    
    def _load_local_data(self):
        """Load local data"""
        try:
            # Load CSV data
            self.dataframe = pd.read_csv(config.data_file)
            self.dataframe['combined_text'] = (
                self.dataframe['Product Name'].fillna('') + " - " + 
                self.dataframe['Description'].fillna('')
            )
            logger.info(f"✅ Loaded {len(self.dataframe)} local products")
            
            # Load model
            self.model = SentenceTransformer(config.model_name, device='cpu')
            logger.info("✅ Semantic search model loaded successfully")
            
            # Load or create index
            self._load_or_create_index()
            
        except Exception as e:
            logger.error(f"❌ Local data loading failed: {e}")
            self.dataframe = None
            self.model = None
            self.index = None
    
    def _load_or_create_index(self):
        """Load or create FAISS index"""
        try:
            if os.path.exists(config.embeddings_file) and os.path.exists(config.index_file):
                logger.info("📂 Loading cached embeddings and index...")
                embeddings = np.load(config.embeddings_file)
                self.index = faiss.read_index(config.index_file)
                
                # Validate index dimension match
                current_dimension = self.model.get_sentence_embedding_dimension()
                if self.index.d != current_dimension:
                    logger.warning(f"⚠️ Index dimension mismatch (cache: {self.index.d}, model: {current_dimension}), recreating...")
                    self._create_new_index()
                else:
                    logger.info("✅ Cache loaded successfully")
            else:
                self._create_new_index()
                
        except Exception as e:
            logger.error(f"❌ Index loading failed: {e}")
            self.index = None
    
    def _create_new_index(self):
        """Create new index"""
        logger.info("🔄 Generating new embeddings and index...")
        texts = self.dataframe['combined_text'].tolist()
        embeddings = self.model.encode(texts, show_progress_bar=True, device='cpu')
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # Save cache
        os.makedirs(os.path.dirname(config.embeddings_file), exist_ok=True)
        os.makedirs(os.path.dirname(config.index_file), exist_ok=True)
        np.save(config.embeddings_file, embeddings)
        faiss.write_index(self.index, config.index_file)
        logger.info("✅ Index created and cached successfully")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Execute local semantic search"""
        if (self.model is None or self.index is None or 
            self.dataframe is None or self.dataframe.empty):
            logger.error("❌ Local search not available")
            return []
        
        logger.local_search_start(query)
        start_time = time.time()
        
        try:
            query_vector = self.model.encode([query], show_progress_bar=False, device='cpu')
            distances, indices = self.index.search(query_vector, top_k)
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                product = self.dataframe.iloc[idx].to_dict()
                product['similarity_score'] = calculate_similarity_score(dist)
                product['source'] = 'local'
                product['search_query'] = query
                product['search_time'] = time.time() - start_time
                results.append(product)
            
            duration = time.time() - start_time
            logger.local_search_complete(query, len(results), duration)
            return results
            
        except Exception as e:
            logger.error(f"❌ Local search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_available(self) -> bool:
        """Check if local search is available"""
        return (self.model is not None and 
                self.index is not None and 
                self.dataframe is not None and 
                not self.dataframe.empty)
    
    def get_product_count(self) -> int:
        """Get product count"""
        if self.dataframe is not None:
            return len(self.dataframe)
        return 0 