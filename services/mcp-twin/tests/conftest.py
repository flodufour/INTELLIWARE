def pytest_configure(config):
    config.addinivalue_line("markers", "orion: live tests requiring a dedicated seeded Orion-LD and MCP twin")
