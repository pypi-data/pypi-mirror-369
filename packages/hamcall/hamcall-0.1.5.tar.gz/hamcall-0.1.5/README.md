# About

The `hamcall` package and command line utility is designed for
ingesting and searching amateur radio callsign databases.  Right now
it only supports data from the US FCC ULS database, however.

# Installation

    pip install hamcall

# Usage

## Initializing the database

    $ hamcall -I

## Loading the database

Grab the weekly amateur license database snapshots (not the
application snapshot) from the [FCC Database] webpage, and unzip it
into a DIRECTORY.  Then load the data from that directory:

    $ Hamcall -L DIRECTORY

## Searching the database

Looking up Joe Walsh's callsign:

    $ hamcall WB6ACU
    WB6ACU:
      Id                  : 893189
      Callsign            : WB6ACU
      Class               : E
      Last name           : WALSH
      First name          : JOSEPH
      Address             : 1501 Summitridge Dr
      City                : Beverly Hills
      State               : CA
      Zip code            : 90210

You can also search by last name:

    $ hamcall -l walsh
    [this will return a lot of entries]

[FCC Database]: https://www.fcc.gov/uls/transactions/daily-weekly
