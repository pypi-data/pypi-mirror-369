import { GetServerlessApplicationColumnConfig } from '../GetServerlessApplicationColumnConfig';

describe('GetServerlessApplicationColumnConfig tests', () => {
  it('should return an array of column configuration objects', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();

    expect(Array.isArray(columnConfig)).toBe(true);
    expect(columnConfig.length).toBe(5);
  });

  it('should have the correct properties in each column configuration object', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();

    columnConfig.forEach((config) => {
      expect(config).toHaveProperty('dataKey');
      expect(config).toHaveProperty('label');
      expect(config).toHaveProperty('disableSort');
      expect(config).toHaveProperty('cellRenderer');
    });
  });

  it('should have the correct dataKey and label values', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();

    expect(columnConfig[0].dataKey).toBe('name');
    expect(columnConfig[0].label).toBe('Name');

    expect(columnConfig[1].dataKey).toBe('id');
    expect(columnConfig[1].label).toBe('ID');

    expect(columnConfig[2].dataKey).toBe('status');
    expect(columnConfig[2].label).toBe('Status');

    expect(columnConfig[3].dataKey).toBe('creationDateTime');
    expect(columnConfig[3].label).toBe('Creation Time');

    expect(columnConfig[4].dataKey).toBe('clusterArn');
    expect(columnConfig[4].label).toBe('Account ID');
  });
});

describe('GetColumnConfig - cellRenderer', () => {
  it('should correctly render the "name" cell', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();
    const rowData = { name: 'John' };

    const renderedValue = columnConfig[0].cellRenderer({ row: rowData });

    expect(renderedValue).toBe('John');
  });

  it('should correctly render the "id" cell', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();
    const rowData = { id: 123 };

    const renderedValue = columnConfig[1].cellRenderer({ row: rowData });

    expect(renderedValue).toBe(123);
  });

  xit('should correctly render the "status" cell', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();
    const rowData = { status: 'STARTED' };

    const renderedValue = columnConfig[2].cellRenderer({ row: rowData });

    expect(renderedValue).toBe('STARTED');
  });

  it('should correctly render the "accountId" cell', () => {
    const columnConfig = GetServerlessApplicationColumnConfig();
    const rowData = { arn: 'arn:aws:emr-serverless:us-west-2:334510439030:applicaion/j-3CLVK7LUVU18O' };

    const renderedValue = columnConfig[4].cellRenderer({ row: rowData });

    expect(renderedValue).toBe('334510439030');
  });
});
