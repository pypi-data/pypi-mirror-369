import os
from dotenv import load_dotenv
import logging

load_dotenv()

CHARTMOGUL_TOKEN = os.getenv('CHARTMOGUL_TOKEN')
MCP_SERVER_NAME = "mcp-chartmogul"
DEPENDENCIES = [
    "chartmogul",
    "python-dotenv"
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(MCP_SERVER_NAME)