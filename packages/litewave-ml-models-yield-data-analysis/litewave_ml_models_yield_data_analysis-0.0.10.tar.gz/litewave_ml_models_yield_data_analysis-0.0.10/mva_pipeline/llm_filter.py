import json
import os
from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


def filter_columns_with_llm(
    df: pd.DataFrame,
    task_description: str,
    columns_to_keep: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Uses an LLM to filter columns from a DataFrame that are not relevant for the given task.

    Args:
        df (pd.DataFrame): The input DataFrame.
        task_description (str): A description of the task for which the features are being engineered.
        columns_to_keep (List[str] | None, optional): A list of columns to preserve. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with irrelevant columns removed.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in .env file or environment variables."
        )

    client = OpenAI(api_key=api_key)

    column_list = df.columns.tolist()

    system_prompt = f"""
You are an expert in feature engineering for machine learning.
Your task is to identify and remove columns from a dataset that are not suitable for statistical analysis in the context of the following task:
{task_description}

Common examples of columns to remove include:
- Identifiers (e.g., IDs, serial numbers)
- Names (e.g., of people, locations)
- Free-form text or descriptive fields that cannot be easily converted to numerical values.
- Date/time stamps that have not been engineered into features.

Please analyze the following list of columns and return a JSON object with a single key "columns_to_remove" containing a list of column names that should be removed.
Only return columns that are present in the provided list.
If you don't think any columns should be removed, return an empty list.
"""

    user_prompt = f"Here are the columns: {json.dumps(column_list)}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content
        if content:
            columns_to_remove_data = json.loads(content)
            columns_to_remove = columns_to_remove_data.get("columns_to_remove", [])

            # Don't remove columns that are explicitly marked to be kept
            if columns_to_keep:
                columns_to_remove = [
                    col for col in columns_to_remove if col not in columns_to_keep
                ]

            # Ensure we only drop columns that actually exist
            columns_to_drop = [col for col in columns_to_remove if col in df.columns]

            if columns_to_drop:
                print(
                    f"LLM identified and removed the following columns: {columns_to_drop}"
                )
                return df.drop(columns=columns_to_drop)

    except Exception as e:
        print(f"An error occurred during LLM-based column filtering: {e}")
        # Return the original dataframe if the LLM call fails
        return df

    return df
