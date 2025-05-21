const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      require('@cypress/code-coverage/task')(on, config);
      return config;
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    viewportWidth: 1280,
    viewportHeight: 720,
    retries: {
      runMode: 2,
      openMode: 0
    }
  },
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack'
    },
    specPattern: 'cypress/component/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.js'
  }
});