import openai
from typing import List
import json
import re
from app.core.config import settings
from app.models.types import DocumentAnalysis

class AIAnalyzer:
    """AI-powered document analysis using OpenAI"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_document(self, text: str, filename: str) -> DocumentAnalysis:
        """Comprehensive document analysis"""
        try:
            summary = await self._generate_summary(text)
            entities = await self._extract_entities(text)
            topics = await self._classify_topics(text)
            sentiment = await self._analyze_sentiment(text)
            
            return DocumentAnalysis(
                summary=summary,
                key_entities=entities,
                topics=topics,
                sentiment=sentiment,
                confidence_score=0.85
            )
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    async def _generate_summary(self, text: str) -> str:
        """Generate document summary"""
        # Truncate text if too long
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional document analyzer. Provide clear, concise summaries in 2-3 sentences."},
                    {"role": "user", "content": f"Summarize this document:\n\n{text}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    async def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from document"""
        max_chars = 6000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Extract key entities (people, organizations, locations, concepts) from text. Return as a JSON list of strings."},
                    {"role": "user", "content": f"Extract entities from:\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            entities_text = response.choices[0].message.content.strip()
            try:
                entities = json.loads(entities_text)
                return entities if isinstance(entities, list) else []
            except:
                # Fallback: simple parsing
                return self._parse_entities_fallback(entities_text)
                
        except Exception as e:
            return [f"Entity extraction failed: {str(e)}"]
    
    async def _classify_topics(self, text: str) -> List[str]:
        """Classify document topics"""
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Classify document topics. Return 3-5 topics as a JSON list."},
                    {"role": "user", "content": f"What are the main topics of:\n\n{text}"}
                ],
                max_tokens=100,
                temperature=0.2
            )
            
            topics_text = response.choices[0].message.content.strip()
            try:
                topics = json.loads(topics_text)
                return topics if isinstance(topics, list) else []
            except:
                return self._parse_topics_fallback(topics_text)
                
        except Exception as e:
            return [f"Topic classification failed: {str(e)}"]
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze document sentiment"""
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:2000] + "..." + text[-1000:]
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Analyze sentiment. Return one word: Positive, Negative, Neutral, Professional, or Informational."},
                    {"role": "user", "content": f"What is the sentiment of:\n\n{text}"}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "Unknown"
    
    def _parse_entities_fallback(self, text: str) -> List[str]:
        """Fallback entity parsing when JSON fails"""
        entities = []
        lines = text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('Entities'):
                clean_line = re.sub(r'^[\d\-\*\•\"\'\[\]]+\s*', '', line.strip())
                if clean_line and len(clean_line) > 2:
                    entities.append(clean_line[:50])
        return entities[:10]
    
    def _parse_topics_fallback(self, text: str) -> List[str]:
        """Fallback topic parsing when JSON fails"""
        topics = []
        lines = text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('Topics'):
                clean_line = re.sub(r'^[\d\-\*\•\"\'\[\]]+\s*', '', line.strip())
                if clean_line and len(clean_line) > 2:
                    topics.append(clean_line[:30])
        return topics[:5]
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for vector search"""
        try:
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = self.client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")