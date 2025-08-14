// Utility functions for manual DOM manipulation with vanilla JS

const injectTableRowAfterDataRow = (
  tableBody: HTMLTableSectionElement,
  dataRow: HTMLTableRowElement,
): HTMLTableRowElement | null => {
  let indexOfDataRow = 1;
  let foundDataRow = false;
  for (let i = 1; i < tableBody.childNodes.length; i++) {
    if (tableBody.childNodes[i].isSameNode(dataRow)) {
      indexOfDataRow = i;
      foundDataRow = true;
      break;
    }
  }
  if (!foundDataRow) return null;
  const newRowIndex = indexOfDataRow + 1 < tableBody.childNodes.length ? indexOfDataRow + 1 : -1;
  return tableBody.insertRow(newRowIndex);
};

/**
 * Get the first index of a header in a table row.
 *
 * @param headerRow the row to search
 * @param header the text of the header we're looking for
 * @returns the index of the header in the row, or -1
 */
const getColumnIndexOfTableHeader = (headerRow: HTMLTableRowElement, header: string): number => {
  for (let i = 0; i < headerRow.childNodes.length; i++) {
    if (headerRow.childNodes[i].textContent?.includes(header)) {
      return i;
    }
  }
  return -1;
};

const removeAllChildNodes = (e: HTMLElement) => {
  try {
    let child = e.lastElementChild;
    while (child) {
      e.removeChild(child);
      child = e.lastElementChild;
    }
  } catch (error) {
    // fail gracefully
  }
};

export { injectTableRowAfterDataRow, getColumnIndexOfTableHeader, removeAllChildNodes };
