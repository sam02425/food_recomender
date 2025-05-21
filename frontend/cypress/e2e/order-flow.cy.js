describe('Order Flow', () => {
  beforeEach(() => {
    cy.visit('/');
    // Check accessibility on each page
    cy.checkA11y();
  });

  it('completes a full order with recommended options', () => {
    // Step 1: Activity Selection
    cy.get('[data-testid="activity-active"]').click();
    cy.get('[data-testid="continue-button"]').click();
    cy.checkA11y();

    // Step 2: Protein Selection
    cy.get('[data-testid="protein-Chicken"]').should('be.visible');
    cy.selectProtein('Chicken');
    cy.get('[data-testid="continue-button"]').click();
    cy.checkA11y();

    // Step 3: Base Selection
    cy.get('[data-testid="base-type-Bowl"]').should('be.visible');
    cy.selectBaseOption('Bowl', 'Bowl');
    cy.get('[data-testid="continue-button"]').click();
    cy.checkA11y();

    // Step 4: Dish Name
    cy.get('[data-testid="dish-name"]').should('be.visible');
    cy.get('[data-testid="continue-button"]').click();
    cy.checkA11y();

    // Step 5: Sauce Selection
    cy.get('[data-testid="sauce-Curry Special"]').should('be.visible');
    cy.selectSauce('Curry Special');
    cy.get('[data-testid="continue-button"]').click();
    cy.checkA11y();

    // Step 6: Veggie Selection
    cy.get('[data-testid="veggie-Bell Pepper"]').should('be.visible');
    cy.selectVeggies(['Bell Pepper', 'Spinach', 'Tomato']);
    cy.get('[data-testid="add-to-order-button"]').click();
    cy.checkA11y();

    // Step 7: Review and Complete
    cy.get('[data-testid="order-summary"]').should('be.visible');
    cy.get('[data-testid="complete-order-button"]').click();
    cy.checkA11y();

    // Verify success message
    cy.get('[data-testid="success-message"]').should('be.visible');
  });

  it('handles going back and modifying selections', () => {
    // Complete initial steps
    cy.get('[data-testid="activity-active"]').click();
    cy.get('[data-testid="continue-button"]').click();
    cy.selectProtein('Chicken');
    cy.get('[data-testid="continue-button"]').click();

    // Go back
    cy.get('[data-testid="back-button"]').click();

    // Change selection
    cy.selectProtein('Paneer/Indian Cheese');
    cy.get('[data-testid="continue-button"]').click();

    // Verify new selection is reflected
    cy.get('[data-testid="base-selection"]').should('be.visible');
  });

  it('validates required selections', () => {
    // Try to proceed without making selections
    cy.get('[data-testid="activity-active"]').click();
    cy.get('[data-testid="continue-button"]').click();
    cy.get('[data-testid="continue-button"]').click();

    // Should show validation error
    cy.get('[data-testid="validation-error"]').should('be.visible');
  });

  it('handles API errors gracefully', () => {
    // Mock API error
    cy.intercept('GET', '/api/recommendations', {
      statusCode: 500,
      body: { error: 'Server error' }
    });

    cy.get('[data-testid="activity-active"]').click();
    cy.get('[data-testid="continue-button"]').click();

    // Should show error message
    cy.get('[data-testid="error-message"]').should('be.visible');
  });

  it('maintains accessibility throughout the flow', () => {
    // Test keyboard navigation
    cy.get('body').tab();
    cy.focused().should('have.attr', 'data-testid', 'activity-active');
    cy.focused().type('{enter}');
    cy.get('[data-testid="continue-button"]').should('be.focused');

    // Test screen reader announcements
    cy.get('[data-testid="activity-active"]').should('haveAccessibleName', 'Active/Gym');
    cy.get('[data-testid="protein-Chicken"]').should('haveAccessibleName', 'Chicken');

    // Test focus management
    cy.get('[data-testid="continue-button"]').click();
    cy.focused().should('have.attr', 'data-testid', 'protein-Chicken');
  });
});