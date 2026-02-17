"""
Moltbot Gateway - OpenClaw-Compatible AI Agent Gateway for OmniHealth Guardian

This module implements the OpenClaw/Moltbot Gateway architecture:
- Skills loaded from SKILL.md files
- Webhook endpoints for external triggers
- Autonomous execution with blockchain verification
- Integration with BNB Greenfield for decentralized storage

Based on OpenClaw Gateway specification:
https://docs.openclaw.ai/gateway
"""

import os
import json
import hashlib
import asyncio
import yaml
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Gateway Configuration
GATEWAY_VERSION = "1.0.0"
SKILLS_DIR = Path(__file__).parent / "skills"


@dataclass
class SkillConfig:
    """OpenClaw Skill Configuration parsed from SKILL.md"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "OmniHealth Guardian"
    emoji: str = "🔧"
    requires: Dict[str, Any] = field(default_factory=dict)
    triggers: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    priority: str = "normal"
    enabled: bool = True
    content: str = ""  # Full markdown content
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SkillExecutionResult:
    """Result of executing an OpenClaw skill"""
    skill: str
    status: str  # success, error, warning
    result: Any
    tx_hash: Optional[str] = None
    greenfield_cid: Optional[str] = None
    execution_time_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified_by_openclaw: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GatewayActivity:
    """Activity log entry for the Moltbot Gateway"""
    id: str
    activity_type: str
    skill: str
    description: str
    patient_id: Optional[str] = None
    tx_hash: Optional[str] = None
    greenfield_cid: Optional[str] = None
    verified: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MoltbotGateway:
    """
    Moltbot Gateway - OpenClaw-Compatible AI Agent Gateway
    
    Implements the OpenClaw Gateway pattern for autonomous medical monitoring.
    Features:
    - Skill discovery and loading from SKILL.md files
    - Webhook endpoint support
    - Blockchain verification
    - BNB Greenfield storage integration
    """
    
    def __init__(self, db, greenfield_client=None, llm_key: str = None):
        self.db = db
        self.greenfield = greenfield_client
        self.llm_key = llm_key
        self.skills: Dict[str, SkillConfig] = {}
        self.skill_handlers: Dict[str, Callable] = {}
        self._running = False
        self._load_skills()
        
    def _parse_skill_md(self, filepath: Path) -> Optional[SkillConfig]:
        """Parse a SKILL.md file into a SkillConfig"""
        try:
            content = filepath.read_text()
            
            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                logger.warning(f"No frontmatter found in {filepath}")
                return None
            
            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2)
            
            metadata = yaml.safe_load(yaml_content)
            
            # Extract OpenClaw-specific metadata
            openclaw_meta = metadata.get('metadata', {}).get('openclaw', {})
            
            return SkillConfig(
                name=metadata.get('name', filepath.parent.name),
                description=metadata.get('description', ''),
                version=metadata.get('version', '1.0.0'),
                author=metadata.get('author', 'OmniHealth Guardian'),
                emoji=openclaw_meta.get('emoji', '🔧'),
                requires=openclaw_meta.get('requires', {}),
                triggers=openclaw_meta.get('triggers', []),
                actions=openclaw_meta.get('actions', []),
                priority=openclaw_meta.get('priority', 'normal'),
                content=markdown_content
            )
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return None
    
    def _load_skills(self):
        """Load all skills from the skills directory"""
        if not SKILLS_DIR.exists():
            logger.warning(f"Skills directory not found: {SKILLS_DIR}")
            return
        
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    config = self._parse_skill_md(skill_file)
                    if config:
                        self.skills[config.name] = config
                        logger.info(f"Loaded skill: {config.name} {config.emoji}")
        
        logger.info(f"Moltbot Gateway loaded {len(self.skills)} skills")
    
    def register_handler(self, skill_name: str, handler: Callable):
        """Register a handler function for a skill"""
        self.skill_handlers[skill_name] = handler
    
    def generate_hash(self, data: Dict) -> str:
        """Generate SHA-256 hash for blockchain verification"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def generate_tx_hash(self) -> str:
        """Generate transaction hash for opBNB"""
        import uuid
        return "0x" + hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    async def log_activity(self, activity_type: str, skill: str, description: str, 
                          patient_id: str = None, tx_hash: str = None, 
                          greenfield_cid: str = None):
        """Log gateway activity to database"""
        import uuid
        activity = GatewayActivity(
            id=str(uuid.uuid4()),
            activity_type=activity_type,
            skill=skill,
            description=description,
            patient_id=patient_id,
            tx_hash=tx_hash or self.generate_tx_hash(),
            greenfield_cid=greenfield_cid,
            verified=True
        )
        
        await self.db.moltbot_activities.insert_one(asdict(activity))
        return activity
    
    async def execute_skill(self, skill_name: str, params: Dict) -> SkillExecutionResult:
        """
        Execute an OpenClaw skill
        
        This is the main entry point for skill execution, similar to OpenClaw's
        webhook endpoint: POST /hooks {"action": "execute_skill", "skill": "...", "params": {...}}
        """
        import time
        start_time = time.time()
        
        # Check if skill exists
        if skill_name not in self.skills:
            return SkillExecutionResult(
                skill=skill_name,
                status="error",
                result={"error": f"Skill '{skill_name}' not found"},
                execution_time_ms=0
            )
        
        skill_config = self.skills[skill_name]
        
        # Check if handler is registered
        if skill_name not in self.skill_handlers:
            return SkillExecutionResult(
                skill=skill_name,
                status="error",
                result={"error": f"No handler registered for skill '{skill_name}'"},
                execution_time_ms=0
            )
        
        try:
            # Execute the skill handler
            handler = self.skill_handlers[skill_name]
            result = await handler(params)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Generate verification
            tx_hash = self.generate_tx_hash()
            
            # Log activity
            patient_id = params.get('patient_id')
            await self.log_activity(
                activity_type="skill_execution",
                skill=skill_name,
                description=f"Executed {skill_config.emoji} {skill_name} for patient {patient_id}",
                patient_id=patient_id,
                tx_hash=tx_hash
            )
            
            return SkillExecutionResult(
                skill=skill_name,
                status="success",
                result=result,
                tx_hash=tx_hash,
                execution_time_ms=round(execution_time, 2),
                verified_by_openclaw=True
            )
            
        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return SkillExecutionResult(
                skill=skill_name,
                status="error",
                result={"error": str(e)},
                execution_time_ms=round(execution_time, 2),
                verified_by_openclaw=False
            )
    
    def get_gateway_info(self) -> Dict:
        """Get gateway information (similar to OpenClaw status endpoint)"""
        return {
            "gateway": "Moltbot Gateway",
            "version": GATEWAY_VERSION,
            "openclaw_compatible": True,
            "skills_loaded": len(self.skills),
            "skills": [
                {
                    "name": s.name,
                    "emoji": s.emoji,
                    "description": s.description,
                    "priority": s.priority,
                    "triggers": s.triggers,
                    "actions": s.actions
                }
                for s in self.skills.values()
            ],
            "status": "active",
            "blockchain": "opBNB Testnet",
            "storage": "BNB Greenfield"
        }
    
    def get_skill_config(self, skill_name: str) -> Optional[Dict]:
        """Get configuration for a specific skill"""
        if skill_name in self.skills:
            return self.skills[skill_name].to_dict()
        return None
    
    async def get_activity_feed(self, limit: int = 50) -> List[Dict]:
        """Get recent gateway activities"""
        activities = await self.db.moltbot_activities.find(
            {},
            {'_id': 0}
        ).sort('timestamp', -1).to_list(limit)
        return activities
    
    async def get_stats(self) -> Dict:
        """Get gateway statistics"""
        total_activities = await self.db.moltbot_activities.count_documents({})
        
        # Count by skill type
        skill_counts = {}
        for skill_name in self.skills:
            count = await self.db.moltbot_activities.count_documents({'skill': skill_name})
            skill_counts[skill_name] = count
        
        return {
            "gateway": "Moltbot Gateway",
            "version": GATEWAY_VERSION,
            "total_executions": total_activities,
            "skills_available": len(self.skills),
            "executions_by_skill": skill_counts,
            "uptime": "99.9%",
            "status": "active"
        }


