"""
Trend analysis module for art-technology knowledge mining.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from loguru import logger

from .embed_store import EmbeddingStore


@dataclass
class TrendData:
    """Represents trend analysis data."""
    time_period: str
    count: int
    trend_slope: Optional[float] = None
    trend_significance: Optional[float] = None
    r_squared: Optional[float] = None


@dataclass
class CooccurrenceData:
    """Represents tag co-occurrence data."""
    tag1: str
    tag2: str
    count: int
    correlation: Optional[float] = None


class TrendAnalyzer:
    """Analyzes trends in art-technology content over time."""
    
    def __init__(self, embedding_store: EmbeddingStore):
        self.embedding_store = embedding_store
        self.date_formats = [
            '%Y-%m-%d',
            '%Y-%m',
            '%Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
    
    def analyze_temporal_trends(self, 
                               facet: str = "all",
                               from_date: Optional[str] = None,
                               to_date: Optional[str] = None,
                               granularity: str = "year") -> List[TrendData]:
        """Analyze temporal trends for a specific facet."""
        try:
            # Get all documents
            all_data = self.embedding_store.collection.get()
            
            if not all_data['documents']:
                return []
            
            # Filter by date range if specified
            filtered_data = self._filter_by_date_range(
                all_data, from_date, to_date
            )
            
            # Group by time period
            time_groups = self._group_by_time_period(
                filtered_data, granularity
            )
            
            # Calculate trends
            trend_data = []
            for period, documents in time_groups.items():
                count = len(documents)
                
                # Calculate trend slope if we have enough data points
                if len(time_groups) >= 3:
                    slope, significance, r_squared = self._calculate_trend_slope(
                        time_groups, period
                    )
                else:
                    slope, significance, r_squared = None, None, None
                
                trend_data.append(TrendData(
                    time_period=period,
                    count=count,
                    trend_slope=slope,
                    trend_significance=significance,
                    r_squared=r_squared
                ))
            
            # Sort by time period
            trend_data.sort(key=lambda x: x.time_period)
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Temporal trend analysis failed: {e}")
            return []
    
    def analyze_tag_cooccurrence(self, 
                                min_cooccurrence: int = 2) -> List[CooccurrenceData]:
        """Analyze co-occurrence of tags/terms."""
        try:
            # Get all documents
            all_data = self.embedding_store.collection.get()
            
            if not all_data['documents']:
                return []
            
            # Extract tags from documents
            tag_sets = []
            for doc in all_data['documents']:
                tags = self._extract_tags(doc)
                if tags:
                    tag_sets.append(set(tags))
            
            # Calculate co-occurrence matrix
            cooccurrence_matrix = defaultdict(int)
            tag_counts = Counter()
            
            for tag_set in tag_sets:
                for tag in tag_set:
                    tag_counts[tag] += 1
                
                # Count co-occurrences
                tag_list = list(tag_set)
                for i in range(len(tag_list)):
                    for j in range(i + 1, len(tag_list)):
                        pair = tuple(sorted([tag_list[i], tag_list[j]]))
                        cooccurrence_matrix[pair] += 1
            
            # Create co-occurrence data
            cooccurrence_data = []
            for (tag1, tag2), count in cooccurrence_matrix.items():
                if count >= min_cooccurrence:
                    # Calculate correlation (simplified)
                    correlation = self._calculate_correlation(
                        tag_counts[tag1], tag_counts[tag2], count, len(tag_sets)
                    )
                    
                    cooccurrence_data.append(CooccurrenceData(
                        tag1=tag1,
                        tag2=tag2,
                        count=count,
                        correlation=correlation
                    ))
            
            # Sort by count
            cooccurrence_data.sort(key=lambda x: x.count, reverse=True)
            
            return cooccurrence_data
            
        except Exception as e:
            logger.error(f"Tag co-occurrence analysis failed: {e}")
            return []
    
    def analyze_technology_trends(self) -> Dict[str, List[TrendData]]:
        """Analyze trends for specific technology categories."""
        technology_categories = {
            'AI': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
            'AR_VR': ['augmented reality', 'virtual reality', 'AR', 'VR'],
            'Robotics': ['robotics', 'robot', 'automation'],
            'Generative': ['generative', 'algorithmic', 'procedural'],
            'HCI': ['human computer interaction', 'interface', 'interaction'],
            'Fabrication': ['3D printing', 'laser cutting', 'CNC', 'fabrication']
        }
        
        trends_by_category = {}
        
        for category, terms in technology_categories.items():
            # Filter documents containing these terms
            filtered_data = self._filter_by_terms(terms)
            
            if filtered_data:
                # Analyze trends for this category
                trend_data = self._analyze_category_trends(filtered_data)
                trends_by_category[category] = trend_data
        
        return trends_by_category
    
    def _filter_by_date_range(self, 
                            data: Dict, 
                            from_date: Optional[str], 
                            to_date: Optional[str]) -> Dict:
        """Filter data by date range."""
        if not from_date and not to_date:
            return data
        
        filtered_documents = []
        filtered_metadatas = []
        filtered_ids = []
        
        for i, metadata in enumerate(data['metadatas']):
            publish_date = metadata.get('publish_date')
            if not publish_date:
                continue
            
            # Parse date
            parsed_date = self._parse_date(publish_date)
            if not parsed_date:
                continue
            
            # Check date range
            if from_date:
                from_parsed = self._parse_date(from_date)
                if from_parsed and parsed_date < from_parsed:
                    continue
            
            if to_date:
                to_parsed = self._parse_date(to_date)
                if to_parsed and parsed_date > to_parsed:
                    continue
            
            filtered_documents.append(data['documents'][i])
            filtered_metadatas.append(metadata)
            filtered_ids.append(data['ids'][i])
        
        return {
            'documents': filtered_documents,
            'metadatas': filtered_metadatas,
            'ids': filtered_ids
        }
    
    def _group_by_time_period(self, 
                            data: Dict, 
                            granularity: str) -> Dict[str, List[Dict]]:
        """Group documents by time period."""
        groups = defaultdict(list)
        
        for i, metadata in enumerate(data['metadatas']):
            publish_date = metadata.get('publish_date')
            if not publish_date:
                continue
            
            parsed_date = self._parse_date(publish_date)
            if not parsed_date:
                continue
            
            # Determine time period
            if granularity == "year":
                period = parsed_date.strftime('%Y')
            elif granularity == "month":
                period = parsed_date.strftime('%Y-%m')
            elif granularity == "quarter":
                year = parsed_date.year
                quarter = (parsed_date.month - 1) // 3 + 1
                period = f"{year}-Q{quarter}"
            else:
                period = parsed_date.strftime('%Y-%m-%d')
            
            groups[period].append({
                'document': data['documents'][i],
                'metadata': metadata,
                'id': data['ids'][i]
            })
        
        return dict(groups)
    
    def _calculate_trend_slope(self, 
                             time_groups: Dict[str, List[Dict]], 
                             current_period: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate trend slope using linear regression."""
        try:
            # Prepare data for regression
            periods = sorted(time_groups.keys())
            counts = [len(time_groups[period]) for period in periods]
            
            if len(periods) < 3:
                return None, None, None
            
            # Convert periods to numeric values
            period_nums = []
            for period in periods:
                try:
                    if '-' in period:
                        year, month = period.split('-')
                        period_nums.append(int(year) * 12 + int(month))
                    else:
                        period_nums.append(int(period))
                except:
                    period_nums.append(len(period_nums))
            
            # Fit linear regression
            X = np.array(period_nums).reshape(-1, 1)
            y = np.array(counts)
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            r_squared = r2_score(y, model.predict(X))
            
            # Calculate significance (simplified)
            significance = self._calculate_significance(X, y, slope)
            
            return slope, significance, r_squared
            
        except Exception as e:
            logger.error(f"Trend slope calculation failed: {e}")
            return None, None, None
    
    def _calculate_significance(self, X: np.ndarray, y: np.ndarray, slope: float) -> float:
        """Calculate statistical significance of trend."""
        try:
            # Simple significance calculation
            n = len(y)
            if n < 3:
                return 0.0
            
            # Calculate standard error
            y_pred = slope * X.flatten()
            residuals = y - y_pred
            mse = np.mean(residuals ** 2)
            
            # Simplified p-value calculation
            if mse == 0:
                return 1.0
            
            t_stat = slope / np.sqrt(mse / n)
            p_value = 2 * (1 - self._t_cdf(abs(t_stat), n - 2))
            
            return max(0.0, min(1.0, p_value))
            
        except:
            return 0.0
    
    def _t_cdf(self, t: float, df: int) -> float:
        """Approximate t-distribution CDF."""
        # Simplified approximation
        if df > 30:
            return 0.5 + 0.5 * np.tanh(t / 2)
        else:
            return 0.5 + 0.5 * np.tanh(t / (2 + df / 10))
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using multiple formats."""
        if not date_str:
            return None
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Try parsing with pandas
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except:
            pass
        
        return None
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text."""
        # Simple tag extraction based on common art-tech terms
        art_tech_terms = [
            'artificial intelligence', 'machine learning', 'computer vision',
            'robotics', 'augmented reality', 'virtual reality', 'AR', 'VR',
            'AI', 'ML', 'algorithm', 'software', 'hardware', 'sensor',
            'interface', 'interaction', 'digital', 'computational',
            'automation', 'data', 'neural network', 'deep learning',
            'computer graphics', '3D printing', 'laser cutting', 'CNC',
            'microcontroller', 'Arduino', 'Raspberry Pi', 'IoT',
            'blockchain', 'NFT', 'cryptocurrency', 'haptic',
            'projection', 'mapping', 'tracking', 'recognition',
            'generation', 'synthesis', 'art', 'artist', 'artwork',
            'exhibition', 'gallery', 'museum', 'installation',
            'sculpture', 'painting', 'drawing', 'photography',
            'video', 'performance', 'creative', 'aesthetic',
            'visual', 'artistic', 'design', 'craft', 'culture',
            'heritage', 'collection', 'curator', 'artistic practice',
            'contemporary art', 'digital art', 'media art',
            'new media', 'interactive art', 'generative art'
        ]
        
        text_lower = text.lower()
        found_tags = []
        
        for term in art_tech_terms:
            if term.lower() in text_lower:
                found_tags.append(term)
        
        return found_tags
    
    def _filter_by_terms(self, terms: List[str]) -> Dict:
        """Filter documents containing specific terms."""
        all_data = self.embedding_store.collection.get()
        
        filtered_documents = []
        filtered_metadatas = []
        filtered_ids = []
        
        for i, doc in enumerate(all_data['documents']):
            doc_lower = doc.lower()
            if any(term.lower() in doc_lower for term in terms):
                filtered_documents.append(doc)
                filtered_metadatas.append(all_data['metadatas'][i])
                filtered_ids.append(all_data['ids'][i])
        
        return {
            'documents': filtered_documents,
            'metadatas': filtered_metadatas,
            'ids': filtered_ids
        }
    
    def _analyze_category_trends(self, data: Dict) -> List[TrendData]:
        """Analyze trends for a specific category."""
        # Group by time period
        time_groups = self._group_by_time_period(data, "year")
        
        # Calculate trends
        trend_data = []
        for period, documents in time_groups.items():
            count = len(documents)
            
            if len(time_groups) >= 3:
                slope, significance, r_squared = self._calculate_trend_slope(
                    time_groups, period
                )
            else:
                slope, significance, r_squared = None, None, None
            
            trend_data.append(TrendData(
                time_period=period,
                count=count,
                trend_slope=slope,
                trend_significance=significance,
                r_squared=r_squared
            ))
        
        trend_data.sort(key=lambda x: x.time_period)
        return trend_data
    
    def _calculate_correlation(self, 
                            count1: int, 
                            count2: int, 
                            cooccurrence: int, 
                            total_docs: int) -> float:
        """Calculate correlation between two tags."""
        try:
            # Simple correlation calculation
            if count1 == 0 or count2 == 0 or total_docs == 0:
                return 0.0
            
            expected_cooccurrence = (count1 * count2) / total_docs
            if expected_cooccurrence == 0:
                return 0.0
            
            correlation = (cooccurrence - expected_cooccurrence) / expected_cooccurrence
            return max(-1.0, min(1.0, correlation))
            
        except:
            return 0.0


