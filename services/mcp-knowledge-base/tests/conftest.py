def pytest_configure(config):
    config.addinivalue_line("markers", "knowledge: live tests requiring NEO4J_TEST_URI")
