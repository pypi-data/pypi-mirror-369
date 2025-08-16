from datetime import datetime
from pathlib import Path
from typing import ClassVar
from warnings import warn

import numpy as np
import rasterio
from pydantic import BaseModel, Field, field_validator, model_validator

from dist_s1.constants import EXPECTED_FORMAT_STRING, PRODUCT_VERSION, TIF_LAYERS, TIF_LAYER_DTYPES
from dist_s1.data_models.data_utils import get_acquisition_datetime
from dist_s1.rio_tools import get_mgrs_profile
from dist_s1.water_mask import apply_water_mask


PRODUCT_TAGS_FOR_EQUALITY = [
    'pre_rtc_opera_ids',
    'post_rtc_opera_ids',
    'low_confidence_alert_threshold',
    'high_confidence_alert_threshold',
    'model_source',
]
REQUIRED_PRODUCT_TAGS = PRODUCT_TAGS_FOR_EQUALITY + ['version']


class ProductNameData(BaseModel):
    mgrs_tile_id: str = Field(description='MGRS (Military Grid Reference System) tile identifier')
    acq_date_time: datetime = Field(description='Acquisition datetime of the Sentinel-1 data')
    processing_date_time: datetime = Field(description='Processing datetime when the product was generated')

    def __str__(self) -> str:
        tokens = [
            'OPERA',
            'L3',
            'DIST-ALERT-S1',
            f'T{self.mgrs_tile_id}',
            self.acq_date_time.strftime('%Y%m%dT%H%M%SZ'),
            self.processing_date_time.strftime('%Y%m%dT%H%M%SZ'),
            'S1',
            '30',
            f'v{PRODUCT_VERSION}',
        ]
        return '_'.join(tokens)

    def name(self) -> str:
        return f'{self}'

    @classmethod
    def validate_product_name(cls, product_name: str) -> bool:
        """
        Validate if a string matches the OPERA L3 DIST-ALERT-S1 product name format.

        Expected format:
        OPERA_L3_DIST-ALERT-S1_T{mgrs_tile_id}_{acq_datetime}_{proc_datetime}_S1_30_v{version}
        """
        tokens = product_name.split('_')

        # Check if we have the correct number of tokens first
        if len(tokens) != 9:
            return False

        conditions = [
            tokens[0] != 'OPERA',
            tokens[1] != 'L3',
            tokens[2] != 'DIST-ALERT-S1',
            not tokens[3].startswith('T'),  # MGRS tile ID
            tokens[6] != 'S1',
            tokens[7] != '30',
            not tokens[8].startswith('v'),  # Version
        ]

        # If any condition is True, validation fails
        if any(conditions):
            return False

        # Validate datetime formats
        datetime.strptime(tokens[4], '%Y%m%dT%H%M%SZ')  # Acquisition datetime
        datetime.strptime(tokens[5], '%Y%m%dT%H%M%SZ')  # Processing datetime

        return True


class ProductFileData(BaseModel):
    path: Path

    @classmethod
    def from_product_path(cls, product_path: str) -> 'ProductFileData':
        """Instantiate from a file path."""
        return cls(path=product_path)

    def compare(
        self, other: 'ProductFileData', rtol: float = 1e-05, atol: float = 1e-08, equal_nan: bool = True
    ) -> tuple[bool, str]:
        """Compare two GeoTIFF files for equality.

        Parameters
        ----------
        other : ProductFileData
            GeoTIFF file to compare against.
        rtol : float, optional
            Relative tolerance for numpy.allclose, default 1e-05.
        atol : float, optional
            Absolute tolerance for numpy.allclose, default 1e-08.
        equal_nan : bool, optional
            Whether NaN values should be considered equal, default True.

        Returns
        -------
        tuple (bool, str)
            - True if the files match, False otherwise.
            - A message describing differences if files do not match.
        """
        # Check if both files exist
        if not self.path.exists():
            return False, f'File not found: {self.path}'
        if not other.path.exists():
            return False, f'File not found: {other.path}'

        with rasterio.open(self.path) as src_self, rasterio.open(other.path) as src_other:
            # Compare image dimensions
            if src_self.shape != src_other.shape:
                return False, f'Shape mismatch: {src_self.shape} != {src_other.shape}'

            # Read raster data
            data_self = src_self.read()
            data_other = src_other.read()

            # Find pixel mismatches
            diff_mask = ~np.isclose(data_self, data_other, rtol=rtol, atol=atol, equal_nan=equal_nan)
            mismatch_count = np.sum(diff_mask)

            if mismatch_count > 0:
                max_diff = np.max(np.abs(data_self - data_other))
                min_diff = np.min(np.abs(data_self - data_other))
                return False, (
                    f'Pixel mismatch count: {mismatch_count}\nMax difference: {max_diff}\nMin difference: {min_diff}'
                )

            # Compare metadata (tags)
            tags_self = src_self.tags()
            tags_other = src_other.tags()
            mismatched_tags = {
                key: (tags_self[key], tags_other[key])
                for key in tags_self.keys() & tags_other.keys()
                if tags_self[key] != tags_other[key]
            }

            if mismatched_tags:
                return False, f'Metadata mismatch in tags: {mismatched_tags}'

        return True, 'Files match perfectly.'


