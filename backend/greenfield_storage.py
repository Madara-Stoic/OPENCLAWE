"""
BNB Greenfield Integration for OmniHealth Guardian
Uses NodeReal Bundle Service for decentralized medical record storage
"""

import os
import json
import hashlib
import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# NodeReal Greenfield Bundle Service Endpoints
GREENFIELD_MAINNET_BUNDLE = "https://gnfd-mainnet-bundle.nodereal.io"
GREENFIELD_TESTNET_BUNDLE = "https://gnfd-testnet-bundle.nodereal.io"

# NodeReal API endpoint from user
NODEREAL_API_ENDPOINT = "https://open-platform.nodereal.io/1f99e1545edd4e82b48c1f6b1e0b2b75/greenfieldbilling-mainnet"

@dataclass
class GreenfieldObject:
    """Represents an object stored on Greenfield"""
    bucket_name: str
    bundle_name: str
    object_name: str
    content_hash: str  # SHA-256 hash of content
    greenfield_url: str
    size: int
    content_type: str
    timestamp: str
    
    def to_cid(self) -> str:
        """Generate a CID-like identifier for the object"""
        return f"gf://{self.bucket_name}/{self.bundle_name}/{self.object_name}"


class GreenfieldStorage:
    """
    BNB Greenfield Storage Client
    Handles medical record storage on decentralized Greenfield network
    """
    
    def __init__(self, use_testnet: bool = True):
        self.base_url = GREENFIELD_TESTNET_BUNDLE if use_testnet else GREENFIELD_MAINNET_BUNDLE
        self.network = "testnet" if use_testnet else "mainnet"
        self.bucket_name = "omnihealth-medical-records"
        self.current_bundle = None
        
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict:
        """Make HTTP request to Greenfield Bundle Service"""
        url = f"{self.base_url}/v1{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(url) as response:
                        return await response.json()
                elif method == "POST":
                    if files:
                        # Multipart form data for file upload
                        form = aiohttp.FormData()
                        for key, value in (data or {}).items():
                            form.add_field(key, str(value))
                        for key, (filename, content, content_type) in files.items():
                            form.add_field(key, content, filename=filename, content_type=content_type)
                        async with session.post(url, data=form) as response:
                            return await response.json()
                    else:
                        async with session.post(url, json=data) as response:
                            return await response.json()
            except Exception as e:
                logger.error(f"Greenfield API error: {e}")
                return {"error": str(e)}
    
    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    async def get_bundler_account(self, user_address: str) -> Dict:
        """Get bundler account for a user"""
        return await self._make_request("POST", f"/bundlerAccount/{user_address}")
    
    async def create_bundle(self, bundle_name: str) -> Dict:
        """Create a new bundle for storing objects"""
        result = await self._make_request("POST", "/createBundle", {
            "bucketName": self.bucket_name,
            "bundleName": bundle_name
        })
        if not result.get("error"):
            self.current_bundle = bundle_name
        return result
    
    async def upload_object(self, object_name: str, content: bytes, content_type: str = "application/json") -> Dict:
        """Upload a single object to the current bundle"""
        if not self.current_bundle:
            # Auto-create bundle if none exists
            bundle_name = f"medical-records-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            await self.create_bundle(bundle_name)
        
        result = await self._make_request(
            "POST", 
            "/uploadObject",
            data={
                "bucketName": self.bucket_name,
                "fileName": object_name,
                "contentType": content_type
            },
            files={
                "file": (object_name, content, content_type)
            }
        )
        
        if not result.get("error"):
            content_hash = self.compute_hash(content)
            result["content_hash"] = content_hash
            result["greenfield_url"] = f"{self.base_url}/view/{self.bucket_name}/{self.current_bundle}/{object_name}"
        
        return result
    
    async def finalize_bundle(self, bundle_name: str = None) -> Dict:
        """Finalize a bundle and upload to Greenfield"""
        bundle = bundle_name or self.current_bundle
        if not bundle:
            return {"error": "No bundle to finalize"}
        
        result = await self._make_request("POST", "/finalizeBundle", {
            "bucketName": self.bucket_name,
            "bundleName": bundle
        })
        
        if not result.get("error"):
            self.current_bundle = None
        
        return result
    
    async def query_bundle(self, bundle_name: str) -> Dict:
        """Query bundle information"""
        return await self._make_request("GET", f"/queryBundle/{self.bucket_name}/{bundle_name}")
    
    async def view_object(self, bundle_name: str, object_name: str) -> Dict:
        """View/retrieve an object from a bundle"""
        return await self._make_request("GET", f"/view/{self.bucket_name}/{bundle_name}/{object_name}")
    
    async def store_medical_record(self, patient_id: str, record_type: str, data: Dict) -> GreenfieldObject:
        """
        Store a medical record on Greenfield
        
        Args:
            patient_id: Patient identifier
            record_type: Type of record (alert, diet_plan, vital_reading, progress)
            data: Record data to store
        
        Returns:
            GreenfieldObject with storage details
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        object_name = f"{patient_id}/{record_type}/{timestamp.replace(':', '-')}.json"
        
        # Add metadata to record
        record = {
            "patient_id": patient_id,
            "record_type": record_type,
            "timestamp": timestamp,
            "data": data,
            "version": "1.0",
            "encrypted": False  # In production, encrypt with patient's key
        }
        
        content = json.dumps(record, indent=2).encode('utf-8')
        content_hash = self.compute_hash(content)
        
        # Upload to Greenfield
        upload_result = await self.upload_object(object_name, content, "application/json")
        
        greenfield_obj = GreenfieldObject(
            bucket_name=self.bucket_name,
            bundle_name=self.current_bundle or "pending",
            object_name=object_name,
            content_hash=content_hash,
            greenfield_url=upload_result.get("greenfield_url", ""),
            size=len(content),
            content_type="application/json",
            timestamp=timestamp
        )
        
        return greenfield_obj
    
    async def store_critical_alert(self, alert_data: Dict) -> Dict:
        """Store a critical alert on Greenfield for tamper-proof audit"""
        patient_id = alert_data.get("patient_id", "unknown")
        
        greenfield_obj = await self.store_medical_record(
            patient_id=patient_id,
            record_type="critical_alert",
            data=alert_data
        )
        
        return {
            "status": "stored",
            "greenfield_cid": greenfield_obj.to_cid(),
            "content_hash": greenfield_obj.content_hash,
            "greenfield_url": greenfield_obj.greenfield_url,
            "bucket": greenfield_obj.bucket_name,
            "bundle": greenfield_obj.bundle_name,
            "object": greenfield_obj.object_name,
            "timestamp": greenfield_obj.timestamp
        }
    
    async def store_diet_plan(self, patient_id: str, diet_data: Dict) -> Dict:
        """Store an AI diet plan on Greenfield"""
        greenfield_obj = await self.store_medical_record(
            patient_id=patient_id,
            record_type="diet_plan",
            data=diet_data
        )
        
        return {
            "status": "stored",
            "greenfield_cid": greenfield_obj.to_cid(),
            "content_hash": greenfield_obj.content_hash,
            "greenfield_url": greenfield_obj.greenfield_url,
            "timestamp": greenfield_obj.timestamp
        }
    
    async def store_daily_progress(self, patient_id: str, progress_data: Dict) -> Dict:
        """Store daily progress report on Greenfield"""
        greenfield_obj = await self.store_medical_record(
            patient_id=patient_id,
            record_type="daily_progress",
            data=progress_data
        )
        
        return {
            "status": "stored",
            "greenfield_cid": greenfield_obj.to_cid(),
            "content_hash": greenfield_obj.content_hash,
            "greenfield_url": greenfield_obj.greenfield_url,
            "timestamp": greenfield_obj.timestamp
        }


class GreenfieldStorageSimulated:
    """
    Simulated Greenfield Storage for development/testing
    Uses local storage with Greenfield-compatible structure
    """
    
    def __init__(self):
        self.network = "simulated"
        self.bucket_name = "omnihealth-medical-records"
        self.storage: Dict[str, Dict] = {}
        self.bundles: Dict[str, list] = {}
        self.current_bundle = None
        
    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    async def create_bundle(self, bundle_name: str) -> Dict:
        """Create a simulated bundle"""
        self.bundles[bundle_name] = []
        self.current_bundle = bundle_name
        return {"status": "created", "bundle": bundle_name}
    
    async def store_medical_record(self, patient_id: str, record_type: str, data: Dict) -> GreenfieldObject:
        """Store a medical record (simulated)"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if not self.current_bundle:
            bundle_name = f"bundle-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            await self.create_bundle(bundle_name)
        
        object_name = f"{patient_id}/{record_type}/{timestamp.replace(':', '-')}.json"
        
        record = {
            "patient_id": patient_id,
            "record_type": record_type,
            "timestamp": timestamp,
            "data": data
        }
        
        content = json.dumps(record).encode('utf-8')
        content_hash = self.compute_hash(content)
        
        # Store locally
        key = f"{self.bucket_name}/{self.current_bundle}/{object_name}"
        self.storage[key] = {
            "content": record,
            "hash": content_hash,
            "timestamp": timestamp
        }
        self.bundles[self.current_bundle].append(object_name)
        
        return GreenfieldObject(
            bucket_name=self.bucket_name,
            bundle_name=self.current_bundle,
            object_name=object_name,
            content_hash=content_hash,
            greenfield_url=f"gf-simulated://{key}",
            size=len(content),
            content_type="application/json",
            timestamp=timestamp
        )
    
    async def store_critical_alert(self, alert_data: Dict) -> Dict:
        """Store critical alert (simulated)"""
        patient_id = alert_data.get("patient_id", "unknown")
        obj = await self.store_medical_record(patient_id, "critical_alert", alert_data)
        
        return {
            "status": "stored_simulated",
            "greenfield_cid": obj.to_cid(),
            "content_hash": obj.content_hash,
            "greenfield_url": obj.greenfield_url,
            "note": "Simulated - connect real Greenfield bucket for production"
        }
    
    async def store_diet_plan(self, patient_id: str, diet_data: Dict) -> Dict:
        """Store diet plan (simulated)"""
        obj = await self.store_medical_record(patient_id, "diet_plan", diet_data)
        
        return {
            "status": "stored_simulated",
            "greenfield_cid": obj.to_cid(),
            "content_hash": obj.content_hash,
            "greenfield_url": obj.greenfield_url
        }
    
    async def store_daily_progress(self, patient_id: str, progress_data: Dict) -> Dict:
        """Store daily progress (simulated)"""
        obj = await self.store_medical_record(patient_id, "daily_progress", progress_data)
        
        return {
            "status": "stored_simulated",
            "greenfield_cid": obj.to_cid(),
            "content_hash": obj.content_hash,
            "greenfield_url": obj.greenfield_url
        }
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        return {
            "total_objects": len(self.storage),
            "total_bundles": len(self.bundles),
            "bucket": self.bucket_name,
            "network": self.network
        }


