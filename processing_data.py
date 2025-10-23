import pandas as pd
import json

def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def generate_data_dict(df: pd.DataFrame) -> dict[str, any]:
    return df.to_dict(orient="index")


def write_json(data: dict[str, any], file_path: str) -> None:
    json_data = json.dumps(
        obj=data,
        indent=4
    )
    with open(file_path, 'w') as f:
        f.write(json_data)

def generate_states_list(df: pd.DataFrame) -> list[str]:
    return df["Location"].to_list()

def main() -> None:
    read_path = "raw_data.csv"
    write_path = "locations.json"

    df = load_data(read_path)
    locations_list = generate_states_list(df)
    write_json(locations_list, write_path)


if __name__ == "__main__":
    main()