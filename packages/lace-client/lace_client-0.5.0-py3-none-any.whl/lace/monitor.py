"""
Lace Training Monitor - Simplified cloud-only version.
Captures loss values and sends to cloud for correlation.
"""

import os
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
import json


class LaceMonitor:
    """
    Zero-overhead training monitor.
    Captures losses and sends to cloud for correlation.
    """
    
    def __init__(self, attestation_id: Optional[str] = None):
        """
        Initialize monitor.
        
        Args:
            attestation_id: Attestation to verify against. If not provided,
                          looks for latest attestation or LACE_ATTESTATION_ID env var.
        """
        self.attestation_id = attestation_id or self._find_attestation_id()
        self.session_id = None
        self.losses = []
        self.start_time = None
        self.client = None
        self._original_backward = None
    
    def start(self):
        """
        Start monitoring training.
        Automatically hooks into PyTorch/TensorFlow.
        """
        self.start_time = time.time()
        
        # Initialize cloud client
        from .client import get_client
        self.client = get_client()
        
        # Start cloud monitoring session
        if self.attestation_id:
            try:
                self.session_id = self.client.monitor_start(self.attestation_id)
                print(f"📊 Lace monitoring started for attestation {self.attestation_id}")
            except Exception as e:
                print(f"⚠️  Could not start cloud monitoring: {e}")
                print("   Losses will be saved locally for later verification")
        
        # Hook into training framework
        self._hook_framework()
    
    def _hook_framework(self):
        """Hook into PyTorch or TensorFlow to capture losses."""
        
        # Try PyTorch first
        try:
            import torch
            
            # Store original backward
            self._original_backward = torch.Tensor.backward
            
            # Create wrapper
            def backward_wrapper(tensor, gradient=None, retain_graph=None, create_graph=False):
                # Capture loss value
                if tensor.numel() == 1:  # Scalar loss
                    loss_value = float(tensor.item())
                    self._record_loss(loss_value)
                
                # Call original backward
                return self._original_backward(
                    tensor, gradient, retain_graph, create_graph
                )
            
            # Monkey-patch
            torch.Tensor.backward = backward_wrapper
            print("✅ Hooked into PyTorch training")
            return
            
        except ImportError:
            pass
        
        # Try TensorFlow
        try:
            import tensorflow as tf
            
            # Hook into GradientTape
            original_gradient = tf.GradientTape.gradient
            
            def gradient_wrapper(tape, target, sources, **kwargs):
                # Capture loss if target is scalar
                if hasattr(target, 'numpy'):
                    try:
                        loss_value = float(target.numpy())
                        self._record_loss(loss_value)
                    except:
                        pass
                
                # Call original
                return original_gradient(tape, target, sources, **kwargs)
            
            tf.GradientTape.gradient = gradient_wrapper
            print("✅ Hooked into TensorFlow training")
            return
            
        except ImportError:
            pass
        
        print("⚠️  No training framework detected. Call monitor.log(loss) manually.")
    
    def _record_loss(self, loss: float):
        """Record loss value."""
        step = len(self.losses)
        self.losses.append({
            'step': step,
            'loss': loss,
            'timestamp': time.time()
        })
        
        # Send to cloud if session active
        if self.session_id and self.client:
            try:
                self.client.monitor_loss(self.session_id, step, loss)
            except:
                pass  # Don't interrupt training
        
        # Print progress occasionally
        if step % 100 == 0:
            print(f"  Step {step}: loss = {loss:.4f}")
    
    def log(self, loss: float):
        """Manually log a loss value."""
        self._record_loss(loss)
    
    def finalize(self) -> Dict[str, Any]:
        """
        Finalize monitoring and get correlation from cloud.
        
        Returns:
            Dictionary with correlation results
        """
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Save losses locally
        self._save_local_losses()
        
        # Get correlation from cloud
        result = {
            'steps': len(self.losses),
            'duration': duration,
            'attestation_id': self.attestation_id
        }
        
        if self.session_id and self.client:
            try:
                cloud_result = self.client.monitor_finalize(self.session_id)
                result.update(cloud_result)
                
                # Display results
                if 'correlation' in cloud_result:
                    corr = cloud_result['correlation']
                    print(f"\n📊 Training Correlation: {corr.get('score', 0):.3f}")
                    print(f"   Verdict: {corr.get('verdict', 'UNKNOWN')}")
                    
            except Exception as e:
                print(f"⚠️  Could not get correlation from cloud: {e}")
                result['error'] = str(e)
        
        # Restore original backward if patched
        if self._original_backward:
            try:
                import torch
                torch.Tensor.backward = self._original_backward
            except:
                pass
        
        print(f"\n✅ Monitoring complete: {len(self.losses)} steps captured")
        
        return result
    
    def _find_attestation_id(self) -> Optional[str]:
        """Find attestation ID from environment or local directory."""
        
        # Check environment variable
        attestation_id = os.getenv('LACE_ATTESTATION_ID')
        if attestation_id:
            return attestation_id
        
        # Look for .lace directory
        current = Path.cwd()
        while current != current.parent:
            lace_dir = current / '.lace'
            if lace_dir.exists():
                # Find latest attestation
                attestations = sorted(lace_dir.glob('attestations/*'))
                if attestations:
                    return attestations[-1].name
            current = current.parent
        
        return None
    
    def _save_local_losses(self):
        """Save losses locally for offline verification."""
        
        if not self.losses:
            return
        
        # Find or create .lace directory
        lace_dir = Path.cwd() / '.lace'
        lace_dir.mkdir(exist_ok=True)
        
        # Save losses
        loss_file = lace_dir / f"losses_{int(time.time())}.json"
        with open(loss_file, 'w') as f:
            json.dump({
                'attestation_id': self.attestation_id,
                'losses': self.losses,
                'duration': time.time() - self.start_time if self.start_time else 0
            }, f, indent=2)
        
        print(f"💾 Losses saved to {loss_file}")


# Convenience function for one-line usage
def monitor(attestation_id: Optional[str] = None) -> LaceMonitor:
    """
    Start monitoring training with one line.
    
    Usage:
        import lace
        lace.monitor()  # Automatically hooks into training
    
    Args:
        attestation_id: Optional attestation to verify against
        
    Returns:
        Monitor instance
    """
    m = LaceMonitor(attestation_id)
    m.start()
    return m