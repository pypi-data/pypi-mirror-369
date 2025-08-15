import {
  insertNotebookCellAndExecute,
  getFirstVisibleNotebookPanel,
  updateConnectionStatus,
  findCodeCellsWithCommand,
  findCodeCellsWithRegex,
} from '../NotebookUtils';

jest.mock('@jupyterlab/notebook', () => ({
  NotebookPanel: jest.fn(),
}));

const mockRunMethod = jest
  .fn()
  .mockImplementationOnce(() => {
    return;
  })
  .mockImplementationOnce(() => new Error())
  .mockImplementationOnce(() => {
    return Promise.reject('reject');
  });

jest.mock('@jupyterlab/notebook', () => ({
  NotebookActions: { run: () => mockRunMethod() },
}));

class WidgetsMock {
  sampleList: { id: number; constructor: { name: string }; isVisible: boolean }[];
  constructor(isNullTest?: boolean) {
    this.sampleList = isNullTest ? this.widgets.slice(0, 2) : this.widgets;
  }
  index = 0;
  widgets = [
    { id: 1, constructor: { name: 'NotebookPanel' }, isVisible: false },
    { id: 2, constructor: { name: 'Nope' }, isVisible: true },
    { id: 3, constructor: { name: 'NotebookPanel' }, isVisible: true },
    { id: 4, constructor: { name: 'NotebookPanel' }, isVisible: true },
  ];
  next() {
    const widget = this.index < this.sampleList.length ? this.sampleList[this.index] : null;
    this.index++;
    return widget;
  }
}

describe('insertNotebookCellAndExecute', () => {
  test('it inserts a cell and executes it', async () => {
    const notebookPanel = {
      content: {
        model: {
          sharedModel: {
            toJSON: () => ({ metadata: {} }),
            insertCell: jest.fn(), // Mocking the insertCell function
          },
        },
        activeCell: {
          outputArea: {
            node: {
              children: [],
            },
          },
        },
        activeCellIndex: 0,
      },
      context: {
        sessionContext: {},
      },
    };

    const pythonCode = 'print("Hello, world!")';
    const result = await insertNotebookCellAndExecute(pythonCode, notebookPanel, true);

    expect(result.html).toEqual([]);
    expect(result.cell).toBeDefined();
    expect(notebookPanel.content.model.sharedModel.insertCell).toHaveBeenCalled();
  });

  test('it rejects when notebookPanel is not provided', async () => {
    await expect(insertNotebookCellAndExecute('code', null, true)).rejects.toEqual('No notebook panel');
  });
});

describe('getFirstVisibleNotebookPanel', () => {
  test('it returns the first visible notebook panel', () => {
    const app = {
      shell: {
        widgets: () => new WidgetsMock(),
      },
    };

    const result = getFirstVisibleNotebookPanel(app);

    expect(result).toBeDefined();
  });
});

describe('updateConnectionStatus', () => {
  test('it updates the connection status', () => {
    const message = {
      content: {
        text: '{"namespace": "sagemaker-analytics", "cluster_id": "j-BOTRBAGQEQWV", "error_message": null, "success": true}',
      },
    };

    const notebookPanel = {};
    const selectedCluster = { id: 'j-BOTRBAGQEQWV' };
    const setConnectedCluster = jest.fn();

    updateConnectionStatus(message, notebookPanel, selectedCluster, setConnectedCluster);

    expect(setConnectedCluster).toHaveBeenCalledWith(selectedCluster);
  });

  test('it does nothing when selectedCluster is not provided', () => {
    const message = {
      content: {
        text: '{"namespace": "sagemaker-analytics", "cluster_id": "j-BOTRBAGQEQWV", "error_message": null, "success": true}',
      },
    };

    const notebookPanel = {};
    const selectedCluster = null;
    const setConnectedCluster = jest.fn();

    updateConnectionStatus(message, notebookPanel, selectedCluster, setConnectedCluster);

    expect(setConnectedCluster).not.toHaveBeenCalled();
  });

  test('it does nothing when message does not contain the expected content', () => {
    const message = {
      content: {
        text: '{"namespace": "other-namespace", "cluster_id": "j-BOTRBAGQEQWV", "error_message": null, "success": true}',
      },
    };

    const notebookPanel = {};
    const selectedCluster = { id: 'j-BOTRBAGQEQWV' };
    const setConnectedCluster = jest.fn();

    updateConnectionStatus(message, notebookPanel, selectedCluster, setConnectedCluster);

    expect(setConnectedCluster).not.toHaveBeenCalled();
  });
});

describe('findCodeCellsWithCommand', () => {
  test('it finds code cells with the given command', () => {
    const notebookPanel = {
      content: {
        widgets: [
          { model: { sharedModel: { source: 'command1' } } },
          { model: { sharedModel: { source: 'command2' } } },
          { model: { sharedModel: { source: 'command1' } } },
        ],
      },
    };

    const command = 'command1';
    const result = findCodeCellsWithCommand(notebookPanel, command);

    expect(result.length).toBe(2);
  });
});

describe('findCodeCellsWithRegex', () => {
  test('it finds code cells that match the regex', () => {
    const notebookPanel = {
      content: {
        widgets: [
          { model: { sharedModel: { source: 'code1' } } },
          { model: { sharedModel: { source: 'code2' } } },
          { model: { sharedModel: { source: 'code1' } } },
        ],
      },
    };

    const regex = /code1/;
    const result = findCodeCellsWithRegex(notebookPanel, regex);

    expect(result.length).toBe(2);
  });
});
