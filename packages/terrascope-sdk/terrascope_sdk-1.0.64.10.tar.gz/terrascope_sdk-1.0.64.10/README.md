# TerraScope SDK

## Description

The TerraScope Platform is a collection of tools to analyze sensor data over space and time. The TerraScope SDK 
(software development kit) is a Python package that simplifies users' interaction with the TerraScope Platform API.

## Installation

[Readme: Installation](https://terrascope.readme.io/docs/installation-1)

## Usage

TerraScope SDK is designed to simplify access to all the [terrascope-api](https://pypi.org/project/terrascope-api/) calls
that are available. Ensure that you have the correct terrascope-api package installed.

Each API uses a client object which requires the following env variables to be set:

```shell
TERRASCOPE_API_HOST=api-papi.qa3.orbitalinsight.io
TERRASCOPE_API_TOKEN=<TerraScope API Token>
TERRASCOPE_TIMEOUT=<Int timeout in seconds> defaults to 60 seconds
```

You will always want to ensure that you have the correct terrascope-sdk version installed. The latest can be found here:
https://pypi.org/project/terrascope-sdk/

To manually build a local version of the terrascope-sdk (for example, if you are making changes and want to test):
1. Update the version specified in the `pyproject.toml` file, e.g. `version = "1.0.6.1"` (must be `pep440`)
2. Execute from the top-level terrascope_sdk folder: `python3 -m build`. If you don't have the `build` package run `pip3 install build`
3. `cd dist/`
4. `pip3 install terrascope_sdk-1.0.6-test-py3-none-any.whl` (this file name may be different based on the version specified)


# CLI Usage #

## Installation ##

1. Pip install terrascope-sdk

```
$ pip install terrascope-sdk
````

If you're a developer working on the CLI itself, you may want to add [extras] in the installation.  This will include aditional packages which are used for building and testing the command line tool:

```
$ pip install 'terrascope-sdk[extras]'
```

2. Set some environment variables (here stashed in a 'source.sh' file).

```
$ cat source.sh
export TERRASCOPE_API_HOST=api-papi.qa3.orbitalinsight.io
export TERRASCOPE_AUTHOR=you@yourdomain.com
export TERRASCOPE_API_ADMIN_TOKEN=<YOUR ADMIN TOKEN>
export TERRASCOPE_API_TOKEN=<YOUR USER TOKEN>

$ source source.sh
```

# Basic usage #

The executible is installed as the `ts` command.  There is a old unix
'ts' command, but it's rarely used by most developers and hopefully
this choice does not create any serious problems with naming
conflicts.

The 'ts' command mirrors the overall structure of Terrascope itself.  The command tree is heirarchical, with groupings of commands.  The `--help` command shows the layout:

```
$ ts --help
Usage: ts [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Command Super-Groups:
  algorithm  'algorithm' super-group
  analysis   'analysis' super-group
  data       'data' super group

Command Groups:
  aoi            'aoi' command group
  credit         'credit' command group
  environment    'environment' command group
  imagery        'imagery' command group
  manifest       'manifest' command group
  permission     'permission' command group
  tasks          'tasks' command group
  toi            'toi' command group
  visualization  'visualization' command group
```

Any command can be used with a abbreviated for, as long as it's
unique.  So, `ts algo` is fine to avoid typing `ts algorithm`, but `ts
a` cannot be disambiguated from `ts analysis` or `ts aoi` commands.

Help is also available for each specific command, e.g. for the `algorithm` command:

```
$ ts algo --help
Usage: ts.py algo [OPTIONS] COMMAND [ARGS]...

  'algorithm' super-group

Options:
  --help  Show this message and exit.

Command Groups:
  computation  Algorithm 'computation' command group
  config       Algorithm 'config' command group
  version      Algorithm 'version' command group

Commands:
  create    Create an algorithm object (no manifest)
  get       Get algorithm info
  register  Create an algorithm, and register it.
  update    Update an existing algorithm with manifest or pricing.
```

Each specific subcommand also has help, e.g. the `ts algo get` subcommand:

```
$ ts alg get --help
Usage: ts.py algo get [OPTIONS]

  Get algorithm info

Options:
  -ia, --algorithm_id TEXT
  -n, --algorithm_name TEXT
  -t, --truncate INTEGER     Truncate columns to this many characters.  Use 0
                             for no truncation.  (36 is the length of a full
                             UUID).
  -v, --verbose
  --help                     Show this message and exit.
```

## Full Command Listing ##

Here is the overall command tree, with comments when it's not self-evident/obvious:

```
ts
`- algorithm           # commands related to TS algorithms
  |--> create          #
  |--> get             #
  |--> register        # create an algorithm, algorithm_version, and (optionally) algorithm_config
  |--> update          # update an existing algorithm by creating a new algo version and (optionally) algo config
  `- computation       # commands related to TS algorithm computations
     |--> create       #
     |--> download     #
     |--> get          #
     `--> run          #
  `- config            # commands related to TS algorithm configs
     |--> create       #
     |--> deactivate   # deactivate (but not delete) a config
     `--> get          #
  `- version           # commands related to TS algorithm versions
     |--> create       #
     |--> deactivate   #
     `--> get          # get algorithm version info (including the manifest)
`- analysis            # commands related to TS analyses
  |--> create          #
  |--> display         # A sort of 'get'++ command that lists each analysis, +versions, +configs and any computations
  |--> get             #
  |--> register        # create an analysis, analysis_version, and (optionally) an analysis_config
  |--> update          # update an existing analysis by creating a new analysis_version, and config
  `- computation       # commands related to TS analysis computations
     |--> create       #
     |--> download     #
     |--> get          #
     `--> run          #
  `- config            # commands related to TS analysis configs
     |--> create       #
     |--> deactivate   #
     `--> get          #
   ` version           # commands related to TS analysis versions
     |--> create       #
     `--> get          # get analysis version info (including the analysis manifest)
`- data                # commands related to TS data types and sources
  `- source            # TS data sources
     | --> get         #
     ` --> list        # list all available data sources
  `- type              # TS data types
     | --> get         #
     ` --> list        # list all available data types
`- aoi                 #
  |--> create          #
  |--> delete          #
  |--> get             #
  |--> list            #
  `--> update          #
`- tasks               # IMPORTANT - tasks commands live here
  |- initialize        # register an algo + analysis ... soup to nuts.
   ` update            # update an algo + analysis ... end to end.
`- environment         #
  `--> check           # verify the environment
`- imagery             #
  `--> search          # search the scenes (ingested) or catalog (orderable) for available images of an AOI/TOI
`- permission          #
  |--> get             # list users with READ permission on analysis
  `--> set             # set READ permission for an algorithm analysis with another user (i.e. share it)
`- credit              #
  |--> get             # get credit price for analysis (not yet working)
  `--> set             # set the credit pricing for an analysis
`- toi                 #
  |--> create          #
  |--> delete          #
  `--> get             #
`- visualization       #
  |--> create          #
  `--> get             #
```


## General Command Patterns ##

The commands generally try to use the same options for the same types
of inputs.  For example, IDs like algorithm_id or analysis_config_id,
will start with 'i' and then a character to denote type of ID
... e.g. `-ia <algorithm_id>`, or `-iv <algorithm_version_id>`.  For
things associated with algorithms, the second character will be lower
case, and for things associated with analysis, the second character
will be upper case.


Here are the main ones that *usually* follow the rules:
```
-i   - IDs

-ia  - algorithm_id
-iv  - algorithm_version_id
-ic  - algorithm_config_id
-ip  - algorithm_computation_id

-iA  - anlaysis_id
-iV  - analysis_version_id
-iC  - analysis_config_id
-iP  - analysis_computation_id

-n   - names

-na  - algorithm_name
-nc  - algorithm_config_name
-nA  - analysis_name
-nC  - analysis_config_name
```

### The Most Frequently Used Commands ###

The `ts` CLI allows you to perform pretty surgical operations in
Terrascope, and most of the commands do very specialized things which
you won't usually need.  For common tasks, there are `tasks` commands
to carry out things that would normally take many commands.  For
example, in order to register a new algorithm and create an analysis
to run it through the Terrascope UI, you normally use the following
commands (specific options are not shown here):

```
$ ts algo create
$ ts algo version create
$ ts algo config create
$ ts analysis create
$ ts analysis version create
$ ts analysis config create
```

All of these commands are bundled together in the `ts tasks init`
command.  If you require surgical control of algorithm registration,
you have it.  But generally, the `tasks` commands will probably suit
most needs.

#### Get algorithm info ####

```
$ ts alg get -na hlnorm
                 name                          algorithm_id                    author
0  hlnorm_foottraffic  deadbeef-5c5a-48d9-b65a-3748ebf9bb8e  wally@orbitalinsight.com
```

#### Look up Data Source and Data Type ####

This is useful when preparing a manifest to register an algorithm.
Data sources and types must be among those supported by terrascope.
To get a listing of the current set, do this:

```
$ ts data source list
```

```
$ ts data type list
```

#### Create a New Algorithm + Analysis ####

To put in a new algorithm and analysis, you have to create a manifest,
and then you can submit it with:

```
$ ts tasks init -m <manifest_yaml> -nC <analysis_config_name (appears in UI)>
```

That will create the algorithm, algorithm_version, algorithm_config, analysis, analysis_version, and analysis_config.


#### Update an Algorithm + Analysis ####

```
$ ts tasks update -m <manifest_yaml> -nC <analysis_config_name> -ia <algo_id> -iA <analysis_id> -V <new version>
```

#### Share an analysis with another user ####

```
$ ts perm set -iC <analysis_config_id> -u <username1> <username2> ...
```


### Finding IDs ###

Terrascope uses UUIDs to identify pretty much everything, and you
often need to get these in order to carry out certain operations.
Here are some of the most useful:


#### Dump IDs for an Analysis ####

This is a heirarchical dump of any analyses matching <search_string>,
and their analysis_versions, analysis_configs, and any computations
(there are options to filter the computations by date if there are too
many).

```
$ ts analysis display -nA <analysis_name_search_string>
```

#### Look up algorithm_id for an Analysis ####

Do find out info about an algorithm node in an analysis, query the
analysis version with `-C all` (get all available columns), and `-T`
(transpose ... so the output is readable).  The algorithm info is
buried in the printout.

```
ts ana version get -iV <analysis_version_id> -C all -T
```


### Testing an Algorithm ###

#### Checking for available imagery ####

In the examples:

- `-S <shapefile>` contains the AOI you wish to find imagery for
- `-ia <aoi_id>` refers to the id of an AOI in the provided shapefile (aois.geojson here).
- `-d` specifies the data source,
- `-p` specifies the 'processing spec' (not queryable through the API, you just have to know it).
- `-ts <start_time>`
- `-te <end_time>`
- `-s <search_service>` can be either 'SCENE' (already ingested images) or 'CATALOG' (available to order)

```
$ ts image search -S aois.geojson -ia <aoi_id> -ts 2023-01-08 -te 2023-01-31 -d planet_PSSceneSD -p PL-PSSceneSR -s CATALOG
```


#### Create and Run an algorithm computation ####

(-f 3 means 'daily')

```
$ ts comp create -iC <algo_config_id> -s 2022-01-01 -e 2022-01-07 -a ./myaois.geojson -f 3
```

The above example to create a computation will print out a computation_id.  Use it to run:

```
$ ts comp run -ip <comp_id>
```

#### Get info about the computation ####

```
$ ts comp get -ip <computation_id>

ecb494a3-e0e1-4c7b-804b-af45067816ba
id                   ecb494a3-e0e1-4c7b-804b-af45067816ba
aoi_collection_id    58111acf-50d8-4079-a562-6a98badd75da
algo_config_id       6b995056-dd72-494f-b7ce-abf27422d6f1
toi_id               aafe2b93-8f80-4cf8-994b-97ab43d346ec
submitted_on         2023-03-24T03:52:01.245849Z
state                COMPLETE
last_execution       2023-03-24T03:59:02.243957Z
progress.succeeded   100.0
```


#### Download computation results ####

```
$ ts algo comp download -ip <computation_id> -o test_result.zip
```

## New Module Functions ##

* The async functions that make the calls to the SDK live in `terrascope/cli/lib/workflow.py`
* Most are short and sweet.  Feel free to add what you need.


## Authors and acknowledgment

Orbital Insight

## License

[LICENSE](LICENSE)

