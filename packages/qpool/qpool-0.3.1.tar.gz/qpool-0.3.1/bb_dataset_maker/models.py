from __future__ import annotations
import re
from typing import List, Optional, Literal, ClassVar, Union
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from geojson.geometry import Geometry


def split_ulx_uly_suffix(name: str) -> str:
    parts = name.rsplit("-", 1)
    if len(parts) == 2:
        ulxy = parts[1].split("_")
        if len(ulxy) == 2 and ulxy[0].isdigit() and ulxy[1].isdigit():
            return parts[0]
    return name


class Label(BaseModel):
    name: str
    label_id: str
    ontology_iri: Optional[str] = None
    ontology_hierarchy: Optional[List[str]] = None


class FeatureProperties(BaseModel):
    label: Label
    pixel_coordinates: List[List[float]]
    full_frame_pixel_coordinates: List[List[float]]
    polygon_collection_datetime: str
    feature_id: Optional[str] = None
    job_id: List[str]
    label_type: str


class Feature(BaseModel):
    type: str = Field(default="Feature")
    geometry: Geometry
    properties: FeatureProperties
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)


class LabelReport(BaseModel):
    image_id: str
    image_pixel_width: Optional[int] = None
    image_pixel_height: Optional[int] = None
    label_acquisition_date: str
    label_version: int
    peer_reviewed: bool
    label_handling_method: str
    considered_iris: List[str]
    considered_classes: List[str]
    considered_ontology_names: List[str]
    full_frame_offset: Optional[List[int]] = None
    label_set_id: str


class SceneData(BaseModel):
    type: str = Field(default="FeatureCollection")
    features: List[Feature]
    label_report: LabelReport


v2_pattern = re.compile(
    r"(?P<featureid>[0-9a-f]{32}|EvwhsVividBasemap)_(?P<deliveryid>\d+[a-zA-Z]?)_(?P<date>\d{4}-\d{2}-\d{2})(?:_(?P<contigid>\d+))?(?:-(?P<xoffset>-?\d+)_(?P<yoffset>-?\d+))?"
)
v2_corrupt_pattern = re.compile(
    r"(?P<featureid>[0-9a-f]{32}|EvwhsVividBasemap)_(?P<deliveryid>\d+[a-zA-Z]?)_(?P<date>\d{4}_\d{2}_\d{2})(?:_(?P<contigid>\d+))?(?:-(?P<xoffset>-?\d+)_(?P<yoffset>-?\d+))?"
)
v1_pattern = re.compile(
    r"(?P<featureid>[0-9a-f]{32}|EvwhsVividBasemap)_(?P<pid>\d+[a-zA-Z]?)_(?P<date>\d{8})_(?P<timestamp>\d+)_(?P<unsureint1>\d+)_(?P<unsureint2>\d+)(?:-(?P<xoffset>-?\d+)_(?P<yoffset>-?\d+))?"
)
v1_wtf_1_pattern = re.compile(
    r"(?P<featureid>[0-9a-f]{32}|EvwhsVividBasemap)_(?P<date>\d{8})_(?P<pid>\d+)_(?P<unsureint1>\d+)_(?P<unsureint2>\d+)_(?P<unsureint3>\d+)"
)
v1_wtf_2_pattern = re.compile(
    r"(?P<featureid>[0-9a-f]{32}|EvwhsVividBasemap)_(?P<pid>\d+)_(?P<date>\d{8})_(?P<timestamp>\d+)"
)


def filename_to_parts(filename):
    for pattern, fmt, fixed in [
        (v2_pattern, "V2", ["contigid"]),
        (v2_corrupt_pattern, "V2_Corrupt", ["contigid"]),
        (v1_pattern, "V1", ["pid"]),
        (v1_wtf_1_pattern, "V1_WTF_1", ["unsureint1", "unsureint2", "unsureint3"]),
        (v1_wtf_2_pattern, "v1_wtf_2_pattern", []),
    ]:
        match = pattern.match(filename)
        if match:
            result = match.groupdict()
            result["format"] = fmt
            # Extract version if available
            if "version" in result and result["version"] is not None:
                try:
                    result["version"] = int(result["version"])
                except Exception:
                    pass
            if fmt.startswith("V1"):
                result["deliveryid"] = (
                    "1" if "deliveryid" not in result else result["deliveryid"]
                )
            for key in fixed:
                if result.get(key) is not None:
                    result[key] = int(result[key])
            result["mosaic_filename"] = split_ulx_uly_suffix(filename)
            return result
    raise ValueError(f"Could not match any pattern for filename: {filename}")


class BBFilename(BaseModel):
    json_filepath: Path
    mosaic_filename: str
    prefix: ClassVar[Literal["MAVEN_METADATA_"]] = "MAVEN_METADATA_"
    feature_id: Union[str, Literal["EvwhsVividBasemap"]] = Field(required=True)
    delivery_id: Optional[str] = None
    extension: ClassVar[Literal[".json"]] = ".json"
    delimiter: ClassVar[Literal["_"]] = "_"
    ux: Optional[int] = None
    uy: Optional[int] = None
    tiled: bool = False
    version: Optional[int] = None  # Added for upgrade comparison

    @staticmethod
    def from_filename(filepath: Path) -> "BBFilename":
        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        filename = filepath.stem.replace(BBFilename.prefix, "").replace(
            BBFilename.extension, ""
        )
        parts = filename_to_parts(filename)
        # Try to extract version if present in filename parts
        version = parts.get("version")
        return BBFilename(
            json_filepath=filepath,
            mosaic_filename=filename,
            feature_id=parts["featureid"],
            delivery_id=parts.get("deliveryid"),
            ux=parts.get("xoffset"),
            uy=parts.get("yoffset"),
            tiled=bool(parts.get("xoffset") or parts.get("yoffset")),
            format=parts["format"],
            version=version,
        )
