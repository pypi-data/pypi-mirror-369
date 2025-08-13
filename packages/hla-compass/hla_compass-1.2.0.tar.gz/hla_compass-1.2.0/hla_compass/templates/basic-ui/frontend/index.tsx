/**
 * Basic Peptide Search UI Component
 * 
 * This React component provides a minimal user interface for the peptide search module.
 * It demonstrates the essential UI patterns for HLA-Compass modules:
 * - Input field for peptide sequences
 * - Search button to trigger execution
 * - Results display in a table format
 * - Error handling and loading states
 */

import React, { useState, useCallback } from 'react';
import { Button, Input, Table, Alert, Card, Space, Typography, Spin, InputNumber, message } from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

// Type definitions for module props and data structures
interface ModuleProps {
  /**
   * Execute function provided by the platform to run the module
   * @param params Input parameters for the module
   * @returns Promise with execution result
   */
  onExecute: (params: any) => Promise<any>;
  
  /**
   * Initial parameters passed to the module (optional)
   */
  initialParams?: {
    peptide_sequences?: string[];
    limit?: number;
  };
}

interface SearchResult {
  query_sequence: string;
  status: 'success' | 'error' | 'invalid';
  matches_found?: number;
  error?: string;
  matches?: Array<{
    id: string;
    sequence: string;
    length: number;
    mass: number;
    source: string;
    organism: string;
    confidence: number;
  }>;
}

/**
 * Main component for the Basic Peptide Search UI
 */
