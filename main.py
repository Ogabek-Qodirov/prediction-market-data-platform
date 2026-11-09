
import logging
from pathlib import Path

from src.extraction.mainfold_api import fetch_markets
from src.storage.local_storage import (
    save_markets,
    save_snapshot_metadata,
    load_markets,
    save_processed_markets
)
from src.transformation.transform_markets import transform_markets
from src.processing.spark_processor import process_markets


# ==========================================
# LOGGING CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger("prediction_market_pipeline")


# ==========================================
# MAIN PIPELINE
# ==========================================

def main():

    logger.info("PREDICTION MARKET PIPELINE STARTED")

    try:

        # STEP 1: Extract
        logger.info("STEP 1: Extracting market data")

        markets = fetch_markets(
            limit=100,
            max_pages=3,
            retries=3
        )

        if not markets:
            raise ValueError("No markets received from API")

        logger.info("Extracted %s markets", len(markets))

        # STEP 2: Save raw data
        logger.info("STEP 2: Saving raw data")

        raw_file = save_markets(markets)
        save_snapshot_metadata(markets, raw_file)

        # STEP 3: Load raw data
        logger.info("STEP 3: Loading raw data")

        loaded_markets = load_markets(raw_file)

        # STEP 4: Transform
        logger.info("STEP 4: Transforming data")

        df = transform_markets(loaded_markets)

        logger.info("Transformed %s records", len(df))

        # STEP 5: Save processed data
        logger.info("STEP 5: Saving processed data")

        processed_file = save_processed_markets(df)

        logger.info("Processed file: %s", processed_file)

        # STEP 6: PySpark analytics
        logger.info("STEP 6: Running PySpark analytics")

        process_markets()

        logger.info("PIPELINE COMPLETED SUCCESSFULLY")

    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    main()
