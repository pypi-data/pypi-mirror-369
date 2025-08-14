/**
 * Advanced Analysis Suite UI
 * 
 * Comprehensive frontend demonstrating all HLA-Compass platform UI capabilities:
 * - Multi-tab interface for different analysis types
 * - Complex input forms with validation
 * - Data visualization components
 * - File upload and export functionality
 * - Real-time progress tracking
 * - Results filtering and sorting
 * - Error recovery and retry mechanisms
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Tabs, Card, Form, Input, Select, Button, Table, Alert, Space, Typography,
  Spin, Progress, Collapse, Tag, Switch, Radio, InputNumber, Upload,
  Tooltip, Badge, Divider, Row, Col, Statistic, message, notification
} from 'antd';
import {
  SearchOutlined, DownloadOutlined, UploadOutlined, ExperimentOutlined,
  BarChartOutlined, FileExcelOutlined, FilePdfOutlined, ReloadOutlined,
  CheckCircleOutlined, WarningOutlined, InfoCircleOutlined
} from '@ant-design/icons';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

// Type definitions
interface ModuleProps {
  onExecute: (params: any) => Promise<any>;
  initialParams?: any;
  onProgress?: (progress: any) => void;
}

interface AnalysisResults {
  peptide_results?: any;
  protein_results?: any;
  sample_results?: any;
  hla_results?: any;
}

/**
 * Main Advanced Analysis Suite Component
 * Demonstrates comprehensive UI patterns and platform integration
 */
