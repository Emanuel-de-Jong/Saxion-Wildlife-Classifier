def get_animal_observation_total(results, mode='leging'):
    '''
    Get a total of all labels, for a given leging OR camera

    Parameters:
        results: JSON
            JSON data of the final results
        mode: String
            Determines if we want to get the data per camera or leging

    Returns:
        observation_animal_count: dictionary
            A dictionary with the needed information
            The dictionary key is the camera or leging
            The dictionary value is the total
    '''
    observation_animal_count = {}
    for result in results:
        camera_id = result['metadata']['camera']
        mode_id = f"{camera_id}_{result['metadata'][mode]}" if mode != 'camera' else camera_id
        observed_total = len(result['labels'])
        if observation_animal_count.get(mode_id) is None:
            observation_animal_count[mode_id] = observed_total
        else:
            observation_animal_count[mode_id] += observed_total
    return observation_animal_count

def get_animal_count(results):
    '''
    Get a total of all different labels

    Parameters:
        results: JSON
            JSON data of the final results

    Returns:
        all_animal_count: dictionary
            A dictionary with the needed information
            The dictionary key is the label
            The dictionary value is the total
    '''
    all_animal_count = {}
    for result in results:
        animals = result['labels']
        for animal in animals:
            if all_animal_count.get(animal) is None:
                all_animal_count[animal] = 1
            else:
                all_animal_count[animal] += 1
    return all_animal_count

def get_species_by_hour(results):
    '''
    Get a dictionary which contains the label total per hour per label

    Parameters:
        results: JSON
            JSON data of the final results

    Returns:
        species_by_hour: dictionary
            A dictionary with dictionaries, with the needed information
            The dictionary key is the label
            The dictionary value is dictionary for that label
                The label dictionary key is which hour (from 0 to 23)
                The label dictionary value is the total
    '''
    species_by_hour = {}
    for result in results:
        hour = result['metadata']['time'].split(':')[0]
        hour = hour[1] if hour[0] == '0' else hour # We do not want an extra zero in front of the single digits
        animals = result['labels']

        temp_dict = {}
        for animal in animals:
            if temp_dict.get(animal) is None:
                temp_dict[animal] = 1
            else:
                temp_dict[animal] += 1

        found_animals = temp_dict.keys()
        for found in found_animals:
            if species_by_hour.get(found) is None:
                species_by_hour[found] = {hour: temp_dict[found]}
            else:
                dict_animal = species_by_hour[found]
                if dict_animal.get(hour) is None:
                    dict_animal[hour] = temp_dict[found]
                else:
                    dict_animal[hour] += temp_dict[found]
                species_by_hour[found] = dict_animal



    return species_by_hour

def get_statistics(results):
    '''
    Get the statistics, generated from the given results

    Parameters:
        results: JSON
            JSON data of the final results

    Returns:
        statistics: JSON
            JSON data, which contains the processed results
    '''
    statistics = {
        'observations_by_specie': get_animal_count(results),
        'observations_by_camera': get_animal_observation_total(results, mode='camera'),
        'observations_by_leging': get_animal_observation_total(results),
        'species_by_hour': get_species_by_hour(results)
    }
    
    return statistics