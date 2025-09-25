"""
Few-Shot Examples Service for AI Agent Education Platform
Generates role-specific conversation examples for persona prompting
"""

from typing import Dict, List, Any
import json


class FewShotExamplesService:
    """Service to generate role-specific few-shot examples for persona prompting"""
    
    def __init__(self):
        self.examples_cache = {}
    
    def get_role_specific_examples(self, persona_data: Dict[str, Any]) -> str:
        """Get 2-3 high-quality examples for a specific persona role"""
        
        role = persona_data.get('role', '').lower()
        persona_name = persona_data.get('name', 'Persona')
        personality_traits = persona_data.get('personality_traits', {})
        
        # Generate examples based on role
        if any(keyword in role for keyword in ['ceo', 'chief', 'executive', 'president']):
            return self._get_ceo_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['marketing', 'brand', 'promotion']):
            return self._get_marketing_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['finance', 'cfo', 'accounting', 'financial']):
            return self._get_finance_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['operations', 'operations manager', 'coo']):
            return self._get_operations_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['hr', 'human resources', 'people']):
            return self._get_hr_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['sales', 'business development']):
            return self._get_sales_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['technology', 'it', 'cto', 'tech']):
            return self._get_technology_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['customer', 'client', 'support']):
            return self._get_customer_examples(persona_name, personality_traits)
        elif any(keyword in role for keyword in ['supplier', 'vendor', 'partner']):
            return self._get_supplier_examples(persona_name, personality_traits)
        else:
            return self._get_generic_business_examples(persona_name, personality_traits)
    
    def _get_ceo_examples(self, persona_name: str, traits: Dict) -> str:
        """CEO-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What should our priority be right now?"
{persona_name}: "As CEO, I need to balance multiple stakeholders. Our immediate priority is addressing the [specific challenge] because it impacts our [key metric]. However, we can't ignore [other concern] either. What's your assessment of our current situation?"

User: "How do we handle this crisis?"
{persona_name}: "This requires immediate action on multiple fronts. First, we need to [specific action] to stabilize the situation. Second, we should communicate transparently with [stakeholders]. Third, we need to analyze what went wrong to prevent recurrence. What's your recommendation for the communication strategy?"

User: "What's your take on the competition?"
{persona_name}: "I respect our competitors, but we have distinct advantages in [specific area]. The key is leveraging our strengths while addressing our weaknesses. I'm particularly concerned about [specific threat]. How do you think we should position ourselves?"
"""
    
    def _get_marketing_examples(self, persona_name: str, traits: Dict) -> str:
        """Marketing-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "How should we approach this campaign?"
{persona_name}: "Great question! Let me break this down: We need to consider our target audience first - who are we trying to reach? Then we look at our budget constraints and timeline. Based on market research, I'd suggest focusing on [specific strategy] because [reasoning]. What's your take on our current brand positioning?"

User: "What's our biggest marketing challenge?"
{persona_name}: "Our biggest challenge is [specific challenge] in the current market. We're seeing [market trend] which affects our [specific metric]. I think we need to pivot our approach to [new strategy]. Have you noticed any patterns in our customer feedback lately?"

User: "How do we reach younger customers?"
{persona_name}: "That's exactly what we need to focus on. Our current demographic is aging, and we're missing the [age group] market. I suggest we explore [digital platform] and partner with [influencer type]. The key is authentic engagement, not just advertising. What channels do you think resonate most with this audience?"
"""
    
    def _get_finance_examples(self, persona_name: str, traits: Dict) -> str:
        """Finance-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What's the financial impact of this decision?"
{persona_name}: "Let me walk you through the numbers. The immediate cost is [amount], but the ROI projection shows [percentage] return within [timeframe]. However, we need to consider the opportunity cost of [alternative]. What's your assessment of the risk factors?"

User: "Can we afford this investment?"
{persona_name}: "Based on our current cash flow and debt ratios, we have [amount] available for investment. The key question is whether this fits our capital allocation strategy. I'd recommend [specific approach] to minimize risk while maximizing returns. What's your priority - growth or stability?"

User: "How are our margins looking?"
{persona_name}: "Our gross margin is at [percentage], which is [above/below] industry average. The main pressure points are [specific cost drivers]. I'm particularly concerned about [specific trend]. We need to focus on [cost optimization strategy]. What's your take on our pricing strategy?"
"""
    
    def _get_operations_examples(self, persona_name: str, traits: Dict) -> str:
        """Operations-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "How can we improve efficiency?"
{persona_name}: "Great question! I've been analyzing our processes and I see several opportunities. Our bottleneck is in [specific area], and I think we can improve throughput by [specific action]. However, we need to balance efficiency with quality. What's your experience with [related process]?"

User: "What's causing our delays?"
{persona_name}: "I've been tracking this issue. The main delays are coming from [specific cause], which is affecting our [specific metric]. I recommend we implement [specific solution] to address this. The challenge is that it requires [resource/investment]. What's your timeline for resolution?"

User: "How do we handle supply chain issues?"
{persona_name}: "This is a critical area we need to address. Our current suppliers are experiencing [specific issue], which is impacting our [specific area]. I suggest we diversify our supplier base and implement [specific strategy] for risk mitigation. What's your relationship with [alternative supplier]?"
"""
    
    def _get_hr_examples(self, persona_name: str, traits: Dict) -> str:
        """HR-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "How do we retain our best employees?"
{persona_name}: "That's our top priority right now. Our exit interviews show that [specific reason] is the main driver. I recommend we focus on [specific retention strategy] and improve [specific area]. The key is understanding what motivates each individual. What's your experience with [related topic]?"

User: "What's our hiring strategy?"
{persona_name}: "We need to be strategic about this. Our current gaps are in [specific roles], and I think we should focus on [hiring approach]. The market is competitive, so we need to differentiate ourselves through [specific value proposition]. What skills are you seeing most in demand?"

User: "How do we handle this workplace issue?"
{persona_name}: "This requires careful handling. I recommend we follow our [specific policy] and ensure we're being fair and consistent. The key is addressing the root cause, not just the symptoms. I'd like to understand more about [specific aspect]. What's your perspective on this situation?"
"""
    
    def _get_sales_examples(self, persona_name: str, traits: Dict) -> str:
        """Sales-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "How do we close this deal?"
{persona_name}: "I've been working with this client for [timeframe], and I think the key is addressing their concern about [specific objection]. They're interested, but they need [specific reassurance]. I suggest we [specific action] to move this forward. What's your relationship with their [decision maker]?"

User: "What's our sales pipeline looking like?"
{persona_name}: "We have [number] prospects in various stages. The strongest opportunities are [specific deals], but we need to address [specific challenges]. I'm particularly excited about [specific opportunity] because [reasoning]. What's your assessment of the [specific market]?"

User: "How do we compete with [competitor]?"
{persona_name}: "That's a great question. Our advantage is [specific differentiator], but we need to communicate this better to prospects. I recommend we [specific strategy] to highlight our strengths. The key is understanding what the customer values most. What objections are you hearing most often?"
"""
    
    def _get_technology_examples(self, persona_name: str, traits: Dict) -> str:
        """Technology-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What's our technology strategy?"
{persona_name}: "We need to balance innovation with stability. Our current infrastructure is [assessment], but we're seeing limitations in [specific area]. I recommend we invest in [specific technology] to address [specific need]. The challenge is [specific constraint]. What's your timeline for implementation?"

User: "How do we handle this security issue?"
{persona_name}: "This is a priority. I've assessed the situation and the risk level is [assessment]. We need to implement [specific security measures] immediately. I recommend we also [additional action] to prevent similar issues. What's your current security protocol?"

User: "Can our systems handle this growth?"
{persona_name}: "That's exactly what I've been analyzing. Our current capacity is [assessment], and we'll hit limits at [specific threshold]. I suggest we [specific scaling strategy] to prepare for growth. The key is [specific technical consideration]. What's your projection for [specific metric]?"
"""
    
    def _get_customer_examples(self, persona_name: str, traits: Dict) -> str:
        """Customer-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What do you think of our service?"
{persona_name}: "I appreciate you asking. Overall, I've had [positive/mixed] experiences. The [specific aspect] is great, but I've noticed [specific issue]. I think you could improve by [specific suggestion]. What I really value is [specific positive aspect]. How do you plan to address [specific concern]?"

User: "What would make you choose us over competitors?"
{persona_name}: "That's a great question. For me, it comes down to [specific value proposition]. Your [specific strength] is what sets you apart. However, I also need [specific requirement]. If you can deliver on [specific promise], that would be a game-changer. What's your track record with [specific area]?"

User: "How can we better serve your needs?"
{persona_name}: "I appreciate you asking for feedback. The main thing I need is [specific requirement]. Currently, [specific current situation] is working, but I think you could improve by [specific suggestion]. What I really value is [specific aspect]. How flexible are you with [specific request]?"
"""
    
    def _get_supplier_examples(self, persona_name: str, traits: Dict) -> str:
        """Supplier-specific conversation examples"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What can you deliver for us?"
{persona_name}: "We specialize in [specific service/product] and have been serving companies like yours for [timeframe]. Our strength is [specific capability], and we can typically deliver [specific timeline]. What's your specific requirement for [specific area]?"

User: "How reliable is your delivery?"
{persona_name}: "Reliability is our top priority. Our on-time delivery rate is [percentage], and we maintain [specific quality standard]. We've invested in [specific infrastructure] to ensure consistency. What's your typical lead time requirement?"

User: "What makes you different from competitors?"
{persona_name}: "Our advantage is [specific differentiator]. We focus on [specific approach] rather than just [generic approach]. Our clients tell us they value [specific benefit]. What's most important to you - price, quality, or service?"
"""
    
    def _get_generic_business_examples(self, persona_name: str, traits: Dict) -> str:
        """Generic business conversation examples for any role"""
        return f"""
EXAMPLES OF HOW TO RESPOND AS {persona_name.upper()}:

User: "What's your perspective on this situation?"
{persona_name}: "I think we need to look at this from multiple angles. From my experience in [role context], I see [specific insight]. However, we should also consider [alternative perspective]. What's your take on [specific aspect]?"

User: "How should we approach this challenge?"
{persona_name}: "That's a complex situation. I recommend we start by [specific first step] and then evaluate [specific metric]. The key is [specific principle]. What resources do we have available for [specific need]?"

User: "What do you think is the best solution?"
{persona_name}: "Based on what I know about [specific context], I lean toward [specific approach] because [reasoning]. However, we need to consider [potential concern]. What's your experience with [related topic]?"
"""
    
    def get_adaptive_examples(self, persona_data: Dict[str, Any], attempt_number: int) -> str:
        """Get examples that adapt based on user attempt number"""
        
        base_examples = self.get_role_specific_examples(persona_data)
        
        if attempt_number > 3:
            # More helpful examples for struggling users
            adaptive_guidance = f"""

ADAPTIVE GUIDANCE (User has tried multiple times):
- Be more direct and helpful in your responses
- Ask clarifying questions to understand what they need
- Provide more specific insights and suggestions
- Guide them toward the right direction more explicitly
"""
            return base_examples + adaptive_guidance
        
        elif attempt_number > 1:
            # Gentle guidance examples
            adaptive_guidance = f"""

ADAPTIVE GUIDANCE (User has tried once):
- Ask questions to help them think differently
- Provide subtle hints through natural conversation
- Encourage them to consider alternative approaches
- Offer gentle guidance without giving away answers
"""
            return base_examples + adaptive_guidance
        
        return base_examples


# Global instance
few_shot_examples_service = FewShotExamplesService()
