import React from 'react';
import BaseSelectionGrid from '../../src/components/BaseSelectionGrid';

describe('BaseSelectionGrid Component', () => {
  const mockBaseTypes = {
    'Biryani': [
      { name: 'Rice', price: 2.00, description: 'Fragrant basmati rice' }
    ],
    'Sandwich & Subs': [
      { name: 'Sourdough', price: 2.50, description: 'Tangy artisan bread' }
    ]
  };

  const defaultProps = {
    title: 'Select Your Base',
    baseTypes: mockBaseTypes,
    recommendations: ['Biryani'],
    selectedBaseType: '',
    selectedBaseOption: '',
    onSelect: cy.stub().as('onSelect')
  };

  beforeEach(() => {
    cy.mount(<BaseSelectionGrid {...defaultProps} />);
    cy.injectAxe();
  });

  it('renders correctly with all base types and options', () => {
    cy.get('h2').should('contain', 'Select Your Base');
    cy.get('h3').should('contain', 'Biryani');
    cy.get('h3').should('contain', 'Sandwich & Subs');
    cy.get('[data-testid="base-option-Rice"]').should('be.visible');
    cy.get('[data-testid="base-option-Sourdough"]').should('be.visible');
  });

  it('highlights recommended base types', () => {
    cy.get('[data-testid="base-type-Biryani"]')
      .should('have.class', 'text-green-600');
  });

  it('handles selection and deselection', () => {
    // Select an option
    cy.get('[data-testid="base-option-Rice"]').click();
    cy.get('@onSelect').should('have.been.calledWith', 'Biryani', 'Rice');

    // Deselect the same option
    cy.get('[data-testid="base-option-Rice"]').click();
    cy.get('@onSelect').should('have.been.calledWith', '', '');
  });

  it('displays prices and descriptions correctly', () => {
    cy.get('[data-testid="base-option-Rice"]')
      .should('contain', '$2.00')
      .and('have.attr', 'title', 'Fragrant basmati rice');
  });

  it('maintains accessibility standards', () => {
    // Check for proper heading structure
    cy.get('h2').should('have.attr', 'id');
    cy.get('h3').should('have.attr', 'aria-labelledby');

    // Check for proper ARIA attributes
    cy.get('[data-testid="base-option-Rice"]')
      .should('have.attr', 'role', 'button')
      .and('have.attr', 'aria-pressed');

    // Run axe accessibility tests
    cy.checkA11y();
  });

  it('handles keyboard navigation', () => {
    // Focus first option
    cy.get('[data-testid="base-option-Rice"]').focus();
    cy.focused().should('have.attr', 'data-testid', 'base-option-Rice');

    // Navigate to next option
    cy.focused().type('{rightArrow}');
    cy.focused().should('have.attr', 'data-testid', 'base-option-Sourdough');

    // Select with keyboard
    cy.focused().type('{enter}');
    cy.get('@onSelect').should('have.been.calledWith', 'Sandwich & Subs', 'Sourdough');
  });

  it('applies correct styling for selected items', () => {
    // Mount with selected item
    cy.mount(
      <BaseSelectionGrid
        {...defaultProps}
        selectedBaseType="Biryani"
        selectedBaseOption="Rice"
      />
    );

    cy.get('[data-testid="base-option-Rice"]')
      .should('have.class', 'border-blue-500')
      .and('have.class', 'bg-blue-50');
  });
});