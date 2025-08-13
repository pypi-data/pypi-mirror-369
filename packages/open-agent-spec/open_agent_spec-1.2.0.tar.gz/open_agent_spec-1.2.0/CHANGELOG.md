# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-12-19

### Added
- **Cortex Intelligence Engine Integration**
  - New `cortex` engine type for advanced AI reasoning
  - Cortex-specific configuration options (`enable_layer3`, `enable_onnx`)
  - Automatic dependency management for `cortex-intelligence` package
  - Environment variable handling for OpenAI and Claude API keys
  - Comprehensive Cortex agent templates and examples
  - Full integration with DACP framework

### Changed
- **Code Quality Improvements**
  - Replaced conflicting `black` + `ruff` tooling with unified `ruff` solution
  - Enhanced ruff configuration for consistent formatting
  - Updated CI workflow to use only `ruff` for linting and formatting
  - Improved code formatting consistency across the project

### Fixed
- **Linting and Formatting Issues**
  - Resolved conflicts between `black` and `ruff format`
  - Fixed all linting errors and warnings
  - Improved CI reliability and consistency
  - Enhanced ruff configuration for better compatibility

### Documentation
- **Cortex Integration Guide**
  - Comprehensive `CORTEX_INTEGRATION.md` documentation
  - Updated `README.md` with Cortex engine documentation
  - Added Cortex examples and templates
  - Enhanced API documentation and usage examples

### Technical
- **Schema Updates**
  - Extended JSON schema to support Cortex engine
  - Added Cortex-specific configuration validation
  - Enhanced type safety and validation rules

## [1.1.0] - Current PyPI Version

### Added
- Support for OpenAI, Anthropic, Grok, and custom engines
- Basic agent generation and validation
- DACP integration framework 