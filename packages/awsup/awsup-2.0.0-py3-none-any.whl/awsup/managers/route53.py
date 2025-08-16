"""
Route53 Manager for DNS operations
"""
import boto3
import time
from typing import Dict, List, Optional, Tuple, Any
from botocore.exceptions import ClientError
from .base import BaseAWSManager
from ..config import DeploymentConfig


class Route53Manager(BaseAWSManager):
    """Manages Route53 hosted zones and DNS records"""
    
    def __init__(self, config: DeploymentConfig):
        super().__init__(config)
        self.client = boto3.client('route53')
        self.domain = config.domain
        self.www_domain = f"www.{config.domain}"
    
    def create_or_get_hosted_zone(self) -> Dict[str, Any]:
        """
        Create or get existing hosted zone
        Returns: Dict with hosted zone info and action taken
        """
        try:
            # Check for existing hosted zone
            existing_zone = self.get_hosted_zone()
            
            if existing_zone:
                self.logger.info(f"Found existing hosted zone: {existing_zone['Id']}")
                
                # Clean up conflicting records
                self.cleanup_conflicting_records(existing_zone['Id'])
                
                # Get NS records
                ns_records = self.get_ns_records(existing_zone['Id'])
                
                return {
                    'hosted_zone_id': existing_zone['Id'],
                    'ns_records': ns_records,
                    'action': 'existing'
                }
            
            # Create new hosted zone
            self.logger.info(f"Creating new hosted zone for {self.domain}")
            
            def create_zone():
                return self.client.create_hosted_zone(
                    Name=self.domain,
                    CallerReference=f"{self.domain}-{int(time.time())}",
                    HostedZoneConfig={
                        'Comment': f'Hosted zone for {self.domain} (Environment: {self.config.environment})',
                        'PrivateZone': False
                    }
                )
            
            response = self.retry_with_backoff(create_zone)
            
            hosted_zone_id = response['HostedZone']['Id']
            ns_records = [ns for ns in response['DelegationSet']['NameServers']]
            
            # Add tags
            self.add_tags(hosted_zone_id)
            
            self.logger.info(f"Created hosted zone: {hosted_zone_id}")
            
            return {
                'hosted_zone_id': hosted_zone_id,
                'ns_records': ns_records,
                'action': 'created'
            }
            
        except Exception as e:
            self.logger.error(f"Hosted zone operation failed: {e}")
            raise
    
    def get_hosted_zone(self) -> Optional[Dict]:
        """Get existing hosted zone for the domain"""
        try:
            def list_zones():
                return self.client.list_hosted_zones_by_name(DNSName=self.domain)
            
            response = self.retry_with_backoff(list_zones)
            
            for zone in response.get('HostedZones', []):
                zone_name = zone['Name'].rstrip('.')
                if zone_name == self.domain:
                    return zone
            
            return None
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchHostedZone':
                return None
            raise
    
    def get_ns_records(self, hosted_zone_id: str) -> List[str]:
        """Get NS records for hosted zone"""
        try:
            def get_records():
                return self.client.list_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    StartRecordType='NS',
                    StartRecordName=self.domain
                )
            
            response = self.retry_with_backoff(get_records)
            
            for record_set in response['ResourceRecordSets']:
                if (record_set['Type'] == 'NS' and 
                    record_set['Name'].rstrip('.') == self.domain):
                    return [r['Value'] for r in record_set['ResourceRecords']]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get NS records: {e}")
            raise
    
    def cleanup_conflicting_records(self, hosted_zone_id: str):
        """Remove conflicting A and CNAME records"""
        try:
            def list_records():
                return self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
            
            response = self.retry_with_backoff(list_records)
            
            changes = []
            for record_set in response['ResourceRecordSets']:
                record_name = record_set['Name'].rstrip('.')
                
                # Check for conflicting records
                if record_name in [self.domain, self.www_domain]:
                    if record_set['Type'] in ['A', 'AAAA', 'CNAME']:
                        # Skip CloudFront aliases (we might want to keep them)
                        if (record_set.get('AliasTarget', {}).get('DNSName', '')
                                .endswith('.cloudfront.net.')):
                            self.logger.info(f"Keeping existing CloudFront alias: {record_name}")
                            continue
                        
                        self.logger.info(f"Removing conflicting {record_set['Type']} record: {record_name}")
                        changes.append({
                            'Action': 'DELETE',
                            'ResourceRecordSet': record_set
                        })
            
            if changes:
                def delete_records():
                    return self.client.change_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        ChangeBatch={'Changes': changes}
                    )
                
                self.retry_with_backoff(delete_records)
                self.logger.info(f"Removed {len(changes)} conflicting records")
                
        except Exception as e:
            self.logger.warning(f"Error cleaning up records: {e}")
    
    def create_alias_records(self, cloudfront_domain: str, hosted_zone_id: str):
        """Create A records pointing to CloudFront distribution"""
        try:
            changes = [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': self.domain,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': 'Z2FDTNDATAQYW2',  # CloudFront hosted zone ID
                            'DNSName': cloudfront_domain,
                            'EvaluateTargetHealth': False
                        }
                    }
                },
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': self.www_domain,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': 'Z2FDTNDATAQYW2',
                            'DNSName': cloudfront_domain,
                            'EvaluateTargetHealth': False
                        }
                    }
                }
            ]
            
            def create_records():
                return self.client.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch={'Changes': changes}
                )
            
            self.retry_with_backoff(create_records)
            self.logger.info(f"Created A records for {self.domain} and {self.www_domain}")
            
        except Exception as e:
            self.logger.error(f"Failed to create Route53 records: {e}")
            raise
    
    def delete_hosted_zone(self, hosted_zone_id: str):
        """Delete hosted zone and all records"""
        try:
            # First delete all records except NS and SOA
            self._delete_all_records(hosted_zone_id)
            
            # Then delete the hosted zone
            def delete_zone():
                return self.client.delete_hosted_zone(Id=hosted_zone_id)
            
            self.retry_with_backoff(delete_zone)
            self.logger.info(f"Deleted hosted zone: {hosted_zone_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete hosted zone: {e}")
            raise
    
    def _delete_all_records(self, hosted_zone_id: str):
        """Delete all records except NS and SOA"""
        try:
            def list_records():
                return self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
            
            response = self.retry_with_backoff(list_records)
            
            changes = []
            for record_set in response['ResourceRecordSets']:
                # Skip NS and SOA records (cannot be deleted)
                if record_set['Type'] in ['NS', 'SOA']:
                    continue
                
                changes.append({
                    'Action': 'DELETE',
                    'ResourceRecordSet': record_set
                })
            
            if changes:
                def delete_records():
                    return self.client.change_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        ChangeBatch={'Changes': changes}
                    )
                
                self.retry_with_backoff(delete_records)
                self.logger.info(f"Deleted {len(changes)} records from hosted zone")
                
        except Exception as e:
            self.logger.warning(f"Error deleting records: {e}")
    
    def add_tags(self, hosted_zone_id: str, additional_tags: Optional[Dict[str, str]] = None):
        """Add tags to hosted zone"""
        try:
            tags = self.config.default_tags.copy()
            if additional_tags:
                tags.update(additional_tags)
            
            tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            def add_zone_tags():
                return self.client.change_tags_for_resource(
                    ResourceType='hostedzone',
                    ResourceId=hosted_zone_id.replace('/hostedzone/', ''),
                    AddTags=tag_list
                )
            
            self.retry_with_backoff(add_zone_tags)
            self.logger.info(f"Added tags to hosted zone: {list(tags.keys())}")
            
        except Exception as e:
            self.logger.warning(f"Failed to add tags: {e}")
    
    def validate_resource_exists(self, hosted_zone_id: str) -> bool:
        """Check if hosted zone exists"""
        try:
            def get_zone():
                return self.client.get_hosted_zone(Id=hosted_zone_id)
            
            self.retry_with_backoff(get_zone)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchHostedZone':
                return False
            raise
    
    def get_resource_status(self, hosted_zone_id: str) -> str:
        """Get hosted zone status"""
        try:
            if self.validate_resource_exists(hosted_zone_id):
                return "active"
            return "not_found"
        except Exception:
            return "error"