const BasicPeptideSearchUI: React.FC<ModuleProps> = ({ onExecute, initialParams }) => {
  // State management
  const [inputText, setInputText] = useState<string>(
    initialParams?.peptide_sequences?.join('\n') || ''
  );
  const [limit, setLimit] = useState<number>(initialParams?.limit || 10);
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle the search button click
   * Validates input, calls the execute function, and displays results
   */
  const handleSearch = useCallback(async () => {
    // Clear previous results and errors
    setError(null);
    setResults(null);
    setSummary(null);
    
    // Parse input text into array of sequences
    const sequences = inputText
      .split('\n')
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    // Validate input
    if (sequences.length === 0) {
      setError('Please enter at least one peptide sequence');
      return;
    }
    
    if (sequences.length > 100) {
      setError('Maximum 100 sequences allowed per search');
      return;
    }
    
    // Validate sequences contain only valid amino acids
    const invalidSequences = sequences.filter(seq => 
      !/^[ACDEFGHIKLMNPQRSTVWY]+$/i.test(seq)
    );
    
    if (invalidSequences.length > 0) {
      setError(`Invalid sequences detected: ${invalidSequences.join(', ')}`);
      return;
    }
    
    // Execute the search
    setLoading(true);
    
    try {
      // Call the platform's execute function with our parameters
      const result = await onExecute({
        peptide_sequences: sequences,
        limit: limit
      });
      
      // Process the results
      if (result.status === 'success') {
        setResults(result.results);
        setSummary(result.summary);
        message.success('Search completed successfully');
      } else {
        setError(result.error?.message || 'Search failed');
      }
    } catch (err) {
      // Handle execution errors
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [inputText, limit, onExecute]);

  /**
   * Clear all inputs and results
   */
  const handleClear = useCallback(() => {
    setInputText('');
    setResults(null);
    setSummary(null);
    setError(null);
    setLimit(10);
  }, []);

  /**
   * Define columns for the results table
   */
  const columns = [
    {
      title: 'Query Sequence',
      dataIndex: 'query_sequence',
      key: 'query_sequence',
      width: 150,
      render: (text: string) => <Text code>{text}</Text>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <span style={{ 
          color: status === 'success' ? 'green' : status === 'error' ? 'red' : 'orange' 
        }}>
          {status}
        </span>
      )
    },
    {
      title: 'Matches Found',
      dataIndex: 'matches_found',
      key: 'matches_found',
      width: 120,
      render: (count: number | undefined) => count ?? 0
    },
    {
      title: 'Top Match',
      key: 'top_match',
      render: (record: SearchResult) => {
        if (record.matches && record.matches.length > 0) {
          const topMatch = record.matches[0];
          return (
            <Space direction="vertical" size="small">
              <Text>{topMatch.source}</Text>
              <Text type="secondary">{topMatch.organism}</Text>
              <Text type="secondary">Confidence: {(topMatch.confidence * 100).toFixed(0)}%</Text>
            </Space>
          );
        }
        return record.error ? <Text type="danger">{record.error}</Text> : '-';
      }
    }
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <Card>
        <Title level={3}>Basic Peptide Search</Title>
        <Paragraph>
          Search for peptide sequences in the HLA-Compass database. 
          Enter one or more peptide sequences using standard single-letter amino acid codes.
        </Paragraph>
      </Card>
      
      {/* Input Section */}
      <Card style={{ marginTop: '20px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Instructions */}
          <Alert
            message="Enter peptide sequences below (one per line)"
            description="Use standard amino acid codes: A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y"
            type="info"
            showIcon
          />
          
          {/* Peptide Input */}
          <div>
            <Text strong>Peptide Sequences:</Text>
            <TextArea
              rows={6}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="SIINFEKL&#10;GILGFVFTL&#10;YLQPRTFLL"
              disabled={loading}
              style={{ fontFamily: 'monospace', fontSize: '14px', marginTop: '8px' }}
            />
          </div>
          
          {/* Results Limit */}
          <div>
            <Text strong>Maximum results per sequence:</Text>
            <br />
            <InputNumber
              min={1}
              max={100}
              value={limit}
              onChange={(value) => setLimit(value || 10)}
              disabled={loading}
              style={{ width: '120px', marginTop: '8px' }}
            />
          </div>
          
          {/* Action Buttons */}
          <Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
              disabled={!inputText.trim()}
              size="large"
            >
              Search
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClear}
              disabled={loading}
              size="large"
            >
              Clear
            </Button>
          </Space>
        </Space>
      </Card>
      
      {/* Error Display */}
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginTop: '20px' }}
        />
      )}
      
      {/* Loading State */}
      {loading && (
        <Card style={{ marginTop: '20px', textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: '10px' }}>
            <Text>Searching peptide database...</Text>
          </div>
        </Card>
      )}
      
      {/* Results Display */}
      {results && !loading && (
        <Card style={{ marginTop: '20px' }}>
          <Title level={4}>Search Results</Title>
          
          {/* Summary Statistics */}
          {summary && (
            <Alert
              message="Summary"
              description={
                <Space>
                  <Text>Total searched: {summary.total_sequences_searched}</Text>
                  <Text>|</Text>
                  <Text>Successful: {summary.successful_searches}</Text>
                  <Text>|</Text>
                  <Text>Total matches: {summary.total_matches_found}</Text>
                  <Text>|</Text>
                  <Text>Avg matches: {summary.average_matches_per_sequence}</Text>
                </Space>
              }
              type="success"
              style={{ marginBottom: '20px' }}
            />
          )}
          
          {/* Results Table */}
          <Table
            dataSource={results}
            columns={columns}
            rowKey={(record) => record.query_sequence}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} sequences`
            }}
            expandable={{
              expandedRowRender: (record: SearchResult) => {
                if (!record.matches || record.matches.length === 0) {
                  return <Text type="secondary">No matches found</Text>;
                }
                
                // Create nested table for all matches
                const matchColumns = [
                  { title: 'ID', dataIndex: 'id', key: 'id', width: 200 },
                  { title: 'Sequence', dataIndex: 'sequence', key: 'sequence' },
                  { title: 'Length', dataIndex: 'length', key: 'length' },
                  { title: 'Mass (Da)', dataIndex: 'mass', key: 'mass' },
                  { title: 'Source', dataIndex: 'source', key: 'source' },
                  { title: 'Organism', dataIndex: 'organism', key: 'organism' },
                  { 
                    title: 'Confidence', 
                    dataIndex: 'confidence', 
                    key: 'confidence',
                    render: (conf: number) => `${(conf * 100).toFixed(0)}%`
                  }
                ];
                
                return (
                  <Table
                    dataSource={record.matches}
                    columns={matchColumns}
                    rowKey="id"
                    pagination={false}
                    size="small"
                  />
                );
              },
              rowExpandable: (record) => record.matches && record.matches.length > 0
            }}
          />
        </Card>
      )}
    </div>
  );
};

// Export the component for the platform to load
export default BasicPeptideSearchUI;