class TrendVisualizer:
    """Creates visualizations for trend data."""
    
    @staticmethod
    def create_trend_chart(trend_data: List[TrendData]) -> str:
        """Create a simple text-based trend chart."""
        if not trend_data:
            return "No trend data available"
        
        # Find max count for scaling
        max_count = max(td.count for td in trend_data)
        
        chart_lines = []
        chart_lines.append("Trend Analysis:")
        chart_lines.append("=" * 50)
        
        for td in trend_data:
            # Create bar representation
            bar_length = int((td.count / max_count) * 30)
            bar = "█" * bar_length
            
            # Add trend indicator
            trend_indicator = ""
            if td.trend_slope is not None:
                if td.trend_slope > 0:
                    trend_indicator = " ↗"
                elif td.trend_slope < 0:
                    trend_indicator = " ↘"
                else:
                    trend_indicator = " →"
            
            chart_lines.append(f"{td.time_period}: {bar} {td.count}{trend_indicator}")
        
        return "\n".join(chart_lines)


if __name__ == "__main__":
    # Test the trend analyzer
    from .embed_store import EmbeddingStore
    
    store = EmbeddingStore()
    analyzer = TrendAnalyzer(store)
    
    # Analyze trends
    trends = analyzer.analyze_temporal_trends()
    print(f"Found {len(trends)} trend data points")
    
    for trend in trends:
        print(f"{trend.time_period}: {trend.count} documents")
        if trend.trend_slope is not None:
            print(f"  Trend slope: {trend.trend_slope:.3f}")
            print(f"  Significance: {trend.trend_significance:.3f}")
