"""
Reader for CO-OPS data.
"""

from typing import Optional
import cf_pandas  # noqa: F401
import cf_xarray  # noqa: F401
import noaa_coops as nc
import numpy as np
import pandas as pd
import xarray as xr

from intake.readers.readers import BaseReader


class COOPSDataframeReader(BaseReader):
    """
    Parameters
    ----------
    stationid : str
        CO-OPS station id.

    Returns
    -------
    Dataframe
    """

    output_instance = "pandas:DataFrame"

    def _read(self, stationid: str):
        """How to load in a specific station once you know it by dataset_id"""
    
        # s = nc.Station(stationid)
        s = self._return_station_object(stationid)

        begin_date = pd.Timestamp(s.deployed).strftime("%Y%m%d")
        end_date = pd.Timestamp(s.retrieved).strftime("%Y%m%d")

        dfs = []
        for bin in s.bins["bins"]:
            depth = bin["depth"]
            num = bin["num"]
            dft = s.get_data(
                begin_date=begin_date,
                end_date=end_date,
                product="currents",
                bin_num=num,
            )
            dft["depth"] = depth
            dfs.append(dft)
        return pd.concat(dfs)
    
    def _return_station_object(self, stationid: str):
        """Return station object."""
        return nc.Station(stationid)

    def _get_dataset_metadata(self, stationid: str):
        """Load metadata once data is loaded."""
        # self._load()
        # metadata = {}
        s = self._return_station_object(stationid)
        # metadata = s.deployments
        # metadata.update(s.lat_lon)
        # metadata.update(
        #     {
        #         "name": s.name,
        #         "observe_dst": s.observe_dst,
        #         "project": s.project,
        #         "project_type": s.project_type,
        #         "timezone_offset": s.timezone_offset,
        #         "units": s.units,
        #     }
        # )
        # import pdb; pdb.set_trace()
        # if moremetadata:
        #     metadata.update(s.metadata)
        return s.metadata


class COOPSXarrayReader(COOPSDataframeReader):
    """Converts returned DataFrame into Dataset

    which for ADCP data is more appropriate.

    Returns
    -------
    Dataset
    """

    output_instance = "xarray:Dataset"

    def _read(self, stationid, process_adcp: Union[str,bool] = False):#, metadata_in: Optional[dict] = None):
        """Read as DataFrame but convert to Dataset."""
        # metadata_in = metadata_in or {}

        reader = COOPSDataframeReader(stationid)

        df = reader.read()
        
        inds = [df.cf["T"].name, df.cf["Z"].name]

        ds = (
            df.reset_index()
            .set_index(inds)
            .sort_index()
            .pivot_table(index=inds)
            .to_xarray()
        )
        ds["t"].attrs = {"standard_name": "time"}
        ds["depth"].attrs = {
            "standard_name": "depth",
            "axis": "Z",
        }
        metadata = self._get_dataset_metadata(stationid)

        ds["longitude"] = metadata["lng"]
        ds["longitude"].attrs = {"standard_name": "longitude"}
        ds["latitude"] = metadata["lat"]
        ds["latitude"].attrs = {"standard_name": "latitude"}
        ds = ds.assign_coords(
            {"longitude": ds["longitude"], "latitude": ds["latitude"]}
        )

        if process_adcp:
            ds = self.process_adcp(metadata, ds, process_adcp)
        
        return ds

    def process_adcp(self, metadata, ds, process_adcp):
        """Process ADCP data.

        Parameters
        ----------
        process_adcp: str, bool

            * "process_uv": process adcp to include `u`/`v` in dataset
            * "process_along": process adcp to include `u`/`v` and `ualong`/`vacross` in dataset
            * "process_subtidal": process adcp to include `u`/`v`, `ualong`/`vacross`, and `ualong_subtidal`/`vacross_subtidal` in dataset
            * True is equivalent to "process_subtidal"

        Returns
        -------
        Dataset
            With u and v, ualong and vacross, and subtidal versions ualong_subtidal, vacross_subtidal
        """

        if process_adcp == True:
            process_adcp = "process_subtidal"

        if process_adcp in ["process_uv", "process_along", "process_subtidal"]:
            ds["u"] = (
                np.cos(np.deg2rad(ds.cf["dir"])) * ds.cf["speed"] / 100
            )
            ds["v"] = (
                np.sin(np.deg2rad(ds.cf["dir"])) * ds.cf["speed"] / 100
            )
            ds["s"] /= 100
            ds["s"].attrs = {"standard_name": "sea_water_speed", "units": "m s-1"}
            ds["d"].attrs = {
                "standard_name": "sea_water_velocity_to_direction",
                "units": "degree",
            }
            ds["u"].attrs = {
                "standard_name": "eastward_sea_water_velocity",
                "units": "m s-1",
            }
            ds["v"].attrs = {
                "standard_name": "northward_sea_water_velocity",
                "units": "m s-1",
            }

        if process_adcp in ["process_along", "process_subtidal"]:
            theta = metadata["deployments"]["flood_direction_degrees"]
            ds["ualong"] = ds["u"] * np.cos(np.deg2rad(theta)) + ds[
                "v"
            ] * np.sin(np.deg2rad(theta))
            ds["vacross"] = -ds["u"] * np.sin(np.deg2rad(theta)) + ds[
                "v"
            ] * np.cos(np.deg2rad(theta))
            ds["ualong"].attrs = {
                "Long name": "Along channel velocity",
                "units": "m s-1",
            }
            ds["vacross"].attrs = {
                "Long name": "Across channel velocity",
                "units": "m s-1",
            }

        if process_adcp == "process_subtidal":
            # calculate subtidal velocities
            ds["ualong_subtidal"] = tidal_filter(ds["ualong"])
            ds["vacross_subtidal"] = tidal_filter(ds["vacross"])
        
        return ds


