"""
Lace Cloud API Client - Minimal implementation for PyPI.
All processing happens in the cloud for IP protection.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib


class LaceClient:
    """
    Minimal Lace client for cloud operations.
    All algorithms and processing happen securely in the cloud.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Lace client.
        
        Args:
            api_key: API key for authentication. If not provided, uses LACE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('LACE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key required. Set LACE_API_KEY environment variable or pass api_key parameter.\n"
                "Get your key at https://withlace.ai/request-demo"
            )
        
        self.api_base = os.getenv(
            'LACE_API_URL',
            'https://usgf90tw68.execute-api.eu-west-1.amazonaws.com/prod'
        )
        
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def attest(self, dataset_path: str, name: Optional[str] = None) -> str:
        """
        Create attestation for a dataset.
        
        Args:
            dataset_path: Path to dataset directory
            name: Optional name for the dataset
            
        Returns:
            Attestation ID
        """
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Start attestation session
        response = requests.post(
            f"{self.api_base}/v1/attest/start",
            json={
                'dataset_path': str(dataset_path),
                'dataset_name': name or dataset_path.name
            },
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to start attestation: {response.text}")
        
        session_id = response.json()['session_id']
        
        # Stream dataset chunks (hashes only, not raw data)
        chunk_index = 0
        for file_path in dataset_path.rglob('*'):
            if file_path.is_file():
                # Hash file content
                chunk_hash = self._hash_file(file_path)
                
                # Send chunk hash to cloud
                response = requests.post(
                    f"{self.api_base}/v1/attest/chunk",
                    json={
                        'session_id': session_id,
                        'chunk_hash': chunk_hash,
                        'chunk_index': chunk_index
                    },
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"Warning: Failed to add chunk {chunk_index}: {response.text}")
                
                chunk_index += 1
        
        # Finalize attestation
        response = requests.post(
            f"{self.api_base}/v1/attest/finalize",
            json={'session_id': session_id},
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to finalize attestation: {response.text}")
        
        result = response.json()
        attestation_id = result['attestation_id']
        
        print(f"✅ Attestation created: {attestation_id}")
        print(f"   Merkle root: {result.get('merkle_root', 'N/A')}")
        
        return attestation_id
    
    def verify(self, attestation_id: str, check_copyright: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify an attestation.
        
        Args:
            attestation_id: ID of attestation to verify
            check_copyright: Optional text to check for copyright
            
        Returns:
            Verification result
        """
        params = {'attestation_id': attestation_id}
        if check_copyright:
            params['check_copyright'] = check_copyright
        
        response = requests.get(
            f"{self.api_base}/v1/verify",
            params=params,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Verification failed: {response.text}")
        
        result = response.json()
        
        # Display results
        if result.get('valid'):
            print(f"✅ Attestation {attestation_id} is valid")
            
            if 'correlation' in result:
                correlation = result['correlation']
                print(f"📊 Correlation Score: {correlation.get('score', 0):.3f}")
                print(f"   Verdict: {correlation.get('verdict', 'UNKNOWN')}")
            
            if 'copyright_check' in result:
                copyright = result['copyright_check']
                if copyright.get('found'):
                    print(f"⚠️  Copyright material potentially found")
                else:
                    print(f"✅ No copyright match found")
        else:
            print(f"❌ Attestation invalid: {result.get('error', 'Unknown error')}")
        
        return result
    
    def monitor_start(self, attestation_id: str) -> str:
        """
        Start monitoring session for training.
        
        Args:
            attestation_id: Attestation to monitor against
            
        Returns:
            Monitor session ID
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/start",
            json={'attestation_id': attestation_id},
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to start monitoring: {response.text}")
        
        return response.json()['session_id']
    
    def monitor_loss(self, session_id: str, step: int, loss: float):
        """
        Send loss value to cloud.
        
        Args:
            session_id: Monitor session ID
            step: Training step
            loss: Loss value
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/loss",
            json={
                'session_id': session_id,
                'step': step,
                'loss': loss
            },
            headers=self.headers
        )
        
        if response.status_code != 200:
            # Don't fail training if monitoring fails
            print(f"Warning: Failed to send loss: {response.text}")
    
    def monitor_finalize(self, session_id: str) -> Dict[str, Any]:
        """
        Finalize monitoring and get correlation.
        
        Args:
            session_id: Monitor session ID
            
        Returns:
            Monitoring results with correlation
        """
        response = requests.post(
            f"{self.api_base}/v1/monitor/finalize",
            json={'session_id': session_id},
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to finalize monitoring: {response.text}")
        
        return response.json()
    
    def _hash_file(self, file_path: Path) -> str:
        """Hash file content."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()


# Convenience functions for one-line usage
_default_client = None

def get_client() -> LaceClient:
    """Get or create default client."""
    global _default_client
    if _default_client is None:
        _default_client = LaceClient()
    return _default_client

def attest(dataset_path: str, name: Optional[str] = None) -> str:
    """Quick attestation."""
    return get_client().attest(dataset_path, name)

def verify(attestation_id: str, check_copyright: Optional[str] = None) -> Dict[str, Any]:
    """Quick verification."""
    return get_client().verify(attestation_id, check_copyright)

def monitor():
    """
    One-line training monitor.
    Automatically hooks into PyTorch/TensorFlow training.
    """
    from .monitor import LaceMonitor
    monitor = LaceMonitor()
    monitor.start()
    return monitor