"""
LLM Service for Amazon Product Analysis
Provides competitive analysis using Groq's Llama models
"""

import os
from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorInsight(BaseModel):
    """Represents insights about a competitor product"""
    asin: str
    title: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    key_points: List[str] = Field(default_factory=list)
    price_difference_pct: Optional[float] = None
    rating_difference: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True

class LLMAnalysisResult(BaseModel):
    """Enhanced structured result from comprehensive LLM analysis"""
    summary: str
    positioning: str
    top_competitors: List[CompetitorInsight] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    pricing_analysis: str
    feature_comparison: str
    market_insights: str
    
    # Enhanced analysis fields
    competitive_threats: str = ""
    action_plan: str = ""
    market_trends: str = ""
    
    # New comprehensive analysis sections
    overall_insights: str = ""
    category_breakdown: Dict[str, str] = Field(default_factory=dict)
    review_analysis: str = ""
    customer_feedback_summary: str = ""
    brand_analysis: str = ""
    seasonal_trends: str = ""
    geographic_insights: str = ""
    optimization_suggestions: List[str] = Field(default_factory=list)
    risk_assessment: str = ""
    opportunity_analysis: str = ""
    
    # Detailed breakdowns
    price_breakdown: Dict[str, Any] = Field(default_factory=dict)
    feature_breakdown: Dict[str, Any] = Field(default_factory=dict)
    competitor_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Scoring and metrics
    market_position_score: Optional[float] = None
    price_competitiveness_score: Optional[float] = None
    feature_competitiveness_score: Optional[float] = None
    brand_strength_score: Optional[float] = None
    customer_satisfaction_score: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True

