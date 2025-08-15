from setuptools import setup


setup(
    use_scm_version={
        "write_to": "intake_coops/_version.py",
        "write_to_template": '__version__ = "{version}"',
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
    entry_points={
        "intake.drivers": [
            "coops-dataframe = intake_coops.coops:COOPSDataframeReader",
            "coops-xarray = intake_coops.coops:COOPSXarrayReader",
            "coops_cat = intake_coops.coops_cat:COOPSCatalogReader",
        ]
    },
)
