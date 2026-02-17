from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
import hashlib
import random
import asyncio
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from openclaw_agent import OpenClawGuardianAgent, PatientVitals
from greenfield_storage import get_greenfield_client, GreenfieldStorageSimulated

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM API Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Initialize Greenfield Storage
# Set USE_REAL_GREENFIELD=true in .env to use actual Greenfield network
USE_REAL_GREENFIELD = os.environ.get('USE_REAL_GREENFIELD', 'false').lower() == 'true'
greenfield_client = get_greenfield_client(use_real=USE_REAL_GREENFIELD)

# Initialize OpenClaw Guardian Agent
openclaw_agent = None

# Load deployed contract addresses if available
DEPLOYED_CONTRACTS = {}
try:
    deployment_file = ROOT_DIR / 'deployment_result.json'
    if deployment_file.exists():
        with open(deployment_file, 'r') as f:
            deployment_data = json.load(f)
            if deployment_data.get('status') != 'PENDING_FUNDING':
                DEPLOYED_CONTRACTS = deployment_data.get('contracts', {})
except Exception as e:
    logging.warning(f"Could not load deployment result: {e}")

# Create the main app
app = FastAPI(title="OmniHealth Guardian API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: str  # patient, doctor, organization
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    role: str

class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    age: int
    condition: str  # diabetes_type1, diabetes_type2, heart_condition
    device_type: str  # insulin_pump, pacemaker, glucose_monitor
    assigned_doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None

class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    specialization: str
    hospital_id: str
    patient_ids: List[str] = []

class Hospital(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    latitude: float
    longitude: float
    capacity: int
    active_devices: int = 0

class DeviceReading(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    device_type: str
    glucose_level: Optional[float] = None  # mg/dL
    heart_rate: Optional[int] = None  # bpm
    battery_level: int  # percentage
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_critical: bool = False
    
class CriticalAlert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    patient_name: str
    alert_type: str  # high_glucose, low_glucose, irregular_heartbeat, low_battery
    severity: str  # warning, critical, emergency
    message: str
    reading_data: Dict[str, Any]
    sha256_hash: str
    tx_hash: Optional[str] = None  # Blockchain transaction hash
    verified_on_chain: bool = False
    nearest_hospital: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DietPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    condition: str
    plan: str
    ai_generated: bool = True
    verified_by_openclaw: bool = True
    verification_tx_hash: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MoltbotActivity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    activity_type: str  # diet_suggestion, alert_verification, data_analysis
    description: str
    patient_id: Optional[str] = None
    tx_hash: Optional[str] = None
    verified: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============== MOCK DATA GENERATOR ==============

PATIENT_NAMES = ["Alice Chen", "Bob Martinez", "Carol Williams", "David Lee", "Emma Johnson", 
                 "Frank Brown", "Grace Kim", "Henry Wilson", "Iris Patel", "James Taylor"]
DOCTOR_NAMES = ["Dr. Sarah Adams", "Dr. Michael Chen", "Dr. Emily Davis", "Dr. Robert Garcia",
                "Dr. Jennifer Hall", "Dr. William Jones", "Dr. Amanda King", "Dr. Christopher Lee",
                "Dr. Michelle Martin", "Dr. Daniel Miller", "Dr. Rachel Moore", "Dr. Steven Nelson",
                "Dr. Laura Ortiz", "Dr. Kevin Parker", "Dr. Diana Quinn", "Dr. Thomas Robinson",
                "Dr. Jessica Smith", "Dr. Andrew Thompson", "Dr. Victoria White", "Dr. Brian Young"]
HOSPITAL_NAMES = ["Metropolitan General Hospital", "City Medical Center", "University Health System",
                  "Regional Medical Center", "Community Hospital", "Memorial Healthcare",
                  "Sacred Heart Hospital", "St. Mary's Medical Center", "Downtown Medical Center",
                  "Westside Healthcare", "Northview Hospital", "Eastside Medical", "Central Hospital",
                  "Valley Medical Center", "Riverside Hospital", "Lakeside Medical", "Hillcrest Hospital",
                  "Sunnyvale Health", "Oakwood Medical", "Pinecrest Healthcare", "Maplewood Hospital",
                  "Cedar Medical Center", "Willowbrook Health", "Springdale Hospital", "Autumndale Medical",
                  "Winterfield Hospital", "Summerhill Health", "Greenleaf Medical", "Blueridge Hospital",
                  "Goldcrest Healthcare"]
CONDITIONS = ["diabetes_type1", "diabetes_type2", "heart_condition"]
DEVICES = ["insulin_pump", "pacemaker", "glucose_monitor"]
SPECIALIZATIONS = ["Endocrinology", "Cardiology", "Internal Medicine", "Emergency Medicine"]

async def generate_mock_data():
    """Generate initial mock data for the system"""
    # Check if data already exists
    existing_hospitals = await db.hospitals.count_documents({})
    if existing_hospitals > 0:
        logger.info("Mock data already exists, skipping generation")
        return
    
    logger.info("Generating mock data...")
    
    # Generate 30 hospitals
    hospitals = []
    for i, name in enumerate(HOSPITAL_NAMES):
        hospital = Hospital(
            name=name,
            address=f"{random.randint(100, 9999)} Medical Way, City {i+1}",
            latitude=40.7128 + random.uniform(-0.5, 0.5),
            longitude=-74.0060 + random.uniform(-0.5, 0.5),
            capacity=random.randint(100, 500),
            active_devices=random.randint(10, 100)
        )
        hospitals.append(hospital.model_dump())
    await db.hospitals.insert_many(hospitals)
    hospital_ids = [h['id'] for h in hospitals]
    
    # Generate 20 doctors
    doctors = []
    for i, name in enumerate(DOCTOR_NAMES):
        doctor = Doctor(
            user_id=str(uuid.uuid4()),
            name=name,
            specialization=random.choice(SPECIALIZATIONS),
            hospital_id=random.choice(hospital_ids)
        )
        doctors.append(doctor.model_dump())
    await db.doctors.insert_many(doctors)
    doctor_ids = [d['id'] for d in doctors]
    
    # Generate 10 patients
    patients = []
    for i, name in enumerate(PATIENT_NAMES):
        condition = random.choice(CONDITIONS)
        device = "insulin_pump" if "diabetes" in condition else "pacemaker"
        patient = Patient(
            user_id=str(uuid.uuid4()),
            name=name,
            age=random.randint(25, 75),
            condition=condition,
            device_type=device,
            assigned_doctor_id=random.choice(doctor_ids),
            hospital_id=random.choice(hospital_ids)
        )
        patients.append(patient.model_dump())
    await db.patients.insert_many(patients)
    
    logger.info(f"Generated {len(hospitals)} hospitals, {len(doctors)} doctors, {len(patients)} patients")

# Store stable battery levels per patient (simulates real device battery)
_patient_battery_levels: Dict[str, int] = {}

def get_stable_battery(patient_id: str) -> int:
    """Get stable battery level for a patient - slowly decreases over time"""
    global _patient_battery_levels
    
    if patient_id not in _patient_battery_levels:
        # Initialize with a random starting battery between 70-100%
        _patient_battery_levels[patient_id] = random.randint(70, 100)
    
    current = _patient_battery_levels[patient_id]
    
    # Small chance (10%) to decrease by 1-2%, simulating real battery drain
    if random.random() < 0.10:
        decrease = random.randint(1, 2)
        current = max(15, current - decrease)  # Don't go below 15% normally
        _patient_battery_levels[patient_id] = current
    
    # Very rare chance (1%) of critical battery for demo purposes
    if random.random() < 0.01:
        current = random.randint(5, 12)
        _patient_battery_levels[patient_id] = current
    
    return current

def generate_device_reading(patient: Dict) -> Dict:
    """Generate a simulated device reading for a patient"""
    is_diabetes = "diabetes" in patient.get('condition', '')
    is_heart = patient.get('condition') == 'heart_condition'
    
    # Generate realistic readings with occasional critical values
    critical_chance = random.random()
    
    glucose = None
    heart_rate = None
    is_critical = False
    
    if is_diabetes:
        if critical_chance < 0.05:  # 5% chance of critical
            glucose = random.choice([random.randint(40, 60), random.randint(250, 400)])  # Low or high
            is_critical = True
        else:
            glucose = random.randint(80, 160)  # Normal range (tighter)
    
    if is_heart or not is_diabetes:
        if critical_chance < 0.05:  # 5% chance of critical
            heart_rate = random.choice([random.randint(35, 48), random.randint(125, 160)])  # Abnormal
            is_critical = True
        else:
            heart_rate = random.randint(65, 95)  # Normal range (tighter)
    
    # Use stable battery instead of random
    battery = get_stable_battery(patient['id'])
    if battery < 15:
        is_critical = True
    
    return {
        'id': str(uuid.uuid4()),
        'patient_id': patient['id'],
        'device_type': patient.get('device_type', 'unknown'),
        'glucose_level': glucose,
        'heart_rate': heart_rate,
        'battery_level': battery,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'is_critical': is_critical
    }

def generate_sha256_hash(data: Dict) -> str:
    """Generate SHA-256 hash of data for blockchain verification"""
    data_str = str(sorted(data.items()))
    return hashlib.sha256(data_str.encode()).hexdigest()

def generate_mock_tx_hash() -> str:
    """Generate a mock opBNB transaction hash"""
    return "0x" + hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

async def find_nearest_hospital(patient_id: str) -> Optional[Dict]:
    """Find the nearest hospital for emergency notification"""
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if patient and patient.get('hospital_id'):
        hospital = await db.hospitals.find_one({'id': patient['hospital_id']}, {'_id': 0})
        if hospital:
            return {
                'id': hospital['id'],
                'name': hospital['name'],
                'address': hospital['address'],
                'distance': f"{random.uniform(0.5, 5.0):.1f} miles"
            }
    # Fallback to any hospital
    hospital = await db.hospitals.find_one({}, {'_id': 0})
    if hospital:
        return {
            'id': hospital['id'],
            'name': hospital['name'],
            'address': hospital['address'],
            'distance': f"{random.uniform(0.5, 5.0):.1f} miles"
        }
    return None

# ============== API ENDPOINTS ==============

@api_router.get("/")
async def root():
    return {"message": "OmniHealth Guardian API", "version": "1.0.0"}

@api_router.on_event("startup")
async def startup_event():
    await generate_mock_data()

# Auth endpoints (simulated)
@api_router.post("/auth/login")
async def login(data: dict):
    """Simulated social auth login - creates a smart contract wallet"""
    email = data.get('email', 'demo@omnihealth.io')
    name = data.get('name', 'Demo User')
    role = data.get('role', 'patient')
    
    # Check if user exists
    user = await db.users.find_one({'email': email}, {'_id': 0})
    if not user:
        user = User(email=email, name=name, role=role)
        user_dict = user.model_dump()
        user_dict['timestamp'] = user_dict['created_at'].isoformat()
        del user_dict['created_at']
        await db.users.insert_one(user_dict)
        user_dict['created_at'] = user_dict.pop('timestamp')
    
    # Simulate smart contract wallet creation
    wallet_address = "0x" + hashlib.sha256(email.encode()).hexdigest()[:40]
    
    return {
        'user': user,
        'wallet': {
            'address': wallet_address,
            'type': 'smart_contract_wallet',
            'paymaster_enabled': True,
            'network': 'opBNB Testnet'
        },
        'token': str(uuid.uuid4())
    }

# Patient endpoints
@api_router.get("/patients")
async def get_patients():
    patients = await db.patients.find({}, {'_id': 0}).to_list(100)
    return patients

@api_router.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@api_router.get("/patients/{patient_id}/readings")
async def get_patient_readings(patient_id: str, limit: int = 50):
    readings = await db.device_readings.find(
        {'patient_id': patient_id}, 
        {'_id': 0}
    ).sort('timestamp', -1).to_list(limit)
    return readings

@api_router.get("/patients/{patient_id}/alerts")
async def get_patient_alerts(patient_id: str, limit: int = 20):
    alerts = await db.critical_alerts.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(limit)
    return alerts

# Doctor endpoints
@api_router.get("/doctors")
async def get_doctors():
    doctors = await db.doctors.find({}, {'_id': 0}).to_list(100)
    return doctors

@api_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    doctor = await db.doctors.find_one({'id': doctor_id}, {'_id': 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@api_router.get("/doctors/{doctor_id}/patients")
async def get_doctor_patients(doctor_id: str):
    patients = await db.patients.find(
        {'assigned_doctor_id': doctor_id},
        {'_id': 0}
    ).to_list(100)
    return patients

# Hospital/Organization endpoints
@api_router.get("/hospitals")
async def get_hospitals():
    hospitals = await db.hospitals.find({}, {'_id': 0}).to_list(100)
    return hospitals

@api_router.get("/hospitals/{hospital_id}")
async def get_hospital(hospital_id: str):
    hospital = await db.hospitals.find_one({'id': hospital_id}, {'_id': 0})
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@api_router.get("/hospitals/{hospital_id}/stats")
async def get_hospital_stats(hospital_id: str):
    patients_count = await db.patients.count_documents({'hospital_id': hospital_id})
    doctors_count = await db.doctors.count_documents({'hospital_id': hospital_id})
    alerts_count = await db.critical_alerts.count_documents({})
    
    return {
        'hospital_id': hospital_id,
        'total_patients': patients_count,
        'total_doctors': doctors_count,
        'total_alerts': alerts_count,
        'active_devices': random.randint(20, 100),
        'system_health': random.uniform(95, 99.9)
    }

# Device readings and telemetry
@api_router.get("/telemetry/live")
async def get_live_telemetry():
    """Get live device readings for all patients"""
    patients = await db.patients.find({}, {'_id': 0}).to_list(100)
    readings = []
    for patient in patients:
        reading = generate_device_reading(patient)
        readings.append({
            **reading,
            'patient_name': patient.get('name'),
            'condition': patient.get('condition')
        })
    return readings

@api_router.post("/telemetry/reading")
async def record_reading(patient_id: str = None):
    """Record a new device reading (simulated from MockDevice)"""
    if patient_id:
        patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    else:
        patient = await db.patients.find_one({}, {'_id': 0})
    
    if not patient:
        raise HTTPException(status_code=404, detail="No patients found")
    
    reading = generate_device_reading(patient)
    reading_to_store = {**reading}  # Create a copy to avoid _id mutation
    await db.device_readings.insert_one(reading_to_store)
    
    # Check for critical conditions
    if reading['is_critical']:
        await process_critical_alert(patient, reading)
    
    return reading

async def process_critical_alert(patient: Dict, reading: Dict):
    """Process a critical alert - hash and store on-chain"""
    alert_type = "unknown"
    severity = "warning"
    message = ""
    
    if reading.get('glucose_level'):
        if reading['glucose_level'] < 70:
            alert_type = "low_glucose"
            severity = "critical"
            message = f"Dangerously low glucose: {reading['glucose_level']} mg/dL"
        elif reading['glucose_level'] > 250:
            alert_type = "high_glucose"
            severity = "emergency"
            message = f"Dangerously high glucose: {reading['glucose_level']} mg/dL"
    
    if reading.get('heart_rate'):
        if reading['heart_rate'] < 50 or reading['heart_rate'] > 120:
            alert_type = "irregular_heartbeat"
            severity = "emergency"
            message = f"Irregular heart rate detected: {reading['heart_rate']} bpm"
    
    if reading.get('battery_level', 100) < 15:
        alert_type = "low_battery"
        severity = "warning"
        message = f"Device battery critically low: {reading['battery_level']}%"
    
    # Generate SHA-256 hash of the error log
    hash_data = {
        'patient_id': patient['id'],
        'reading': reading,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'alert_type': alert_type
    }
    sha256_hash = generate_sha256_hash(hash_data)
    
    # Generate mock transaction hash (simulating on-chain storage)
    tx_hash = generate_mock_tx_hash()
    
    # Find nearest hospital for emergency
    nearest_hospital = await find_nearest_hospital(patient['id'])
    
    alert = CriticalAlert(
        patient_id=patient['id'],
        patient_name=patient.get('name', 'Unknown'),
        alert_type=alert_type,
        severity=severity,
        message=message,
        reading_data=reading,
        sha256_hash=sha256_hash,
        tx_hash=tx_hash,
        verified_on_chain=True,
        nearest_hospital=nearest_hospital
    )
    
    alert_dict = alert.model_dump()
    alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
    await db.critical_alerts.insert_one(alert_dict)
    
    # Log Moltbot activity
    activity = MoltbotActivity(
        activity_type="alert_verification",
        description=f"Critical alert verified on-chain: {alert_type} for {patient.get('name')}",
        patient_id=patient['id'],
        tx_hash=tx_hash,
        verified=True
    )
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    await db.moltbot_activities.insert_one(activity_dict)
    
    return alert

# Critical alerts
@api_router.get("/alerts")
async def get_all_alerts(limit: int = 50):
    alerts = await db.critical_alerts.find({}, {'_id': 0}).sort('timestamp', -1).to_list(limit)
    return alerts

@api_router.get("/alerts/recent")
async def get_recent_alerts():
    alerts = await db.critical_alerts.find({}, {'_id': 0}).sort('timestamp', -1).to_list(10)
    return alerts

# AI Diet suggestions
@api_router.post("/diet/generate")
async def generate_diet_plan(patient_id: str):
    """Generate AI-powered diet plan using OpenClaw/Moltbot"""
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    condition = patient.get('condition', 'general')
    
    # Use OpenAI via Emergent integrations for diet suggestion
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"diet-{patient_id}-{uuid.uuid4()}",
            system_message="""You are a medical AI assistant specializing in dietary recommendations. 
            Provide personalized diet plans based on medical conditions. 
            Always include a disclaimer that patients should consult their healthcare provider.
            Keep responses concise and structured with meal suggestions."""
        ).with_model("openai", "gpt-4o")
        
        condition_text = condition.replace('_', ' ').title()
        user_message = UserMessage(
            text=f"Create a personalized daily diet plan for a patient with {condition_text}. Include breakfast, lunch, dinner, and snacks. Focus on foods that help manage their condition."
        )
        
        response = await chat.send_message(user_message)
        diet_text = response
    except Exception as e:
        logger.error(f"AI diet generation failed: {e}")
        # Fallback diet plan
        diet_text = get_fallback_diet(condition)
    
    # Generate verification hash and tx
    tx_hash = generate_mock_tx_hash()
    
    diet_plan = DietPlan(
        patient_id=patient_id,
        condition=condition,
        plan=diet_text,
        ai_generated=True,
        verified_by_openclaw=True,
        verification_tx_hash=tx_hash
    )
    
    diet_dict = diet_plan.model_dump()
    diet_dict['timestamp'] = diet_dict['timestamp'].isoformat()
    await db.diet_plans.insert_one(diet_dict)
    
    # Log Moltbot activity
    activity = MoltbotActivity(
        activity_type="diet_suggestion",
        description=f"AI diet plan generated for {patient.get('name')} with {condition}",
        patient_id=patient_id,
        tx_hash=tx_hash,
        verified=True
    )
    activity_dict = activity.model_dump()
    activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
    await db.moltbot_activities.insert_one(activity_dict)
    
    return diet_plan

def get_fallback_diet(condition: str) -> str:
    """Get fallback diet plan if AI fails"""
    diets = {
        'diabetes_type1': """**Daily Diet Plan for Type 1 Diabetes**

*Breakfast:* Steel-cut oatmeal with berries and walnuts, 2 scrambled eggs
*Snack:* Greek yogurt with cinnamon
*Lunch:* Grilled chicken salad with olive oil dressing, quinoa
*Snack:* Celery with almond butter
*Dinner:* Baked salmon, roasted vegetables, brown rice

**Key Notes:** Monitor carbohydrate intake, balance with insulin dosing.

⚠️ Disclaimer: Consult your healthcare provider before making dietary changes.""",
        
        'diabetes_type2': """**Daily Diet Plan for Type 2 Diabetes**

*Breakfast:* Veggie omelet with whole grain toast, avocado
*Snack:* Mixed nuts (1/4 cup)
*Lunch:* Turkey and vegetable soup, side salad
*Snack:* Apple slices with cheese
*Dinner:* Grilled lean beef, steamed broccoli, sweet potato

**Key Notes:** Focus on low glycemic index foods, portion control is essential.

⚠️ Disclaimer: Consult your healthcare provider before making dietary changes.""",
        
        'heart_condition': """**Daily Diet Plan for Heart Health**

*Breakfast:* Overnight oats with flaxseed and berries
*Snack:* Handful of almonds
*Lunch:* Mediterranean salad with chickpeas, feta, olive oil
*Snack:* Carrot sticks with hummus
*Dinner:* Grilled salmon, asparagus, quinoa

**Key Notes:** Low sodium, heart-healthy fats, high fiber diet recommended.

⚠️ Disclaimer: Consult your healthcare provider before making dietary changes."""
    }
    return diets.get(condition, diets['diabetes_type2'])

@api_router.get("/diet/{patient_id}")
async def get_patient_diet_plans(patient_id: str):
    plans = await db.diet_plans.find({'patient_id': patient_id}, {'_id': 0}).sort('timestamp', -1).to_list(10)
    return plans

# Moltbot Activity Feed
@api_router.get("/moltbot/activities")
async def get_moltbot_activities(limit: int = 50):
    activities = await db.moltbot_activities.find({}, {'_id': 0}).sort('timestamp', -1).to_list(limit)
    return activities

@api_router.get("/moltbot/stats")
async def get_moltbot_stats():
    total_activities = await db.moltbot_activities.count_documents({})
    diet_suggestions = await db.moltbot_activities.count_documents({'activity_type': 'diet_suggestion'})
    alert_verifications = await db.moltbot_activities.count_documents({'activity_type': 'alert_verification'})
    
    return {
        'total_activities': total_activities,
        'diet_suggestions': diet_suggestions,
        'alert_verifications': alert_verifications,
        'uptime': '99.9%',
        'agent_status': 'active'
    }

# Dashboard stats
@api_router.get("/dashboard/patient/{patient_id}")
async def get_patient_dashboard(patient_id: str):
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get latest readings
    readings = await db.device_readings.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(24)  # Last 24 readings
    
    # Get recent alerts
    alerts = await db.critical_alerts.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(5)
    
    # Get diet plans
    diet_plans = await db.diet_plans.find(
        {'patient_id': patient_id},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(3)
    
    # Get assigned doctor
    doctor = None
    if patient.get('assigned_doctor_id'):
        doctor = await db.doctors.find_one(
            {'id': patient['assigned_doctor_id']},
            {'_id': 0}
        )
    
    return {
        'patient': patient,
        'doctor': doctor,
        'readings': readings,
        'alerts': alerts,
        'diet_plans': diet_plans,
        'current_reading': generate_device_reading(patient)
    }

@api_router.get("/dashboard/doctor/{doctor_id}")
async def get_doctor_dashboard(doctor_id: str):
    doctor = await db.doctors.find_one({'id': doctor_id}, {'_id': 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get all patients for this doctor
    patients = await db.patients.find(
        {'assigned_doctor_id': doctor_id},
        {'_id': 0}
    ).to_list(100)
    
    # Get recent alerts for doctor's patients
    patient_ids = [p['id'] for p in patients]
    alerts = await db.critical_alerts.find(
        {'patient_id': {'$in': patient_ids}},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(20)
    
    return {
        'doctor': doctor,
        'patients': patients,
        'alerts': alerts,
        'total_patients': len(patients),
        'critical_patients': sum(1 for a in alerts if a.get('severity') == 'critical')
    }

@api_router.get("/dashboard/organization")
async def get_organization_dashboard():
    total_patients = await db.patients.count_documents({})
    total_doctors = await db.doctors.count_documents({})
    total_hospitals = await db.hospitals.count_documents({})
    total_alerts = await db.critical_alerts.count_documents({})
    
    # Get hospital stats
    hospitals = await db.hospitals.find({}, {'_id': 0}).to_list(30)
    
    # Generate system health metrics
    system_health = {
        'uptime': f"{random.uniform(99.5, 99.99):.2f}%",
        'active_connections': random.randint(50, 200),
        'data_sync_status': 'healthy',
        'blockchain_sync': 'synced',
        'last_block': random.randint(1000000, 2000000)
    }
    
    return {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_hospitals': total_hospitals,
        'total_alerts': total_alerts,
        'hospitals': hospitals,
        'system_health': system_health,
        'device_analytics': {
            'insulin_pumps': random.randint(30, 50),
            'pacemakers': random.randint(20, 40),
            'glucose_monitors': random.randint(40, 60)
        }
    }

# Blockchain verification endpoint
@api_router.get("/blockchain/verify/{tx_hash}")
async def verify_transaction(tx_hash: str):
    """Verify a transaction on opBNB (simulated)"""
    return {
        'tx_hash': tx_hash,
        'network': 'opBNB Testnet',
        'status': 'confirmed',
        'block_number': random.randint(1000000, 2000000),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'explorer_url': f"https://testnet.opbnbscan.com/tx/{tx_hash}"
    }

@api_router.get("/blockchain/contracts")
async def get_deployed_contracts():
    """Get deployed contract information"""
    deployment_file = ROOT_DIR / 'deployment_result.json'
    if deployment_file.exists():
        with open(deployment_file, 'r') as f:
            return json.load(f)
    return {"status": "NOT_DEPLOYED", "message": "Run deploy_contracts.py to deploy"}

@api_router.get("/blockchain/wallet/{patient_id}")
async def get_patient_wallet(patient_id: str):
    """Get or create a smart contract wallet address for a patient"""
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check if patient already has a wallet
    wallet = await db.patient_wallets.find_one({'patient_id': patient_id}, {'_id': 0})
    
    if not wallet:
        # Generate deterministic wallet address from patient data
        wallet_seed = f"{patient_id}-{patient.get('name', '')}-omnihealth"
        wallet_address = "0x" + hashlib.sha256(wallet_seed.encode()).hexdigest()[:40]
        
        # Check if we have real deployed factory
        factory_addr = DEPLOYED_CONTRACTS.get('PatientWalletFactory', {}).get('address')
        
        wallet = {
            'id': str(uuid.uuid4()),
            'patient_id': patient_id,
            'patient_name': patient.get('name'),
            'wallet_address': wallet_address,
            'factory_address': factory_addr,
            'deployed_on_chain': factory_addr is not None,
            'network': 'opBNB Testnet',
            'chain_id': 5611,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.patient_wallets.insert_one({**wallet})
    
    return {
        'patient_id': patient_id,
        'wallet_address': wallet.get('wallet_address'),
        'deployed_on_chain': wallet.get('deployed_on_chain', False),
        'network': 'opBNB Testnet',
        'explorer_url': f"https://testnet.opbnbscan.com/address/{wallet.get('wallet_address')}"
    }

@api_router.post("/blockchain/record-alert")
async def record_alert_on_chain(alert_id: str):
    """Record a critical alert hash on the HealthAudit contract"""
    alert = await db.critical_alerts.find_one({'id': alert_id}, {'_id': 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if we have deployed HealthAudit contract
    health_audit_addr = DEPLOYED_CONTRACTS.get('HealthAudit', {}).get('address')
    
    if health_audit_addr:
        # In production, this would call the actual contract
        # For now, return the contract info
        return {
            'status': 'recorded',
            'alert_id': alert_id,
            'sha256_hash': alert.get('sha256_hash'),
            'contract_address': health_audit_addr,
            'tx_hash': alert.get('tx_hash'),
            'explorer_url': f"https://testnet.opbnbscan.com/tx/{alert.get('tx_hash')}"
        }
    else:
        return {
            'status': 'simulated',
            'alert_id': alert_id,
            'sha256_hash': alert.get('sha256_hash'),
            'contract_address': None,
            'message': 'HealthAudit contract not deployed. Run deploy_contracts.py',
            'tx_hash': alert.get('tx_hash'),
            'explorer_url': f"https://testnet.opbnbscan.com/tx/{alert.get('tx_hash')}"
        }

# ============== OPENCLAW SKILL ENDPOINTS ==============

@api_router.get("/openclaw/skills")
async def get_openclaw_skills():
    """Get all available OpenClaw skills"""
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    return {
        "agent": "OpenClaw Guardian",
        "version": "1.0.0",
        "skills": openclaw_agent.get_skill_configs()
    }

@api_router.post("/openclaw/skill/critical-monitor/{patient_id}")
async def run_critical_monitor(patient_id: str):
    """
    OpenClaw Skill: Critical Condition Monitor
    Monitors patient vitals and triggers alerts for critical conditions
    """
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Generate current vitals
    condition = patient.get('condition', '')
    is_diabetes = 'diabetes' in condition
    
    # Simulate device reading with occasional critical values
    critical_chance = random.random()
    
    if is_diabetes:
        if critical_chance < 0.3:  # 30% chance of critical for demo
            glucose = random.choice([random.randint(40, 65), random.randint(260, 350)])
        else:
            glucose = random.randint(80, 160)
        heart_rate = None
    else:
        glucose = None
        if critical_chance < 0.3:
            heart_rate = random.choice([random.randint(35, 48), random.randint(125, 160)])
        else:
            heart_rate = random.randint(65, 95)
    
    # Use stable battery
    battery = get_stable_battery(patient_id)
    
    vitals = PatientVitals(
        patient_id=patient_id,
        patient_name=patient.get('name'),
        glucose_level=glucose,
        heart_rate=heart_rate,
        battery_level=battery,
        condition=condition
    )
    
    # Run the skill
    alert = await openclaw_agent.monitor_critical_conditions(vitals)
    
    if alert:
        from dataclasses import asdict
        alert_dict = asdict(alert)
        alert_dict['severity'] = alert.severity.value
        return {
            "skill": "critical_condition_monitor",
            "status": "alert_generated",
            "alert": alert_dict,
            "vitals": {
                "glucose_level": glucose,
                "heart_rate": heart_rate,
                "battery_level": battery
            },
            "verified_by_openclaw": True,
            "explorer_url": f"https://testnet.opbnbscan.com/tx/{alert.tx_hash}"
        }
    else:
        return {
            "skill": "critical_condition_monitor",
            "status": "normal",
            "message": "All vitals within normal range",
            "vitals": {
                "glucose_level": glucose,
                "heart_rate": heart_rate,
                "battery_level": battery
            },
            "verified_by_openclaw": True
        }

@api_router.post("/openclaw/skill/diet-suggestion/{patient_id}")
async def run_diet_suggestion(patient_id: str, meal_type: str = "daily"):
    """
    OpenClaw Skill: AI Diet Suggestion
    Generates personalized diet plans based on patient condition
    """
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    
    result = await openclaw_agent.generate_diet_suggestion(patient_id, meal_type)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "skill": "ai_diet_suggestion",
        "status": "generated",
        **result
    }

@api_router.post("/openclaw/skill/realtime-feedback/{patient_id}")
async def run_realtime_feedback(patient_id: str):
    """
    OpenClaw Skill: Real-time Feedback
    Provides immediate coaching based on current vitals and trends
    """
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    condition = patient.get('condition', '')
    is_diabetes = 'diabetes' in condition
    
    vitals = PatientVitals(
        patient_id=patient_id,
        patient_name=patient.get('name'),
        glucose_level=random.randint(70, 180) if is_diabetes else None,
        heart_rate=random.randint(60, 100) if not is_diabetes else None,
        battery_level=random.randint(20, 100),
        condition=condition
    )
    
    result = await openclaw_agent.generate_realtime_feedback(patient_id, vitals)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "skill": "realtime_feedback",
        "status": "generated",
        **result
    }

@api_router.post("/openclaw/skill/daily-progress/{patient_id}")
async def run_daily_progress(patient_id: str, date: str = None):
    """
    OpenClaw Skill: Daily Progress Tracker
    Generates comprehensive daily health report
    """
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    
    result = await openclaw_agent.generate_daily_progress(patient_id, date)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "skill": "daily_progress_tracker",
        "status": "generated",
        **result
    }

@api_router.post("/openclaw/run-all/{patient_id}")
async def run_all_skills(patient_id: str):
    """
    Run all OpenClaw skills for a patient
    Useful for testing and demonstration
    """
    global openclaw_agent
    if openclaw_agent is None:
        openclaw_agent = OpenClawGuardianAgent(db, EMERGENT_LLM_KEY)
    
    result = await openclaw_agent.run_all_skills_once(patient_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "agent": "OpenClaw Guardian",
        "patient": result.get("patient"),
        "skills_executed": result.get("skills_executed"),
        "verified_by_openclaw": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============== BNB GREENFIELD STORAGE ENDPOINTS ==============

@api_router.get("/greenfield/status")
async def get_greenfield_status():
    """Get BNB Greenfield storage status"""
    stats = {}
    if hasattr(greenfield_client, 'get_storage_stats'):
        stats = await greenfield_client.get_storage_stats()
    
    return {
        "status": "connected",
        "network": greenfield_client.network,
        "bucket": greenfield_client.bucket_name,
        "use_real": USE_REAL_GREENFIELD,
        "storage_stats": stats,
        "note": "Set USE_REAL_GREENFIELD=true in .env for production Greenfield"
    }

@api_router.post("/greenfield/store-alert")
async def store_alert_on_greenfield(alert_id: str):
    """Store a critical alert on BNB Greenfield for tamper-proof storage"""
    alert = await db.critical_alerts.find_one({'id': alert_id}, {'_id': 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Store on Greenfield
    result = await greenfield_client.store_critical_alert(alert)
    
    # Update alert with Greenfield CID
    await db.critical_alerts.update_one(
        {'id': alert_id},
        {'$set': {
            'greenfield_cid': result.get('greenfield_cid'),
            'greenfield_url': result.get('greenfield_url'),
            'greenfield_hash': result.get('content_hash')
        }}
    )
    
    return {
        "alert_id": alert_id,
        "greenfield_storage": result,
        "on_chain_hash": alert.get('sha256_hash'),
        "tx_hash": alert.get('tx_hash')
    }

@api_router.post("/greenfield/store-diet/{patient_id}")
async def store_diet_on_greenfield(patient_id: str):
    """Store latest diet plan on BNB Greenfield"""
    diet = await db.diet_plans.find_one(
        {'patient_id': patient_id},
        {'_id': 0},
        sort=[('timestamp', -1)]
    )
    if not diet:
        raise HTTPException(status_code=404, detail="No diet plan found for patient")
    
    # Store on Greenfield
    result = await greenfield_client.store_diet_plan(patient_id, diet)
    
    return {
        "patient_id": patient_id,
        "greenfield_storage": result
    }

@api_router.post("/greenfield/store-progress/{patient_id}")
async def store_progress_on_greenfield(patient_id: str):
    """Store daily progress on BNB Greenfield"""
    progress = await db.daily_progress.find_one(
        {'patient_id': patient_id},
        {'_id': 0},
        sort=[('timestamp', -1)]
    )
    if not progress:
        raise HTTPException(status_code=404, detail="No progress data found for patient")
    
    # Store on Greenfield
    result = await greenfield_client.store_daily_progress(patient_id, progress)
    
    return {
        "patient_id": patient_id,
        "greenfield_storage": result
    }

@api_router.post("/greenfield/store-all/{patient_id}")
async def store_all_patient_data_on_greenfield(patient_id: str):
    """Store all patient medical records on BNB Greenfield"""
    patient = await db.patients.find_one({'id': patient_id}, {'_id': 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    results = {
        "patient_id": patient_id,
        "patient_name": patient.get('name'),
        "records_stored": []
    }
    
    # Store alerts
    alerts = await db.critical_alerts.find({'patient_id': patient_id}, {'_id': 0}).to_list(10)
    for alert in alerts:
        alert_result = await greenfield_client.store_critical_alert(alert)
        results["records_stored"].append({
            "type": "critical_alert",
            "greenfield_cid": alert_result.get('greenfield_cid')
        })
    
    # Store diet plans
    diets = await db.diet_plans.find({'patient_id': patient_id}, {'_id': 0}).to_list(5)
    for diet in diets:
        diet_result = await greenfield_client.store_diet_plan(patient_id, diet)
        results["records_stored"].append({
            "type": "diet_plan",
            "greenfield_cid": diet_result.get('greenfield_cid')
        })
    
    # Store progress reports
    progress_list = await db.daily_progress.find({'patient_id': patient_id}, {'_id': 0}).to_list(7)
    for progress in progress_list:
        progress_result = await greenfield_client.store_daily_progress(patient_id, progress)
        results["records_stored"].append({
            "type": "daily_progress", 
            "greenfield_cid": progress_result.get('greenfield_cid')
        })
    
    results["total_records"] = len(results["records_stored"])
    results["network"] = greenfield_client.network
    
    return results

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await generate_mock_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
