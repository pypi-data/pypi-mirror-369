"""
Basic Peptide Search Module

This is a simple module that demonstrates the core functionality of the HLA-Compass
platform. It searches for peptide sequences in the scientific database and returns
structured results in JSON format.

This module showcases:
- Using the Module base class from the SDK
- Accessing peptide data via the API
- Input validation and error handling
- Structured output formatting
"""

from hla_compass import Module
from typing import Dict, Any, List


class BasicPeptideSearch(Module):
    """
    A basic peptide search module that queries the HLA-Compass database
    
    This module accepts a list of peptide sequences and searches for them
    in the platform's scientific database, returning matches with metadata.
    """
    
    def __init__(self):
        """Initialize the module"""
        super().__init__()
        self.logger.info("BasicPeptideSearch module initialized")
    
    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution function that performs peptide search
        
        Args:
            input_data: Contains 'peptide_sequences' (list) and optional 'limit' (int)
            context: Execution context with job_id, user_id, etc.
            
        Returns:
            Dictionary with search results for each input sequence
        """
        try:
            # Extract and validate input parameters
            sequences = input_data.get('peptide_sequences', [])
            limit = input_data.get('limit', 10)
            
            # Validate sequences input
            if not sequences:
                return self.error("Missing required parameter: peptide_sequences")
            
            if not isinstance(sequences, list):
                return self.error("peptide_sequences must be a list")
            
            if len(sequences) > 100:
                return self.error("Maximum 100 sequences allowed per request")
            
            # Validate limit parameter
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                return self.error("limit must be an integer between 1 and 100")
            
            # Log the search request
            self.logger.info(f"Searching for {len(sequences)} peptide sequences")
            
            # Initialize results structure
            results = []
            total_found = 0
            
            # Search for each sequence
            for sequence in sequences:
                # Clean and validate the sequence
                sequence = str(sequence).upper().strip()
                
                # Basic sequence validation (only standard amino acids)
                if not self._validate_sequence(sequence):
                    self.logger.warning(f"Invalid sequence skipped: {sequence}")
                    results.append({
                        'query_sequence': sequence,
                        'status': 'invalid',
                        'error': 'Sequence contains invalid characters',
                        'matches': []
                    })
                    continue
                
                try:
                    # Search for the peptide using the SDK data access API
                    # The self.peptides object is automatically initialized by the Module base class
                    matches = self.peptides.search(
                        sequence=sequence,
                        limit=limit
                    )
                    
                    # Process and format the matches
                    formatted_matches = []
                    for match in matches:
                        formatted_matches.append({
                            'id': match.get('id'),
                            'sequence': match.get('sequence'),
                            'length': match.get('length'),
                            'mass': match.get('mass'),
                            'source': match.get('source', 'Unknown'),
                            'organism': match.get('organism', 'Unknown'),
                            'confidence': match.get('confidence', 0.0)
                        })
                    
                    # Add to results
                    results.append({
                        'query_sequence': sequence,
                        'status': 'success',
                        'matches_found': len(formatted_matches),
                        'matches': formatted_matches
                    })
                    
                    total_found += len(formatted_matches)
                    self.logger.info(f"Found {len(formatted_matches)} matches for {sequence}")
                    
                except Exception as e:
                    # Handle errors for individual sequence searches
                    self.logger.error(f"Error searching for {sequence}: {str(e)}")
                    results.append({
                        'query_sequence': sequence,
                        'status': 'error',
                        'error': str(e),
                        'matches': []
                    })
            
            # Create summary statistics
            summary = {
                'total_sequences_searched': len(sequences),
                'successful_searches': sum(1 for r in results if r['status'] == 'success'),
                'failed_searches': sum(1 for r in results if r['status'] == 'error'),
                'invalid_sequences': sum(1 for r in results if r['status'] == 'invalid'),
                'total_matches_found': total_found,
                'average_matches_per_sequence': round(total_found / len(sequences), 2) if sequences else 0
            }
            
            # Return successful response with results
            return self.success(
                results=results,
                summary=summary
            )
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Module execution failed: {str(e)}")
            return self.error(f"Module execution failed: {str(e)}")
    
    def _validate_sequence(self, sequence: str) -> bool:
        """
        Validate that a sequence contains only standard amino acids
        
        Args:
            sequence: Peptide sequence to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Standard single-letter amino acid codes
        valid_amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
        
        # Check if all characters are valid amino acids
        return all(aa in valid_amino_acids for aa in sequence.upper())


# Lambda handler for AWS Lambda execution
def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    This function is called when the module is executed in AWS Lambda.
    It creates an instance of the module and delegates to the handle_lambda method.
    
    Args:
        event: Lambda event containing input parameters
        context: Lambda context with request metadata
        
    Returns:
        Module execution result
    """
    module = BasicPeptideSearch()
    return module.handle_lambda(event, context)