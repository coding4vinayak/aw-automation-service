#!/usr/bin/env python3
"""
AI Lead Scoring System
Score and qualify leads automatically based on intent signals
"""

from typing import List, Dict, Any
from datetime import datetime
import re


class LeadScorer:
    """AI-powered lead scoring based on behavior and intent signals"""
    
    def __init__(self):
        self scoring_rules = {
            "email_engagement": {
                "opened_email": 10,
                "clicked_link": 20,
                "replied_email": 30,
                "unsubscribed": -50
            },
            "website_behavior": {
                "visited_pricing": 40,
                "visited_demo": 35,
                "visited_features": 20,
                "visited_about": 10,
                "downloaded_resource": 25,
                "watched_demo_video": 30
            },
            "form_engagement": {
                "filled_contact_form": 50,
                "filled_demo_request": 60,
                "filled_pricing_inquiry": 70,
                "filledNewsletter": 15
            },
            "social_engagement": {
                "liked_post": 5,
                "commented_post": 15,
                "shared_post": 20,
                "mentioned_brand": 25,
                "followed_account": 10
            },
            "firmographic_fit": {
                "company_size_50plus": 30,
                "company_size_10plus": 20,
                "company_size_1to10": 10,
                "decision_maker": 40,
                "has_budget": 30,
                "recent_funding": 25
            }
        }
        
        self.score_thresholds = {
            "hot": 80,
            "warm": 50,
            "cold": 20,
            "dead": 0
        }
    
    def score_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Score a lead based on multiple signals"""
        
        total_score = 0
        score_breakdown = {}
        
        # Email engagement
        email_score = 0
        for action, points in self.scoring_rules["email_engagement"].items():
            if lead.get(f"email_{action}"):
                email_score += points
        score_breakdown["email_engagement"] = email_score
        total_score += email_score
        
        # Website behavior
        website_score = 0
        for action, points in self.scoring_rules["website_behavior"].items():
            if lead.get(f"website_{action}"):
                website_score += points
        score_breakdown["website_behavior"] = website_score
        total_score += website_score
        
        # Form engagement
        form_score = 0
        for action, points in self.scoring_rules["form_engagement"].items():
            if lead.get(f"form_{action}"):
                form_score += points
        score_breakdown["form_engagement"] = form_score
        total_score += form_score
        
        # Social engagement
        social_score = 0
        for action, points in self.scoring_rules["social_engagement"].items():
            if lead.get(f"social_{action}"):
                social_score += points
        score_breakdown["social_engagement"] = social_score
        total_score += social_score
        
        # Firmographic fit
        firmographic_score = 0
        for action, points in self.scoring_rules["firmographic_fit"].items():
            if lead.get(f"firm_{action}"):
                firmographic_score += points
        score_breakdown["firmographic_fit"] = firmographic_score
        total_score += firmographic_score
        
        # Determine lead temperature
        temperature = "dead"
        for temp, threshold in sorted(self.score_thresholds.items(), key=lambda x: x[1], reverse=True):
            if total_score >= threshold:
                temperature = temp
                break
        
        # Calculate engagement velocity (trend)
        velocity = self._calculate_velocity(lead)
        
        result = {
            "lead_id": lead.get("id"),
            "email": lead.get("email"),
            "total_score": min(total_score, 100),
            "temperature": temperature,
            "score_breakdown": score_breakdown,
            "velocity": velocity,
            "recommended_action": self._get_recommendation(temperature, velocity),
            "scored_at": datetime.now().isoformat()
        }
        
        return result
    
    def _calculate_velocity(self, lead: Dict[str, Any]) -> str:
        """Calculate lead engagement velocity (trend)"""
        
        recent_activity = lead.get("recent_activity_count", 0)
        previous_activity = lead.get("previous_activity_count", 0)
        
        if previous_activity == 0:
            return "new"
        
        change = ((recent_activity - previous_activity) / previous_activity) * 100
        
        if change > 50:
            return "accelerating"
        elif change > 0:
            return "steady"
        elif change > -50:
            return "decelerating"
        else:
            return "cooling"
    
    def _get_recommendation(self, temperature: str, velocity: str) -> Dict[str, str]:
        """Get recommended action based on score and velocity"""
        
        recommendations = {
            "hot": {
                "accelerating": {
                    "action": "IMMEDIATE CONTACT",
                    "priority": "urgent",
                    "message": "Lead is highly engaged and accelerating. Contact immediately via phone."
                },
                "steady": {
                    "action": "PERSONALIZED OUTREACH",
                    "priority": "high",
                    "message": "Lead is hot and stable. Send personalized email within 1 hour."
                },
                "decelerating": {
                    "action": "RE-ENGAGE",
                    "priority": "high",
                    "message": "Lead was hot but cooling. Send targeted offer to re-engage."
                },
                "cooling": {
                    "action": "URGENT INTERVENTION",
                    "priority": "urgent",
                    "message": "Hot lead is cooling fast. Call immediately with special offer."
                }
            },
            "warm": {
                "accelerating": {
                    "action": "NURTURE",
                    "priority": "medium",
                    "message": "Lead is warming up. Add to nurture sequence."
                },
                "steady": {
                    "action": "FOLLOW UP",
                    "priority": "medium",
                    "message": "Lead is warm. Send follow-up email with case study."
                },
                "decelerating": {
                    "action": "VALUE ADD",
                    "priority": "medium",
                    "message": "Lead is cooling. Send valuable content to re-engage."
                },
                "cooling": {
                    "action": "RE-ENGAGE",
                    "priority": "medium",
                    "message": "Lead is going cold. Send special offer or free resource."
                }
            },
            "cold": {
                "accelerating": {
                    "action": "NURTURE",
                    "priority": "low",
                    "message": "Lead is warming up slowly. Add to long-term nurture."
                },
                "steady": {
                    "action": "EDUCATE",
                    "priority": "low",
                    "message": "Lead is cold. Send educational content to build trust."
                },
                "decelerating": {
                    "action": "MONITOR",
                    "priority": "low",
                    "message": "Lead is barely active. Monitor but don't invest time."
                },
                "cooling": {
                    "action": "ARCHIVE",
                    "priority": "low",
                    "message": "Lead is dead. Archive and focus on warmer leads."
                }
            },
            "dead": {
                "accelerating": {
                    "action": "MONITOR",
                    "priority": "low",
                    "message": "Dead lead showing signs of life. Monitor closely."
                },
                "steady": {
                    "action": "ARCHIVE",
                    "priority": "low",
                    "message": "Lead is dead. Archive for future reactivation campaigns."
                },
                "decelerating": {
                    "action": "ARCHIVE",
                    "priority": "low",
                    "message": "Lead is inactive. Archive immediately."
                },
                "cooling": {
                    "action": "ARCHIVE",
                    "priority": "low",
                    "message": "Lead is inactive. Archive immediately."
                }
            }
        }
        
        return recommendations.get(temperature, {}).get(velocity, {
            "action": "MONITOR",
            "priority": "low",
            "message": "Continue monitoring this lead."
        })
    
    def batch_score(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score multiple leads and return summary"""
        
        scored_leads = []
        temperature_counts = {"hot": 0, "warm": 0, "cold": 0, "dead": 0}
        
        for lead in leads:
            result = self.score_lead(lead)
            scored_leads.append(result)
            temperature_counts[result["temperature"]] += 1
        
        # Sort by score (highest first)
        scored_leads.sort(key=lambda x: x["total_score"], reverse=True)
        
        return {
            "total_leads": len(leads),
            "scored_leads": scored_leads,
            "temperature_distribution": temperature_counts,
            "average_score": sum(l["total_score"] for l in scored_leads) / len(scored_leads) if leads else 0,
            "high_priority_count": temperature_counts["hot"] + temperature_counts["warm"]
        }
    
    def get_lead_profile(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive lead profile"""
        
        score_result = self.score_lead(lead)
        
        profile = {
            "basic_info": {
                "name": lead.get("name"),
                "email": lead.get("email"),
                "company": lead.get("company"),
                "title": lead.get("title"),
                "phone": lead.get("phone")
            },
            "scoring": score_result,
            "engagement_summary": {
                "total_emails_opened": lead.get("email_open_count", 0),
                "total_links_clicked": lead.get("email_click_count", 0),
                "pages_visited": lead.get("website_visit_count", 0),
                "forms_filled": lead.get("form_submission_count", 0),
                "social_interactions": lead.get("social_interaction_count", 0)
            },
            "timeline": lead.get("activity_timeline", []),
            "next_steps": score_result["recommended_action"]
        }
        
        return profile


# Example usage
if __name__ == "__main__":
    scorer = LeadScorer()
    
    # Sample lead
    lead = {
        "id": "lead_001",
        "name": "John Smith",
        "email": "john@example.com",
        "company": "Acme Corp",
        "title": "CEO",
        "website_visited_pricing": True,
        "website_visited_demo": True,
        "form_filled_demo_request": True,
        "email_opened_email": True,
        "email_clicked_link": True,
        "social_liked_post": True,
        "firm_company_size_50plus": True,
        "firm_decision_maker": True,
        "recent_activity_count": 15,
        "previous_activity_count": 8
    }
    
    result = scorer.score_lead(lead)
    print(f"Score: {result['total_score']}")
    print(f"Temperature: {result['temperature']}")
    print(f"Action: {result['recommended_action']['action']}")
    print(f"Message: {result['recommended_action']['message']}")
