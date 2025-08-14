"""
API client for HLA-Compass platform

This module provides the APIClient class that handles all communication
with the HLA-Compass REST API. It's used internally by the data access
classes (PeptideData, ProteinData, SampleData) to fetch scientific data.
"""

import requests
import logging
import time
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from .auth import Auth
from .config import Config


logger = logging.getLogger(__name__)


class APIError(Exception):
    """API request error"""
    def __init__(self, message: str, status_code: int = None, details: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class APIClient:
    """
    Client for interacting with HLA-Compass API
    
    This client handles:
    - Authentication using JWT tokens
    - Request formatting and response parsing
    - Error handling and retries
    - Pagination support
    """
    
    def __init__(self):
        """Initialize API client with authentication"""
        self.auth = Auth()
        self.config = Config()
        self.base_url = self.config.get_api_endpoint()
        
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     params: Dict = None, 
                     json_data: Dict = None,
                     max_retries: int = 3) -> Dict[str, Any]:
        """
        Make an authenticated API request with retries and timeouts
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., /v1/scientific/peptides)
            params: Query parameters
            json_data: JSON body data
            max_retries: Maximum number of retry attempts for transient errors
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: If request fails
        """
        # Ensure we have authentication
        if not self.auth.is_authenticated():
            raise APIError("Not authenticated. Please run 'hla-compass auth login' first")
        
        # Build full URL
        url = f"{self.base_url}{endpoint}"
        
        # Get auth headers
        headers = self.auth.get_headers()
        
        # Retry logic for transient errors
        for attempt in range(max_retries):
            try:
                # Make request with timeout (5s connect, 30s read)
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=(5, 30)
                )
                
                # Handle 401 - try to refresh token once
                if response.status_code == 401 and attempt == 0:
                    logger.info("Token expired, attempting refresh")
                    new_token = self.auth.refresh_token()
                    if new_token:
                        headers = self.auth.get_headers()
                        continue  # Retry with new token
                    else:
                        raise APIError("Authentication expired. Please run 'hla-compass auth login' again")
                
                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
                        logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                        time.sleep(retry_after)
                        continue
                    else:
                        raise APIError("Rate limit exceeded. Please try again later.", 429)
                
                # Handle server errors with retry
                if response.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Server error {response.status_code}, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                
                # Check for other errors
                if response.status_code >= 400:
                    # Try to parse JSON error response, but handle non-JSON responses gracefully
                    try:
                        error_data = response.json() if response.text else {}
                        error_msg = error_data.get('error', {}).get('message', f'API error: {response.status_code}')
                        error_details = error_data.get('error', {})
                    except (json.JSONDecodeError, ValueError):
                        # If response is not JSON, use the text content as error message
                        error_msg = response.text if response.text else f'API error: {response.status_code}'
                        error_details = {'raw_response': response.text}
                    
                    raise APIError(error_msg, response.status_code, error_details)
                
                # Parse successful response
                data = response.json()
                
                # Handle success wrapper format
                if isinstance(data, dict) and data.get('success'):
                    return data.get('data', data)
                
                return data
                
            except requests.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request timeout, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError("Request timed out. Please check your connection and try again.")
                    
            except requests.RequestException as e:
                if attempt < max_retries - 1 and "connection" in str(e).lower():
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection error, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Network error: {str(e)}")
    
    # Peptide endpoints
    
    def get_peptides(self, 
                    filters: Dict = None, 
                    limit: int = 100, 
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search peptides with filters
        
        Args:
            filters: Search filters (sequence, min_length, max_length, etc.)
            limit: Maximum results to return
            offset: Pagination offset
            
        Returns:
            List of peptide records
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        # Add filters to params
        if filters:
            # Map internal filter names to API parameter names
            filter_mapping = {
                'sequence': 'sequence',
                'min_length': 'min_length',
                'max_length': 'max_length',
                'mass': 'mass',
                'mass_tolerance': 'mass_tolerance',
                'modifications': 'modifications',
                'hla_allele': 'hla',
                'organ': 'organ',
                'disease': 'disease'
            }
            
            for key, value in filters.items():
                api_param = filter_mapping.get(key, key)
                if isinstance(value, list):
                    params[api_param] = ','.join(str(v) for v in value)
                else:
                    params[api_param] = value
        
        result = self._make_request('GET', '/v1/scientific/peptides', params=params)
        
        # Extract peptides from response
        if isinstance(result, dict):
            return result.get('peptides', result.get('items', []))
        return result if isinstance(result, list) else []
    
    def get_peptide(self, peptide_id: str) -> Dict[str, Any]:
        """Get single peptide by ID"""
        result = self._make_request('GET', f'/v1/scientific/peptides/{peptide_id}')
        return result.get('peptide', result)
    
    def get_peptide_samples(self, peptide_id: str) -> List[Dict[str, Any]]:
        """Get samples containing a peptide"""
        result = self._make_request('GET', f'/v1/scientific/peptides/{peptide_id}/samples')
        return result.get('samples', result.get('items', []))
    
    def get_peptide_proteins(self, peptide_id: str) -> List[Dict[str, Any]]:
        """Get proteins containing a peptide"""
        result = self._make_request('GET', f'/v1/scientific/peptides/{peptide_id}/proteins')
        return result.get('proteins', result.get('items', []))
    
    def search_peptides_by_mass(self, 
                               mass: float, 
                               tolerance: float = 0.01, 
                               unit: str = 'Da') -> List[Dict[str, Any]]:
        """Search peptides by mass"""
        params = {
            'mass': mass,
            'tolerance': tolerance,
            'unit': unit
        }
        result = self._make_request('GET', '/v1/scientific/peptides/search/mass', params=params)
        return result.get('peptides', result.get('items', []))
    
    # Protein endpoints
    
    def get_proteins(self, 
                    filters: Dict = None, 
                    limit: int = 100, 
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search proteins with filters
        
        Args:
            filters: Search filters (accession, gene_name, organism, etc.)
            limit: Maximum results to return
            offset: Pagination offset
            
        Returns:
            List of protein records
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if filters:
            params.update(filters)
        
        result = self._make_request('GET', '/v1/scientific/proteins', params=params)
        
        # Extract proteins from response
        if isinstance(result, dict):
            return result.get('proteins', result.get('items', []))
        return result if isinstance(result, list) else []
    
    def get_protein(self, protein_id: str) -> Dict[str, Any]:
        """Get single protein by ID"""
        result = self._make_request('GET', f'/v1/scientific/proteins/{protein_id}')
        return result.get('protein', result)
    
    def get_protein_peptides(self, protein_id: str) -> List[Dict[str, Any]]:
        """Get peptides from a protein"""
        result = self._make_request('GET', f'/v1/scientific/proteins/{protein_id}/peptides')
        return result.get('peptides', result.get('items', []))
    
    def get_protein_coverage(self, protein_id: str) -> Dict[str, Any]:
        """Get protein coverage information"""
        result = self._make_request('GET', f'/v1/scientific/proteins/{protein_id}/coverage')
        return result
    
    # Sample endpoints
    
    def get_samples(self, 
                   filters: Dict = None, 
                   limit: int = 100, 
                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search samples with filters
        
        Args:
            filters: Search filters (tissue, disease, cell_line, etc.)
            limit: Maximum results to return
            offset: Pagination offset
            
        Returns:
            List of sample records
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if filters:
            params.update(filters)
        
        result = self._make_request('GET', '/v1/scientific/samples', params=params)
        
        # Extract samples from response
        if isinstance(result, dict):
            return result.get('samples', result.get('items', []))
        return result if isinstance(result, list) else []
    
    def get_sample(self, sample_id: str) -> Dict[str, Any]:
        """Get single sample by ID"""
        result = self._make_request('GET', f'/v1/scientific/samples/{sample_id}')
        return result.get('sample', result)
    
    def get_sample_peptides(self, sample_id: str) -> List[Dict[str, Any]]:
        """Get peptides from a sample"""
        result = self._make_request('GET', f'/v1/scientific/samples/{sample_id}/peptides')
        return result.get('peptides', result.get('items', []))
    
    def compare_samples(self, 
                       sample_ids: List[str], 
                       metric: str = 'jaccard') -> Dict[str, Any]:
        """Compare multiple samples"""
        json_data = {
            'sample_ids': sample_ids,
            'metric': metric
        }
        return self._make_request('POST', '/v1/scientific/samples/compare', json_data=json_data)
    
    # HLA endpoints
    
    def get_hla_alleles(self, 
                       locus: str = None, 
                       resolution: str = '2-digit') -> List[str]:
        """Get list of HLA alleles"""
        params = {
            'resolution': resolution
        }
        if locus:
            params['locus'] = locus
        
        result = self._make_request('GET', '/v1/scientific/hla/alleles', params=params)
        return result.get('alleles', result if isinstance(result, list) else [])
    
    def get_hla_frequencies(self, population: str = None) -> Dict[str, float]:
        """Get HLA allele frequencies"""
        params = {}
        if population:
            params['population'] = population
        
        result = self._make_request('GET', '/v1/scientific/hla/frequencies', params=params)
        return result.get('frequencies', result if isinstance(result, dict) else {})
    
    def predict_hla_binding(self, 
                          peptides: List[str], 
                          alleles: List[str], 
                          method: str = 'netmhcpan') -> List[Dict[str, Any]]:
        """Predict HLA-peptide binding"""
        json_data = {
            'peptides': peptides,
            'alleles': alleles,
            'method': method
        }
        result = self._make_request('POST', '/v1/scientific/hla/predict', json_data=json_data)
        return result.get('predictions', result if isinstance(result, list) else [])
    
    # Module endpoints
    
    def execute_module(self, 
                      module_id: str, 
                      parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a module with parameters
        
        Args:
            module_id: Module ID to execute
            parameters: Input parameters for the module
            
        Returns:
            Job information including job_id
        """
        json_data = {
            'parameters': parameters
        }
        return self._make_request('POST', f'/v1/modules/{module_id}/execute', json_data=json_data)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job execution status"""
        return self._make_request('GET', f'/v1/modules/jobs/{job_id}/status')
    
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Get job execution result"""
        return self._make_request('GET', f'/v1/modules/jobs/{job_id}/result')
    
    def list_modules(self, 
                    category: str = None, 
                    limit: int = 100) -> List[Dict[str, Any]]:
        """List available modules"""
        params = {'limit': limit}
        if category:
            params['category'] = category
        
        result = self._make_request('GET', '/v1/modules', params=params)
        return result.get('modules', result.get('items', []))
    
    def upload_module(self, 
                     module_path: str, 
                     module_name: str, 
                     version: str) -> Dict[str, Any]:
        """
        Upload module package to platform
        
        Args:
            module_path: Path to module zip file
            module_name: Name of the module
            version: Module version
            
        Returns:
            Upload response with module_id
        """
        import os
        
        # Check file exists
        if not os.path.exists(module_path):
            raise APIError(f"Module package not found: {module_path}")
        
        # Get file size
        file_size = os.path.getsize(module_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise APIError(f"Module package too large: {file_size / 1024 / 1024:.1f}MB (max 50MB)")
        
        # Prepare multipart upload
        with open(module_path, 'rb') as f:
            files = {
                'module': (f'{module_name}-{version}.zip', f, 'application/zip')
            }
            data = {
                'name': module_name,
                'version': version
            }
            
            # Make request with file upload
            headers = self.auth.get_headers()
            url = f"{self.base_url}/v1/modules/upload"
            
            response = requests.post(
                url=url,
                headers=headers,
                files=files,
                data=data,
                timeout=(10, 60)  # 10s connect, 60s read for upload
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get('error', {}).get('message', f'Upload failed: {response.status_code}')
                except:
                    error_msg = f'Upload failed: {response.status_code}'
                raise APIError(error_msg, response.status_code)
            
            result = response.json()
            if isinstance(result, dict) and result.get('success'):
                return result.get('data', result)
            return result
    
    def register_module(self, 
                       module_id: str, 
                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register uploaded module in platform
        
        Args:
            module_id: Module ID from upload
            metadata: Module metadata (manifest info)
            
        Returns:
            Registration confirmation
        """
        json_data = {
            'module_id': module_id,
            'metadata': metadata
        }
        return self._make_request('POST', '/v1/modules/register', json_data=json_data)