class plfilt(object):
    """
    pl33 filter class, to remove tides and inertial motions from timeseries

    Examples
    --------

    >>> pl33 = plfilt(dt=4.0)   # 33 hr filter

    >>> pl33d = plfilt(dt=4.0, cutoff_period=72.0)  # 3 day filter

    dt is the time resolution of the timeseries to be filtered in hours.  Default dt=1
    cutoff_period defines the timescales to low pass filter. Default cutoff_period=33.0
    Calling the class instance can have two forms:

    >>> uf = pl33(u)   # returns a filtered timeseries, uf.  Half the filter length is
                       # removed from each end of the timeseries

    >>> uf, tf = pl33(u, t)  # returns a filtered timeseries, uf, plus a new time
                             # variable over the valid range of the filtered timeseries.

    Notes
    -----
    Taken from Rob Hetland's octant package.
    """

    _pl33 = np.array(
        [
            -0.00027,
            -0.00114,
            -0.00211,
            -0.00317,
            -0.00427,
            -0.00537,
            -0.00641,
            -0.00735,
            -0.00811,
            -0.00864,
            -0.00887,
            -0.00872,
            -0.00816,
            -0.00714,
            -0.0056,
            -0.00355,
            -0.00097,
            0.00213,
            0.00574,
            0.0098,
            0.01425,
            0.01902,
            0.024,
            0.02911,
            0.03423,
            0.03923,
            0.04399,
            0.04842,
            0.05237,
            0.05576,
            0.0585,
            0.06051,
            0.06174,
            0.06215,
            0.06174,
            0.06051,
            0.0585,
            0.05576,
            0.05237,
            0.04842,
            0.04399,
            0.03923,
            0.03423,
            0.02911,
            0.024,
            0.01902,
            0.01425,
            0.0098,
            0.00574,
            0.00213,
            -0.00097,
            -0.00355,
            -0.0056,
            -0.00714,
            -0.00816,
            -0.00872,
            -0.00887,
            -0.00864,
            -0.00811,
            -0.00735,
            -0.00641,
            -0.00537,
            -0.00427,
            -0.00317,
            -0.00211,
            -0.00114,
            -0.00027,
        ],
        dtype="d",
    )

    _dt = np.linspace(-33, 33, 67)

    def __init__(self, dt=1.0, cutoff_period=33.0):
        """Initialize."""

        if np.isscalar(dt):
            self.dt = float(dt) * (33.0 / cutoff_period)
        else:
            self.dt = np.diff(dt).mean() * (33.0 / cutoff_period)

        filter_time = np.arange(0.0, 33.0, self.dt, dtype="d")
        self.Nt = len(filter_time)
        self.filter_time = np.hstack((-filter_time[-1:0:-1], filter_time))

        self.pl33 = np.interp(self.filter_time, self._dt, self._pl33)
        self.pl33 /= self.pl33.sum()

    def __call__(self, u, t=None, mode="valid"):
        """Do the filtering."""
        uf = np.convolve(u, self.pl33, mode=mode)
        if t is None:
            return uf
        else:
            tf = t[self.Nt - 1 : -self.Nt + 1]
            return uf, tf


def tidal_filter(da_to_filter):
    """Filter DataArray for tides."""

    tkey, zkey = da_to_filter.dims

    # set up tidal filter
    dt = da_to_filter[tkey][1] - da_to_filter[tkey][0]
    dt = float(dt / 1e9) / 3600  # convert nanoseconds to hours
    pl33 = plfilt(dt=dt)

    ufiltered = []
    # loop over depths
    for depth in da_to_filter[zkey]:
        # can't have any nan's, so fill signal first
        u_in = da_to_filter.sel(depth=depth).interpolate_na(dim=tkey, method="linear")
        ufiltered_out, t_out = pl33(u_in, da_to_filter[tkey])
        ufiltered.append(ufiltered_out)

    ufiltered = np.asarray(ufiltered).T
    attrs = {
        key: f"{value}, subtidal"
        for key, value in da_to_filter.attrs.items()
        if key != "units"
    }
    u = xr.full_like(da_to_filter, np.nan)
    u[pl33.Nt - 1 : -pl33.Nt + 1, :] = ufiltered
    u.attrs = attrs
    return u
