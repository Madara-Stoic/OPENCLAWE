"""
BNB Greenfield Integration for OmniHealth Guardian
Uses NodeReal Bundle Service for decentralized medical record storage

REQUIREMENTS FOR REAL GREENFIELD:
1. Create a bucket on Greenfield (use DCellar: https://dcellar.io)
2. Grant permissions to bundler account
3. Set GREENFIELD_BUCKET_NAME in .env
"""

import os
import json
import hashlib
import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# NodeReal Greenfield Bundle Service Endpoints
GREENFIELD_MAINNET_BUNDLE = "https://gnfd-mainnet-bundle.nodereal.io"
GREENFIELD_TESTNET_BUNDLE = "https://gnfd-testnet-bundle.nodereal.io"

@dataclass
class GreenfieldObject:
    """Represents an object stored on Greenfield"""
    bucket_name: str
    bundle_name: str
    object_name: str
    content_hash: str
    greenfield_url: str
    size: int
    content_type: str
    timestamp: str
    tx_status: str = "pending"
    
    def to_cid(self) -> str:
        """Generate a CID-like identifier for the object"""
        return f"gf://{self.bucket_name}/{self.bundle_name}/{self.object_name}"


class GreenfieldBundleService:
    """
    BNB Greenfield Storage using NodeReal Bundle Service
    
    Prerequisites:
    1. Create bucket on Greenfield via DCellar (https://dcellar.io)
    2. Grant bundler account permissions (get account via /bundlerAccount/{address})
    3. Set bucket name in environment
    """
    
    def __init__(self, use_testnet: bool = True, bucket_name: str = None):
        self.base_url = GREENFIELD_TESTNET_BUNDLE if use_testnet else GREENFIELD_MAINNET_BUNDLE
        self.network = "greenfield-testnet" if use_testnet else "greenfield-mainnet"
        self.bucket_name = bucket_name or os.environ.get('GREENFIELD_BUCKET_NAME', 'omnihealth-medical-records')
        self.current_bundle = None
        self._session = None
        
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    async def get_bundler_account(self, user_address: str) -> Dict:
        """Get bundler account for a user - needed for granting permissions"""
        session = await self._get_session()
        url = f"{self.base_url}/v1/bundlerAccount/{user_address}"
        
        try:
            async with session.post(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    return {"error": f"Status {response.status}: {text}"}
        except Exception as e:
            logger.error(f"Get bundler account error: {e}")
            return {"error": str(e)}
    
    async def create_bundle(self, bundle_name: str = None) -> Dict:
        """Create a new bundle for storing objects"""
        session = await self._get_session()
        
        if bundle_name is None:
            bundle_name = f"medical-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        url = f"{self.base_url}/v1/createBundle"
        payload = {
            "bucketName": self.bucket_name,
            "bundleName": bundle_name
        }
        
        try:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                if response.status == 200 and not result.get("error"):
                    self.current_bundle = bundle_name
                    logger.info(f"Created bundle: {bundle_name}")
                return result
        except Exception as e:
            logger.error(f"Create bundle error: {e}")
            return {"error": str(e)}
    
    async def upload_object(self, object_name: str, content: bytes, content_type: str = "application/json") -> Dict:
        """Upload a single object to the current bundle"""
        session = await self._get_session()
        
        if not self.current_bundle:
            create_result = await self.create_bundle()
            if "error" in create_result:
                return create_result
        
        url = f"{self.base_url}/v1/uploadObject"
        
        # Create multipart form data
        form = aiohttp.FormData()
        form.add_field('bucketName', self.bucket_name)
        form.add_field('bundleName', self.current_bundle)
        form.add_field('fileName', object_name)
        form.add_field('contentType', content_type)
        form.add_field('file', content, filename=object_name, content_type=content_type)
        
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    result = await response.json()
                    content_hash = self.compute_hash(content)
                    result["content_hash"] = content_hash
                    result["greenfield_url"] = f"{self.base_url}/view/{self.bucket_name}/{self.current_bundle}/{object_name}"
                    result["cid"] = f"gf://{self.bucket_name}/{self.current_bundle}/{object_name}"
                    return result
                else:
                    text = await response.text()
                    return {"error": f"Upload failed: Status {response.status} - {text}"}
        except Exception as e:
            logger.error(f"Upload object error: {e}")
            return {"error": str(e)}
    
    async def finalize_bundle(self, bundle_name: str = None) -> Dict:
        """Finalize a bundle and seal it on Greenfield"""
        session = await self._get_session()
        bundle = bundle_name or self.current_bundle
        
        if not bundle:
            return {"error": "No bundle to finalize"}
        
        url = f"{self.base_url}/v1/finalizeBundle"
        payload = {
            "bucketName": self.bucket_name,
            "bundleName": bundle
        }
        
        try:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    self.current_bundle = None
                    logger.info(f"Finalized bundle: {bundle}")
                return result
        except Exception as e:
            logger.error(f"Finalize bundle error: {e}")
            return {"error": str(e)}
    
    async def query_bundle(self, bundle_name: str) -> Dict:
        """Query bundle information"""
        session = await self._get_session()
        url = f"{self.base_url}/v1/queryBundle/{self.bucket_name}/{bundle_name}"
        
        try:
            async with session.get(url) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Query bundle error: {e}")
            return {"error": str(e)}
    
    async def view_object(self, bundle_name: str, object_name: str) -> Dict:
        """View/retrieve an object from a bundle"""
        session = await self._get_session()
        url = f"{self.base_url}/view/{self.bucket_name}/{bundle_name}/{object_name}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    return {
                        "status": "found",
                        "content": content.decode('utf-8'),
                        "url": url
                    }
                else:
                    return {"error": f"Object not found: {response.status}"}
        except Exception as e:
            logger.error(f"View object error: {e}")
            return {"error": str(e)}
    
    async def store_medical_record(self, patient_id: str, record_type: str, data: Dict) -> Dict:
        """
        Store a medical record on Greenfield
        
        Args:
            patient_id: Patient identifier
            record_type: Type of record (critical_alert, diet_plan, daily_progress)
            data: Record data to store
        
        Returns:
            Storage result with Greenfield CID
        """
        timestamp = datetime.now(timezone.utc)
        object_name = f"{patient_id}/{record_type}/{timestamp.strftime('%Y%m%d-%H%M%S')}.json"
        
        # Build complete record with metadata
        record = {
            "schema_version": "1.0",
            "record_type": record_type,
            "patient_id": patient_id,
            "timestamp": timestamp.isoformat(),
            "network": self.network,
            "data": data
        }
        
        content = json.dumps(record, indent=2, default=str).encode('utf-8')
        content_hash = self.compute_hash(content)
        
        # Upload to Greenfield
        upload_result = await self.upload_object(object_name, content, "application/json")
        
        if "error" in upload_result:
            # Return with error but include hash for verification
            return {
                "status": "upload_failed",
                "error": upload_result["error"],
                "content_hash": content_hash,
                "record_type": record_type,
                "patient_id": patient_id,
                "timestamp": timestamp.isoformat(),
                "note": "Data hashed locally. Create Greenfield bucket to enable storage."
            }
        
        return {
            "status": "stored",
            "greenfield_cid": upload_result.get("cid"),
            "content_hash": content_hash,
            "greenfield_url": upload_result.get("greenfield_url"),
            "bucket": self.bucket_name,
            "bundle": self.current_bundle,
            "object": object_name,
            "size": len(content),
            "timestamp": timestamp.isoformat(),
            "network": self.network
        }
    
    async def store_critical_alert(self, alert_data: Dict) -> Dict:
        """Store a critical alert on Greenfield"""
        patient_id = alert_data.get("patient_id", "unknown")
        return await self.store_medical_record(patient_id, "critical_alert", alert_data)
    
    async def store_diet_plan(self, patient_id: str, diet_data: Dict) -> Dict:
        """Store an AI diet plan on Greenfield"""
        return await self.store_medical_record(patient_id, "diet_plan", diet_data)
    
    async def store_daily_progress(self, patient_id: str, progress_data: Dict) -> Dict:
        """Store daily progress report on Greenfield"""
        return await self.store_medical_record(patient_id, "daily_progress", progress_data)
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        return {
            "network": self.network,
            "bucket": self.bucket_name,
            "endpoint": self.base_url,
            "current_bundle": self.current_bundle,
            "status": "connected"
        }


