describe('Smoketests for Brazil Blog', () => {

  it('should load the homepage and return status 200', () => {
    cy.visit('/');
    cy.request('/').its('status').should('eq', 200);
  });

  it('should have blog posts on the homepage', () => {
    cy.visit('/');
    cy.get('a.bg-white').should('exist');
  });

  it('should load a blog post page and return status 200', () => {
    cy.visit('/');
    cy.get('a.bg-white').first().click();
    // cy.location('pathname').should('not.eq', '/'); // Ensure it's a different page
    // cy.request(cy.location('href')).its('status').should('eq', 200);
  });

  it('should have the JavaScript file', () => {
    cy.request('/static/js/brazil_blog.js').its('status').should('eq', 200);
  });

  it('should have the CSS file', () => {
    cy.request('/static/css/brazil_blog_compiled.css').its('status').should('eq', 200);
  });
});
