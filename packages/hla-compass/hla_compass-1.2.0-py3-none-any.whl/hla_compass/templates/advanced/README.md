# Advanced Analysis Suite

Comprehensive HLA-Compass module demonstrating all platform capabilities in a single, integrated solution.

## Overview

This advanced template showcases the full potential of the HLA-Compass platform:

### Backend Capabilities
- **Multi-modal Analysis**: Peptide, protein, sample, and HLA analysis in one module
- **Complex Filtering**: Advanced search parameters and batch processing
- **Data Integration**: Cross-referencing between different data types
- **Progress Tracking**: Real-time updates for long-running analyses
- **Error Recovery**: Robust error handling with partial result support
- **Multiple Output Formats**: JSON, CSV, and Excel export
- **Cloud Storage**: S3 integration for result persistence
- **Performance Metrics**: Detailed execution statistics

### Frontend Capabilities
- **Multi-tab Interface**: Organized analysis types with dedicated forms
- **Complex Forms**: Advanced input validation and dynamic fields
- **Data Visualization**: Charts and graphs for result interpretation
- **File Operations**: Upload parameters and download results
- **Progress Indicators**: Real-time feedback during execution
- **Results Management**: Filtering, sorting, and pagination
- **Error Recovery**: User-friendly error messages with retry options
- **Responsive Design**: Adaptive layout for different screen sizes

## Analysis Types

### 1. Comprehensive Analysis
Runs all four analysis types with configurable parameters for each.

### 2. Peptide Search
- Sequence-based searching with wildcards
- Length and mass filtering
- Similarity calculations
- Organism and source filtering

### 3. Protein Analysis  
- UniProt accession lookup
- Gene name searching
- Peptide coverage calculation
- Unique peptide identification

### 4. Sample Comparison
- Tissue and disease filtering
- Multi-sample overlap analysis
- Jaccard similarity calculations
- Abundance-based filtering

### 5. HLA Prediction
- Multi-allele binding predictions
- Multiple prediction methods
- Strong binder identification
- Percentile rank calculations

## Input Parameters

### Common Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `analysis_type` | string | Type of analysis to perform |
| `output_format` | string | Output format (json/csv/excel) |
| `save_to_storage` | boolean | Save results to cloud storage |

### Peptide Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `sequences` | array | Peptide sequences to search |
| `min_length` | integer | Minimum peptide length |
| `max_length` | integer | Maximum peptide length |
| `mass_tolerance` | float | Mass tolerance in Daltons |

### Protein Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `accession` | string | UniProt accession |
| `gene_name` | string | Gene name |
| `organism` | string | Organism ID or name |

### Sample Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `sample_ids` | array | Specific sample IDs |
| `tissue` | string | Tissue type filter |
| `disease` | string | Disease filter |

### HLA Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `peptides` | array | Peptides for prediction |
| `alleles` | array | HLA alleles |
| `method` | string | Prediction method |

## Usage

### Local Development

1. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

2. **Build frontend**:
   ```bash
   npm run build
   ```

3. **Test module**:
   ```bash
   hla-compass test --input examples/input.json
   ```

### Deployment

```bash
# Build module package
hla-compass build

# Deploy to platform
hla-compass deploy dist/advanced-analysis-suite-1.0.0.zip --env dev
```

## Architecture

### Backend Structure
```
backend/
├── main.py                 # Main module implementation
├── requirements.txt        # Python dependencies
└── tests/                  # Unit tests (optional)
```

### Frontend Structure
```
frontend/
├── index.tsx              # Main React component
├── package.json           # Node dependencies
├── components/            # Sub-components (optional)
└── styles/               # CSS modules (optional)
```

### Key Classes and Methods

#### Backend
- `AdvancedAnalysisSuite`: Main module class
- `_analyze_peptides()`: Peptide search logic
- `_analyze_proteins()`: Protein analysis logic
- `_compare_samples()`: Sample comparison logic
- `_predict_hla_binding()`: HLA prediction logic
- `_generate_visualizations()`: Create chart data
- `_format_output()`: Export to different formats

#### Frontend
- `AdvancedAnalysisSuite`: Main React component
- `handleExecute()`: Form submission handler
- `renderPeptideForm()`: Peptide input form
- `renderProteinForm()`: Protein input form
- `renderSampleForm()`: Sample input form
- `renderHLAForm()`: HLA input form
- `renderResults()`: Results display logic

## Performance Considerations

### Backend Optimization
- **Batch Processing**: Groups API calls for efficiency
- **Parallel Queries**: Concurrent data fetching where possible
- **Result Caching**: Temporary caching of intermediate results
- **Pagination**: Limits result size to prevent memory issues

### Frontend Optimization
- **Lazy Loading**: Components loaded on demand
- **Virtual Scrolling**: For large result tables
- **Memoization**: Prevents unnecessary re-renders
- **Debouncing**: For search inputs

## Error Handling

### Backend
- Individual operation errors don't fail entire analysis
- Partial results returned when possible
- Detailed error logging for debugging
- Retry logic for transient failures

### Frontend
- User-friendly error messages
- Recovery suggestions
- Retry buttons for failed operations
- Form validation before submission

## Security Considerations

- Input validation on both frontend and backend
- Parameterized queries to prevent injection
- Rate limiting awareness
- Secure credential handling

## Extension Points

### Adding New Analysis Types
1. Add new parameter interface in manifest.json
2. Create analysis method in backend/main.py
3. Add form section in frontend/index.tsx
4. Update results display component

### Custom Visualizations
1. Generate visualization data in backend
2. Add chart component in frontend
3. Use Recharts or Plotly for rendering

### Export Formats
1. Add format handler in `_format_output()`
2. Implement serialization logic
3. Update frontend export options

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   hla-compass auth login --env dev
   ```

2. **Module Build Failures**:
   - Check all dependencies are installed
   - Verify manifest.json syntax
   - Ensure frontend is built

3. **API Rate Limiting**:
   - Reduce batch sizes
   - Add delays between requests
   - Use pagination effectively

4. **Memory Issues**:
   - Limit result sizes
   - Use streaming for large datasets
   - Implement pagination

## Best Practices

1. **Always validate input** before processing
2. **Handle errors gracefully** with informative messages
3. **Log important events** for debugging
4. **Test with various input sizes** to ensure scalability
5. **Document complex logic** with inline comments
6. **Follow platform conventions** for consistency
7. **Optimize API usage** to minimize calls
8. **Provide progress feedback** for long operations

## Support

For questions or issues, refer to the [HLA-Compass Developer Documentation](https://docs.hla-compass.com) or contact the platform team.