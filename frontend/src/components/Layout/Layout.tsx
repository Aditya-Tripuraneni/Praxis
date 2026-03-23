import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';

const mainStyle: React.CSSProperties = {
  maxWidth: '960px',
  margin: '0 auto',
  padding: 'var(--space-8) var(--space-6)',
};

const fullWidthMainStyle: React.CSSProperties = {
  maxWidth: '100%',
  margin: 0,
  padding: 0,
};

export default function Layout() {
  const location = useLocation();
  const isAboutPraxisRoute = location.pathname === '/about-praxis';

  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <main id="main-content" style={isAboutPraxisRoute ? fullWidthMainStyle : mainStyle}>
        <Outlet />
      </main>
    </>
  );
}
