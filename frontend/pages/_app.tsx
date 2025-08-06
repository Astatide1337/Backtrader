import type { AppProps } from 'next/app';
import { SWRConfig } from 'swr';
import { swrConfig } from 'lib/swr';
import 'styles/globals.css';
import AppLayout from 'components/layout/AppLayout';

const MyApp: React.FC<AppProps> = ({ Component, pageProps }) => {
  return (
    <SWRConfig value={swrConfig}>
      <AppLayout>
        <Component {...pageProps} />
      </AppLayout>
    </SWRConfig>
  );
};

export default MyApp;