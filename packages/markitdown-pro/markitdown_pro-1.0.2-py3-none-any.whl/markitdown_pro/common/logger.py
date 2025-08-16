import logging
import os

log_level = int(os.getenv("LOG_LEVEL", "20"))
logger = logging.getLogger(__name__)
logging.basicConfig(level=log_level, format="[%(asctime)s] [%(levelname)s] %(message)s")

# Quiet the Azure SDK HTTP logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies._universal").setLevel(logging.WARNING)

# 2) Azure Monitor exporter "Transmission succeeded..." spam
logging.getLogger("azure.monitor.opentelemetry.exporter").setLevel(logging.WARNING)
logging.getLogger("azure.monitor.opentelemetry.exporter._transmission").setLevel(logging.WARNING)

# 3) Quiet the rest of the Azure SDK + OTel + urllib3 connection noise
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
