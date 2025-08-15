import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { ModalHeader, ModalHeaderProps } from '../ModalHeader';

// Mock the closeIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    closeIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="close-icon">Close Icon</span>),
    },
  };
});

describe('ModalHeader Component', () => {
  // Helper function to render the component with props
  const renderModalHeader = (props: Partial<ModalHeaderProps> = {}) => {
    const defaultProps: ModalHeaderProps = {
      heading: 'Test Heading',
      shouldDisplayCloseButton: false,
    };
    return render(<ModalHeader {...defaultProps} {...props} />);
  };

  it('should render the heading', () => {
    const { getByText } = renderModalHeader();
    expect(getByText('Test Heading')).toBeInTheDocument();
  });

  it('should display close button when shouldDisplayCloseButton is true', async () => {
    const { getByTestId } = renderModalHeader({ shouldDisplayCloseButton: true });
    expect(await getByTestId('close-button')).toBeInTheDocument();
  });

  it('should call onClickCloseButton when close button is clicked', async () => {
    const onClickCloseButton = jest.fn();
    const { getByTestId } = renderModalHeader({ shouldDisplayCloseButton: true, onClickCloseButton });
    const closeButton = await getByTestId('close-button');
    fireEvent.click(closeButton);
    expect(await onClickCloseButton).toHaveBeenCalled();
  });

  it('should render actionButtons', () => {
    const actionButtons = [
      { label: 'Button 1', onClick: jest.fn() },
      { label: 'Button 2', onClick: jest.fn() },
    ];
    const { getByText } = renderModalHeader({ actionButtons });
    expect(getByText('Button 1')).toBeInTheDocument();
    expect(getByText('Button 2')).toBeInTheDocument();
  });
});
