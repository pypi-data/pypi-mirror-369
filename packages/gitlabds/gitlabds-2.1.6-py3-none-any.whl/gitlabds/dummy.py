import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings


def dummy_code(
    df: pd.DataFrame,
    dv: Optional[str] = None,
    columns: Union[str, List[str]] = "all",
    categorical: bool = True,
    numeric: bool = True,
    categorical_max_levels: int = 20,
    numeric_max_levels: int = 10,
    dummy_na: bool = False,
    prefix_sep: str = "_dummy_", 
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, List[Any]]]:
    """
    Dummy code (one-hot encode) categorical and numeric columns based on specified parameters.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input pandas dataframe
    dv : str, optional
        The column name of your outcome. This will prevent this column from being dummy coded.
    columns : list or str, default="all"
        Will examine all columns by default. To limit to a subset of columns, 
        pass a list of column names.
    categorical : bool, default=True
        Whether to dummy code categorical columns
    numeric : bool, default=True
        Whether to dummy code numeric columns
    categorical_max_levels : int, default=20
        Maximum number of levels a categorical column can have to be eligible for dummy coding.
    numeric_max_levels : int, default=10
        Maximum number of levels a numeric column can have to be eligible for dummy coding.
    dummy_na : bool, default=False
        Whether to create a dummy coded column for missing values.
    prefix_sep : str, default="_dummy_"
        The string to use as a separator between the column name and dummy value.
    verbose : bool, default=True
        Whether to print detailed information about the process.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, List[Any]]]
        A tuple containing:
        - The transformed DataFrame with dummy-coded columns
        - Dictionary of dummy coding information that can be used with apply_dummy()
    """
    import pandas as pd
    import warnings
    from typing import Dict, List, Any, Union, Optional, Tuple
    
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if categorical_max_levels < 2:
        raise ValueError(f"categorical_max_levels must be at least 2, got {categorical_max_levels}")
        
    if numeric_max_levels < 2:
        raise ValueError(f"numeric_max_levels must be at least 2, got {numeric_max_levels}")
    
    # Determine columns to process
    if columns == "all":
        var_list = df.columns.tolist()
        if verbose:
            print("Will examine all variables as candidates for dummy coding")
    else:
        if isinstance(columns, list):
            var_list = columns
        else:
            raise TypeError(f"columns must be a list or 'all', got {type(columns)}")
            
        # Validate columns exist in the dataframe
        missing_columns = [col for col in var_list if col not in df.columns]
        if missing_columns:
            warnings.warn(f"Columns {missing_columns} not found in dataframe and will be skipped")
            var_list = [col for col in var_list if col in df.columns]
            
        if verbose:
            print(f"Will examine the following variables as candidates for dummy coding: {var_list}")

    # Do not dummy code outcome variable
    if dv is not None:
        if dv not in df.columns:
            warnings.warn(f"Specified DV '{dv}' not found in dataframe")
        elif dv in var_list:
            var_list.remove(dv)
            if verbose:
                print(f"Excluding outcome variable '{dv}' from dummy coding")

    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Dictionary to store dummy coding information for later use
    dummy_info = {}

    # Handle categorical columns
    if categorical:
        # Determine number of levels for each field
        cat_levels = df[var_list].select_dtypes(include="object").nunique(dropna=True, axis=0)
        
        # Filter columns by level count criteria
        eligible_cat_cols = cat_levels[(cat_levels <= categorical_max_levels) & (cat_levels > 1)]
        
        if verbose:
            print(f"\nCategorical columns considered for dummy coding:")
            print(cat_levels)
            print(f"\nCategorical columns below categorical_max_levels threshold of {categorical_max_levels} levels:")
            print(eligible_cat_cols)
        
        # Get final list of columns to dummy code
        cat_columns = eligible_cat_cols.index.tolist()
        
        # Store mapping of categorical values for each column
        for col in cat_columns:
            # Store unique values for later use
            values = df[col].dropna().unique().tolist()
            dummy_info[col] = values
        
        # Perform dummy coding if we have columns to encode
        if cat_columns:
            work_df = pd.get_dummies(
                data=work_df, 
                prefix_sep=prefix_sep,
                columns=cat_columns, 
                dummy_na=dummy_na, 
                dtype='int'
            )
            
            # Remove dummy coded categorical fields from var_list because pandas removes them automatically from the df
            var_list = [col for col in var_list if col not in cat_columns]

    # Handle numeric columns
    if numeric:
        # Determine number of levels for each field
        num_levels = df[var_list].select_dtypes(include=["number"]).nunique(dropna=True, axis=0)
                
        # Filter columns by level count criteria
        eligible_num_cols = num_levels[(num_levels <= numeric_max_levels) & (num_levels > 1)]
        
        if verbose:
            print(f"\nNumeric columns considered for dummy coding:")
            print(num_levels)
            print(f"\nNumeric columns below threshold of {numeric_max_levels} levels:")
            print(eligible_num_cols)
        
        # Get final list of columns to dummy code
        num_columns = eligible_num_cols.index.tolist()
        
        # Store mapping of numeric values for each column
        for col in num_columns:
            # Store unique values for later use
            values = sorted(df[col].dropna().unique().tolist())
            
            # create column names with float format for numeric data
            formatted_values = []
            for v in values:
                if isinstance(v, (int, float)):
                    # Store as float to match get_dummies column naming
                    formatted_values.append(float(v))
                else:
                    formatted_values.append(v)
            
            dummy_info[col] = formatted_values
        
        # Perform dummy coding if we have columns to encode
        if num_columns:
            # Save numeric columns to add back later
            num_df = work_df[num_columns].copy(deep=True)
            
            # Dummy code
            work_df = pd.get_dummies(
                data=work_df, 
                prefix_sep=prefix_sep,
                columns=num_columns, 
                dummy_na=dummy_na, 
                dtype='int'
            )
            
            # Concat back together
            work_df = pd.concat([work_df, num_df], axis=1)

    # Store the prefix_sep in the dummy_info to use with apply_dummy
    dummy_info["_config"] = {"prefix_sep": prefix_sep}

    return work_df, dummy_info


