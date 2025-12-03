*   **Security First:**
    *   **SAST (Static Application Security Testing):** We use `Snyk` to scan our code for vulnerabilities. See the [Snyk Security Instructions](./.github/instructions/snyk_rules.instructions.md) for more details.
    *   **Dependency Scanning:** Automated scanning of dependencies for known vulnerabilities using `Snyk` or `dependabot`.
    *   **Secrets Management:** We will use `HashiCorp Vault` or a similar tool to manage secrets. We will demonstrate how to fetch secrets at runtime and not store them in environment variables.