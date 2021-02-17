describe("Login Form", () => {
  it("should load", () => {
    cy.visit("/login");
    cy.get("h1").contains("Login");
  });

  it("should reject invalid credentials", () => {
    cy.visit("/login");
    cy.contains("Username or password wrong").should("not.exist");
    cy.get("#username").type("john");
    cy.get("#password").type("doe");
    cy.get("form").last().submit();

    cy.contains("Username or password wrong").should("exist");
    cy.get("#username").should("have.attr", "value", "john");
  });

  it("should redirect to the home page after logging in", () => {
    cy.visit("/login");
    cy.contains("Home").should("not.exist");
    cy.get("#username").type("john");
    cy.get("#password").type("!john");
    cy.get("form").last().submit();

    cy.contains("Home");
  });

  it("should redirect from a secured page to the login page and then back", () => {
    cy.visit("/proposals");

    cy.contains("Proposals").should("not.exist");
    cy.get("#username").type("john");
    cy.get("#password").type("!john");
    cy.get("form").last().submit();

    cy.contains("Proposals").should("exist");
  });
});
