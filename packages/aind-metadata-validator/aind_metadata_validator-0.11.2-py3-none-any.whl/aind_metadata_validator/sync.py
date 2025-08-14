"""Main entrypoint"""

from aind_metadata_validator.metadata_validator import validate_metadata
from aind_data_access_api.document_db import MetadataDbClient
from aind_data_access_api.rds_tables import RDSCredentials
from aind_data_access_api.rds_tables import Client
import pandas as pd
import os
import logging
from pathlib import Path
import argparse

API_GATEWAY_HOST = os.getenv(
    "API_GATEWAY_HOST", "api.allenneuraldynamics-test.org"
)

OUTPUT_FOLDER = Path(os.getenv("OUTPUT_FOLDER", "/results"))
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

client = MetadataDbClient(
    host=API_GATEWAY_HOST,
    version="v2",
)

DEV_OR_PROD = "dev" if "test" in API_GATEWAY_HOST else "prod"
REDSHIFT_SECRETS = f"/aind/{DEV_OR_PROD}/redshift/credentials/readwrite"
RDS_TABLE_NAME = f"metadata_status_{DEV_OR_PROD}_v2"

CHUNK_SIZE = 1000

rds_client = Client(
    credentials=RDSCredentials(aws_secrets_name=REDSHIFT_SECRETS),
)

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler(
            OUTPUT_FOLDER / "app.log"
        ),  # Write logs to a file named "app.log"
        logging.StreamHandler(),  # Optional: also log to the console
    ],
)


def run(test_mode: bool = False, force: bool = False):
    logging.info(
        f"(METADATA VALIDATOR): Starting run, targeting: {API_GATEWAY_HOST}"
    )

    # Get all unique location values in the database
    uniquelocations = client.aggregate_docdb_records(
        pipeline=[
            {"$group": {"_id": None, "locations": {"$addToSet": "$location"}}},
            {"$project": {"_id": 0, "locations": 1}},
        ],
    )
    uniquelocations = list(uniquelocations[0]["locations"])

    if test_mode:
        logging.info("(METADATA VALIDATOR): Running in test mode")
        uniquelocations = uniquelocations[:10]

    logging.info(f"(METADATA VALIDATOR): Retrieved {len(uniquelocations)} records")
    original_df = rds_client.read_table(RDS_TABLE_NAME)

    if "location" not in original_df.columns or len(original_df) < 10:
        logging.info(
            "(METADATA VALIDATOR): No previous validation results found, starting fresh"
        )
        original_df = None

    results = []

    # Go through the unique IDs in chunks of 100

    for i in range(0, len(uniquelocations), 100):
        chunk = uniquelocations[i: i + 100]

        response = client.retrieve_docdb_records(
            filter_query={"location": {"$in": chunk}},
            limit=0,
            paginate_batch_size=100,
        )

        for record in response:
            if (
                original_df is not None
                and record["location"] in original_df["location"].values
            ):
                # Get the matching row from the original dataframe as a dictionary
                prev_validation = original_df.loc[
                    original_df["location"] == record["location"]
                ].to_dict(orient="records")[0]
                results.append(
                    validate_metadata(
                        record, prev_validation if not force else None
                    )
                )
            else:
                results.append(validate_metadata(record, None))

    df = pd.DataFrame(results)
    # Log results
    df.to_csv(OUTPUT_FOLDER / "validation_results.csv", index=False)

    logging.info("(METADATA VALIDATOR) Dataframe built -- pushing to RDS")

    if test_mode:
        logging.info(
            "(METADATA VALIDATOR) Running in test mode, would have written table"
        )
    else:
        if len(df) < CHUNK_SIZE:
            rds_client.overwrite_table_with_df(df, RDS_TABLE_NAME)
        else:
            # chunk into CHUNK_SIZE row chunks
            logging.info("(METADATA VALIDATOR) Chunking required for RDS")
            rds_client.overwrite_table_with_df(
                df[0:CHUNK_SIZE], RDS_TABLE_NAME
            )
            for i in range(CHUNK_SIZE, len(df), CHUNK_SIZE):
                rds_client.append_df_to_table(
                    df[i : i + CHUNK_SIZE], RDS_TABLE_NAME
                )

    # Roundtrip the table and ensure that the number of rows matches
    df_in_rds = rds_client.read_table(RDS_TABLE_NAME)

    if not test_mode and (len(df) != len(df_in_rds)):
        logging.error(
            f"(METADATA VALIDATOR) Mismatch in number of rows between input and output: {len(df)} vs {len(df_in_rds)}"
        )
    else:
        logging.info("(METADATA VALIDATOR) Success")


if __name__ == "__main__":
    # Use argparse to check if we are running in test mode, if so limit the number of records
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        help="Run in test mode with a limited number of records",
        action="store_true",
    )
    parser.add_argument(
        "--force",
        help="Force validation to ignore previous results",
        action="store_true",
    )
    args = parser.parse_args()
    run(args.test, args.force)
