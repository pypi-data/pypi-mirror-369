import React from 'react';
import { cx } from '@emotion/css';
import { launcherIcon } from '@jupyterlab/ui-components';

import styles from './styles';

enum LinkType {
  Content,
  External,
  Notebook,
}

type HTMLAnchorProps = React.DetailedHTMLProps<React.AnchorHTMLAttributes<HTMLAnchorElement>, HTMLAnchorElement>;

// TODO: if it's needed to use Anchor type property, then `LinkProps.type` must be renamed
interface LinkProps extends Omit<HTMLAnchorProps, 'type'> {
  readonly className?: string;
  readonly disabled?: boolean;
  readonly href?: string;
  readonly onClick?: React.MouseEventHandler<HTMLAnchorElement>;
  readonly type?: LinkType;
  readonly hideExternalIcon?: boolean;
}

const Link: React.FC<LinkProps> = ({
  children,
  className,
  disabled = false,
  href,
  onClick,
  type = LinkType.Content,
  hideExternalIcon = false,
  ...otherProps
}) => {
  const external = type === LinkType.External;
  const props = {
    className: cx(styles.link, className, {
      'sm-emr-content': type === LinkType.Content,
    }),
    href,
    onClick: disabled ? undefined : onClick,
    target: external ? '_blank' : undefined,
    rel: external ? 'noopener noreferrer' : undefined,
    ...otherProps,
  };

  const LaunchIcon =
    external && !hideExternalIcon ? (
      <span className={styles.externalIconClass}>
        <launcherIcon.react tag="span" />
      </span>
    ) : null;

  return (
    <a role={'link'} {...props}>
      {children}
      {LaunchIcon}
    </a>
  );
};

export { Link, LinkType, LinkProps };