const AdvancedAnalysisSuite: React.FC<ModuleProps> = ({ onExecute, initialParams, onProgress }) => {
  // Form instance for input management
  const [form] = Form.useForm();
  
  // State management
  const [activeTab, setActiveTab] = useState<string>('comprehensive');
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [progressText, setProgressText] = useState<string>('');
  
  /**
   * Handle form submission and execute analysis
   * Demonstrates async execution with progress tracking
   */
  const handleExecute = useCallback(async (values: any) => {
    setError(null);
    setResults(null);
    setSummary(null);
    setVisualizations([]);
    setProgress(0);
    setLoading(true);
    
    try {
      // Prepare parameters based on active tab
      const params: any = {
        analysis_type: activeTab,
        output_format: values.output_format || 'json',
        save_to_storage: values.save_to_storage || false
      };
      
      // Add type-specific parameters
      if (activeTab === 'peptide_search' || activeTab === 'comprehensive') {
        params.peptide_params = {
          sequences: values.peptide_sequences?.split('\n').filter((s: string) => s.trim()),
          min_length: values.min_length,
          max_length: values.max_length,
          mass_tolerance: values.mass_tolerance
        };
      }
      
      if (activeTab === 'protein_analysis' || activeTab === 'comprehensive') {
        params.protein_params = {
          accession: values.protein_accession,
          gene_name: values.gene_name,
          organism: values.organism
        };
      }
      
      if (activeTab === 'sample_comparison' || activeTab === 'comprehensive') {
        params.sample_params = {
          sample_ids: values.sample_ids,
          tissue: values.tissue,
          disease: values.disease
        };
      }
      
      if (activeTab === 'hla_prediction' || activeTab === 'comprehensive') {
        params.hla_params = {
          peptides: values.hla_peptides?.split('\n').filter((s: string) => s.trim()),
          alleles: values.hla_alleles,
          method: values.prediction_method
        };
      }
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);
      
      // Execute analysis
      const result = await onExecute(params);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Process results
      if (result.status === 'success') {
        setResults(result.results);
        setSummary(result.summary);
        setVisualizations(result.visualizations || []);
        
        // Show success notification
        notification.success({
          message: 'Analysis Complete',
          description: `Successfully completed ${result.summary?.analyses_performed?.length || 0} analyses`,
          placement: 'topRight'
        });
      } else {
        throw new Error(result.error?.message || 'Analysis failed');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      notification.error({
        message: 'Analysis Failed',
        description: err instanceof Error ? err.message : 'An unexpected error occurred',
        placement: 'topRight'
      });
    } finally {
      setLoading(false);
      setProgress(0);
    }
  }, [activeTab, onExecute]);
  
  /**
   * Render peptide search form
   * Demonstrates complex form with validation
   */
  const renderPeptideForm = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Form.Item
        name="peptide_sequences"
        label="Peptide Sequences"
        rules={[{ required: activeTab === 'peptide_search' }]}
      >
        <TextArea
          rows={4}
          placeholder="Enter peptide sequences (one per line)"
          style={{ fontFamily: 'monospace' }}
        />
      </Form.Item>
      
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="min_length" label="Min Length">
            <InputNumber min={7} max={15} placeholder="7" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="max_length" label="Max Length">
            <InputNumber min={7} max={15} placeholder="15" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="mass_tolerance" label="Mass Tolerance (Da)">
            <InputNumber min={0.01} step={0.01} placeholder="0.01" />
          </Form.Item>
        </Col>
      </Row>
    </Space>
  );
  
  /**
   * Render protein analysis form
   */
  const renderProteinForm = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Form.Item name="protein_accession" label="UniProt Accession">
        <Input placeholder="e.g., P01234" />
      </Form.Item>
      
      <Form.Item name="gene_name" label="Gene Name">
        <Input placeholder="e.g., TP53" />
      </Form.Item>
      
      <Form.Item name="organism" label="Organism">
        <Select placeholder="Select organism">
          <Option value="9606">Human (Homo sapiens)</Option>
          <Option value="10090">Mouse (Mus musculus)</Option>
          <Option value="10116">Rat (Rattus norvegicus)</Option>
        </Select>
      </Form.Item>
    </Space>
  );
  
  /**
   * Render sample comparison form
   */
  const renderSampleForm = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Form.Item name="sample_ids" label="Sample IDs (optional)">
        <Select mode="multiple" placeholder="Select or enter sample IDs">
          <Option value="sample1">Sample 1</Option>
          <Option value="sample2">Sample 2</Option>
          <Option value="sample3">Sample 3</Option>
        </Select>
      </Form.Item>
      
      <Form.Item name="tissue" label="Tissue Type">
        <Select placeholder="Select tissue type">
          <Option value="lung">Lung</Option>
          <Option value="liver">Liver</Option>
          <Option value="brain">Brain</Option>
          <Option value="blood">Blood</Option>
        </Select>
      </Form.Item>
      
      <Form.Item name="disease" label="Disease">
        <Input placeholder="e.g., cancer, diabetes" />
      </Form.Item>
    </Space>
  );
  
  /**
   * Render HLA prediction form
   */
  const renderHLAForm = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Form.Item
        name="hla_peptides"
        label="Peptides for Prediction"
        rules={[{ required: activeTab === 'hla_prediction' }]}
      >
        <TextArea
          rows={3}
          placeholder="Enter peptides (one per line)"
          style={{ fontFamily: 'monospace' }}
        />
      </Form.Item>
      
      <Form.Item name="hla_alleles" label="HLA Alleles">
        <Select mode="multiple" placeholder="Select HLA alleles">
          <Option value="HLA-A*02:01">HLA-A*02:01</Option>
          <Option value="HLA-A*01:01">HLA-A*01:01</Option>
          <Option value="HLA-B*07:02">HLA-B*07:02</Option>
          <Option value="HLA-B*08:01">HLA-B*08:01</Option>
        </Select>
      </Form.Item>
      
      <Form.Item name="prediction_method" label="Prediction Method">
        <Radio.Group defaultValue="netmhcpan">
          <Radio value="netmhcpan">NetMHCpan</Radio>
          <Radio value="mhcflurry">MHCflurry</Radio>
          <Radio value="consensus">Consensus</Radio>
        </Radio.Group>
      </Form.Item>
    </Space>
  );
  
  /**
   * Render results section
   * Demonstrates complex results display with multiple formats
   */
  const renderResults = () => {
    if (!results) return null;
    
    return (
      <div>
        {/* Summary Statistics */}
        {summary && (
          <Card title="Analysis Summary" style={{ marginBottom: 20 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="Analyses Performed"
                  value={summary.analyses_performed?.length || 0}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Records Processed"
                  value={summary.total_records_processed || 0}
                  prefix={<BarChartOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="API Calls"
                  value={summary.total_api_calls || 0}
                  prefix={<ExperimentOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Success Rate"
                  value={summary.success_rate || 0}
                  suffix="%"
                  valueStyle={{ color: summary.success_rate > 90 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
            </Row>
          </Card>
        )}
        
        {/* Results Tabs */}
        <Tabs defaultActiveKey="1">
          {results.peptide_results && (
            <TabPane tab="Peptide Results" key="1">
              <PeptideResults data={results.peptide_results} />
            </TabPane>
          )}
          
          {results.protein_results && (
            <TabPane tab="Protein Results" key="2">
              <ProteinResults data={results.protein_results} />
            </TabPane>
          )}
          
          {results.sample_results && (
            <TabPane tab="Sample Results" key="3">
              <SampleResults data={results.sample_results} />
            </TabPane>
          )}
          
          {results.hla_results && (
            <TabPane tab="HLA Results" key="4">
              <HLAResults data={results.hla_results} />
            </TabPane>
          )}
          
          {visualizations.length > 0 && (
            <TabPane tab="Visualizations" key="5">
              <VisualizationPanel visualizations={visualizations} />
            </TabPane>
          )}
        </Tabs>
      </div>
    );
  };
  
  return (
    <div style={{ padding: 20 }}>
      <Card>
        <Title level={3}>
          <ExperimentOutlined /> Advanced Analysis Suite
        </Title>
        <Paragraph>
          Comprehensive analysis platform demonstrating all HLA-Compass capabilities
        </Paragraph>
      </Card>
      
      {/* Analysis Type Tabs */}
      <Card style={{ marginTop: 20 }}>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Comprehensive" key="comprehensive">
            <Alert
              message="Run all analyses"
              description="This will perform peptide, protein, sample, and HLA analyses"
              type="info"
              showIcon
              style={{ marginBottom: 20 }}
            />
          </TabPane>
          
          <TabPane tab="Peptide Search" key="peptide_search" />
          <TabPane tab="Protein Analysis" key="protein_analysis" />
          <TabPane tab="Sample Comparison" key="sample_comparison" />
          <TabPane tab="HLA Prediction" key="hla_prediction" />
        </Tabs>
        
        {/* Input Form */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleExecute}
          initialValues={{
            output_format: 'json',
            save_to_storage: false,
            prediction_method: 'netmhcpan',
            ...initialParams
          }}
        >
          {/* Type-specific forms */}
          {(activeTab === 'peptide_search' || activeTab === 'comprehensive') && (
            <Collapse defaultActiveKey={activeTab === 'peptide_search' ? ['1'] : []}>
              <Panel header="Peptide Analysis Parameters" key="1">
                {renderPeptideForm()}
              </Panel>
            </Collapse>
          )}
          
          {(activeTab === 'protein_analysis' || activeTab === 'comprehensive') && (
            <Collapse defaultActiveKey={activeTab === 'protein_analysis' ? ['1'] : []}>
              <Panel header="Protein Analysis Parameters" key="1">
                {renderProteinForm()}
              </Panel>
            </Collapse>
          )}
          
          {(activeTab === 'sample_comparison' || activeTab === 'comprehensive') && (
            <Collapse defaultActiveKey={activeTab === 'sample_comparison' ? ['1'] : []}>
              <Panel header="Sample Comparison Parameters" key="1">
                {renderSampleForm()}
              </Panel>
            </Collapse>
          )}
          
          {(activeTab === 'hla_prediction' || activeTab === 'comprehensive') && (
            <Collapse defaultActiveKey={activeTab === 'hla_prediction' ? ['1'] : []}>
              <Panel header="HLA Prediction Parameters" key="1">
                {renderHLAForm()}
              </Panel>
            </Collapse>
          )}
          
          {/* Common Options */}
          <Divider />
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="output_format" label="Output Format">
                <Radio.Group>
                  <Radio value="json">JSON</Radio>
                  <Radio value="csv">CSV</Radio>
                  <Radio value="excel">Excel</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="save_to_storage" label="Save to Cloud Storage" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          {/* Action Buttons */}
          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SearchOutlined />}
                loading={loading}
                size="large"
              >
                Execute Analysis
              </Button>
              
              <Button
                icon={<ReloadOutlined />}
                onClick={() => form.resetFields()}
                disabled={loading}
                size="large"
              >
                Reset
              </Button>
              
              <Upload
                accept=".json,.csv"
                showUploadList={false}
                beforeUpload={(file) => {
                  // Handle file upload for batch processing
                  message.info('File upload functionality would be implemented here');
                  return false;
                }}
              >
                <Button icon={<UploadOutlined />} size="large">
                  Import Parameters
                </Button>
              </Upload>
            </Space>
          </Form.Item>
        </Form>
      </Card>
      
      {/* Progress Indicator */}
      {loading && (
        <Card style={{ marginTop: 20 }}>
          <Progress percent={progress} status="active" />
          <div style={{ textAlign: 'center', marginTop: 10 }}>
            <Spin />
            <Text style={{ marginLeft: 10 }}>{progressText || 'Processing...'}</Text>
          </div>
        </Card>
      )}
      
      {/* Error Display */}
      {error && (
        <Alert
          message="Analysis Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginTop: 20 }}
        />
      )}
      
      {/* Results Display */}
      {results && !loading && (
        <Card style={{ marginTop: 20 }}>
          {renderResults()}
        </Card>
      )}
    </div>
  );
};

// Sub-components for different result types
const PeptideResults: React.FC<{ data: any }> = ({ data }) => (
  <div>
    {data.statistics && (
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={6}>
          <Statistic title="Total Peptides" value={data.statistics.total_peptides} />
        </Col>
        <Col span={6}>
          <Statistic title="Unique Sequences" value={data.statistics.unique_sequences} />
        </Col>
        <Col span={6}>
          <Statistic title="Avg Length" value={data.statistics.avg_length} />
        </Col>
        <Col span={6}>
          <Statistic title="Avg Mass" value={data.statistics.avg_mass} suffix="Da" />
        </Col>
      </Row>
    )}
    
    {data.searched_sequences && (
      <Table
        dataSource={data.searched_sequences}
        columns={[
          { title: 'Query', dataIndex: 'query', key: 'query' },
          { title: 'Matches', dataIndex: 'count', key: 'count' },
          {
            title: 'Top Match',
            key: 'top',
            render: (record: any) => record.matches?.[0]?.sequence || '-'
          }
        ]}
        size="small"
        pagination={false}
      />
    )}
  </div>
);

const ProteinResults: React.FC<{ data: any }> = ({ data }) => (
  <div>
    {data.coverage_analysis && (
      <Table
        dataSource={data.coverage_analysis}
        columns={[
          { title: 'Accession', dataIndex: 'accession', key: 'accession' },
          { title: 'Total Peptides', dataIndex: 'total_peptides', key: 'total_peptides' },
          { title: 'Unique Peptides', dataIndex: 'unique_peptides', key: 'unique_peptides' },
          {
            title: 'Coverage %',
            dataIndex: 'coverage_percentage',
            key: 'coverage_percentage',
            render: (val: number) => <Progress percent={val} size="small" />
          }
        ]}
        size="small"
      />
    )}
  </div>
);

const SampleResults: React.FC<{ data: any }> = ({ data }) => (
  <div>
    {data.samples_found && (
      <div>
        <Title level={5}>Samples Found</Title>
        <Table
          dataSource={data.samples_found}
          columns={[
            { title: 'Sample ID', dataIndex: 'id', key: 'id' },
            { title: 'Type', dataIndex: 'type', key: 'type' },
            { title: 'Tissue', dataIndex: 'tissue', key: 'tissue' }
          ]}
          size="small"
          pagination={{ pageSize: 5 }}
        />
      </div>
    )}
  </div>
);

const HLAResults: React.FC<{ data: any }> = ({ data }) => (
  <div>
    {data.predictions && (
      <Table
        dataSource={data.predictions}
        columns={[
          { title: 'Peptide', dataIndex: 'peptide', key: 'peptide' },
          { title: 'Allele', dataIndex: 'allele', key: 'allele' },
          { title: 'Score', dataIndex: 'score', key: 'score' },
          {
            title: 'Binding Class',
            dataIndex: 'binding_class',
            key: 'binding_class',
            render: (val: string) => (
              <Tag color={val === 'Strong Binder' ? 'green' : val === 'Weak Binder' ? 'orange' : 'red'}>
                {val}
              </Tag>
            )
          }
        ]}
        size="small"
      />
    )}
  </div>
);

const VisualizationPanel: React.FC<{ visualizations: any[] }> = ({ visualizations }) => (
  <div>
    <Alert
      message="Visualization Preview"
      description="In production, these would render as interactive charts using Recharts or Plotly"
      type="info"
      showIcon
      style={{ marginBottom: 20 }}
    />
    {visualizations.map((viz, index) => (
      <Card key={index} title={viz.title} style={{ marginBottom: 10 }}>
        <pre>{JSON.stringify(viz.data, null, 2)}</pre>
      </Card>
    ))}
  </div>
);

export default AdvancedAnalysisSuite;