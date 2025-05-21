// Import commands.js using ES2015 syntax:
import './commands';

// Import cypress-axe for accessibility testing
import 'cypress-axe';

// Import cypress-real-events for better event simulation
import 'cypress-real-events';

// Import code coverage support
import '@cypress/code-coverage/support';

// Add custom commands for common operations
Cypress.Commands.add('checkA11y', () => {
  cy.injectAxe();
  cy.checkA11y();
});

Cypress.Commands.add('selectBaseOption', (baseType, option) => {
  cy.get(`[data-testid="base-type-${baseType}"]`).click();
  cy.get(`[data-testid="base-option-${option}"]`).click();
});

Cypress.Commands.add('selectProtein', (protein) => {
  cy.get(`[data-testid="protein-${protein}"]`).click();
});

Cypress.Commands.add('selectSauce', (sauce) => {
  cy.get(`[data-testid="sauce-${sauce}"]`).click();
});

Cypress.Commands.add('selectVeggies', (veggies) => {
  veggies.forEach(veggie => {
    cy.get(`[data-testid="veggie-${veggie}"]`).click();
  });
});

// Add custom assertions
chai.Assertion.addMethod('haveAccessibleName', function(expectedName) {
  const obj = this._obj;
  const actualName = obj.attr('aria-label') || obj.attr('aria-labelledby');
  this.assert(
    actualName === expectedName,
    `expected #{this} to have accessible name #{exp} but got #{act}`,
    `expected #{this} not to have accessible name #{exp}`,
    expectedName,
    actualName
  );
});