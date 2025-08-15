"""
Set up a catalog for NOAA CO-OPS assets.
"""

from typing import Union

from intake.readers.readers import BaseReader
from intake.readers.entry import Catalog, DataDescription

from .coops import COOPSDataframeReader, COOPSXarrayReader


class COOPSCatalogReader(BaseReader):
    """
    Makes data readers out of all datasets for a given AXDS data type.

    Have this cover all data types for now, then split out.
    """

    name = "coops_cat"
    output_instance = "intake.readers.entry:Catalog"

    def __init__(
        self,
        station_list,
        # verbose: bool = False,
        process_adcp: Union[str,bool] = False,
        name: str = "catalog",
        description: str = "Catalog of NOAA CO-OPS assets.",
        metadata: dict = None,
        include_reader_metadata: bool = True,
        # ttl: int = 86400,
        **kwargs,
    ):
        """Initialize a NOAA CO-OPS Catalog.

        Parameters
        ----------
        process_adcp: str, bool

            * "process_uv": process adcp to include `u`/`v` in dataset
            * "process_along": process adcp to include `u`/`v` and `ualong`/`vacross` in dataset
            * "process_subtidal": process adcp to include `u`/`v`, `ualong`/`vacross`, and `ualong_subtidal`/`vacross_subtidal` in dataset
            * True is equivalent to "process_subtidal"

        verbose : bool, optional
            Set to True for helpful information.
        ttl : int, optional
            Time to live for catalog (in seconds). How long before force-reloading catalog. Set to None to not do this. Currently default is set to a large number because the available version of intake does not have a change to accept None.
        name : str, optional
            Name for catalog.
        description : str, optional
            Description for catalog.
        metadata : dict, optional
            Metadata for catalog.
        kwargs:
            Other input arguments are passed to the intake Catalog class. They can includegetenv, getshell, persist_mode, storage_options, and user_parameters, in addition to some that are surfaced directly in this class.
        """

        self.station_list = station_list
        self.include_reader_metadata = include_reader_metadata
        self._process_adcp = process_adcp

        # Put together catalog-level stuff
        metadata = metadata or {}
        # metadata["station_list"] = self.station_list
        
        super(COOPSCatalogReader, self).__init__(
            metadata=metadata,
        )
        # self.name = name
        # self.metadata = metadata
        
    def read(self):
        """Find all dataset ids and create catalog."""

        plugin = "intake_coops.coops:COOPSXarrayReader"

        entries, aliases = {}, {}

        for station_id in self.station_list:
            args = {
                "stationid": station_id,
                "process_adcp": self._process_adcp,
            }

            if self.include_reader_metadata:
                metadata = COOPSDataframeReader(station_id)._get_dataset_metadata(station_id)
            else:
                metadata = {}

            entries[station_id] = DataDescription(
                plugin,
                kwargs={**args},
                metadata=metadata,
            )
            aliases[station_id] = station_id

        cat = Catalog(
            data=entries,
            aliases=aliases,
        )
        return cat
