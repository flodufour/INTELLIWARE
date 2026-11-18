FROM python:3.12-slim
WORKDIR /app
COPY contracts/mcp /contracts/mcp
RUN pip install --no-cache-dir /contracts/mcp
COPY services/mcp-twin/pyproject.toml ./
COPY services/mcp-twin/src ./src
RUN pip install --no-cache-dir .
CMD ["python", "-m", "mcp_twin"]
