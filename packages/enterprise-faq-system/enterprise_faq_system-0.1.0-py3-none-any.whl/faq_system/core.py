import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple, Dict, Optional
import json
import re
import pickle
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProductionFAQSystem:
    def __init__(self, model_name='all-MiniLM-L6-v2', cache_dir='./faq_cache'):
        """Production-ready FAQ system with caching and logging"""
        self.encoder = SentenceTransformer(model_name)
        self.knowledge_base = []
        self.embeddings = None
        self.index = None
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.tfidf_matrix = None
        self.cache_dir = cache_dir
        self.query_log = []
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
    def load_knowledge_base(self, qa_file: str = None):
        """Load knowledge base from file or use default"""
        if qa_file and os.path.exists(qa_file):
            with open(qa_file, 'r') as f:
                qa_data = json.load(f)
                self.knowledge_base = [(item['question'], item['answer']) for item in qa_data]
        else:
            self.knowledge_base = self._get_default_knowledge_base()
        
        self._build_indices()
        
    def save_knowledge_base(self, qa_file: str):
        """Save current knowledge base to file"""
        qa_data = [{'question': q, 'answer': a} for q, a in self.knowledge_base]
        with open(qa_file, 'w') as f:
            json.dump(qa_data, f, indent=2)
    
    def add_qa_pair(self, question: str, answer: str):
        """Add new Q&A pair and rebuild indices"""
        self.knowledge_base.append((question, answer))
        self._build_indices()
        
    def _build_indices(self):
        """Build search indices with caching"""
        cache_file = os.path.join(self.cache_dir, 'indices.pkl')
        
        # Try to load from cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if len(cache_data['knowledge_base']) == len(self.knowledge_base):
                        self.embeddings = cache_data['embeddings']
                        self.index = cache_data['index']
                        self.tfidf_matrix = cache_data['tfidf_matrix']
                        self.tfidf_vectorizer = cache_data['tfidf_vectorizer']
                        print("Loaded indices from cache")
                        return
            except Exception as e:
                print(f"Cache loading failed: {e}")
        
        # Build indices from scratch
        print("Building search indices...")
        questions = [qa[0] for qa in self.knowledge_base]
        
        # Semantic embeddings
        self.embeddings = self.encoder.encode(questions)
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        # TF-IDF
        self.tfidf_vectorizer.fit(questions)
        self.tfidf_matrix = self.tfidf_vectorizer.transform(questions)
        
        # Save to cache
        cache_data = {
            'knowledge_base': self.knowledge_base,
            'embeddings': self.embeddings,
            'index': self.index,
            'tfidf_matrix': self.tfidf_matrix,
            'tfidf_vectorizer': self.tfidf_vectorizer
        }
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        print("Indices built and cached")
        
    def preprocess_query(self, query: str) -> str:
        """Enhanced query preprocessing"""
        query = query.lower().strip()
        
        # Remove common filler words that don't add meaning
        query = re.sub(r'\b(please|can you|could you|would you|tell me|i want to know|i need|help me)\b', '', query)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Normalize variations
        replacements = {
            'your': 'the',
            'you': 'we',
            'pricing': 'subscription plans',
            'cost': 'subscription plans',
            'price': 'subscription plans',
            'support': 'customer support',
            'help': 'customer support',
            'what documents do you support': 'what types of documents can I analyze',
            'what documents': 'what types of documents',
            'documents': 'document types',
            'analyze': 'document analysis',
            'cancel': 'cancel subscription',
        }
        
        for old, new in replacements.items():
            query = re.sub(r'\b' + old + r'\b', new, query)
            
        return query
    
    def answer_question(self, query: str, threshold: float = 0.2, log_query: bool = True) -> Dict:
        """Main method to get answer with metadata"""
        if log_query:
            self.query_log.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'processed_query': self.preprocess_query(query)
            })
        
        if not self.index:
            return {
                'answer': "System not initialized. Please load knowledge base first.",
                'confidence': 0.0,
                'matched_question': None,
                'method': 'error'
            }
        
        processed_query = self.preprocess_query(query)
        results = self._hybrid_search(processed_query, top_k=3)
        
        if results and results[0][1] >= threshold:
            best_idx, confidence, method = results[0]
            matched_question = self.knowledge_base[best_idx][0]
            answer = self.knowledge_base[best_idx][1]
            
            return {
                'answer': answer,
                'confidence': confidence,
                'matched_question': matched_question,
                'method': method,
                'alternatives': [self.knowledge_base[r[0]][0] for r in results[1:3] if r[1] > 0.1]
            }
        else:
            return {
                'answer': self._smart_fallback(query, results),
                'confidence': results[0][1] if results else 0.0,
                'matched_question': None,
                'method': 'fallback',
                'suggestions': [self.knowledge_base[r[0]][0] for r in results[:2] if r[1] > 0.1]
            }
    
    def _hybrid_search(self, query: str, top_k: int = 3) -> List[Tuple[int, float, str]]:
        """Hybrid semantic + keyword search"""
        # Semantic search
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, top_k)
        semantic_results = [(indices[0][i], scores[0][i]) for i in range(len(indices[0]))]
        
        # Keyword search
        query_tfidf = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        keyword_results = [(idx, similarities[idx]) for idx in top_indices]
        
        # Combine scores
        combined_scores = {}
        for idx, score in semantic_results:
            combined_scores[idx] = combined_scores.get(idx, 0) + 0.7 * score
            
        for idx, score in keyword_results:
            combined_scores[idx] = combined_scores.get(idx, 0) + 0.3 * score
        
        # Sort and add method info
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in sorted_results[:top_k]:
            method = "hybrid"
            if idx in [r[0] for r in semantic_results[:1]]:
                method += "+semantic"
            if idx in [r[0] for r in keyword_results[:1]]:
                method += "+keyword"
            results.append((idx, score, method))
            
        return results
    
    def _smart_fallback(self, query: str, results: List) -> str:
        """Enhanced fallback with better suggestions"""
        suggestions = []
        if results:
            for idx, score, _ in results[:2]:
                if score > 0.1:
                    suggestions.append(self.knowledge_base[idx][0])
        
        fallback_msg = "I couldn't find an exact match for your question."
        
        if suggestions:
            fallback_msg += " Here are some related topics that might help:\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                fallback_msg += f"• {suggestion}\n"
            fallback_msg += "\n"
        
        fallback_msg += "For personalized assistance, please:\n"
        fallback_msg += "📧 Email: hi@askbuddy.ai\n"
        fallback_msg += "💬 Live Chat: Available in the platform\n\n"
        fallback_msg += "I'm specifically designed to help with Enterprise AI Document Analysis Software questions about features, pricing, and support."
        
        return fallback_msg
    
    def _get_default_knowledge_base(self):
        """Default comprehensive knowledge base"""
        return [
            ("What is Enterprise AI Document Analysis Software?", 
             "Enterprise AI Document Analysis Software is an AI-powered platform that helps businesses efficiently analyze, review, and manage documents. It offers structured workflows for contracts, resumes, policies, and more while integrating advanced search and chat capabilities."),
            ("Tell me about your software", 
             "Enterprise AI Document Analysis Software is an AI-powered platform that helps businesses efficiently analyze, review, and manage documents. It offers structured workflows for contracts, resumes, policies, and more while integrating advanced search and chat capabilities."),
            ("What does your platform do?", 
             "Our platform uses AI to help businesses analyze, review, and manage documents efficiently. We provide structured workflows for various document types including contracts, resumes, and policies."),
            ("What are the subscription plans?",
             "We offer three subscription plans:\n\n• **Free Plan ($0/month)**: 1 GB storage, 1 document review per month (up to 20K words), AI-powered search, workflows for Contract, NDA, Policy, and Resume Review\n\n• **Pro Plan ($50/month)**: 10 GB storage, 50 document reviews per month, AI-powered search, same workflows as Free Plan\n\n• **Enterprise Plan (Custom Pricing)**: All Pro features plus custom seats, storage, and dedicated support."),
            ("Tell me about pricing",
             "We offer three subscription plans:\n\n• **Free Plan ($0/month)**: 1 GB storage, 1 document review per month (up to 20K words), AI-powered search, workflows for Contract, NDA, Policy, and Resume Review\n\n• **Pro Plan ($50/month)**: 10 GB storage, 50 document reviews per month, AI-powered search, same workflows as Free Plan\n\n• **Enterprise Plan (Custom Pricing)**: All Pro features plus custom seats, storage, and dedicated support."),
            ("How much does it cost?",
             "We have three pricing tiers: Free Plan at $0/month with basic features, Pro Plan at $50/month with enhanced capabilities, and Enterprise Plan with custom pricing for larger organizations."),
            ("What's included in the free plan?",
             "The Free Plan ($0/month) includes:\n• 1 GB storage for document storage and retrieval\n• 1 document review per month (up to 20K words)\n• AI-powered search capabilities\n• Workflows for Contract, NDA, Policy, and Resume Review\n• Access to core platform features"),
            ("What does the pro plan offer?",
             "The Pro Plan ($50/month) includes:\n• 10 GB storage\n• 50 document reviews per month\n• AI-powered search\n• All workflow features (Contract, NDA, Policy, Resume Review)\n• Priority support\n• Advanced analytics"),
            ("What types of documents can I analyze?",
             "You can analyze various business documents including:\n• Loan Policies\n• Non-Disclosure Agreements (NDAs)\n• Master Service Agreements (MSAs)\n• Resumes and CVs\n• Business contracts\n• Compliance documents\n• Policy documents\n\nOur AI reviews these for compliance, obligations, risk assessment, and key terms extraction."),
            ("What documents do you support?",
             "We support analysis of:\n• Loan Policies\n• Non-Disclosure Agreements (NDAs)\n• Master Service Agreements (MSAs)\n• Resumes and CVs\n• Business contracts\n• Compliance documents\n• Policy documents\n\nOur AI extracts key information, identifies risks, and ensures compliance."),
            ("How do I contact customer support?",
             "You can reach our support team through:\n• **Email**: hi@askbuddy.ai\n• **Live Chat**: Available within the platform\n• **Response Time**: Typically within 24 hours\n• **Enterprise customers** receive priority support with dedicated account managers"),
            ("How can I get support?",
             "Contact our support team at hi@askbuddy.ai or use the in-platform live chat for immediate assistance. Enterprise customers receive priority support."),
            ("What payment methods do you accept?",
             "We accept multiple payment methods:\n• Credit/Debit Cards (Visa, Mastercard, American Express)\n• Apple Pay\n• Google Pay\n• Bank Transfers/ACH (Enterprise customers only)\n\nAll payments are processed securely through Stripe with PCI-DSS compliance."),
            ("How do I cancel my subscription?",
             "You can cancel your subscription anytime:\n1. Go to your account settings\n2. Navigate to subscription management\n3. Click 'Cancel Subscription'\n4. Your access continues until the end of your current billing cycle\n5. No cancellation fees apply"),
            ("Is there a free trial?",
             "Yes! Our Free Plan serves as an extended trial, allowing you to:\n• Explore all core features\n• Test document analysis workflows\n• Experience AI-powered search\n• Process up to 1 document per month\n• Upgrade anytime to Pro or Enterprise plans"),
            ("Can I try it for free?",
             "Absolutely! Start with our Free Plan to explore the platform's core features at no cost. You can analyze documents, test workflows, and experience our AI capabilities before deciding to upgrade."),
        ]
    
    def get_analytics(self) -> Dict:
        """Get system analytics"""
        return {
            'total_qa_pairs': len(self.knowledge_base),
            'total_queries': len(self.query_log),
            'recent_queries': self.query_log[-10:] if self.query_log else [],
            'cache_status': os.path.exists(os.path.join(self.cache_dir, 'indices.pkl'))
        }