# Factory function to get appropriate storage client
def get_greenfield_client(use_real: bool = False) -> GreenfieldStorage:
    """
    Get Greenfield storage client
    
    Args:
        use_real: If True, use real Greenfield network (requires bucket setup)
                  If False, use simulated storage
    """
    if use_real:
        return GreenfieldStorage(use_testnet=True)
    else:
        return GreenfieldStorageSimulated()


# Test function
async def test_greenfield():
    """Test Greenfield integration"""
    client = get_greenfield_client(use_real=False)  # Use simulated for testing
    
    # Test storing a critical alert
    alert_result = await client.store_critical_alert({
        "patient_id": "test-patient-001",
        "alert_type": "high_glucose",
        "severity": "critical",
        "message": "Glucose level 285 mg/dL",
        "reading": {"glucose": 285, "timestamp": datetime.now(timezone.utc).isoformat()}
    })
    print("Alert stored:", alert_result)
    
    # Test storing a diet plan
    diet_result = await client.store_diet_plan("test-patient-001", {
        "condition": "diabetes_type2",
        "breakfast": ["Oatmeal", "Eggs", "Berries"],
        "ai_model": "OpenClaw/GPT-4o"
    })
    print("Diet stored:", diet_result)
    
    # Get stats
    if hasattr(client, 'get_storage_stats'):
        stats = await client.get_storage_stats()
        print("Storage stats:", stats)


if __name__ == "__main__":
    asyncio.run(test_greenfield())
