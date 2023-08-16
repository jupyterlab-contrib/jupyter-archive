/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

// Trick to customize the fixture `waitForApplication`
process.env.IS_NOTEBOOK = '1';

module.exports = {
  ...baseConfig,
  use: {
    ...baseConfig.use,
    appPath: ''
  },
  webServer: {
    command: 'jlpm start:notebook',
    url: 'http://localhost:8888/tree',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
};
