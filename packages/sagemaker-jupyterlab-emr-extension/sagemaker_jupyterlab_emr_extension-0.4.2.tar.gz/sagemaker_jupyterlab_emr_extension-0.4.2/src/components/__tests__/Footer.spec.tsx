import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect'; // For expect().toBeInTheDocument()
import { Footer } from '../Footer'; // Import your Footer component

describe('Footer Component', () => {
  it('should render correctly', () => {
    const onCloseModal = jest.fn();
    const onConnect = jest.fn();

    const { getByText } = render(<Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={false} />);

    expect(getByText('Cancel')).toBeInTheDocument();
    expect(getByText('Connect')).toBeInTheDocument();
  });

  it('should call onCloseModal when "Cancel" button is clicked', () => {
    const onCloseModal = jest.fn();
    const onConnect = jest.fn();
    const { getByText } = render(<Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={false} />);

    const cancelButton = getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(onCloseModal).toHaveBeenCalledTimes(1);
    expect(onConnect).not.toHaveBeenCalled();
  });

  it('should call onConnect when "Connect" button is clicked', () => {
    const onCloseModal = jest.fn();
    const onConnect = jest.fn();

    const { getByText } = render(<Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={false} />);

    const connectButton = getByText('Connect');
    fireEvent.click(connectButton);

    expect(onConnect).toHaveBeenCalledTimes(1);
    expect(onCloseModal).not.toHaveBeenCalled();
  });

  it('should disable "Connect" button when disabled is true', () => {
    const onCloseModal = jest.fn();
    const onConnect = jest.fn();

    const { getByText } = render(<Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={true} />);

    const connectButton = getByText('Connect');

    expect(connectButton).toBeDisabled();
  });
});
