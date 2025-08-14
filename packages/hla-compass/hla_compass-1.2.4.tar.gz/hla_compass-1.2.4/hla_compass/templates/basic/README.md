# Basic Peptide Search Module

A simple HLA-Compass module that demonstrates core platform functionality by searching for peptide sequences in the scientific database.

## Overview

This module is designed as a minimal template for developers getting started with the HLA-Compass platform. It showcases:

- **API Integration**: Connecting to the HLA-Compass API for data access
- **Input Validation**: Proper parameter validation and error handling
- **Data Access**: Using the SDK's peptide search capabilities
- **Structured Output**: Returning results in the standard module format

## Features

- Search for multiple peptide sequences in a single request
- Validate peptide sequences for standard amino acids
- Return detailed matches with metadata
- Provide summary statistics for the search

## Input Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `peptide_sequences` | array | Yes | List of peptide sequences to search (1-100 sequences) | - |
| `limit` | integer | No | Maximum results per sequence (1-100) | 10 |

## Output Format

The module returns a JSON object with the following structure:

```json
{
  "status": "success",
  "results": [
    {
      "query_sequence": "string",
      "status": "success|error|invalid",
      "matches_found": "integer",
      "matches": [
        {
          "id": "string",
          "sequence": "string",
          "length": "integer",
          "mass": "float",
          "source": "string",
          "organism": "string",
          "confidence": "float"
        }
      ]
    }
  ],
  "summary": {
    "total_sequences_searched": "integer",
    "successful_searches": "integer",
    "failed_searches": "integer",
    "invalid_sequences": "integer",
    "total_matches_found": "integer",
    "average_matches_per_sequence": "float"
  },
  "metadata": {
    "module": "string",
    "version": "string",
    "execution_time": "ISO 8601 timestamp",
    "duration_seconds": "float",
    "parameters": "object"
  }
}
```

## Usage

### Local Testing

1. **Set up authentication**:
   ```bash
   hla-compass auth login --env dev
   ```

2. **Test the module**:
   ```bash
   # From the module directory
   hla-compass test --input examples/input.json
   ```

### Deployment

1. **Build the module**:
   ```bash
   hla-compass build
   ```

2. **Deploy to platform** (requires deployment permissions):
   ```bash
   hla-compass deploy dist/basic-peptide-search-1.0.0.zip --env dev
   ```

## Code Structure

### Main Components

1. **`BasicPeptideSearch` Class**:
   - Inherits from `hla_compass.Module`
   - Implements the `execute()` method for main logic
   - Uses `self.peptides.search()` for database queries

2. **Input Validation**:
   - Checks for required parameters
   - Validates sequence format (standard amino acids only)
   - Enforces limits on batch size

3. **Error Handling**:
   - Individual sequence errors don't fail the entire batch
   - Clear error messages for debugging
   - Comprehensive logging for troubleshooting

### Key Methods

- `execute()`: Main entry point for module execution
- `_validate_sequence()`: Validates peptide sequences
- `lambda_handler()`: AWS Lambda integration point

## Development Tips

1. **Authentication**: Ensure you're authenticated before testing:
   ```bash
   hla-compass auth login --env dev
   ```

2. **Logging**: Use `self.logger` for debugging:
   ```python
   self.logger.info("Processing sequence")
   self.logger.error(f"Error: {str(e)}")
   ```

3. **Error Handling**: Use `self.error()` for module errors:
   ```python
   return self.error("Invalid input provided")
   ```

4. **Success Response**: Use `self.success()` for results:
   ```python
   return self.success(results=data, summary=stats)
   ```

## Example Input

```json
{
  "peptide_sequences": [
    "SIINFEKL",
    "GILGFVFTL",
    "YLQPRTFLL"
  ],
  "limit": 10
}
```

## Requirements

- Python 3.9+
- HLA-Compass SDK 1.0.0
- Valid developer account credentials

## Support

For questions or issues, refer to the [HLA-Compass Developer Documentation](https://docs.hla-compass.com) or contact the platform team.