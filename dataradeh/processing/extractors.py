import pandas as pd
import json

def extract_event_types(out_df, verbose = False):
    """
    Used by io.readers.generate_event_type_map
    """
    event_type_map = {}
    failed_event_types = []
    for event_type in out_df.event_type.unique():
        event_type_df = out_df[out_df.event_type == event_type]
        if event_type not in event_type_map:
            event_type_map[event_type] = []
        for idx, row in event_type_df.iterrows():
            try:
                # String operations to load JSON data in proper format
                loaded = json.loads(row["event_properties"].replace("'",'"').replace('n"s',"n's").replace('False', '"False"').replace('True', '"True"'))
            except Exception as e:
                if verbose: 
                    print(e)
                    print(event_type, row['event_properties'], type(row["event_properties"]))
                failed_event_types.append(event_type)
                
            for key in loaded.keys():
                if key not in event_type_map[event_type]:
                    event_type_map[event_type].append(key)
                    
    unlanded_types = [e_type for e_type in failed_event_types if e_type not in event_type_map]
    
    return {
        'event_type_map': event_type_map, # map of all event type and their possible event properties
        'failed_event_types': failed_event_types, # event types with at least 1 fail (could still be present in event_type_map)
        'unlanded_types': unlanded_types # event types that were in the out_df but failed on parsing the keys
    }