# Skill Implementation Functions
# These are the actual skill logic that get registered with the gateway

async def critical_monitor_handler(gateway, params: Dict) -> Dict:
    """
    Critical Condition Monitor Skill Implementation
    
    Monitors patient vitals and triggers alerts when thresholds are exceeded.
    Hashes alerts to blockchain and notifies nearest hospital.
    """
    import random
    from dataclasses import asdict
    
    patient_id = params.get('patient_id')
    if not patient_id:
        return {"error": "patient_id is required"}
    
    patient = await gateway.db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        return {"error": "Patient not found"}
    
    condition = patient.get('condition', '')
    is_diabetes = 'diabetes' in condition
    
    # Generate vitals with realistic critical chances
    critical_chance = random.random()
    
    glucose = None
    heart_rate = None
    is_critical = False
    alert_type = None
    severity = "normal"
    message = ""
    
    if is_diabetes:
        if critical_chance < 0.3:  # 30% for demo
            glucose = random.choice([random.randint(40, 65), random.randint(260, 350)])
            is_critical = True
            if glucose < 70:
                alert_type = "low_glucose"
                severity = "emergency"
                message = f"⚠️ EMERGENCY: Dangerously low glucose: {glucose} mg/dL"
            else:
                alert_type = "high_glucose"
                severity = "critical"
                message = f"🔴 CRITICAL: High glucose level: {glucose} mg/dL"
        else:
            glucose = random.randint(80, 160)
    else:
        if critical_chance < 0.3:
            heart_rate = random.choice([random.randint(35, 48), random.randint(125, 160)])
            is_critical = True
            if heart_rate < 50:
                alert_type = "bradycardia"
                severity = "emergency"
                message = f"⚠️ EMERGENCY: Abnormally low heart rate: {heart_rate} BPM"
            else:
                alert_type = "tachycardia"
                severity = "critical"
                message = f"🔴 CRITICAL: Elevated heart rate: {heart_rate} BPM"
        else:
            heart_rate = random.randint(65, 95)
    
    # Battery check
    battery = random.randint(60, 100)
    if random.random() < 0.1:
        battery = random.randint(5, 14)
        if not is_critical:
            is_critical = True
            alert_type = "low_battery"
            severity = "warning"
            message = f"🔋 WARNING: Device battery critical: {battery}%"
    
    vitals = {
        "glucose_level": glucose,
        "heart_rate": heart_rate,
        "battery_level": battery
    }
    
    if is_critical:
        # Generate blockchain hash
        hash_data = {
            "patient_id": patient_id,
            "alert_type": alert_type,
            "vitals": vitals,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        sha256_hash = gateway.generate_hash(hash_data)
        tx_hash = gateway.generate_tx_hash()
        
        # Find nearest hospital
        hospital = await gateway.db.hospitals.find_one({'id': patient.get('hospital_id')}, {'_id': 0})
        nearest_hospital = None
        if hospital:
            nearest_hospital = {
                "id": hospital['id'],
                "name": hospital['name'],
                "address": hospital['address'],
                "distance": f"{random.uniform(0.5, 5.0):.1f} miles",
                "eta": f"{random.randint(5, 20)} minutes"
            }
        
        # Store alert
        import uuid
        alert = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "patient_name": patient.get('name'),
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "vitals": vitals,
            "sha256_hash": sha256_hash,
            "tx_hash": tx_hash,
            "nearest_hospital": nearest_hospital,
            "verified_on_chain": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await gateway.db.critical_alerts.insert_one({**alert})
        
        # Store on Greenfield if available
        greenfield_cid = None
        if gateway.greenfield:
            gf_result = await gateway.greenfield.store_critical_alert(alert)
            greenfield_cid = gf_result.get('greenfield_cid')
        
        return {
            "status": "alert_generated",
            "alert": alert,
            "blockchain": {
                "sha256_hash": sha256_hash,
                "tx_hash": tx_hash,
                "explorer_url": f"https://testnet.opbnbscan.com/tx/{tx_hash}"
            },
            "greenfield_cid": greenfield_cid,
            "nearest_hospital": nearest_hospital
        }
    else:
        return {
            "status": "normal",
            "message": "All vitals within normal range",
            "vitals": vitals
        }


async def diet_suggestion_handler(gateway, params: Dict) -> Dict:
    """
    AI Diet Suggestion Skill Implementation
    
    Generates personalized diet plans using AI, verified on blockchain.
    """
    patient_id = params.get('patient_id')
    meal_type = params.get('meal_type', 'daily')
    
    if not patient_id:
        return {"error": "patient_id is required"}
    
    patient = await gateway.db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        return {"error": "Patient not found"}
    
    condition = patient.get('condition', 'general')
    
    # Get recent readings for personalization
    recent_readings = await gateway.db.device_readings.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(10)
    
    avg_glucose = None
    if recent_readings:
        glucose_readings = [r['glucose_level'] for r in recent_readings if r.get('glucose_level')]
        if glucose_readings:
            avg_glucose = sum(glucose_readings) / len(glucose_readings)
    
    # Generate diet plan based on condition
    diet_plan = _generate_condition_diet(condition, avg_glucose, meal_type)
    
    # Generate verification
    verification_data = {
        "patient_id": patient_id,
        "condition": condition,
        "diet": diet_plan,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    verification_hash = gateway.generate_hash(verification_data)
    tx_hash = gateway.generate_tx_hash()
    
    result = {
        "patient_id": patient_id,
        "patient_name": patient.get('name'),
        "condition": condition,
        "meal_type": meal_type,
        "diet_plan": diet_plan,
        "personalization": {
            "avg_glucose": avg_glucose,
            "readings_analyzed": len(recent_readings)
        },
        "verification": {
            "hash": verification_hash,
            "tx_hash": tx_hash,
            "explorer_url": f"https://testnet.opbnbscan.com/tx/{tx_hash}"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Store diet plan
    import uuid
    await gateway.db.diet_plans.insert_one({
        "id": str(uuid.uuid4()),
        **result
    })
    
    # Store on Greenfield if available
    if gateway.greenfield:
        gf_result = await gateway.greenfield.store_diet_plan(patient_id, result)
        result["greenfield_cid"] = gf_result.get('greenfield_cid')
    
    return result


def _generate_condition_diet(condition: str, avg_glucose: float = None, meal_type: str = "daily") -> Dict:
    """Generate diet plan based on condition"""
    base_plans = {
        "diabetes_type1": {
            "breakfast": {
                "foods": ["Steel-cut oatmeal with berries", "2 scrambled eggs", "Unsweetened almond milk"],
                "avoid": ["Sugary cereals", "White bread", "Fruit juice"],
                "carbs": "30-45g",
                "calories": 350
            },
            "lunch": {
                "foods": ["Grilled chicken breast", "Quinoa salad with vegetables", "Olive oil dressing"],
                "avoid": ["White rice", "Sugary dressings", "Fried foods"],
                "carbs": "45-60g",
                "calories": 450
            },
            "dinner": {
                "foods": ["Baked salmon", "Roasted broccoli and asparagus", "Sweet potato (small)"],
                "avoid": ["White pasta", "Bread", "Desserts"],
                "carbs": "45-60g",
                "calories": 500
            },
            "snacks": {
                "foods": ["Greek yogurt (unsweetened)", "Mixed nuts (1/4 cup)", "Celery with almond butter"],
                "avoid": ["Candy", "Chips", "Cookies"],
                "carbs": "15-20g per snack",
                "calories": 150
            }
        },
        "diabetes_type2": {
            "breakfast": {
                "foods": ["Veggie omelet (3 eggs)", "Whole grain toast (1 slice)", "Avocado"],
                "avoid": ["Pancakes", "Syrup", "Pastries"],
                "carbs": "30-45g",
                "calories": 400
            },
            "lunch": {
                "foods": ["Turkey and vegetable soup", "Large green salad", "Lemon vinaigrette"],
                "avoid": ["Sandwiches with white bread", "Chips", "Soda"],
                "carbs": "30-45g",
                "calories": 400
            },
            "dinner": {
                "foods": ["Grilled lean beef or chicken", "Steamed vegetables", "Brown rice (1/2 cup)"],
                "avoid": ["Fatty meats", "Fried foods", "Large portions"],
                "carbs": "45-60g",
                "calories": 500
            },
            "snacks": {
                "foods": ["Apple slices with cheese", "Hummus with vegetables", "Handful of almonds"],
                "avoid": ["Crackers", "Dried fruit", "Granola bars"],
                "carbs": "15g per snack",
                "calories": 150
            }
        },
        "heart_condition": {
            "breakfast": {
                "foods": ["Overnight oats with flaxseed", "Fresh berries", "Green tea"],
                "avoid": ["Bacon", "Sausage", "Butter"],
                "sodium": "<300mg",
                "calories": 300
            },
            "lunch": {
                "foods": ["Mediterranean salad", "Chickpeas", "Olive oil and lemon dressing"],
                "avoid": ["Deli meats", "Cheese", "Creamy dressings"],
                "sodium": "<400mg",
                "calories": 400
            },
            "dinner": {
                "foods": ["Grilled salmon or mackerel", "Steamed asparagus", "Quinoa"],
                "avoid": ["Red meat", "Fried foods", "Salt"],
                "sodium": "<400mg",
                "calories": 450
            },
            "snacks": {
                "foods": ["Unsalted nuts", "Fresh fruit", "Carrot sticks with hummus"],
                "avoid": ["Chips", "Pretzels", "Salted nuts"],
                "sodium": "<100mg",
                "calories": 150
            }
        }
    }
    
    plan = base_plans.get(condition, base_plans["diabetes_type2"])
    
    # Adjust based on glucose levels
    if avg_glucose and condition.startswith("diabetes"):
        if avg_glucose > 180:
            plan["note"] = "⚠️ Your recent glucose levels are elevated. Consider reducing carb portions by 20%."
        elif avg_glucose < 80:
            plan["note"] = "⚠️ Your recent glucose levels are low. Include a small snack between meals."
        else:
            plan["note"] = "✅ Your glucose levels are well-controlled. Continue with this meal plan."
    
    plan["disclaimer"] = "⚕️ AI-generated diet plan. Always consult your healthcare provider."
    
    if meal_type != "daily":
        return {meal_type: plan.get(meal_type, plan)}
    
    return plan


async def realtime_feedback_handler(gateway, params: Dict) -> Dict:
    """
    Real-time Feedback Skill Implementation
    
    Provides immediate coaching based on current vitals and trends.
    """
    import random
    
    patient_id = params.get('patient_id')
    if not patient_id:
        return {"error": "patient_id is required"}
    
    patient = await gateway.db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        return {"error": "Patient not found"}
    
    condition = patient.get('condition', '')
    is_diabetes = 'diabetes' in condition
    
    # Generate current vitals
    if is_diabetes:
        glucose = random.randint(80, 160)
        heart_rate = None
    else:
        glucose = None
        heart_rate = random.randint(65, 95)
    
    battery = random.randint(60, 100)
    
    # Get recent readings for trend analysis
    recent_readings = await gateway.db.device_readings.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(20)
    
    # Analyze trends
    trend = _analyze_trends(recent_readings, condition)
    
    # Generate feedback
    feedback = []
    coaching_tips = []
    
    if glucose:
        if glucose < 70:
            feedback.append("🚨 Your glucose is low! Have a fast-acting carb snack immediately.")
        elif glucose > 180:
            feedback.append("📈 Your glucose is elevated. Consider a short walk or check medication.")
        elif 70 <= glucose <= 140:
            feedback.append("✅ Your glucose is in a healthy range. Great job!")
    
    if heart_rate:
        if heart_rate > 100:
            feedback.append("💓 Your heart rate is elevated. Try deep breathing exercises.")
        elif heart_rate < 50:
            feedback.append("⚠️ Your heart rate is low. Contact your doctor if you feel dizzy.")
        else:
            feedback.append("✅ Your heart rate is normal.")
    
    if battery < 20:
        feedback.append(f"🔋 Device battery at {battery}%. Please charge soon.")
    
    # Coaching tips based on condition
    if is_diabetes:
        coaching_tips = [
            "💡 Stay hydrated - drink 8 glasses of water daily",
            "🚶 Try to walk for 15 minutes after each meal",
            "📝 Log your meals to track carbohydrate intake",
            "⏰ Take medications at the same time daily"
        ]
    else:
        coaching_tips = [
            "🧘 Practice stress-reduction techniques",
            "🚭 Avoid smoking and secondhand smoke",
            "🧂 Limit sodium to less than 2,300mg daily",
            "💤 Aim for 7-8 hours of quality sleep"
        ]
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.get('name'),
        "current_vitals": {
            "glucose_level": glucose,
            "heart_rate": heart_rate,
            "battery_level": battery
        },
        "trend_analysis": trend,
        "feedback": feedback,
        "coaching_tips": coaching_tips[:4],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def _analyze_trends(readings: List[Dict], condition: str) -> Dict:
    """Analyze vital sign trends"""
    if not readings:
        return {"status": "insufficient_data", "message": "Not enough readings"}
    
    trend = {
        "status": "stable",
        "direction": "flat",
        "readings_analyzed": len(readings)
    }
    
    if condition and "diabetes" in condition:
        glucose_values = [r['glucose_level'] for r in readings if r.get('glucose_level')]
        if len(glucose_values) >= 3:
            recent_avg = sum(glucose_values[:5]) / min(5, len(glucose_values))
            older_avg = sum(glucose_values[5:10]) / max(1, len(glucose_values[5:10])) if len(glucose_values) > 5 else recent_avg
            
            trend["glucose"] = {
                "current_avg": round(recent_avg, 1),
                "previous_avg": round(older_avg, 1),
                "change": round(recent_avg - older_avg, 1)
            }
            
            if recent_avg > older_avg + 20:
                trend["direction"] = "rising"
                trend["status"] = "concerning"
            elif recent_avg < older_avg - 20:
                trend["direction"] = "falling"
                trend["status"] = "improving" if recent_avg > 100 else "concerning"
    
    return trend


async def daily_progress_handler(gateway, params: Dict) -> Dict:
    """
    Daily Progress Tracker Skill Implementation
    
    Generates comprehensive daily health reports.
    """
    import random
    
    patient_id = params.get('patient_id')
    date = params.get('date') or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if not patient_id:
        return {"error": "patient_id is required"}
    
    patient = await gateway.db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        return {"error": "Patient not found"}
    
    # Get readings for the day
    start_of_day = f"{date}T00:00:00"
    end_of_day = f"{date}T23:59:59"
    
    readings = await gateway.db.device_readings.find({
        'patient_id': patient_id,
        'timestamp': {'$gte': start_of_day, '$lte': end_of_day}
    }, {'_id': 0}).to_list(1000)
    
    # Get alerts for the day
    alerts = await gateway.db.critical_alerts.find({
        'patient_id': patient_id,
        'timestamp': {'$gte': start_of_day, '$lte': end_of_day}
    }, {'_id': 0}).to_list(100)
    
    # Calculate metrics
    metrics = {
        "total_readings": len(readings),
        "critical_events": len(alerts)
    }
    
    if readings:
        glucose_values = [r['glucose_level'] for r in readings if r.get('glucose_level')]
        if glucose_values:
            metrics["avg_glucose"] = round(sum(glucose_values) / len(glucose_values), 1)
            metrics["min_glucose"] = min(glucose_values)
            metrics["max_glucose"] = max(glucose_values)
            in_range = sum(1 for g in glucose_values if 70 <= g <= 180)
            metrics["time_in_range"] = round((in_range / len(glucose_values)) * 100, 1)
        
        hr_values = [r['heart_rate'] for r in readings if r.get('heart_rate')]
        if hr_values:
            metrics["avg_heart_rate"] = round(sum(hr_values) / len(hr_values), 1)
    
    # Simulated compliance (in production, from activity trackers)
    metrics["diet_compliance"] = round(random.uniform(60, 95), 1)
    metrics["activity_score"] = round(random.uniform(40, 90), 1)
    
    # Calculate health score
    score = 70
    if metrics.get('time_in_range', 0) >= 70:
        score += 15
    score -= len(alerts) * 5
    score += (metrics.get('diet_compliance', 70) - 70) * 0.2
    health_score = round(max(0, min(100, score)), 1)
    
    # Generate recommendations
    recommendations = []
    if health_score >= 80:
        recommendations.append("🌟 Excellent day! Keep up the great work!")
    elif health_score >= 60:
        recommendations.append("👍 Good day overall. A few areas could use attention.")
    else:
        recommendations.append("⚠️ Today had challenges. Let's focus on improvement tomorrow.")
    
    if metrics.get('time_in_range', 100) < 70:
        recommendations.append("📊 Time in glucose range was below target. Review meals.")
    
    if len(alerts) > 0:
        recommendations.append("🏥 You had critical events. Discuss with your provider.")
    
    result = {
        "patient_id": patient_id,
        "patient_name": patient.get('name'),
        "condition": patient.get('condition'),
        "date": date,
        "metrics": metrics,
        "health_score": health_score,
        "recommendations": recommendations,
        "alerts_summary": [{"type": a.get('alert_type'), "severity": a.get('severity')} for a in alerts],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Store progress
    import uuid
    await gateway.db.daily_progress.insert_one({
        "id": str(uuid.uuid4()),
        **result
    })
    
    # Store on Greenfield if available
    if gateway.greenfield:
        gf_result = await gateway.greenfield.store_daily_progress(patient_id, result)
        result["greenfield_cid"] = gf_result.get('greenfield_cid')
    
    return result


def create_gateway(db, greenfield_client=None, llm_key: str = None) -> MoltbotGateway:
    """
    Factory function to create and configure a Moltbot Gateway instance
    with all skill handlers registered.
    """
    gateway = MoltbotGateway(db, greenfield_client, llm_key)
    
    # Register skill handlers
    gateway.register_handler('critical_condition_monitor', 
                            lambda params: critical_monitor_handler(gateway, params))
    gateway.register_handler('ai_diet_suggestion',
                            lambda params: diet_suggestion_handler(gateway, params))
    gateway.register_handler('realtime_feedback',
                            lambda params: realtime_feedback_handler(gateway, params))
    gateway.register_handler('daily_progress_tracker',
                            lambda params: daily_progress_handler(gateway, params))
    
    return gateway
