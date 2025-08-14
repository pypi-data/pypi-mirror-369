This module serves as a central place for providing utilities for our python backends.

- **Auth**: Authentication and authorization for APIs with API key and JWT bearer token support
- **Ansi Colors**: ANSI color codes for terminal text formatting and colorful console output
- **Decorators**: Utility decorators for model manipulation, including `partial_model` for optional fields
- **Enums**: Common enumerations for type safety and consistency
- **Errors**: Comprehensive error handling system with HTTP exceptions and error content structures
- **Exceptions**: Custom exception classes and error handling utilities
- **Logging**: Logging configuration and utilities for consistent formatting
- **Middleware**: API middleware components for request/response processing
- **Mixins**: Reusable functionality components for class mixing
- **Pagination**: Utilities for paginated API responses and cursor-based pagination
- **Router**: API routing utilities and components
- **Scopes**: Authorization scope definitions and management for API access control
- **Urls**: URL management utilities including base URLs, service endpoints, and API versioning
- **Utils**: General utility functions and helper methods
- **Warnings**: Warning handling and custom warning types
- **Metrics**: Shared metrics collection from APIs for visualization

# Changelog

<!-- changelog-insertion -->

## v0.2.0 (2025-08-13)

### Features

- Deprecate partial_model decorator and update warning mechanism
  ([`18ad112`](https://github.com/crypticorn-ai/util-libraries/commit/18ad112bd5d843951381cc3e0714676b389597d5))

### Refactoring

- Update deprecation warnings to use CrypticornDeprecatedSince01 for consistency across modules
  ([`aa27472`](https://github.com/crypticorn-ai/util-libraries/commit/aa274725d714da0243c145a3ed63ab672c28bca2))


## v0.1.2 (2025-07-22)

### Bug Fixes

- Failing scope comparison in some environments
  ([`004495d`](https://github.com/crypticorn-ai/util-libraries/commit/004495da87b973f43b3e32abe96493dac1b6204a))


## v0.1.1 (2025-07-20)


## v0.1.1-rc.2 (2025-07-18)

### Bug Fixes

- Change verify api key request
  ([`11af6c2`](https://github.com/crypticorn-ai/util-libraries/commit/11af6c2c12a92b0a4c1c3b83ba86aca2a401ac45))

### Testing

- Fix failing auth test
  ([`03a3db1`](https://github.com/crypticorn-ai/util-libraries/commit/03a3db1341aaf51c6162454924cb929d6cfee94a))


## v0.1.1-rc.1 (2025-07-02)

### Bug Fixes

- Assign correct status code to invalid coupon
  ([`e4068ac`](https://github.com/crypticorn-ai/util-libraries/commit/e4068ac5a739bac69313b18bc3f4c208d024d06d))

- Make read coupons scope public
  ([`6f5f213`](https://github.com/crypticorn-ai/util-libraries/commit/6f5f213a53cf7a51c0f9a5bb19c927b5348255a9))


## v0.1.0 (2025-06-27)


## v0.1.0-rc.1 (2025-06-23)

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))

### Features

- Initial release
  ([`4da5fe3`](https://github.com/crypticorn-ai/util-libraries/commit/4da5fe3d33abd31b3b35462e93052db0cde077c2))


## Unreleased

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))
