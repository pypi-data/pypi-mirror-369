import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { Link, LinkType } from '../Link';

// Mock the launcherIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    launcherIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="launcher-icon">Launcher Icon</span>),
    },
  };
});

describe('Link Component', () => {
  it('renders a content link', () => {
    render(<Link type={LinkType.Content}>Content Link</Link>);
    const linkElement = screen.getByRole('link');
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveTextContent('Content Link');
  });

  it('renders a disabled link', () => {
    render(<Link disabled>Disabled Link</Link>);
    const linkElement = screen.getByRole('link');
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveTextContent('Disabled Link');
  });

  it('renders a notebook link', () => {
    render(
      <Link type={LinkType.Notebook} href="/notebook/123">
        Notebook Link
      </Link>,
    );
    const linkElement = screen.getByRole('link');
    expect(linkElement).toBeInTheDocument();
    expect(linkElement).toHaveTextContent('Notebook Link');
  });

  it('hides external icon when hideExternalIcon prop is true', () => {
    render(
      <Link type={LinkType.External} href="https://example.com" hideExternalIcon>
        External Link
      </Link>,
    );
    const linkElement = screen.getByRole('link');
    expect(linkElement).toBeInTheDocument();
    const externalIcon = screen.queryByTestId('external-icon'); // Should not be found
    expect(externalIcon).not.toBeInTheDocument();
  });
});
