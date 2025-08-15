from __future__ import annotations
import os
import re
import asyncio
from typing import List, Optional, Literal, Dict
from pathlib import Path
from glob import glob
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel
from bb_dataset_maker import __version__
from bb_dataset_maker.models import BBFilename, split_ulx_uly_suffix
from wombat.multiprocessing.worker import Worker
from wombat.multiprocessing.orchestrator import Orchestrator
from wombat.multiprocessing.tasks import Task, TaskState, RetryableTask
from wombat.multiprocessing.models import RequiresProps, Prop, PositionalActionable
import json
from tqdm import tqdm
import traceback


class FindFileTask(Task, PositionalActionable):
    action: str = "find_file"


async def find_file(worker: Worker, pattern: str) -> Optional[Path]:
    return glob(pattern, recursive=True)


def fail(worker: Worker):
    raise Exception("This function always fails.")


def fetch_db_credentials():
    load_dotenv()
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
    }


class ValidateJsonTask(Task):
    action: str = "validate_json"


def explode_pydantic_models(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist.")
    if not isinstance(df[column_name].iloc[0], BaseModel):
        raise ValueError(
            f"The column '{column_name}' does not contain Pydantic models."
        )
    expanded_df = df[column_name].apply(lambda x: x.model_dump())
    expanded_df = pd.json_normalize(expanded_df)
    return pd.concat([df.drop(columns=[column_name]), expanded_df], axis=1)


def choose_ontology(considered_ontologies):
    if len(considered_ontologies) == 1:
        return considered_ontologies[0]
    max_nClass = None
    max_version = None
    simple_ontologies = []
    re_has_version = re.compile(r"([0-9]+\.)+(.*)")
    re_has_class_count = re.compile(r"([0-9]+)class")
    for ontology in considered_ontologies:
        ont_has_version = bool(re_has_version.search(ontology))
        ont_has_class_count = bool(re_has_class_count.search(ontology))
        if not ont_has_version and not ont_has_class_count:
            simple_ontologies.append(ontology)


def process_file(filename):
    filepath = Path(filename)
    try:
        final_dataset: Dict = {}
        BLACKBIRD_DELIMITERS = ["-", "_"]
        MURSIS_DELIMITERS = ["_"]
        blackbird_parts = filepath.stem.split(BLACKBIRD_DELIMITERS[0])
        cgi_parts = (blackbird_parts[0].split(MURSIS_DELIMITERS[0]))[2:]
        nitf_filename = MURSIS_DELIMITERS[0].join(cgi_parts) + ".nitf"
        creds = fetch_db_credentials()
        conn = psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            database=creds["database"],
            user=creds["user"],
            password=creds["password"],
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT scene_id, version, filepath
                    FROM blackbird_old.scene_nitf_version
                    WHERE filename = %s
                    """,
                    (nitf_filename,),
                )
                result = cur.fetchone()
                if not result:
                    print(nitf_filename)
                    return final_dataset
                scene_id, version, scene_filepath = result
            if nitf_filename not in final_dataset:
                final_dataset[scene_filepath] = {}
            feature_id = cgi_parts[0]
            image_dttm = cgi_parts[1]
            with open(filename) as fp:
                data = dict(json.load(fp))
                c = None
                r = None
                chip_key: str = "UNCHIPPED"
                if len(blackbird_parts) > 1:
                    c, r = tuple(blackbird_parts[1].split(BLACKBIRD_DELIMITERS[1]))
                    chip_key = f"{c}_{r}"
                if chip_key not in final_dataset[scene_filepath]:
                    final_dataset[scene_filepath][chip_key] = {}
                if (
                    "source_json_filename"
                    not in final_dataset[scene_filepath][chip_key]
                ):
                    final_dataset[scene_filepath][chip_key]["source_json_filename"] = (
                        set()
                    )
                final_dataset[scene_filepath][chip_key]["source_json_filename"].add(
                    str(filepath)
                )
                if "label_report" in data:
                    final_dataset[scene_filepath][chip_key]["label_report"] = data[
                        "label_report"
                    ]
                else:
                    Exception(
                        "Required key 'label_report' missing from data, data bad or script needs updated"
                    )
                if "raw_features" not in final_dataset[scene_filepath][chip_key]:
                    final_dataset[scene_filepath][chip_key]["raw_features"] = []
                final_dataset[scene_filepath][chip_key]["raw_features"] = (
                    final_dataset[scene_filepath][chip_key]["raw_features"]
                    + data["features"]
                )
                if "scene_id" not in final_dataset[scene_filepath][chip_key]:
                    final_dataset[scene_filepath][chip_key]["scene_id"] = scene_id
                    final_dataset[scene_filepath][chip_key]["db_version"] = version
                    final_dataset[scene_filepath][chip_key][
                        "bb_dataset_maker_version"
                    ] = __version__
                if "ontologies" not in final_dataset[scene_filepath][chip_key]:
                    final_dataset[scene_filepath][chip_key]["ontologies"] = set()
                if len(data["features"]) > 0:
                    for feature in data["features"]:
                        feature_label = feature["properties"]["label"]["name"]
                        feature_properties = feature["properties"].keys()
                        if "considered_ontology_names" in feature["properties"].keys():
                            feature_ontologies = feature["properties"][
                                "considered_ontology_names"
                            ]
                        else:
                            feature_ontologies = []
                        ontology_version = "1-0-0"
                        if (
                            len(feature_ontologies) > 0
                            and "jiko" in feature_ontologies[0]
                        ):
                            ontology_string = feature_ontologies[0]
                            parts = ontology_string.split("-")
                            version_parts = []
                            for part in parts[1:]:
                                if part.isdigit():
                                    version_parts.append(part)
                                else:
                                    break
                            if version_parts:
                                ontology_version = "-".join(version_parts)
                            final_dataset[scene_filepath][chip_key]["ontologies"].add(
                                feature_ontologies[0]
                            )
                        final_dataset[scene_filepath][chip_key]["ontology_version"] = (
                            ontology_version
                        )
                return final_dataset
        finally:
            conn.close()
    except Exception as e:
        print(f"[process_file] Exception for {filepath}: {e}")
        traceback.print_exc()


async def main():
    creds = fetch_db_credentials()
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"],
    )

    # Fetch all tag/ontology info
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id, t.name, o.name
            FROM blackbird_old.tag t
            JOIN blackbird_old.ontology o ON t.ontology_id = o.id
        """)
        tags_rows = cur.fetchall()
    tags_df = pd.DataFrame(tags_rows, columns=["tag_id", "tag_name", "ontology_name"])

    # Fetch only the latest scene_nitf_version per filename
    with conn.cursor() as cur:
        cur.execute("""
            SELECT snv.filename, snv.version, s.delivery_id
            FROM blackbird_old.scene_nitf_version snv
            JOIN blackbird_old.scene s ON s.id = snv.scene_id
            INNER JOIN (
                SELECT filename, MAX(version) as max_version
                FROM blackbird_old.scene_nitf_version
                GROUP BY filename
            ) latest
            ON snv.filename = latest.filename AND snv.version = latest.max_version
        """)
        upgraded_rows = cur.fetchall()
    upgraded_df = pd.DataFrame(
        upgraded_rows,
        columns=["mosaic_filename_with_extension", "db_version", "delivery_id"],
    )

    if Path("filepaths.csv").exists():
        df = pd.read_csv(
            "filepaths.csv", converters={"filepath": BBFilename.from_filename}
        )
    else:
        raw = pd.read_csv("filenames.txt")["filename"].to_list()
        json_files = [BBFilename.from_filename(Path(f)) for f in raw]
        df = pd.DataFrame({"filepath": json_files})

    expanded_df = explode_pydantic_models(df, "filepath")
    expanded_df["mosaic_filename_with_extension"] = expanded_df[
        "mosaic_filename"
    ].apply(lambda x: split_ulx_uly_suffix(x) + ".nitf")
    # ENSURE delivery_id DOES NOT EXIST IN expanded_df (fix for merge issue)
    if "delivery_id" in expanded_df.columns:
        expanded_df = expanded_df.drop(columns=["delivery_id"])

    # Track the original version before merging
    expanded_df["input_version"] = expanded_df["version"]

    merged_df = pd.merge(
        expanded_df,
        upgraded_df,
        left_on="mosaic_filename_with_extension",
        right_on="mosaic_filename_with_extension",
        how="left",
    )
    merged_df["delivery_id"] = merged_df["delivery_id"].astype("Int64").astype("str")

    # Print upgrade details
    total_files = len(merged_df)
    found_in_db = merged_df["db_version"].notna().sum()
    not_in_db = merged_df["db_version"].isna().sum()

    # "Upgraded" means: DB found, and input_version != db_version (ignoring null input_version)
    merged_df["db_version"] = pd.to_numeric(merged_df["db_version"], errors="coerce")

    # "Upgraded" means the DB version is greater than 1
    upgraded = (merged_df["db_version"] > 1).sum()

    # "Already at latest version" can now be defined as files at version 1
    already_latest = (merged_df["db_version"] == 1).sum()

    print(f"Total input files: {total_files}")
    print(f"Files found in DB: {found_in_db}")
    print(f"Files not found in DB: {not_in_db}")
    print(f"Files upgraded to latest DB version: {upgraded}")
    print(f"Files already at latest version: {already_latest}")

    mask_missing = (
        merged_df["delivery_id"].isin(["<NA>", "nan", "NaN", "None"])
        | merged_df["delivery_id"].isna()
    )

    # Multi-process option
    orchestrator = Orchestrator(
        num_workers=os.cpu_count(),
        show_progress=True,
        task_models=[FindFileTask],
        actions={"find_file": find_file},
    )
    if len(mask_missing[mask_missing]) > 0:
        tasks_list = []
        for i, row in merged_df[mask_missing].iterrows():
            mosaic_path = Path(
                f"/cgi/data/blackbird/CGI_MOSAIC_DELIVERIES_TO_BLACKBIRD/arctic_ground_squirrel/mosaics_v3/nitfs/{row['mosaic_filename']}.nitf"
            )
            if mosaic_path.exists():
                merged_df.at[i, "filepath"] = str(mosaic_path)
                merged_df.at[i, "delivery_id"] = 6
            else:
                tasks_list.append(FindFileTask(args=[str(mosaic_path)]))
        await orchestrator.add_tasks(tasks_list)
        orchestrator.stop_workers()


    processed_data = []
    for idx, row in merged_df.iterrows():
        filepath = row.get("json_filepath")
        if not filepath or not Path(filepath).exists():
            processed_data.append(None)
            continue
        try:
            file_result = process_file(filepath)
        except Exception as e:
            print(f"[main/process_file] Exception for {filepath}: {e}")
            traceback.print_exc()
            processed_data.append(None)
            continue
        ontologies = set()
        if file_result:
            for scene_dict in file_result.values():
                for chip_dict in scene_dict.values():
                    onts = chip_dict.get("ontologies", [])
                    ontologies.update(onts)
            ontologies = list(ontologies)
            chosen_ontology = choose_ontology(ontologies) if ontologies else None
            if chosen_ontology:
                for scene_dict in file_result.values():
                    for chip_dict in scene_dict.values():
                        chip_dict["chosen_ontology"] = chosen_ontology
        processed_data.append(file_result)
    merged_df["processed_data"] = processed_data

    feature_rows = []
    for _, row in merged_df.iterrows():
        processed = row.get("processed_data")
        if not processed:
            continue
        for scene_data in processed.values():
            for chip_data in scene_data.values():
                chosen_ontology = chip_data.get("chosen_ontology")
                if not chosen_ontology:
                    continue
                features = chip_data.get("raw_features", [])
                for feature in features:
                    tag_name = (
                        feature.get("properties", {}).get("label", {}).get("name")
                    )
                    if tag_name:
                        feature_rows.append(
                            {"tag_name": tag_name, "ontology_name": chosen_ontology}
                        )

    features_df = pd.DataFrame(feature_rows)
    features_df = features_df.merge(
        tags_df, how="left", on=["tag_name", "ontology_name"]
    )
    counts_df = features_df.groupby("tag_id").size().reset_index(name="count")
    print(counts_df)

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