def dummy_top(
    df: pd.DataFrame,
    dv: Optional[str] = None,
    columns: Union[str, List[str]] = "all",
    min_threshold: float = 0.05,
    drop_categorical: bool = True,
    prefix_sep: str = "_dummy_",
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, List[Any]]]:
    """
    Dummy code only categorical levels that exceed a minimum threshold of occurrence.
    
    This is useful when a column contains many levels but there is not a need to
    dummy code every level. Only generates dummy variables for categorical columns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input pandas dataframe
    dv : str, optional
        The column name of your outcome. Will prevent this column from being dummy coded.
    columns : list or str, default="all"
        Will examine all columns by default. To limit to a subset of columns, 
        pass a list of column names.
    min_threshold : float, default=0.05
        The minimum proportion of rows a level must appear in to be dummy coded.
        Default of 0.05 means levels appearing in at least 5% of rows will be coded.
    drop_categorical : bool, default=True
        Whether to drop original categorical columns after dummy coding them.
    prefix_sep : str, default="_dummy_"
        The string to use as a separator between the column name and dummy value.
    verbose : bool, default=True
        Whether to print detailed information about the process.
    
    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, List[Any]]]
        A tuple containing:
        - The transformed DataFrame with dummy-coded columns
        - Dictionary of dummy coding information that can be used with apply_dummy()
    """
    import pandas as pd
    import warnings
    from typing import Dict, List, Any, Union, Optional, Tuple
    
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if not 0 < min_threshold < 1:
        raise ValueError(f"min_threshold must be between 0 and 1, got {min_threshold}")
    
    # Determine columns to process
    if columns == "all":
        var_list = df.columns.tolist()
        if verbose:
            print("Will examine all remaining categorical variables as candidates for dummy top coding")
    else:
        if isinstance(columns, list):
            var_list = columns
        else:
            raise TypeError(f"columns must be a list or 'all', got {type(columns)}")
            
        # Validate columns exist in the dataframe
        missing_columns = [col for col in var_list if col not in df.columns]
        if missing_columns:
            warnings.warn(f"Columns {missing_columns} not found in dataframe and will be skipped")
            var_list = [col for col in var_list if col in df.columns]
            
        if verbose:
            print(f"Will examine the following categorical variables as candidates for dummy top coding: {var_list}")

    # Do not dummy code outcome variable
    if dv is not None:
        if dv not in df.columns:
            warnings.warn(f"Specified DV '{dv}' not found in dataframe")
        elif dv in var_list:
            var_list.remove(dv)
            if verbose:
                print(f"Excluding outcome variable '{dv}' from dummy coding")
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Dictionary to store dummy top coding information for later use
    dummy_info = {}

    # Get categorical columns
    cat_candidates = df[var_list].select_dtypes(include="object")
    cat_columns = cat_candidates.columns.tolist()
    
    if verbose:
        print(f"\nCategorical columns selected for dummy top coding using threshold of {min_threshold*100}%:")
        if cat_columns:
            nunique = cat_candidates.nunique(dropna=True, axis=0)
            print(nunique)
        else:
            print("No categorical columns found")

    # Collect all dummy columns to create at once
    all_dummy_cols = {}
    columns_to_drop = []

    # Create dummy codes for categorical fields that exceed min_threshold
    for col in cat_columns:
        # Calculate value frequencies
        value_counts = df[col].value_counts(dropna=True)
        value_freqs = value_counts / len(df)
        
        # Find values that exceed threshold
        high_freq_values = value_freqs[value_freqs > min_threshold]
        high_freq_list = high_freq_values.index.tolist()
        
        if verbose:
            print(f"\n{col}")
            print(f"The following levels exceed min_threshold of {min_threshold*100}%:")
            print(high_freq_values)
        
        # Skip if no values exceed threshold
        if not high_freq_list:
            if verbose:
                print(f"No levels exceed threshold for column '{col}'")
            continue
        
        # For numeric columns, ensure float format to match what get_dummies creates
        if pd.api.types.is_numeric_dtype(df[col]):
            formatted_values = [float(v) if isinstance(v, (int, float)) else v for v in high_freq_list]
        else:
            formatted_values = high_freq_list
            
        dummy_info[col] = formatted_values
        
        # Create dummies for values that exceed threshold
        for value in high_freq_list:
            dummy_name = f"{col}{prefix_sep}{value}"
            # Create dummy column (1 if equal to value, 0 otherwise)
            all_dummy_cols[dummy_name] = (work_df[col] == value).astype(int)
        
        # Mark for dropping if requested
        if drop_categorical:
            columns_to_drop.append(col)

    # Create all dummy columns at once using concat (prevents fragmentation)
    if all_dummy_cols:
        dummy_df = pd.DataFrame(all_dummy_cols, index=work_df.index)
        work_df = pd.concat([work_df, dummy_df], axis=1)

    # Drop categorical fields if requested
    if columns_to_drop:
        work_df = work_df.drop(columns=columns_to_drop)

    # Store the prefix_sep in the dummy_info to use with apply_dummy
    dummy_info["_config"] = {"prefix_sep": prefix_sep}
    
    return work_df, dummy_info