class LLMService:
    """Service for AI-powered product analysis using Groq"""
    
    def __init__(self):
        """Initialize the LLM service with Groq configuration"""
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
    
    def analyze_product_with_competitors(
        self,
        main_product: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        analysis_focus: List[str] = None
    ) -> LLMAnalysisResult:
        """Analyze product against competitors using Groq LLM"""
        
        logger.info(f"Starting competitive analysis for product: {main_product.get('title', 'Unknown')}")
        logger.info(f"Found {len(competitors)} competitors to analyze")
        
        if not self.groq_api_key:
            logger.warning("Groq API key not configured, using fallback analysis")
            return self._create_fallback_analysis(main_product, competitors)
        
        if analysis_focus is None:
            analysis_focus = ["pricing", "features", "positioning", "recommendations"]
        
        try:
            from groq import Groq
            
            # Initialize Groq client
            client = Groq(api_key=self.groq_api_key)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(main_product, competitors, analysis_focus)
            
            # Call Groq API
            logger.info(f"Sending analysis request to Groq using model: {self.groq_model}")
            
            response = client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Amazon marketplace analyst. Provide detailed, data-driven competitive analysis with specific actionable insights."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            analysis_text = response.choices[0].message.content
            logger.info("Successfully received analysis from Groq LLM")
            
            # Parse and structure the response
            result = self._parse_analysis_response(analysis_text, main_product, competitors)
            
            logger.info("Analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Groq LLM analysis failed: {e}")
            return self._create_fallback_analysis(main_product, competitors)
    
    def _format_categories(self, categories: List[Any]) -> str:
        """Format categories for display, handling nested structures"""
        if not categories:
            return "N/A"
        
        formatted = []
        for cat in categories:
            if isinstance(cat, str):
                formatted.append(cat)
            elif isinstance(cat, dict):
                # Handle nested category structures
                if 'ladder' in cat and isinstance(cat['ladder'], list):
                    ladder_names = [item.get('name', '') for item in cat['ladder'] if isinstance(item, dict) and item.get('name')]
                    if ladder_names:
                        formatted.extend(ladder_names)
                elif 'name' in cat:
                    formatted.append(cat['name'])
        
        return ', '.join(formatted) if formatted else "N/A"
    
    def _create_analysis_prompt(
        self, 
        main_product: Dict[str, Any], 
        competitors: List[Dict[str, Any]],
        analysis_focus: List[str]
    ) -> str:
        """Create comprehensive analysis prompt for Groq"""
        
        # Calculate competitor statistics for context
        competitor_prices = [c.get('price') for c in competitors if c.get('price')]
        competitor_ratings = [c.get('rating') for c in competitors if c.get('rating')]
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
        avg_competitor_rating = sum(competitor_ratings) / len(competitor_ratings) if competitor_ratings else 0
        
        main_price = main_product.get('price', 0)
        main_rating = main_product.get('rating', 0)
        
        prompt = f"""
# COMPREHENSIVE AMAZON COMPETITIVE ANALYSIS REPORT

## 📊 PRODUCT OVERVIEW
**Target Product:** {main_product.get('title', 'Unknown Product')}
**Brand:** {main_product.get('brand', 'Unknown')}
**ASIN:** {main_product.get('asin', 'N/A')}
**Current Price:** ${main_price:.2f} {main_product.get('currency', 'USD')}
**Customer Rating:** {main_rating}/5.0 ({main_product.get('review_count', 0):,} reviews)
**Product Categories:** {self._format_categories(main_product.get('categories', []))}
**Availability:** {main_product.get('availability', 'In Stock')}
**Ships From:** {main_product.get('ships_from', 'Amazon')}

## 🏪 MARKETPLACE CONTEXT
- **Total Competitors Analyzed:** {len(competitors)}
- **Average Competitor Price:** ${avg_competitor_price:.2f}
- **Average Competitor Rating:** {avg_competitor_rating:.1f}/5.0
- **Price Position:** {'Above Average' if main_price > avg_competitor_price else 'Below Average' if main_price < avg_competitor_price else 'At Market Average'}
- **Rating Position:** {'Above Average' if main_rating > avg_competitor_rating else 'Below Average' if main_rating < avg_competitor_rating else 'At Market Average'}

## 🎯 TOP COMPETITORS DETAILED BREAKDOWN
"""
        
        # Enhanced competitor analysis
        for i, competitor in enumerate(competitors[:5], 1):
            comp_price = competitor.get('price', 0)
            comp_rating = competitor.get('rating', 0)
            price_diff = ((comp_price - main_price) / main_price * 100) if main_price > 0 else 0
            rating_diff = comp_rating - main_rating if comp_rating and main_rating else 0
            
            prompt += f"""
### 🏆 Competitor #{i} - {competitor.get('brand', 'Unknown Brand')}
**Product:** {competitor.get('title', 'Unknown')[:120]}{'...' if len(competitor.get('title', '')) > 120 else ''}
**ASIN:** {competitor.get('asin', 'N/A')}
**Price:** ${comp_price:.2f} {competitor.get('currency', 'USD')} ({price_diff:+.1f}% vs main product)
**Rating:** {comp_rating}/5.0 ({competitor.get('review_count', 0):,} reviews) ({rating_diff:+.1f} vs main product)
**Key Features:** {', '.join(competitor.get('features', [])[:3]) if competitor.get('features') else 'Not specified'}
**Prime Eligible:** {competitor.get('is_prime', 'Unknown')}
**Seller:** {competitor.get('seller', 'Unknown')}
"""

        prompt += f"""

## 📋 COMPREHENSIVE ANALYSIS REQUIREMENTS
As a senior e-commerce analyst and Amazon marketplace expert, provide an exhaustive competitive analysis covering ALL aspects below:

**ANALYSIS FOCUS AREAS:** {', '.join(analysis_focus)}

**CRITICAL INSTRUCTIONS:**
- Provide specific data points, percentages, and dollar amounts
- Include actionable, measurable recommendations with ROI estimates
- Analyze customer sentiment and review patterns
- Consider seasonal trends, geographic variations, and market dynamics
- Assess risks and opportunities across multiple dimensions
- Use competitive benchmarking with precise comparisons

---

### 🎯 EXECUTIVE SUMMARY
Provide a comprehensive 4-5 sentence executive summary covering:
- Current competitive position with quantified metrics
- Key opportunities and threats identified
- Primary competitive advantages and disadvantages
- Recommended immediate priority actions
- Expected market trajectory and positioning changes

### 📊 OVERALL STRATEGIC INSIGHTS
**Market Leadership Analysis:**
- Where does this product rank in the competitive landscape?
- What are the key differentiators vs top competitors?
- Market share implications and growth trajectory
- Competitive moats and vulnerability assessment
- Innovation gaps and technology advantages

### 🏷️ DETAILED CATEGORY BREAKDOWN
Analyze performance across these specific categories:

**📱 Product Categories:**
- Performance within primary category vs subcategories
- Cross-category competitive positioning
- Category-specific consumer preferences and trends
- Seasonal variations by category
- Category growth rates and market opportunities

**🌍 Geographic Performance:**
- Regional pricing variations and competitiveness
- Geographic demand patterns and seasonality
- International market opportunities
- Shipping and logistics competitive advantages
- Regional brand recognition and trust factors

**👥 Customer Segments:**
- Primary vs secondary customer demographics
- Customer acquisition cost comparison
- Lifetime value analysis vs competitors
- Customer loyalty and retention patterns
- Segment-specific competitive advantages

### ⭐ CUSTOMER REVIEW & FEEDBACK ANALYSIS
**Review Pattern Analysis:**
- Overall rating trends vs competitors over time
- Most frequently mentioned positive attributes
- Common complaint themes and pain points
- Review velocity and engagement patterns
- Verified vs unverified purchase patterns
- Response to negative reviews and customer service quality

**Top Review Insights:**
- Analysis of 5-star vs 1-star review themes
- Feature mentions in positive reviews
- Problem areas highlighted in negative reviews
- Comparison mentions of competitors in reviews
- Customer use case patterns and applications

**Customer Satisfaction Breakdown:**
- Product quality satisfaction scores
- Shipping and logistics satisfaction
- Value-for-money perception analysis
- Customer support experience ratings
- Return and refund experience analysis

### 💰 COMPREHENSIVE PRICING ANALYSIS
**Current Price Positioning:**
- Exact percentile ranking in competitive set
- Price elasticity assessment and demand sensitivity
- Historical pricing trends and competitor responses
- Dynamic pricing opportunities and optimal timing
- Bundle and promotional pricing effectiveness

**Price Strategy Recommendations:**
- Optimal price points for maximum revenue
- Competitive response scenarios and counter-strategies
- Seasonal pricing adjustments and timing
- Geographic pricing variations and arbitrage opportunities
- Psychological pricing thresholds and consumer behavior

### 🔧 DETAILED FEATURE COMPARISON
**Feature Gap Analysis:**
- Missing features that competitors offer
- Unique features that provide competitive advantage
- Feature importance ranking based on customer feedback
- Technical specification comparison matrix
- Innovation opportunities and R&D priorities

**Feature Value Assessment:**
- Features that drive purchase decisions vs nice-to-have
- Cost-benefit analysis of feature additions
- Customer willingness to pay for specific features
- Feature adoption trends in the category
- Emerging features and technology disruptions

### 🚀 STRATEGIC RECOMMENDATIONS (10-15 Items)
Provide prioritized, detailed recommendations:

**🔴 IMMEDIATE ACTIONS (0-30 days):**
- Critical price adjustments with specific amounts
- Urgent listing optimizations and content updates
- Inventory management and availability improvements
- Customer service enhancements and response protocols

**🟡 SHORT-TERM INITIATIVES (1-3 months):**
- Product feature enhancements and updates
- Marketing campaign launches and targeting
- Partnership and distribution channel expansion
- Supply chain optimizations and cost reductions

**🟢 LONG-TERM STRATEGY (6-12 months):**
- New product development and line extensions
- Market expansion and geographic growth
- Technology investments and automation
- Brand building and reputation management

### 📈 MARKET TRENDS & INSIGHTS
**Industry Trends:**
- Category growth rates and market expansion
- Consumer behavior shifts and preferences
- Technology adoption and disruption patterns
- Regulatory changes and compliance requirements
- Sustainability trends and environmental considerations

**Seasonal Patterns:**
- Peak demand periods and inventory planning
- Seasonal pricing strategies and optimization
- Holiday and event-driven sales opportunities
- Weather and climate impact on demand
- Back-to-school, holiday, and special event trends

### ⚠️ RISK ASSESSMENT & OPPORTUNITY ANALYSIS
**Competitive Threats:**
- New entrants and disruptive technologies
- Aggressive competitor pricing strategies
- Market consolidation and acquisition risks
- Supply chain disruptions and cost increases
- Economic factors and consumer spending changes

**Growth Opportunities:**
- Underserved customer segments and niches
- Geographic expansion possibilities
- Product line extension opportunities
- Technology integration and automation
- Strategic partnership and collaboration potential

### 🎯 OPTIMIZATION SUGGESTIONS
**Listing Optimization:**
- Title, bullet points, and description improvements
- Keyword optimization and search ranking enhancement
- Image quality and content recommendations
- A+ Content and Enhanced Brand Content opportunities
- Video content and demonstration suggestions

**Operational Excellence:**
- Inventory management and forecasting improvements
- Customer service response time and quality enhancements
- Shipping speed and logistics optimization
- Return process and policy improvements
- Quality control and defect reduction strategies

### 📅 90-DAY ACTION PLAN
**Week 1-2 (Quick Wins):**
- Specific price adjustments and immediate optimizations
- Critical listing updates and content improvements
- Customer service protocol enhancements

**Month 1 (Foundation Building):**
- Marketing campaign launches and optimization
- Inventory planning and supply chain improvements
- Customer feedback collection and analysis systems

**Month 2-3 (Growth Acceleration):**
- Feature enhancements and product improvements
- Market expansion and new channel development
- Brand building and reputation management initiatives

**Success Metrics & KPIs:**
- Revenue targets and growth expectations
- Market share objectives and competitive positioning
- Customer satisfaction and retention goals
- Operational efficiency and cost reduction targets

### 🏆 COMPETITIVE ADVANTAGE ASSESSMENT
**Current Strengths:**
- Unique selling propositions and differentiators
- Cost advantages and operational efficiencies
- Brand recognition and customer loyalty
- Technology and innovation capabilities
- Distribution and logistics advantages

**Improvement Areas:**
- Competitive gaps and vulnerability points
- Investment priorities and resource allocation
- Skill development and capability building
- Technology upgrades and modernization needs
- Market expansion and growth initiatives

**FORMATTING REQUIREMENTS:**
- Use bullet points and numbered lists for clarity
- Include specific percentages, dollar amounts, and metrics
- Provide concrete examples and case studies
- Use competitive benchmarking data throughout
- Include implementation timelines and resource requirements
- Specify success metrics and measurement criteria
"""
        
        return prompt
    
    def _parse_analysis_response(
        self, 
        analysis_text: str, 
        main_product: Dict[str, Any], 
        competitors: List[Dict[str, Any]]
    ) -> LLMAnalysisResult:
        """Parse Groq LLM response into structured analysis result"""
        
        try:
            # Extract sections using simple text parsing
            sections = self._extract_sections(analysis_text)
            
            # Process top competitors
            top_competitors = []
            for i, competitor in enumerate(competitors[:5]):
                price_diff = None
                rating_diff = None
                
                if main_product.get('price') and competitor.get('price'):
                    price_diff = ((competitor['price'] - main_product['price']) / main_product['price']) * 100
                
                if main_product.get('rating') and competitor.get('rating'):
                    rating_diff = competitor['rating'] - main_product['rating']
                
                # Get category name safely
                category_name = "same category"
                categories = main_product.get('categories', [])
                if categories:
                    if isinstance(categories, list) and len(categories) > 0:
                        first_cat = categories[0]
                        if isinstance(first_cat, str):
                            category_name = first_cat
                        elif isinstance(first_cat, dict) and 'ladder' in first_cat:
                            ladder = first_cat['ladder']
                            if isinstance(ladder, list) and len(ladder) > 0 and 'name' in ladder[0]:
                                category_name = ladder[0]['name']
                
                top_competitors.append(CompetitorInsight(
                    asin=competitor.get('asin', ''),
                    title=competitor.get('title'),
                    price=competitor.get('price'),
                    currency=competitor.get('currency'),
                    rating=competitor.get('rating'),
                    key_points=[f"Competitive product in {category_name}"],
                    price_difference_pct=price_diff,
                    rating_difference=rating_diff
                ))
            
            # Extract recommendations and additional data
            recommendations = self._extract_recommendations(sections.get('STRATEGIC RECOMMENDATIONS', ''))
            optimization_suggestions = self._extract_recommendations(sections.get('OPTIMIZATION SUGGESTIONS', ''))
            
            # Extract category breakdown
            category_breakdown = self._parse_category_breakdown(sections.get('DETAILED CATEGORY BREAKDOWN', sections.get('CATEGORY BREAKDOWN', '')))
            
            # Calculate all competitive scores
            price_score = self._calculate_price_competitiveness(main_product, competitors)
            market_score = self._calculate_market_position(main_product, competitors)
            brand_score = self._calculate_brand_strength(main_product, competitors)
            satisfaction_score = self._calculate_customer_satisfaction(main_product, competitors)
            
            # Create detailed breakdowns
            price_breakdown = self._create_price_breakdown(main_product, competitors)
            feature_breakdown = self._create_feature_breakdown(main_product, competitors)
            competitor_breakdown = self._create_competitor_breakdown(competitors)
            
            return LLMAnalysisResult(
                summary=sections.get('EXECUTIVE SUMMARY', sections.get('SUMMARY', f"Comprehensive competitive analysis for {main_product.get('title', 'product')} reveals {len(competitors)} active competitors with strategic positioning opportunities across pricing, features, and market presence.")),
                positioning=sections.get('MARKET POSITIONING ANALYSIS', sections.get('MARKET POSITIONING', sections.get('POSITIONING', f"Product positioned as {price_position if 'price_position' in locals() else 'competitive'} option with strategic opportunities for market differentiation and customer acquisition."))),
                top_competitors=top_competitors,
                recommendations=recommendations if recommendations else [
                    "Optimize pricing strategy based on competitive analysis",
                    "Enhance product features to address market gaps",
                    "Improve customer review management",
                    "Develop strategic marketing positioning",
                    "Monitor competitor activities regularly"
                ],
                pricing_analysis=sections.get('COMPREHENSIVE PRICING ANALYSIS', sections.get('PRICING ANALYSIS', sections.get('PRICING', f"Price analysis shows competitive positioning at ${main_product.get('price', 0):.2f} with optimization opportunities based on {len(competitors)} competitor analysis."))),
                feature_comparison=sections.get('DETAILED FEATURE COMPARISON', sections.get('FEATURE COMPARISON', sections.get('FEATURES', "Feature analysis reveals competitive advantages and improvement opportunities across key product attributes and customer value propositions."))),
                market_insights=sections.get('MARKET TRENDS & INSIGHTS', sections.get('MARKET INSIGHTS', sections.get('INSIGHTS', f"Market analysis of {len(competitors)} competitors reveals growth opportunities, competitive dynamics, and strategic positioning potential."))),
                competitive_threats=sections.get('RISK ASSESSMENT & OPPORTUNITY ANALYSIS', sections.get('COMPETITIVE THREATS', sections.get('THREATS', "Competitive landscape analysis reveals market positioning challenges and strategic opportunities for differentiation."))),
                action_plan=sections.get('90-DAY ACTION PLAN', sections.get('ACTION PLAN', "Strategic 90-day implementation roadmap includes pricing optimization, feature enhancements, marketing positioning, and competitive monitoring initiatives.")),
                market_trends=sections.get('MARKET TRENDS', sections.get('TRENDS', "Market trend analysis shows evolving customer preferences, competitive dynamics, and growth opportunities for strategic positioning.")),
                
                # New comprehensive sections with proper fallbacks
                overall_insights=sections.get('OVERALL STRATEGIC INSIGHTS', f"Strategic analysis reveals competitive positioning opportunities with {len(competitors)} market competitors. Key insights include pricing optimization, feature differentiation, and market expansion potential."),
                category_breakdown=category_breakdown if 'category_breakdown' in locals() else f"Category analysis shows competitive landscape across {len(set([c.get('category', 'General') for c in competitors]))} product segments with differentiation opportunities.",
                review_analysis=sections.get('CUSTOMER REVIEW & FEEDBACK ANALYSIS', sections.get('REVIEW ANALYSIS', f"Customer review analysis across {len(competitors)} competitors reveals satisfaction patterns, feature preferences, and improvement opportunities for strategic advantage.")),
                customer_feedback_summary=sections.get('CUSTOMER REVIEW & FEEDBACK ANALYSIS', f"Customer feedback analysis shows competitive review patterns with average {sum([c.get('rating', 0) for c in competitors if c.get('rating')])/len([c for c in competitors if c.get('rating')]):.1f} rating across competitors."),
                brand_analysis=sections.get('COMPETITIVE ADVANTAGE ASSESSMENT', f"Brand positioning analysis reveals competitive strengths in market presence, customer loyalty, and differentiation opportunities compared to {len(competitors)} competitors."),
                seasonal_trends=sections.get('MARKET TRENDS & INSIGHTS', "Seasonal analysis shows market fluctuation patterns, demand cycles, and strategic timing opportunities for competitive advantage."),
                geographic_insights=sections.get('DETAILED CATEGORY BREAKDOWN', "Geographic market analysis reveals regional competitive dynamics and expansion opportunities across different market segments."),
                optimization_suggestions=optimization_suggestions if 'optimization_suggestions' in locals() and optimization_suggestions else [
                    "Optimize product pricing based on competitive analysis",
                    "Enhance product listing with competitor insights",
                    "Improve customer service based on review analysis",
                    "Develop unique value propositions",
                    "Monitor competitor changes regularly"
                ],
                risk_assessment=sections.get('RISK ASSESSMENT & OPPORTUNITY ANALYSIS', "Risk assessment identifies competitive pressures, market challenges, and strategic threats requiring mitigation strategies."),
                opportunity_analysis=sections.get('RISK ASSESSMENT & OPPORTUNITY ANALYSIS', "Opportunity analysis reveals market gaps, competitive advantages, and growth potential for strategic positioning."),
                
                # Detailed breakdowns with fallbacks
                price_breakdown=price_breakdown if 'price_breakdown' in locals() else {
                    "competitive_position": f"Priced at ${main_product.get('price', 0):.2f} vs market average",
                    "price_range": f"${min([c.get('price', 0) for c in competitors if c.get('price', 0)] + [main_product.get('price', 0)]):.2f} - ${max([c.get('price', 0) for c in competitors if c.get('price', 0)] + [main_product.get('price', 0)]):.2f}",
                    "recommendations": "Strategic pricing optimization opportunities identified"
                },
                feature_breakdown=feature_breakdown if 'feature_breakdown' in locals() else {
                    "competitive_advantages": "Unique product features and value propositions",
                    "improvement_areas": "Feature enhancement opportunities identified",
                    "market_gaps": "Unmet customer needs and market opportunities"
                },
                competitor_breakdown=competitor_breakdown if 'competitor_breakdown' in locals() else [
                    {"name": comp.get('title', 'Unknown')[:50], "strength": "Market presence", "weakness": "Positioning gap"} 
                    for comp in competitors[:5]
                ],
                
                # All scoring metrics with calculated fallbacks
                market_position_score=market_score if 'market_score' in locals() else self._calculate_market_position(main_product, competitors),
                price_competitiveness_score=price_score if 'price_score' in locals() else self._calculate_price_competitiveness(main_product, competitors),
                brand_strength_score=brand_score if 'brand_score' in locals() else 75.0,  # Default reasonable score
                customer_satisfaction_score=satisfaction_score if 'satisfaction_score' in locals() else min(100.0, (main_product.get('rating', 3.5) / 5.0) * 100)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Groq LLM response: {e}")
            return self._create_fallback_analysis(main_product, competitors)
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from analysis text"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a section header
            if line.startswith('###') and any(keyword in line.upper() for keyword in [
                'EXECUTIVE SUMMARY', 'OVERALL STRATEGIC INSIGHTS', 'MARKET POSITIONING', 'POSITIONING ANALYSIS',
                'DETAILED CATEGORY BREAKDOWN', 'CATEGORY BREAKDOWN', 'CUSTOMER REVIEW', 'FEEDBACK ANALYSIS', 
                'REVIEW ANALYSIS', 'COMPREHENSIVE PRICING', 'PRICING ANALYSIS', 'DETAILED FEATURE', 
                'FEATURE COMPARISON', 'STRATEGIC RECOMMENDATIONS', 'MARKET TRENDS', 'MARKET INSIGHTS',
                'RISK ASSESSMENT', 'OPPORTUNITY ANALYSIS', 'OPTIMIZATION SUGGESTIONS', 'ACTION PLAN', 
                '90-DAY ACTION', 'COMPETITIVE ADVANTAGE', 'COMPETITIVE THREATS'
            ]):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.replace('###', '').strip().upper()
                current_content = []
            else:
                if current_section and line:
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_recommendations(self, recommendations_text: str) -> List[str]:
        """Extract recommendations from text"""
        recommendations = []
        
        lines = recommendations_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                recommendations.append(line.lstrip('-•* '))
            elif line and len(line) > 20 and not line.endswith(':'):
                recommendations.append(line)
        
        # If no bullet points found, split by sentences
        if not recommendations and recommendations_text:
            sentences = recommendations_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:
                    recommendations.append(sentence + '.')
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def _extract_list_items(self, text: str, item_type: str) -> List[str]:
        """Extract list items from text for opportunities or gaps"""
        items = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                item = line.lstrip('-•* ')
                if item_type in item.lower() or len(item) > 20:
                    items.append(item)
        
        return items[:5]  # Limit to 5 items
    
    def _calculate_price_competitiveness(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> float:
        """Calculate price competitiveness score (0-100)"""
        try:
            main_price = main_product.get('price')
            if not main_price:
                return 50.0  # Neutral score if no price
            
            competitor_prices = [c.get('price') for c in competitors if c.get('price')]
            if not competitor_prices:
                return 50.0
            
            # Calculate percentile ranking
            cheaper_count = len([p for p in competitor_prices if p < main_price])
            total_count = len(competitor_prices)
            
            # Score: 100 = cheapest, 0 = most expensive
            score = (cheaper_count / total_count) * 100 if total_count > 0 else 50.0
            return round(score, 1)
        except:
            return 50.0
    
    def _calculate_market_position(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> float:
        """Calculate overall market position score (0-100)"""
        try:
            # Combine price and rating scores
            price_score = self._calculate_price_competitiveness(main_product, competitors)
            
            # Rating score
            main_rating = main_product.get('rating', 0)
            competitor_ratings = [c.get('rating') for c in competitors if c.get('rating')]
            
            if competitor_ratings:
                avg_rating = sum(competitor_ratings) / len(competitor_ratings)
                rating_score = (main_rating / 5.0) * 100 if main_rating else 50.0
                rating_advantage = ((main_rating - avg_rating) / 5.0) * 50 if main_rating and avg_rating else 0
                rating_score = min(100, max(0, rating_score + rating_advantage))
            else:
                rating_score = 50.0
            
            # Weighted average (40% rating, 30% price, 20% review count, 10% availability)
            review_count = main_product.get('review_count', 0)
            review_score = min(100, (review_count / 1000) * 50) if review_count else 0  # Normalize review count
            
            overall_score = (rating_score * 0.4) + (price_score * 0.3) + (review_score * 0.2) + (50 * 0.1)  # 50 as baseline for availability
            return round(overall_score, 1)
        except:
            return 50.0
    
    def _calculate_brand_strength(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> float:
        """Calculate brand strength score (0-100)"""
        try:
            main_brand = main_product.get('brand', '').lower()
            main_rating = main_product.get('rating', 0)
            main_reviews = main_product.get('review_count', 0)
            
            # Brand recognition score (based on review count and rating)
            brand_score = 50.0  # Base score
            
            if main_reviews > 1000:
                brand_score += 20
            elif main_reviews > 500:
                brand_score += 10
            elif main_reviews > 100:
                brand_score += 5
            
            if main_rating >= 4.5:
                brand_score += 20
            elif main_rating >= 4.0:
                brand_score += 10
            elif main_rating >= 3.5:
                brand_score += 5
            
            # Compare with competitors
            competitor_ratings = [c.get('rating', 0) for c in competitors if c.get('rating')]
            if competitor_ratings:
                avg_comp_rating = sum(competitor_ratings) / len(competitor_ratings)
                if main_rating > avg_comp_rating:
                    brand_score += 10
            
            return min(100, round(brand_score, 1))
        except:
            return 50.0
    
    def _calculate_customer_satisfaction(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> float:
        """Calculate customer satisfaction score (0-100)"""
        try:
            main_rating = main_product.get('rating', 0)
            main_reviews = main_product.get('review_count', 0)
            
            # Base satisfaction score from rating
            satisfaction_score = (main_rating / 5.0) * 100 if main_rating else 50.0
            
            # Adjust based on review volume (more reviews = more reliable)
            if main_reviews > 5000:
                satisfaction_score += 5
            elif main_reviews > 1000:
                satisfaction_score += 3
            elif main_reviews > 500:
                satisfaction_score += 1
            
            # Compare with competitors
            competitor_ratings = [c.get('rating', 0) for c in competitors if c.get('rating')]
            if competitor_ratings:
                avg_comp_rating = sum(competitor_ratings) / len(competitor_ratings)
                rating_advantage = ((main_rating - avg_comp_rating) / 5.0) * 20 if main_rating and avg_comp_rating else 0
                satisfaction_score += rating_advantage
            
            return min(100, max(0, round(satisfaction_score, 1)))
        except:
            return 50.0
    
    def _parse_category_breakdown(self, text: str) -> Dict[str, str]:
        """Parse category breakdown into structured data"""
        breakdown = {}
        current_category = None
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('**') and line.endswith(':**'):
                # Save previous category
                if current_category and current_content:
                    breakdown[current_category] = '\n'.join(current_content).strip()
                # Start new category
                current_category = line.replace('**', '').replace(':', '')
                current_content = []
            elif current_category and line:
                current_content.append(line)
        
        # Save last category
        if current_category and current_content:
            breakdown[current_category] = '\n'.join(current_content).strip()
        
        return breakdown
    
    def _create_price_breakdown(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed price breakdown analysis"""
        try:
            main_price = main_product.get('price', 0)
            competitor_prices = [c.get('price') for c in competitors if c.get('price')]
            
            if not competitor_prices:
                return {"error": "No competitor pricing data available"}
            
            return {
                "main_product_price": main_price,
                "competitor_count": len(competitor_prices),
                "min_competitor_price": min(competitor_prices),
                "max_competitor_price": max(competitor_prices),
                "avg_competitor_price": round(sum(competitor_prices) / len(competitor_prices), 2),
                "median_competitor_price": sorted(competitor_prices)[len(competitor_prices) // 2],
                "price_percentile": round((len([p for p in competitor_prices if p < main_price]) / len(competitor_prices)) * 100, 1),
                "cheaper_than_percent": round((len([p for p in competitor_prices if p > main_price]) / len(competitor_prices)) * 100, 1),
                "price_gap_to_cheapest": round(main_price - min(competitor_prices), 2) if main_price else 0,
                "price_gap_to_avg": round(main_price - (sum(competitor_prices) / len(competitor_prices)), 2) if main_price else 0
            }
        except:
            return {"error": "Failed to calculate price breakdown"}
    
    def _create_feature_breakdown(self, main_product: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed feature breakdown analysis"""
        try:
            main_features = main_product.get('features', [])
            all_competitor_features = []
            
            for comp in competitors:
                comp_features = comp.get('features', [])
                all_competitor_features.extend(comp_features)
            
            # Count feature frequency
            feature_counts = {}
            for feature in all_competitor_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            common_features = [f for f, count in feature_counts.items() if count >= len(competitors) * 0.5]
            
            return {
                "main_product_features": main_features,
                "total_main_features": len(main_features),
                "common_competitor_features": common_features,
                "missing_common_features": [f for f in common_features if f not in main_features],
                "unique_features": [f for f in main_features if f not in all_competitor_features],
                "feature_overlap_percentage": round((len([f for f in main_features if f in all_competitor_features]) / max(len(main_features), 1)) * 100, 1)
            }
        except:
            return {"error": "Failed to calculate feature breakdown"}
    
    def _create_competitor_breakdown(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create detailed breakdown for each competitor"""
        breakdown = []
        
        for i, comp in enumerate(competitors[:10]):  # Limit to top 10
            try:
                comp_data = {
                    "rank": i + 1,
                    "asin": comp.get('asin', ''),
                    "title": comp.get('title', ''),
                    "brand": comp.get('brand', ''),
                    "price": comp.get('price'),
                    "currency": comp.get('currency'),
                    "rating": comp.get('rating'),
                    "review_count": comp.get('review_count', 0),
                    "availability": comp.get('availability', 'Unknown'),
                    "prime_eligible": comp.get('is_prime', False),
                    "seller": comp.get('seller', 'Unknown'),
                    "key_features": comp.get('features', [])[:5],  # Top 5 features
                    "competitive_advantages": [],
                    "potential_threats": []
                }
                
                # Add competitive analysis
                if comp.get('price') and comp.get('rating'):
                    if comp['rating'] >= 4.5:
                        comp_data["competitive_advantages"].append("High customer satisfaction")
                    if comp.get('review_count', 0) > 1000:
                        comp_data["competitive_advantages"].append("Strong market presence")
                    if comp.get('is_prime'):
                        comp_data["competitive_advantages"].append("Prime shipping advantage")
                
                breakdown.append(comp_data)
            except Exception as e:
                continue
        
        return breakdown
    
    def _create_fallback_analysis(
        self, 
        main_product: Dict[str, Any], 
        competitors: List[Dict[str, Any]]
    ) -> LLMAnalysisResult:
        """Create fallback analysis when Groq LLM is not available"""
        
        # Calculate basic statistics
        competitor_prices = [c.get('price') for c in competitors if c.get('price')]
        competitor_ratings = [c.get('rating') for c in competitors if c.get('rating')]
        
        avg_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
        avg_rating = sum(competitor_ratings) / len(competitor_ratings) if competitor_ratings else 0
        
        main_price = main_product.get('price', 0)
        main_rating = main_product.get('rating', 0)
        
        # Basic competitive analysis
        price_position = "competitive" if abs(main_price - avg_price) / avg_price < 0.15 else ("premium" if main_price > avg_price else "budget")
        rating_position = "strong" if main_rating > avg_rating else "needs improvement"
        
        # Create top competitors list
        top_competitors = []
        for competitor in competitors[:5]:
            price_diff = None
            rating_diff = None
            
            if main_price and competitor.get('price'):
                price_diff = ((competitor['price'] - main_price) / main_price) * 100
            
            if main_rating and competitor.get('rating'):
                rating_diff = competitor['rating'] - main_rating
            
            top_competitors.append(CompetitorInsight(
                asin=competitor.get('asin', ''),
                title=competitor.get('title'),
                price=competitor.get('price'),
                currency=competitor.get('currency'),
                rating=competitor.get('rating'),
                key_points=["Competitive product in same category"],
                price_difference_pct=price_diff,
                rating_difference=rating_diff
            ))
        
        return LLMAnalysisResult(
            summary=f"Analysis for {main_product.get('title', 'product')} found {len(competitors)} competitors in the marketplace. The product is positioned as a {price_position} option with {rating_position} customer satisfaction ratings compared to competitors.",
            positioning=f"This product is positioned as a {price_position} option with {rating_position} customer satisfaction ratings compared to competitors. Market analysis shows competitive dynamics with opportunities for strategic positioning.",
            top_competitors=top_competitors,
            recommendations=[
                "Monitor competitor pricing regularly for market dynamics",
                "Analyze product reviews for improvement opportunities", 
                "Consider market expansion based on competitor presence",
                "Evaluate feature gaps compared to top competitors",
                "Optimize product listing and marketing messaging",
                "Consider strategic partnerships or bundling options",
                "Focus on unique value proposition development"
            ],
            pricing_analysis=f"Your product is priced at ${main_price:.2f} compared to competitor average of ${avg_price:.2f}, positioning it as a {price_position} option in the market. Price competitiveness analysis shows strategic opportunities for optimization.",
            feature_comparison="Detailed feature comparison shows competitive positioning across key product attributes. Analysis reveals differentiation opportunities and feature gap assessments for strategic advantage.",
            market_insights=f"The market shows {len(competitors)} active competitors with average ratings of {avg_rating:.1f} stars, indicating a competitive landscape with opportunities for differentiation and market positioning.",
            competitive_threats="Competitive analysis reveals market dynamics and strategic positioning opportunities. Threat assessment includes pricing pressures and feature competition.",
            action_plan="90-day strategic action plan includes immediate pricing optimization, feature enhancement evaluation, and competitive positioning strategies for market advantage.",
            market_trends="Market trend analysis shows evolving competitive dynamics with opportunities for strategic positioning and customer acquisition.",
            category_breakdown="Category analysis reveals market segmentation opportunities and competitive positioning across different product segments.",
            review_analysis="Review analysis provides customer sentiment insights and competitive advantage opportunities based on customer feedback patterns.",
            swot_analysis="SWOT analysis reveals strategic strengths, weaknesses, opportunities, and threats for competitive market positioning.",
            competitive_matrix="Competitive matrix analysis provides comprehensive comparison across key performance indicators and market positioning factors.",
            opportunities=["Market expansion opportunities", "Feature differentiation potential", "Pricing optimization strategies"],
            feature_gaps=["Identified feature enhancement areas", "Competitive feature analysis", "Innovation opportunities"],
            market_position_score=market_score,
            price_competitiveness_score=price_score
        )

    def analyze_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single product without competitors"""
        
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_api_key)
            
            prompt = f"""
Analyze this Amazon product and provide insights:

Product: {product.get("title", "Unknown")}
Brand: {product.get("brand", "Unknown")}
Price: {product.get("currency", "USD")} {product.get("price", "N/A")}
Rating: {product.get("rating", "N/A")}
Categories: {", ".join(product.get("categories", []))}

Provide a brief analysis covering:
1. Market positioning
2. Price competitiveness assessment  
3. Product strengths and weaknesses
4. Improvement recommendations

Keep the analysis concise and actionable.
"""
            
            response = client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert Amazon marketplace analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {"analysis": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Single product analysis failed: {e}")
            return {"analysis": f"Analysis failed: {str(e)}"}
    
    def generate_market_insights(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market insights from multiple products"""
        
        if not products:
            return {"insights": "No products available for analysis"}
        
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_api_key)
            
            # Format products for analysis
            product_summary = []
            for i, product in enumerate(products[:20], 1):  # Limit to 20 products
                title = product.get("title", "Unknown")[:60]
                price = product.get("price", "N/A")
                rating = product.get("rating", "N/A")
                domain = product.get("amazon_domain", "com")
                
                product_summary.append(f"{i}. {title} | ${price} | {rating}★ | .{domain}")
            
            products_text = "\n".join(product_summary)
            
            prompt = f"""
Analyze these Amazon products and provide market insights:

PRODUCTS:
{products_text}

Provide insights on:
1. Price distribution and trends
2. Rating patterns and quality indicators  
3. Market segments and opportunities
4. Domain/regional differences
5. Competitive landscape overview

Keep insights data-driven and actionable.
"""
            
            response = client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert market research analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return {"insights": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            return {"insights": f"Insights generation failed: {str(e)}"}