class DistS1ProductDirectory(BaseModel):
    product_name: str
    dst_dir: Path | str
    tif_layer_dtypes: ClassVar[dict[str, str]] = dict(TIF_LAYER_DTYPES)

    @property
    def product_dir_path(self) -> Path:
        path = self.dst_dir / self.product_name
        return path

    def __str__(self) -> str:
        return str(self.product_dir_path)

    @field_validator('product_name')
    def validate_product_name(cls, product_name: str) -> str:
        if not ProductNameData.validate_product_name(product_name):
            raise ValueError(f'Invalid product name: {product_name}; should match: {EXPECTED_FORMAT_STRING}')
        return product_name

    @field_validator('dst_dir')
    def validate_dst_dir(cls, dst_dir: Path | str) -> Path:
        return Path(dst_dir)

    @model_validator(mode='after')
    def validate_product_directory(self) -> Path:
        product_dir = self.product_dir_path
        if product_dir.exists() and not product_dir.is_dir():
            raise ValueError(f'Path {product_dir} exists but is not a directory')
        if not product_dir.exists():
            product_dir.mkdir(parents=True, exist_ok=True)
        return self

    @property
    def layers(self) -> list[str]:
        return list(TIF_LAYERS)

    @property
    def layer_path_dict(self) -> dict[str, Path]:
        layer_dict = {layer: self.product_dir_path / f'{self.product_name}_{layer}.tif' for layer in self.layers}
        layer_dict['browse'] = self.product_dir_path / f'{self.product_name}.png'
        return layer_dict

    @property
    def acq_datetime(self) -> datetime:
        return get_acquisition_datetime(self.product_dir_path)

    def validate_layer_paths(self) -> bool:
        failed_layers = []
        for layer, path in self.layer_path_dict.items():
            if layer not in TIF_LAYERS:
                continue
            if not path.exists():
                warn(f'Layer {layer} does not exist at path: {path}', UserWarning)
                failed_layers.append(layer)
        return len(failed_layers) == 0

    def validate_tif_layer_dtypes(self) -> bool:
        failed_layers = []
        for layer, path in self.layer_path_dict.items():
            if layer not in TIF_LAYERS:
                continue
            if path.suffix == '.tif':
                with rasterio.open(path) as src:
                    if src.dtypes[0] != TIF_LAYER_DTYPES[layer]:
                        warn(
                            f'Layer {layer} has incorrect dtype: {src.dtypes[0]}; should be: {TIF_LAYER_DTYPES[layer]}',
                            UserWarning,
                        )
                        failed_layers.append(layer)
        return len(failed_layers) == 0

    def __eq__(
        self, other: 'DistS1ProductDirectory', *, rtol: float = 1e-05, atol: float = 1e-05, equal_nan: bool = True
    ) -> bool:
        """Compare two ProductDirectoryData instances for equality.

        Checks that:
        1. The MGRS tile IDs match
        2. The acquisition datetimes match
        3. All TIF layers have numerically close data using numpy.allclose

        Parameters
        ----------
        other : ProductDirectoryData
            The other instance to compare against
        rtol : float, optional
            Relative tolerance for numpy.allclose, by default 1e-05
        atol : float, optional
            Absolute tolerance for numpy.allclose, by default 1e-08
        equal_nan : bool, optional
            Whether to compare NaN's as equal, by default True

        Returns
        -------
        bool
            True if the instances are considered equal, False otherwise
        """
        import numpy as np

        # Parse product names to get MGRS tile ID and acquisition datetime
        tokens_self = self.product_name.split('_')
        tokens_other = other.product_name.split('_')

        equality = True

        # Compare MGRS tile IDs
        mgrs_self = tokens_self[3][1:]  # Remove 'T' prefix
        mgrs_other = tokens_other[3][1:]
        if mgrs_self != mgrs_other:
            warn(f'MGRS tile IDs do not match: {mgrs_self} != {mgrs_other}', UserWarning)
            equality = False

        # Compare acquisition datetimes
        acq_dt_self = datetime.strptime(tokens_self[4], '%Y%m%dT%H%M%SZ')
        acq_dt_other = datetime.strptime(tokens_other[4], '%Y%m%dT%H%M%SZ')
        if acq_dt_self != acq_dt_other:
            warn(f'Acquisition datetimes do not match: {acq_dt_self} != {acq_dt_other}', UserWarning)
            equality = False

        # Compare TIF layer data
        unequal_layers = []
        for layer in self.layers:
            path_self = self.layer_path_dict[layer]
            path_other = other.layer_path_dict[layer]

            with rasterio.open(path_self) as src_self, rasterio.open(path_other) as src_other:
                data_self = src_self.read()
                data_other = src_other.read()
                if not np.allclose(data_self, data_other, rtol=rtol, atol=atol, equal_nan=equal_nan):
                    warn(f'Layer {layer} arrays do not match', UserWarning)
                    unequal_layers.append(layer)
                    equality = False

                tags_self = src_self.tags()
                tags_other = src_other.tags()
                keys_self = tags_self.keys()
                keys_other = tags_other.keys()
                missing_tag_keys_self = [key for key in REQUIRED_PRODUCT_TAGS if key not in keys_self]
                if missing_tag_keys_self:
                    warn(
                        f'Layer {layer} is missing required tags in left product: {",".join(missing_tag_keys_self)}',
                        UserWarning,
                    )
                    equality = False
                missing_tag_keys_other = [key for key in REQUIRED_PRODUCT_TAGS if key not in keys_other]
                if missing_tag_keys_other:
                    warn(
                        f'Layer {layer} is missing required tags in right product: {",".join(missing_tag_keys_other)}',
                        UserWarning,
                    )
                    equality = False
                for key in PRODUCT_TAGS_FOR_EQUALITY:
                    if tags_self[key] != tags_other[key]:
                        warn(f'Layer {layer} metadata value for key {key} do not match', UserWarning)
                        equality = False

        return equality

    @classmethod
    def from_product_path(cls, product_dir_path: Path | str) -> 'DistS1ProductDirectory':
        """Create a ProductDirectoryData instance from an existing product directory path.

        Parameters
        ----------
        product_dir_path : Path or str
            Path to an existing DIST-ALERT-S1 product directory

        Returns
        -------
        ProductDirectoryData
            Instance of ProductDirectoryData initialized from the directory

        Raises
        ------
        ValueError
            If product directory is invalid or missing required files/layers
        """
        product_dir_path = Path(product_dir_path)
        if not product_dir_path.exists() or not product_dir_path.is_dir():
            raise ValueError(f'Product directory does not exist or is not a directory: {product_dir_path}')

        product_name = product_dir_path.name
        if not ProductNameData.validate_product_name(product_name):
            raise ValueError(f'Invalid product name: {product_name}')

        obj = cls(product_name=product_name, dst_dir=product_dir_path.parent)

        # Validate all layers exist and have correct dtypes
        if not obj.validate_layer_paths():
            raise ValueError(f'Product directory missing required layers: {product_dir_path}')
        if not obj.validate_tif_layer_dtypes():
            raise ValueError(f'Product directory contains layers with incorrect dtypes: {product_dir_path}')

        return obj

    @classmethod
    def generate_product_path_with_placeholders(
        cls,
        mgrs_tile_id: str,
        acq_datetime: datetime,
        dst_dir: Path | str,
        water_mask_path: Path | str | None = None,
        overwrite: bool = False,
    ) -> 'DistS1ProductDirectory':
        """Generate a product directory with placeholder GeoTIFF files containing zeros.

        Parameters
        ----------
        mgrs_tile_id : str
            MGRS tile ID for the product
        acq_datetime : datetime
            Acquisition datetime for the product
        dst_dir : Path | str
            Directory where the product will be created
        water_mask_path : Path | str | None, optional
            Path to water mask file. If provided, water mask will be validated and applied to all layers.
            If None, no water mask is applied.
        overwrite : bool, optional
            If True, overwrite existing files. If False, skip if files exist.

        Returns
        -------
        ProductDirectoryData
            Instance of ProductDirectoryData with generated placeholder files

        Raises
        ------
        FileNotFoundError
            If water_mask_path is provided but the file doesn't exist
        ValueError
            If product name validation fails, water mask doesn't cover the MGRS tile, or water mask application fails
        """
        # Create processing datetime (current time)
        processing_datetime = datetime.now()

        # Create product name data
        product_name_data = ProductNameData(
            mgrs_tile_id=mgrs_tile_id, acq_date_time=acq_datetime, processing_date_time=processing_datetime
        )

        # Create product directory data
        product_dir_data = cls(product_name=str(product_name_data), dst_dir=dst_dir)

        # Validate water mask if provided
        if water_mask_path is not None:
            water_mask_path = Path(water_mask_path)
            if not water_mask_path.exists():
                raise FileNotFoundError(f'Water mask file does not exist: {water_mask_path}')

        # Create placeholder arrays for each layer
        for layer_name in TIF_LAYERS:
            layer_path = product_dir_data.layer_path_dict[layer_name]

            # Skip if file exists and overwrite is False
            if layer_path.exists() and not overwrite:
                continue

            # Get dtype for this layer
            dtype_str = cls.tif_layer_dtypes[layer_name]
            dtype = np.dtype(dtype_str)

            # Set nodata value based on dtype
            if np.issubdtype(dtype, np.floating):
                nodata_value = np.nan
            else:
                nodata_value = 255

            # Get MGRS profile for the tile with correct dtype and nodata
            mgrs_profile = get_mgrs_profile(mgrs_tile_id, dtype=dtype, nodata=nodata_value)

            # Create zero array with correct shape and dtype
            height = mgrs_profile['height']
            width = mgrs_profile['width']
            zero_array = np.zeros((height, width), dtype=dtype)

            # Apply water mask if provided
            if water_mask_path is not None:
                zero_array = apply_water_mask(zero_array, mgrs_profile, water_mask_path)

            # Write the GeoTIFF file
            with rasterio.open(layer_path, 'w', **mgrs_profile) as dst:
                dst.write(zero_array, 1)

        return product_dir_data
