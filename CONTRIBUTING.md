# Contributing to Art & Technology Knowledge Miner

Thank you for your interest in contributing to the Art & Technology Knowledge Miner! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

- Use the [GitHub Issues](https://github.com/suhasramanand/art-tech-knowledge-miner/issues) page
- Search existing issues before creating new ones
- Use clear, descriptive titles
- Include steps to reproduce bugs
- Provide system information (OS, Python version, etc.)

### Suggesting Features

- Use the [GitHub Discussions](https://github.com/suhasramanand/art-tech-knowledge-miner/discussions) for feature requests
- Describe the problem you're trying to solve
- Explain why this feature would be valuable
- Consider implementation complexity and maintenance

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests**: `make test`
6. **Run linting**: `make lint`
7. **Commit changes**: `git commit -m 'Add amazing feature'`
8. **Push to branch**: `git push origin feature/amazing-feature`
9. **Open a Pull Request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/art-tech-knowledge-miner.git
cd art-tech-knowledge-miner

# Add upstream remote
git remote add upstream https://github.com/suhasramanand/art-tech-knowledge-miner.git

# Install dependencies
make install

# Start development environment
make dev
```

### Testing

```bash
# Run all tests
make test

# Run specific test suites
cd pipeline && python -m pytest tests/ -v
cd backend && python -m pytest tests/ -v
cd frontend && npm test

# Run with coverage
cd pipeline && python -m pytest tests/ --cov=pipeline --cov-report=html
cd backend && python -m pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Type checking
cd backend && mypy app/
cd frontend && npm run type-check
```

## 📝 Coding Standards

### Python

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Use meaningful variable and function names
- Keep functions focused and small

```python
def process_document(content: str, metadata: Dict[str, Any]) -> ProcessedChunk:
    """
    Process a document into a chunk with metadata.
    
    Args:
        content: Raw document content
        metadata: Document metadata
        
    Returns:
        ProcessedChunk object with cleaned content and metadata
        
    Raises:
        ValueError: If content is empty or invalid
    """
    if not content.strip():
        raise ValueError("Content cannot be empty")
    
    # Implementation here
    return ProcessedChunk(...)
```

### TypeScript/React

- Use TypeScript for all components
- Follow React best practices and hooks patterns
- Use meaningful component and prop names
- Keep components focused and reusable
- Use proper error handling

```typescript
interface SearchResultProps {
  result: SearchResult;
  query: string;
  onSourceClick?: (url: string) => void;
}

const SearchResult: React.FC<SearchResultProps> = ({ 
  result, 
  query, 
  onSourceClick 
}) => {
  // Implementation here
};
```

### Git Commit Messages

Use clear, descriptive commit messages:

```
feat: add hybrid search functionality
fix: resolve memory leak in embedding store
docs: update API documentation
test: add unit tests for trend analysis
refactor: simplify content preprocessing logic
```

## 🧪 Testing Guidelines

### Unit Tests

- Write tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

```python
def test_content_preprocessor_chunking():
    """Test that content is properly chunked with overlap."""
    preprocessor = ContentPreprocessor(chunk_size=100, chunk_overlap=20)
    long_content = "word " * 200  # 1000 characters
    
    chunks = preprocessor.chunk_content(long_content, {})
    
    assert len(chunks) > 1
    assert all(len(chunk.content) <= 100 for chunk in chunks)
    assert chunks[0].chunk_index == 0
```

### Integration Tests

- Test API endpoints with real data
- Test database interactions
- Test external service integrations

### Frontend Tests

- Test component rendering
- Test user interactions
- Test API integration
- Use React Testing Library

```typescript
test('renders search results correctly', () => {
  const mockResults = [
    { content: 'Test content', title: 'Test Title', url: 'http://test.com' }
  ];
  
  render(<SearchResults results={mockResults} query="test" />);
  
  expect(screen.getByText('Test Title')).toBeInTheDocument();
  expect(screen.getByText('Test content')).toBeInTheDocument();
});
```

## 📚 Documentation

### Code Documentation

- Write clear docstrings for all functions and classes
- Include type hints and parameter descriptions
- Document complex algorithms and business logic
- Keep README files updated

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error codes and responses
- Keep OpenAPI specs updated

### User Documentation

- Write clear user guides
- Include screenshots and examples
- Document installation and setup
- Keep troubleshooting guides updated

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **System information** (OS, Python version, etc.)
5. **Error messages** and logs
6. **Screenshots** if applicable

### Bug Report Template

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## System Information
- OS: [e.g. macOS 13.0]
- Python Version: [e.g. 3.11.0]
- Node Version: [e.g. 18.17.0]
- Browser: [e.g. Chrome 118]

## Additional Context
Any other context about the problem
```

## 🚀 Feature Requests

When suggesting features, please include:

1. **Problem description** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives considered** - What other options were considered?
4. **Additional context** - Any other relevant information

### Feature Request Template

```markdown
## Feature Description
Brief description of the feature

## Problem
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives
What alternatives have you considered?

## Additional Context
Any other context or screenshots
```

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Documentation is updated
- [ ] Commit messages are clear

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏷️ Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared
- [ ] Docker images built and tested

## 🤔 Questions?

- 💬 [GitHub Discussions](https://github.com/suhasramanand/art-tech-knowledge-miner/discussions)
- 📧 [Email](mailto:suhasreddy024@gmail.com)
- 🐛 [Issues](https://github.com/suhasramanand/art-tech-knowledge-miner/issues)

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for contributing to the Art & Technology Knowledge Miner! 🎨🤖
