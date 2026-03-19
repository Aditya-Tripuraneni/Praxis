import { Outlet } from 'react-router-dom';
import Header from './Header';

const mainStyle: React.CSSProperties = {
  maxWidth: '960px',
  margin: '0 auto',
  padding: 'var(--space-8) var(--space-6)',
};

export default function Layout() {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <main id="main-content" style={mainStyle}>
        <Outlet />
      </main>
    </>
  );
}
