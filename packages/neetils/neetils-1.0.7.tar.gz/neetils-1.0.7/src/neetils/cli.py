import fire
import os
from neetils import load_jsonl, write_json
import pandas as pd


class Converter(object):
    def _get_format(self, output_file: str):
        ext = os.path.splitext(output_file)[1]
        if ext == ".json":
            return "json"
        elif ext == ".csv":
            return "csv"
        elif ext == ".tsv":
            return "tsv"
        elif ext == ".xlsx":
            return "xlsx"
        else:
            raise ValueError(f"Unsupported file format {ext}")

    def convert(
        self,
        input_file: str,
        output_file: str,
        format: str = None,
        overwrite: bool = True,
    ) -> str:
        """
        Convert the input JSONL file to the specified format.

        Args:
            input_file (str): The path to the input JSONL file.
            output_file (str): The path to the output
            format (str): The format to convert the JSONL file to. If None, it will be determined based on the extension of the output file.
        """
        data = load_jsonl(input_file)
        if format is None:
            format = self._get_format(output_file)
        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(f"Output file {output_file} already exists")

        if format == "json":
            write_json(output_file, data)
        elif format == "csv" or format == "tsv":
            pd.DataFrame(data).to_csv(
                output_file, index=False, sep="\t" if format == "tsv" else ","
            )
        elif format == "xlsx":
            pd.DataFrame(data).to_excel(output_file, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
        return output_file


def main():
    fire.Fire(Converter)
