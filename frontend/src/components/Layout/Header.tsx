import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import PraxisLogo from '../Brand/PraxisLogo';
import { APP_NAME } from '../Brand/brand';

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: 'var(--space-4) var(--space-7)',
  backgroundColor: 'var(--nav-bg)',
  position: 'sticky',
  top: 0,
  zIndex: 50,
};

const navStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-6)',
};

const linkBase: React.CSSProperties = {
  textDecoration: 'none',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 500,
  color: 'var(--nav-link)',
  padding: 'var(--space-1) 0',
  borderBottom: '2px solid transparent',
  transition: 'color var(--transition-fast), border-color var(--transition-fast)',
};

const linkActive: React.CSSProperties = {
  ...linkBase,
  color: 'var(--nav-text)',
  borderBottomColor: 'var(--nav-link-active-border)',
};

export default function Header() {
  const { isAuthenticated } = useAuth();

  return (
    <header style={headerStyle}>
      <Link to="/" style={{ textDecoration: 'none' }} aria-label={`${APP_NAME} home`}>
        <PraxisLogo variant="full" colorScheme="dark" height={28} />
      </Link>
      <nav style={navStyle} aria-label="Main navigation">
        <NavLink
          to="/generate"
          style={({ isActive }) => (isActive ? linkActive : linkBase)}
        >
          Generate
        </NavLink>
        {!isAuthenticated && (
          <NavLink
            to="/sample-preview"
            style={({ isActive }) => (isActive ? linkActive : linkBase)}
          >
            Sample
          </NavLink>
        )}
        {isAuthenticated && (
          <NavLink
            to="/dashboard"
            style={({ isActive }) => (isActive ? linkActive : linkBase)}
          >
            Dashboard
          </NavLink>
        )}
      </nav>
    </header>
  );
}
