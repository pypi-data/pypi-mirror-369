"""
Module that adds the policy scenarios from ELEVATE to xr_total
"""

# =========================================================== #
# PREAMBULE
# Put in packages that we need
# =========================================================== #

import logging
from pathlib import Path

import country_converter as coco
import numpy as np
import pandas as pd
import pooch
import xarray as xr

from effortsharing.config import Config

# Configure the logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# =========================================================== #
# CLASS OBJECT
# =========================================================== #


class policyscenadding(object):
    """
    Class that adds the policy scenarios from ELEVATE to xr_total
    """

    # =========================================================== #
    # =========================================================== #

    def __init__(self, config: Config):
        logger.info("Initializing policyscenadding class")

        self.current_dir = Path.cwd()
        self.xr_total_co2 = None

        # Scenario names
        self.scenarios = {
            "ELV-SSP2-CP-D0": "CurPol",
            "ELV-SSP2-CP-D0-N": "CurPol",
            "Current Policies": "CurPol",
            "ELV-SSP2-NDC-D0": "NDC",
            "ELV-SSP2-LTS": "NetZero",
        }

        # Read in Input YAML file
        self.config = config
        self.xr_total = xr.open_dataset(
            self.config.paths.output / f'startyear_{config.params.start_year_analysis}' / "xr_dataread.nc"
        )

    # =========================================================== #
    # =========================================================== #

    def read_filter_scenario_data(self):
        """
        Read in the ELEVATE data and filter for relevant scenarios and variables.
        Data can be downloaded from: https://zenodo.org/records/15114066
        """
        logger.info("Reading and filtering ELEVATE scenario data")

        # Read the raw data
        file_path = pooch.retrieve(
            url="https://zenodo.org/records/15478922/files/Data_D2.3_vetted_20250519.csv?download=1",
            known_hash="SHA256:77f01ccde860860320a6d4e2cb7449848bb3a5c043e6e576628f7fa3a7cbdcf6",
            fname="Data_D2.3_vetted_20250519.csv",
        )

        df_scenarios_raw = pd.read_csv(
            file_path,
            header=0,
        )

        # Filter for scenarios and variables
        variables = ["Emissions|Kyoto Gases", "Emissions|CO2"]

        df_scenarios_filtered = df_scenarios_raw[
            df_scenarios_raw.Scenario.isin(self.scenarios.keys())
            & df_scenarios_raw.Variable.isin(variables)
        ].copy()
        df_scenarios_filtered = df_scenarios_filtered.reset_index(drop=True)

        return df_scenarios_filtered

    def rename_and_preprocess(self, df_scenarios_filtered):
        """
        Rename columns, regions and scenarios
        """
        logger.info("Renaming columns, regions and scenarios")

        # Rename columns: Remove leading 'X' from year columns
        df_scenarios_filtered.columns = [
            col[1:] if col.startswith("X") and col[1:].isdigit() else col
            for col in df_scenarios_filtered.columns
        ]

        # Rename scenarios
        df_scenarios_filtered["Scenario"] = df_scenarios_filtered["Scenario"].replace(
            self.scenarios
        )

        # Rename regions
        region_mapping = {
            "World": "EARTH",
            "United States of America": "USA",
            "South-East Asia": "Southeast Asia",
            "South East Asia": "Southeast Asia",
            "European Union": "EU",
        }
        df_scenarios_filtered["Region"] = df_scenarios_filtered["Region"].replace(region_mapping)

        df_scenarios_renamed = df_scenarios_filtered.copy()

        return df_scenarios_renamed

    # =========================================================== #
    # =========================================================== #

    def deduplicate_regions(self, df_scenarios_renamed):
        """
        Some regions are written as model|region, some only as region. Models often reported
        both versions, but these are often duplicates and need to be removed.
        More info on the AR9 and AR10 regions here:
        https://github.com/IAMconsortium/common-definitions/blob/main/definitions/region/common.yaml
        """
        logger.info("Deduplicating regions")

        # Split the region column by '|' and expand into new columns
        split_columns = df_scenarios_renamed["Region"].str.split("|", expand=True)

        # To check if regions are already cleaned up or not:
        if split_columns.shape[1] == 2:
            split_columns.columns = ["Model_2", "Region_2"]
            # Add the new columns to the original DataFrame
            df_scenarios_renamed = pd.concat([df_scenarios_renamed, split_columns], axis=1)

            # If a region was Model|Region, we don't need the model name twice so replace with NaN
            df_scenarios_renamed["Model_2"] = np.where(
                df_scenarios_renamed["Model_2"] == df_scenarios_renamed["Model"],
                np.nan,
                df_scenarios_renamed["Model_2"],
            )

            # Merge the data on region into a new column 'Region_cleaned'
            df_scenarios_renamed["Region_cleaned"] = df_scenarios_renamed["Model_2"].combine_first(
                df_scenarios_renamed["Region_2"]
            )

            # Drop helper columns and reorder the DataFrame
            df_scenarios_renamed.drop(columns=["Model_2", "Region_2", "Region"], inplace=True)
            df_scenarios_renamed = df_scenarios_renamed.rename(columns={"Region_cleaned": "Region"})
        elif split_columns.shape[1] == 1:
            # Only one column, region format seems fine so no action needed
            pass
        else:
            raise ValueError(
                f"Unexpected number of columns after splitting 'Region': {split_columns.shape[1]}. "
                "Expected {region} or {model}|{region} so 1 or 2 columns after splitting. "
                "Check the format of the 'Region' column."
            )

        # Sort the dataframe by 'Region' and reset the index
        # Sorting it to give preference to e.g. "India" over "India (AR10)"
        df_scenarios_renamed.sort_values(by=["Region"], inplace=True)
        df_scenarios_renamed.reset_index(drop=True, inplace=True)

        # TODO figure out why some duplicates are not the same, maybe problems from modelling teams?
        # For now this keeps the first duplicate and removes the rest
        df_scenarios_deduplicated = df_scenarios_renamed.groupby(
            ["Model", "Scenario", "Variable", "Region"], as_index=True
        ).first()

        # Removing columns from index
        df_scenarios_deduplicated.reset_index(inplace=True)

        # Convert countries to ISO3 codes only if "R10" is not in the column
        logger.info("Converting country names to ISO3 codes")
        cc = coco.CountryConverter()

        def conditional_convert(region):
            if "R10" in region:
                return region  # Keep the original value if "R10" is present
            return cc.convert(names=region, to="ISO3", not_found=None)

        # Apply the conditional conversion to the 'Region' column
        df_scenarios_deduplicated["Region"] = df_scenarios_deduplicated["Region"].apply(
            conditional_convert
        )

        # Take the lists in "Region" and convert them to text divided by comma
        df_scenarios_deduplicated["Region"] = df_scenarios_deduplicated["Region"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else x
        )

        # Reorder the columns
        columns_to_keep = [
            "Model",
            "Scenario",
            "Region",
            "Variable",
            "Unit",
        ] + [col for col in df_scenarios_deduplicated.columns if col.isdigit()]
        df_scenarios_deduplicated = df_scenarios_deduplicated[columns_to_keep]

        return df_scenarios_deduplicated

    def format_to_xarray(self, df_co2_or_kyoto):
        """
        Convert a DataFrame to an xarray object
        """
        logger.info("Converting DataFrame to xarray objects")

        # Melt the DataFrame to long format
        df_melted = df_co2_or_kyoto.melt(
            id_vars=["Scenario", "Model", "Region"],
            var_name="Time",
            value_name="Value",
        )

        # Convert the 'Time' column to integers
        df_melted["Time"] = np.array(df_melted["Time"].astype(int))

        # Interpolate missing years for each scenario, model, and region
        logger.info("Interpolating missing years")

        years_full = np.arange(1850, 2101)

        def interpolate_group(group):
            group = group.dropna(subset=["Value"])
            if group.empty:
                # If all values are missing, return empty DataFrame
                return pd.DataFrame(columns=group.columns)
            return pd.DataFrame(
                {
                    "Scenario": group["Scenario"].iloc[0],
                    "Model": group["Model"].iloc[0],
                    "Region": group["Region"].iloc[0],
                    "Time": years_full,
                    "Value": np.interp(years_full, group["Time"], group["Value"]),
                }
            )

        df_interp = (
            df_melted.groupby(["Scenario", "Model", "Region"], as_index=False)
            .apply(interpolate_group)
            .reset_index(drop=True)
        )

        # Set the index for the xarray object
        df_interp.set_index(["Scenario", "Model", "Region", "Time"], inplace=True)

        # TODO Do we want to drop duplicates here? Or keep all empty years?
        # df_interp = df_interp.drop_duplicates()

        # Convert to xarray Dataset
        xr_dataset = xr.Dataset.from_dataframe(df_interp)

        return xr_dataset

    def filter_and_convert(self, df_scenarios_deduplicated):
        """
        Split the dataframe into co2 and kyoto gas and convert to xarray objects
        """
        logger.info("Splitting and converting DataFrame to xarray objects")

        # Split df_scenarios_deduplicated into two DataFrames
        df_scenarios_co2 = df_scenarios_deduplicated[
            df_scenarios_deduplicated["Variable"] == "Emissions|CO2"
        ].copy()
        df_scenarios_kyoto = df_scenarios_deduplicated[
            df_scenarios_deduplicated["Variable"] == "Emissions|Kyoto Gases"
        ].copy()

        # Drop the 'Variable' column from both DataFrames
        df_scenarios_co2.drop(columns=["Variable", "Unit"], inplace=True)
        df_scenarios_kyoto.drop(columns=["Variable", "Unit"], inplace=True)
        df_scenarios_co2.reset_index(drop=True, inplace=True)
        df_scenarios_kyoto.reset_index(drop=True, inplace=True)

        # Convert to xarray objects
        xr_kyoto = self.format_to_xarray(df_scenarios_kyoto)
        xr_co2 = self.format_to_xarray(df_scenarios_co2) if not df_scenarios_co2.empty else None

        return xr_kyoto, xr_co2

    # =========================================================== #
    # =========================================================== #

    def add_to_xr(self, xr_kyoto, xr_co2):
        """'
        Add the policy scenarios to the xarray object'
        """
        logger.info("Adding policy scenarios to xarray object")

        # Kyoto gas/GHG version
        xr_total = self.xr_total.assign(NDC=xr_kyoto["Value"].sel(Scenario="NDC"))
        xr_total = xr_total.assign(CurPol=xr_kyoto["Value"].sel(Scenario="CurPol"))
        xr_total = xr_total.assign(NetZero=xr_kyoto["Value"].sel(Scenario="NetZero"))
        xr_total = xr_total.reindex(Time=np.arange(1850, 2101))
        self.xr_total = xr_total.interpolate_na(dim="Time", method="linear")
        xr_total_onlyalloc = self.xr_total[["NDC", "CurPol", "NetZero"]]
        xr_total_onlyalloc.to_netcdf(
            self.config.paths.output / "xr_policyscen.nc"
        )

        # CO2 version (not all datasets have CO2 data)
        if xr_co2 is not None:
            xr_total2 = self.xr_total.assign(NDC=xr_co2["Value"].sel(Scenario="NDC"))
            xr_total2 = xr_total2.assign(CurPol=xr_co2["Value"].sel(Scenario="CurPol"))
            xr_total2 = xr_total2.assign(NetZero=xr_co2["Value"].sel(Scenario="NetZero"))
            xr_total2 = xr_total2.reindex(Time=np.arange(1850, 2101))
            self.xr_total_co2 = xr_total2.interpolate_na(dim="Time", method="linear")
            xr_total_onlyalloc_co2 = self.xr_total_co2[["NDC", "CurPol", "NetZero"]]
            xr_total_onlyalloc_co2.to_netcdf(
                self.config.paths.output / "xr_policyscen_co2.nc"
            )

        self.xr_total.close()

        return xr_total, xr_total_onlyalloc

def policy_scenarios(config: Config):
    policyscen = policyscenadding(config)
    df_filtered = policyscen.read_filter_scenario_data()
    df_renamed = policyscen.rename_and_preprocess(df_filtered)
    df_deduplicated = policyscen.deduplicate_regions(df_renamed)
    xr_kyoto, xr_co2 = policyscen.filter_and_convert(df_deduplicated)
    xr_total, xr_total_onlyalloc = policyscen.add_to_xr(xr_kyoto, xr_co2)
    return xr_total, xr_total_onlyalloc, policyscen.xr_total_co2