# Demo and testing
def demo_production_system():
    """Demonstrate the production system"""
    print("🚀 Initializing Production FAQ System...")
    
    faq = ProductionFAQSystem()
    faq.load_knowledge_base()
    
    test_questions = [
        "What is your software?",
        "Tell me about pricing",
        "What's included in free plan?", 
        "How to cancel subscription?",
        "What documents do you support?",
        "How can I contact support?",
        "Can I try for free?",
        "What's the weather today?",
        "Is there a trial?",
    ]
    
    print("\n" + "="*70)
    print("🎯 PRODUCTION FAQ SYSTEM DEMO")
    print("="*70)
    
    for question in test_questions:
        result = faq.answer_question(question)
        
        print(f"\n❓ Question: {question}")
        print(f"🔍 Confidence: {result['confidence']:.3f}")
        print(f"📊 Method: {result['method']}")
        if result['matched_question']:
            print(f"🎯 Matched: {result['matched_question']}")
        print(f"💬 Answer: {result['answer']}")
        print("-" * 70)
    
    # Show analytics
    analytics = faq.get_analytics()
    print(f"\n📈 System Analytics:")
    print(f"   Knowledge Base: {analytics['total_qa_pairs']} Q&A pairs")
    print(f"   Total Queries: {analytics['total_queries']}")
    print(f"   Cache Status: {'✅ Active' if analytics['cache_status'] else '❌ Not found'}")

if __name__ == "__main__":
    demo_production_system()