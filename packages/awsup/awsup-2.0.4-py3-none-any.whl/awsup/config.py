"""
Configuration management for AWS Website Deployer
"""
import os
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError


@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    domain: str
    region: str = 'us-east-1'
    environment: str = 'prod'
    
    # S3 Configuration
    enable_versioning: bool = True
    enable_encryption: bool = True
    
    # CloudFront Configuration
    price_class: str = 'PriceClass_All'
    http_version: str = 'http2and3'
    enable_ipv6: bool = True
    
    # Certificate Configuration
    certificate_validation_method: str = 'DNS'
    
    # Timeouts (seconds)
    certificate_validation_timeout: int = 600
    distribution_deployment_timeout: int = 1200
    dns_propagation_check_timeout: int = 600
    
    # Retry Configuration
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    
    # Tags
    default_tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.default_tags is None:
            self.default_tags = {
                'ManagedBy': 'AWSWebsiteDeployer',
                'Environment': self.environment,
                'Domain': self.domain
            }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'DeploymentConfig':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def to_file(self, config_path: str):
        """Save configuration to JSON file"""
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    def validate(self):
        """Validate configuration values"""
        errors = []
        
        # Validate domain format
        if not self.domain or '.' not in self.domain:
            errors.append("Invalid domain format")
        
        # Validate region
        valid_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-central-1', 'ap-southeast-1',
            'ap-southeast-2', 'ap-northeast-1'
        ]
        if self.region not in valid_regions:
            errors.append(f"Invalid region: {self.region}")
        
        # Validate price class
        valid_price_classes = ['PriceClass_100', 'PriceClass_200', 'PriceClass_All']
        if self.price_class not in valid_price_classes:
            errors.append(f"Invalid price class: {self.price_class}")
        
        # Validate timeouts
        if self.certificate_validation_timeout < 60:
            errors.append("Certificate validation timeout too low (minimum 60s)")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


class AWSCredentialValidator:
    """Validates AWS credentials and permissions"""
    
    @staticmethod
    def validate_credentials() -> bool:
        """Check if AWS credentials are properly configured"""
        try:
            sts = boto3.client('sts')
            response = sts.get_caller_identity()
            return bool(response.get('Account'))
        except Exception:
            return False
    
    @staticmethod
    def validate_permissions(config: DeploymentConfig) -> Dict[str, bool]:
        """Check required AWS permissions"""
        permissions = {
            'route53': False,
            's3': False,
            'cloudfront': False,
            'acm': False
        }
        
        try:
            # Test Route53 permissions
            route53 = boto3.client('route53')
            route53.list_hosted_zones_by_name(DNSName=config.domain, MaxItems='1')
            permissions['route53'] = True
        except ClientError:
            pass
        
        try:
            # Test S3 permissions
            s3 = boto3.client('s3', region_name=config.region)
            s3.list_buckets()
            permissions['s3'] = True
        except ClientError:
            pass
        
        try:
            # Test CloudFront permissions
            cloudfront = boto3.client('cloudfront')
            cloudfront.list_distributions(MaxItems='1')
            permissions['cloudfront'] = True
        except ClientError:
            pass
        
        try:
            # Test ACM permissions
            acm = boto3.client('acm', region_name='us-east-1')
            acm.list_certificates(MaxItems=1)
            permissions['acm'] = True
        except ClientError:
            pass
        
        return permissions
    
    @staticmethod
    def get_account_id() -> Optional[str]:
        """Get AWS account ID"""
        try:
            sts = boto3.client('sts')
            return sts.get_caller_identity()['Account']
        except Exception:
            return None


class StateManager:
    """Manages deployment state"""
    
    def __init__(self, domain: str, environment: str = 'prod'):
        self.domain = domain
        self.environment = environment
        self.state_dir = Path('.aws-deployer-state')
        self.state_file = self.state_dir / f"{domain}_{environment}_state.json"
        
        # Ensure state directory exists
        self.state_dir.mkdir(exist_ok=True)
    
    def load_state(self) -> Dict:
        """Load deployment state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load state file: {e}")
        return {}
    
    def save_state(self, state: Dict):
        """Save deployment state"""
        try:
            state['last_updated'] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save state file: {e}")
    
    def clear_state(self):
        """Clear deployment state"""
        if self.state_file.exists():
            self.state_file.unlink()
    
    def get_state_summary(self) -> Dict:
        """Get deployment state summary"""
        state = self.load_state()
        return {
            'domain': self.domain,
            'environment': self.environment,
            'phase1_complete': bool(state.get('hosted_zone_id')),
            'phase2_complete': bool(state.get('distribution_id')),
            'last_updated': state.get('last_updated'),
            'resources': {
                'hosted_zone_id': state.get('hosted_zone_id'),
                'certificate_arn': state.get('certificate_arn'),
                'bucket_name': state.get('bucket_name'),
                'distribution_id': state.get('distribution_id')
            }
        }