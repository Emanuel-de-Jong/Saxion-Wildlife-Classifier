import pandas as pd

from ..config.constants import DATE_TIME_FORMAT

# This is in seconds. We CAN NOT go lower than 60, because there are some images that only contain hour and minutes as metadata (AM/PM images)
ACCEPTED_TIME_DIFFERENCE = 60
# Which number the first batch should have
BATCH_START_NUMBER = 0

def __generate_batches(to_batch):
    '''
    Generate a list, where each data entry has a batch number

    Parameters
    ----------
    to_batch: list
        A list (of dictionaries) containing data that needs to be batched
    
    Returns
    -------
    batched_data: pandas DataFrame
        A dataframe containing the original data with batch numbers
    '''
    # Get date, time and camera also inside the dataframe as columns, instead of having to call it from the 'metadata' column
    for item in to_batch:
        item['date'] = item['metadata']['date']
        item['time'] = item['metadata']['time']
        item['camera'] = item['metadata']['camera']

    batched_data = pd.DataFrame.from_dict(to_batch) # Make a dataframe from the list
    batched_data['datetime'] = pd.to_datetime(batched_data['date'] + ' ' + batched_data['time'], format=DATE_TIME_FORMAT) # Create a date time field, so we can calculate time difference
    batched_data = batched_data.sort_values(['camera', 'datetime']).reset_index(drop=True) # Sort the dataframe on camera and date time
    batched_data['time_diff'] = batched_data.groupby('camera')['datetime'].diff().dt.total_seconds() # Calculate the time difference between data rows
    batched_data['batch'] = (
        batched_data.groupby('camera')['time_diff']
          .apply(lambda x: (x > ACCEPTED_TIME_DIFFERENCE).cumsum() + BATCH_START_NUMBER)
    ) # Get the batch number
    batched_data['batch'] = batched_data['camera'] + '_' + batched_data['batch'].astype(str)
    batched_data = batched_data.drop(columns=['time_diff', 'datetime'])

    return batched_data

def __generate_average_score(dataframe):
    dataframe['avg_score'] = dataframe['scores'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    return dataframe

def __process_labels(label_lst):
    if not label_lst:
        return 'none'
    temp_dict = {animal: label_lst.count(animal) for animal in label_lst}
    ordered_lst = sorted(set(label_lst))
    return '__'.join(f'{animal}_{temp_dict[animal]}' for animal in ordered_lst)

def __generate_labels_as_string(dataframe):
    dataframe['label_str'] = dataframe['labels'].apply(__process_labels)
    return dataframe

def __get_items_to_keep(batch_list):
    '''
    Generate a list with a list of labels, that we want to keep
    This is done by checking if a list of labels is not a subset of 
    another list of labels. This way, we only have the unique label combinations.

    Parameters
    ----------
    batch_list: list
        A list with all labels from a specific batch
    
    Returns
    -------
    unique_labels: list
        A list with a list of labels that we want to keep
    '''
    # Sort by length in descending order
    indexed_lst = sorted(
        ((index, lst) for index, lst in enumerate(batch_list)),
        key=lambda x: len(x[1]), reverse=True
    )
    
    reduced_lists = []
    for index, lst in indexed_lst:
        if not any(set(lst).issubset(set(other)) for _, other in reduced_lists):
            reduced_lists.append((index, lst))
    
    # Process the labels and return the final result
    unique_labels = [__process_labels(lst) for _, lst in reduced_lists]
    return unique_labels

def __get_file_names(dataframe, final_list):
    '''
    Gets the file names that we want to keep, based on the given final_list

    Parameters
    ----------
    dataframe: DataFrame
        A dataframe with all needed data for the selection
    final_list:
        A list of tuples, with the batch number and labels of the
        images that we want to keep
    
    Returns
    -------
    filtered_final_list: list
        A list with the name of images that we want to keep
    '''
    filtered_final_list = []

    for batch, label_list in final_list:
        for label in label_list:
            matching_rows = dataframe[(dataframe['batch'] == batch) & (dataframe['label_str'] == label)]
            if not matching_rows.empty:
                # Get the row with the highest score for that origin-label combo
                max_score_row = matching_rows.loc[matching_rows['avg_score'].idxmax()]

                # Append the filename of that row to the result
                filtered_final_list.append(max_score_row['target_filename'])

    return filtered_final_list

def __make_selection(dataframe):
    '''
    Makes a selection of images that we will keep

    Parameters
    ----------
    dataframe: DataFrame
        A dataframe with all needed data for the selection
    
    Returns
    -------
    filtered_final_result: DataFrame
        A dataframe with the final selection of images that we want to keep
    '''
    all_batch_names = list(set(dataframe['batch']))

    final_result = []
    for batch in all_batch_names:
        batch_data = dataframe[dataframe['batch'] == batch]
        to_keep = __get_items_to_keep(batch_data['labels'])
        final_result.append((batch, to_keep))
   
    filtered_final_result = __get_file_names(dataframe, final_result)
    return filtered_final_result
    

def remove_duplicates(to_filter):
    '''
    Automatically remove duplicate results from the processed image data

    Parameters
    ----------
    to_filter: list
        A list containing data of all processed image data
    
    Returns
    -------
    return_filtered_results: list
        A list containing all data of images that we DO want to use
    '''
    batch_result = __generate_batches(to_filter)

    modified_dataframe = __generate_average_score(batch_result)
    modified_dataframe = __generate_labels_as_string(modified_dataframe)

    filtered_results = __make_selection(modified_dataframe)
    return_filtered_results = [item for item in to_filter if item['target_filename'] in filtered_results]

    return return_filtered_results