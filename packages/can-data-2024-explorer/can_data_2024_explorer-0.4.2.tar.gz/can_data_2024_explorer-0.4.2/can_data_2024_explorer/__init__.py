#!/usr/bin/env python3
"""Library for viewing CAN bus data from HSM research machines.

Copyright iFOS GmbH

Authors: Jakub Wołosz, Lukas Schreiber

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
UT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.4.2"

# Imports

# standard libraries
from pathlib import Path
import glob
import os
from pkg_resources import resource_filename
import sys
import subprocess


# third party libraries
import pandas as pd
import cantools
import cantools.subparsers.decode
import cantools.logreader

### Constants

TZ = "Europe/Berlin"


###  Defined Functions


def Boundaries(datetime_start: str, time_to_add: str, tz: str = TZ) -> pd.Interval:
    """
    Creates a time period as a pandas Interval from the given datetime and the incremented time.

    Args:
        datetime_start (str): The start datetime string in 'YYYY-MM-DDTHHMMSS' format.
        time_to_add (str): The time to add in 'X XX XX XX' format, representing days, hours, minutes, and seconds.

    Returns:
        pd.Interval: A pandas Interval object representing the time period.

    Raises:
        ValueError: If the input strings do not match the expected format.
    """

    # Check and convert the input datetime string to a pandas Timestamp object
    try:
        start_datetime = pd.to_datetime(
            datetime_start, format="%Y-%m-%dT%H%M%S"
        ).tz_localize(tz)
    except ValueError:
        raise ValueError("datetime_start must be in 'YYYY-MM-DDTHHMMSS' format.")

    # Parse the time_to_add string
    try:
        days, hours, minutes, seconds = map(int, time_to_add.split())
    except ValueError:
        raise ValueError(
            "time_to_add must be in 'X XX XX XX' format, representing days, hours, minutes, and seconds."
        )

    # Check if the parsed values are non-negative
    if any(x < 0 for x in [days, hours, minutes, seconds]):
        raise ValueError(
            "Days, hours, minutes, and seconds must be non-negative integers."
        )

    # Create a Timedelta object with the specified amount of time
    time_delta = pd.Timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    # Calculate the end datetime
    end_datetime = start_datetime + time_delta
    # Create a pandas Interval object representing the time period
    time_period = pd.Interval(left=start_datetime, right=end_datetime, closed="both")

    return time_period


def Localize(cwd: str, tz: str = TZ) -> pd.DataFrame:
    """
    The function localizes all .log files within a current working directory according to the machine type,
    splits the contained information e.g. date, time and signal duration (converted to decimal values), and stores it as pd.DataFrame.

    Args:
        cwd: str

    Returns:
        pd.Dataframe, which contains data extracted from log files.
    """

    # Find all .log files within cwd and store them in a list
    directory = Path(cwd)
    # filepath = glob.glob(str(directory / '*.log'))
    filepath = sorted(glob.glob("can_????-??-??T??????_#*.log", root_dir=directory))
    # Extract components from filenames
    formatted_files = [os.path.basename(f)[4:21] for f in filepath]
    # Create a dictionary from lists
    datadict = {"name": filepath, "datetime": formatted_files}
    # Create pandas DataFrame from dictionary
    df = pd.DataFrame.from_dict(data=datadict)

    # Format DataFrame columns
    df["name"] = pd.Series(df["name"], dtype="string")
    df["datetime"] = pd.to_datetime(
        df["datetime"], format="%Y-%m-%dT%H%M%S"
    ).dt.tz_localize(
        tz
    )  # Assuming 'date' is in 'YYYY-MM-DD' format

    # # Calculate duration in hours (as decimal numbers)
    df["duration"] = (
        (df["datetime"].shift(-1) - df["datetime"])
        .dt.total_seconds()
        .div(3600)
        .fillna(0)
        .astype(float)
    )

    # # Set duration value to 0 for each last row of a currnt date.

    # Extract the date from 'datetime'
    df["date"] = df["datetime"].dt.date
    # Identify the last occurrence of each date
    last_indices = df.groupby("date").tail(1).index
    # Set the 'duration' value to 0 for these identified rows
    df.loc[last_indices, "duration"] = 0
    # Drop the 'date' column as it is no longer needed
    df = df.drop(columns=["date"])

    # #Calculate total working time (sum of the duration of the signals)
    total_working_time = df["duration"].sum()
    print("Total working time is :", round(total_working_time, 2), "h")

    return df


def File_validation(date_range: pd.Interval, data: pd.DataFrame) -> pd.DataFrame:
    """
    The function filters .log files which meet the date criteria (desired date range)
    It returns a DataFrame containing rows meeting the criteria.
    The output has the same columns as the Localize() function.

    Parameters:
    date_range: pd.Interval - The interval to filter the 'datetime' column.
    data: pd.DataFrame - The DataFrame containing log data with 'datetime' and 'duration' columns.

    Returns:
    pd.DataFrame - A DataFrame which contains desired log files (filtered by the constraints from input_info() function).
    """

    # Filter the rows where the 'datetime' is within the specified 'date_range'
    approved_files_df = data[
        (data["datetime"] >= date_range.left)
        & (data["datetime"] <= date_range.right).shift(1, fill_value=True)
    ]

    if approved_files_df.empty:
        raise ValueError("The DataFrame is empty. Check the Input Parameters!")

    total_working_time = approved_files_df["duration"].sum()
    print(
        "Total working time for desired period is :", round(total_working_time, 2), "h"
    )

    return approved_files_df


def Fuel_consumption(
    database_path: str,
    files: pd.DataFrame,
    cwd: str,
    date_range: pd.Interval,
    _progress_bar=None,
) -> str:
    """
    The function calculates the fuel consumption over log files which satisfy the desired date range.

    Parameters:
    - database_path: str, path to the DBC file.
    - files: pd.DataFrame, DataFrame containing file names and durations.
    - cwd: str, current working directory where log files are located.
    - date_range: pd.Interval to apply to the first and last file in files.

    Returns: information about total fuel burned over desired time.
    """
    # Load the DBC file
    database = cantools.database.load_file(database_path)

    # Initialize a list to hold results
    results = []

    # Iterate over each row in the files DataFrame
    length = len(files.index)
    for index, row in files.reset_index().iterrows():
        file_name = row["name"]
        duration = row["duration"]
        check_timestamp = index in {files.index[0], files.index[-1]}

        path = os.path.join(cwd, file_name)

        # Open and parse the log file
        with open(path) as log:
            fuel_rates = []
            EN_duration = []
            parser = cantools.logreader.Parser(log)

            for line, frame in parser.iterlines(keep_unknowns=True):
                if check_timestamp and frame.timestamp not in date_range:
                    continue
                if frame is not None and frame.frame_id == 385:
                    message = database.get_message_by_frame_id(frame.frame_id)
                    decoded_message = message.decode(frame.data)
                    fuel_rates.append(decoded_message["Fuelrate"])
                    EN_duration.append(decoded_message["RPM_Diesel"])

            # Calculate the average fuel rate for the current file
            if fuel_rates:
                avg_fuel_rate = sum(fuel_rates) / len(fuel_rates)
                total_fuel_rate = avg_fuel_rate * duration
                if EN_duration:
                    count_greater_than_zero = sum(1 for x in EN_duration if x > 0)
                    time_coefficient = count_greater_than_zero / len(EN_duration)
                    working_time = duration * time_coefficient
                    results.append(
                        {
                            "File": file_name,
                            "Total Fuelrate": total_fuel_rate,
                            "Working_time": working_time,
                        }
                    )

        if _progress_bar:
            Progress, root = _progress_bar
            Progress["value"] = (100 * index) // length
            root.update_idletasks()

    # Convert results to a DataFrame
    result_df = pd.DataFrame.from_dict(results)
    # result_df_fuel = result_df['Total Fuelrate'].sum()
    result_df = result_df.sum()
    # # Round the total fuel consumption to 3 decimal places
    total_fuel_consumption = round(result_df["Total Fuelrate"], 3)
    working_time = round(result_df["Working_time"], 3)
    consumption_and_time = {
        "consumption": total_fuel_consumption,
        "working_time": working_time,
    }
    return consumption_and_time


def Draw_a_chart(elements: list, dbc_path: str, patterns: list):

    patterns = [elem for pattern in patterns for elem in (pattern, "-")][:-1]

    style_path = resource_filename("can_data_2024_explorer", "assets/ifos.mplstyle")
    args = (
        [sys.executable, "-m", "cantools", "plot", dbc_path]
        + patterns
        + ["--style", style_path]
    )
    cat = ["cmd", "/c", "type"] if sys.platform == "win32" else ["cat"]
    combined = subprocess.Popen(cat + elements, stdout=subprocess.PIPE)
    subprocess.Popen(args, stdin=combined.stdout)
