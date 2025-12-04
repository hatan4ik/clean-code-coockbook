# Contribution Guidelines

This section provides clear instructions for how to contribute to the "Clean Code Cookbook." We welcome contributions from the community.

* **Code Style:**
  * **Python:** We follow `PEP 8` and use `black` for formatting. `ruff` is used for linting.
  * **Go:** We follow the standard `gofmt` style. `golangci-lint` is used for linting.
* **Commit Message Format:**
  * We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
  * **Example:**
    * `feat(python): add chapter on structured logging with structlog`
    * `fix(go): correct worker pool example`
    * `docs(readme): update contribution guidelines`
* **Pull Request (PR) Process:**
    1. **Fork & Branch:** Fork the repository and create a new branch for your feature or bug fix.
    2. **Develop:** Make your changes. Add new content, fix bugs, or improve existing examples.
    3. **Test:** If you are adding code, ensure it is accompanied by tests. Run the existing test suite to make sure you haven't introduced any regressions.
    4. **Lint:** Run the linters to ensure your code adheres to our style guidelines.
    5. **Submit PR:** Submit a pull request with a clear description of the changes. Reference any related issues.
    6. **Review:** The PR will be reviewed by at least one core contributor. We will provide feedback and may request changes.
* **Code of Conduct:**
  * We are committed to providing a welcoming and inclusive environment for all.
  * All contributors are expected to adhere to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Any violations will be taken seriously.