class GreenfieldStorageLocal:
    """
    Local fallback storage with Greenfield-compatible structure
    Used when Greenfield bucket is not configured
    """
    
    def __init__(self):
        self.network = "local-simulated"
        self.bucket_name = "omnihealth-medical-records"
        self.storage: Dict[str, Dict] = {}
        self.bundles: Dict[str, List] = {}
        self.current_bundle = None
        
    def compute_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    
    async def create_bundle(self, bundle_name: str = None) -> Dict:
        if bundle_name is None:
            bundle_name = f"local-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.bundles[bundle_name] = []
        self.current_bundle = bundle_name
        return {"status": "created", "bundle": bundle_name, "network": "local"}
    
    async def store_medical_record(self, patient_id: str, record_type: str, data: Dict) -> Dict:
        timestamp = datetime.now(timezone.utc)
        
        if not self.current_bundle:
            await self.create_bundle()
        
        object_name = f"{patient_id}/{record_type}/{timestamp.strftime('%Y%m%d-%H%M%S')}.json"
        
        record = {
            "record_type": record_type,
            "patient_id": patient_id,
            "timestamp": timestamp.isoformat(),
            "data": data
        }
        
        content = json.dumps(record).encode('utf-8')
        content_hash = self.compute_hash(content)
        
        key = f"{self.bucket_name}/{self.current_bundle}/{object_name}"
        self.storage[key] = {"content": record, "hash": content_hash}
        self.bundles[self.current_bundle].append(object_name)
        
        return {
            "status": "stored_locally",
            "greenfield_cid": f"gf-local://{key}",
            "content_hash": content_hash,
            "bucket": self.bucket_name,
            "bundle": self.current_bundle,
            "object": object_name,
            "timestamp": timestamp.isoformat(),
            "network": "local-simulated",
            "note": "Stored locally. Configure GREENFIELD_BUCKET_NAME for real Greenfield storage."
        }
    
    async def store_critical_alert(self, alert_data: Dict) -> Dict:
        patient_id = alert_data.get("patient_id", "unknown")
        return await self.store_medical_record(patient_id, "critical_alert", alert_data)
    
    async def store_diet_plan(self, patient_id: str, diet_data: Dict) -> Dict:
        return await self.store_medical_record(patient_id, "diet_plan", diet_data)
    
    async def store_daily_progress(self, patient_id: str, progress_data: Dict) -> Dict:
        return await self.store_medical_record(patient_id, "daily_progress", progress_data)
    
    async def get_storage_stats(self) -> Dict:
        return {
            "network": self.network,
            "bucket": self.bucket_name,
            "total_objects": len(self.storage),
            "total_bundles": len(self.bundles),
            "current_bundle": self.current_bundle,
            "status": "local_mode"
        }
    
    async def close(self):
        pass


