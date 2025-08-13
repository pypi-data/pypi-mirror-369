# Basic Peptide Search Module with UI

A peptide search module that demonstrates HLA-Compass platform capabilities with a minimal user interface.

## Overview

This module extends the basic peptide search functionality with a React-based user interface, showcasing:

- **Frontend Integration**: React component with Ant Design UI
- **User Input Handling**: Text area for peptide sequences with validation
- **Results Visualization**: Table display with expandable details
- **Error Management**: User-friendly error messages and loading states
- **Platform Integration**: Module Federation for secure UI loading

## Features

### Backend (Same as Basic module)
- Search multiple peptide sequences
- Validate amino acid sequences
- Return detailed matches with metadata
- Provide summary statistics

### Frontend (New)
- **Input Interface**: 
  - Multi-line text area for peptide sequences
  - Configurable results limit
  - Clear instructions and help text
- **Results Display**:
  - Summary statistics
  - Sortable, paginated table
  - Expandable rows for detailed matches
- **User Experience**:
  - Loading indicators
  - Error messages with recovery options
  - Success notifications

## UI Components

### Input Section
- **Peptide Sequences**: Multi-line text area accepting one sequence per line
- **Results Limit**: Number input (1-100) for maximum results per sequence
- **Action Buttons**: Search and Clear buttons with appropriate states

### Results Section
- **Summary Card**: Overview statistics of the search
- **Results Table**: 
  - Query sequence with status
  - Number of matches found
  - Top match preview
  - Expandable rows for all matches

### Error Handling
- Input validation with clear error messages
- Network error handling
- Empty state messaging

## Input Parameters

| Parameter | Type | Required | Description | Default | UI Component |
|-----------|------|----------|-------------|---------|--------------|
| `peptide_sequences` | array | Yes | List of peptide sequences | - | TextArea |
| `limit` | integer | No | Max results per sequence | 10 | InputNumber |

## Usage

### Local Development

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Build frontend**:
   ```bash
   npm run build
   ```

3. **Test module**:
   ```bash
   hla-compass test --input ../examples/input.json
   ```

### Deployment

1. **Build module package**:
   ```bash
   hla-compass build
   ```

2. **Deploy to platform**:
   ```bash
   hla-compass deploy dist/basic-peptide-search-ui-1.0.0.zip --env dev
   ```

## Code Structure

### Backend (`backend/main.py`)
- Identical to the basic module
- `BasicPeptideSearch` class with peptide search logic
- Input validation and error handling
- Lambda handler for AWS execution

### Frontend (`frontend/index.tsx`)
- **React Component**: `BasicPeptideSearchUI`
- **State Management**: React hooks for form state and results
- **UI Components**: Ant Design components for professional look
- **Type Safety**: TypeScript interfaces for data structures

### Key Frontend Features

1. **Input Validation**:
   ```typescript
   const invalidSequences = sequences.filter(seq => 
     !/^[ACDEFGHIKLMNPQRSTVWY]+$/i.test(seq)
   );
   ```

2. **Async Execution**:
   ```typescript
   const result = await onExecute({
     peptide_sequences: sequences,
     limit: limit
   });
   ```

3. **Results Display**:
   ```typescript
   <Table
     dataSource={results}
     columns={columns}
     expandable={{...}}
   />
   ```

## UI Screenshots

### Input State
```
┌──────────────────────────────────────┐
│ Basic Peptide Search                 │
│                                       │
│ [i] Enter peptide sequences below    │
│                                       │
│ Peptide Sequences:                   │
│ ┌──────────────────────────────────┐ │
│ │ SIINFEKL                         │ │
│ │ GILGFVFTL                        │ │
│ │ YLQPRTFLL                        │ │
│ └──────────────────────────────────┘ │
│                                       │
│ Max results: [10]                    │
│                                       │
│ [Search] [Clear]                     │
└──────────────────────────────────────┘
```

### Results State
```
┌──────────────────────────────────────┐
│ Search Results                        │
│                                       │
│ ✓ Summary: 3 searched, 3 successful  │
│                                       │
│ Query      Status   Matches  Top     │
│ SIINFEKL   success  2        OVA     │
│ GILGFVFTL  success  1        Flu M1  │
│ YLQPRTFLL  success  0        -       │
└──────────────────────────────────────┘
```

## Development Tips

1. **Testing UI Locally**: Use the platform's module development server
2. **Debugging**: Check browser console for React errors
3. **Styling**: Follow Ant Design patterns for consistency
4. **State Management**: Keep state minimal and close to usage

## Platform Integration

The UI integrates with the HLA-Compass platform through:

1. **Module Federation**: Secure loading without iframes
2. **API Calls**: Through platform's `onExecute` prop
3. **Authentication**: Handled by platform wrapper
4. **Error Boundaries**: Platform catches and displays module errors

## Requirements

- Python 3.9+
- Node.js 18+
- HLA-Compass SDK 1.0.0
- React 19.0.0
- Ant Design 5.0.0

## Support

For questions or issues, refer to the [HLA-Compass Developer Documentation](https://docs.hla-compass.com) or contact the platform team.