def apply_dummy(
    df: pd.DataFrame, 
    dummy_info: Dict[str, List[Any]],
    drop_original: bool = False,
    dummy_na: bool = False,
) -> pd.DataFrame:
    """
    Apply dummy coding to a new dataframe using the information from a previous
    dummy_code or dummy_top operation.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to transform.
    dummy_info : dict
        Dictionary of dummy coding information previously generated by 
        dummy_code() or dummy_top().
    drop_original : bool, default=False
        Whether to drop the original columns after dummy coding.
    dummy_na : bool, default=False
        Whether to create dummy variables for NA values.
    
    Returns
    -------
    pd.DataFrame
        Transformed dataframe with dummy-coded columns.
    """
    import pandas as pd
    import warnings
    from typing import Dict, List, Any
    
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
        
    if not isinstance(dummy_info, dict):
        raise TypeError("dummy_info must be a dictionary")
        
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Get the prefix_sep from dummy_info or use default
    prefix_sep = "_dummy_"
    processing_dummy_info = dummy_info.copy()
    
    if "_config" in dummy_info and "prefix_sep" in dummy_info["_config"]:
        prefix_sep = dummy_info["_config"]["prefix_sep"]
        # Remove _config from processing
        processing_dummy_info = {k: v for k, v in dummy_info.items() if k != "_config"}
    
    # Create a copy to avoid modifying the original
    work_df = df.copy(deep=True)
    
    # Collect all new dummy columns in a dictionary
    new_dummy_cols = {}
    columns_to_drop = []
    
    # Process each column in the dummy_info dictionary
    for col, values in processing_dummy_info.items():
        if col not in work_df.columns:
            warnings.warn(f"Column '{col}' not found in dataframe and will be skipped")
            continue
        
        # Create dummies for each value
        for value in values:
            dummy_name = f"{col}{prefix_sep}{value}"
            
            # Handle type mismatches between config and actual data
            # Try both the original value and converted versions
            if pd.api.types.is_numeric_dtype(work_df[col]):
                # For numeric columns, try both int and float versions
                try:
                    # First try exact match
                    mask = (work_df[col] == value)
                    
                    # If no matches and value types differ, try conversion
                    if not mask.any():
                        if isinstance(value, float) and work_df[col].dtype in ['int64', 'int32', 'int8']:
                            # Config expects float (1.0) but data is int (1)
                            mask = (work_df[col] == int(value))
                        elif isinstance(value, int) and work_df[col].dtype in ['float64', 'float32']:
                            # Config expects int (1) but data is float (1.0)
                            mask = (work_df[col] == float(value))
                    
                    new_dummy_cols[dummy_name] = mask.astype(int)
                    
                except (ValueError, TypeError):
                    # Fallback to string comparison if numeric conversion fails
                    new_dummy_cols[dummy_name] = (work_df[col].astype(str) == str(value)).astype(int)
            else:
                # For non-numeric columns, use direct comparison
                new_dummy_cols[dummy_name] = (work_df[col] == value).astype(int)
            
        # Create dummy for NA values if requested
        if dummy_na:
            dummy_name = f"{col}{prefix_sep}nan"
            new_dummy_cols[dummy_name] = work_df[col].isna().astype(int)
            
        # Mark column for dropping if requested
        if drop_original:
            # For categorical columns (from dummy_code) or any column (from dummy_top)
            # if its object type or explicitly requested
            if pd.api.types.is_object_dtype(work_df[col]) or drop_original:
                columns_to_drop.append(col)
    
    # Create all dummy columns at once using concat
    if new_dummy_cols:
        dummy_df = pd.DataFrame(new_dummy_cols, index=work_df.index)
        work_df = pd.concat([work_df, dummy_df], axis=1)
    
    # Drop original columns if requested
    if columns_to_drop:
        work_df = work_df.drop(columns=columns_to_drop)
    
    return work_df