def get_greenfield_client(use_real: bool = True):
    """
    Get Greenfield storage client
    
    If GREENFIELD_BUCKET_NAME is set, uses real Greenfield Bundle Service
    Otherwise falls back to local storage
    """
    bucket_name = os.environ.get('GREENFIELD_BUCKET_NAME')
    
    if use_real and bucket_name:
        logger.info(f"Using real Greenfield with bucket: {bucket_name}")
        return GreenfieldBundleService(use_testnet=True, bucket_name=bucket_name)
    else:
        logger.info("Using local Greenfield simulation (set GREENFIELD_BUCKET_NAME for real storage)")
        return GreenfieldStorageLocal()


# Test function
async def test_greenfield():
    """Test Greenfield integration"""
    print("Testing Greenfield Storage...")
    
    client = get_greenfield_client(use_real=True)
    
    # Test storing a critical alert
    result = await client.store_critical_alert({
        "patient_id": "test-001",
        "alert_type": "high_glucose",
        "severity": "critical",
        "message": "Glucose level 285 mg/dL",
        "reading": {"glucose": 285}
    })
    print(f"Alert storage result: {json.dumps(result, indent=2)}")
    
    # Get stats
    stats = await client.get_storage_stats()
    print(f"Storage stats: {json.dumps(stats, indent=2)}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_greenfield())
