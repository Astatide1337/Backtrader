import Document, { Html, Head, Main, NextScript, DocumentContext } from 'next/document';

class MyDocument extends Document {
  static async getInitialProps(ctx: DocumentContext) {
    const initialProps = await Document.getInitialProps(ctx);
    return { ...initialProps };
  }

  render() {
    return (
      <Html lang="en">
        <Head>
          <meta name="theme-color" content="#2563eb" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <meta name="description" content="Backtrader dashboard" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <body className="layout-root">
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;