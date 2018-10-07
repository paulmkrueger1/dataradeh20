import pandas as pd

def process_appsee_session(session_json):
	"""
	session_json is output from io.readers.get_appsee_session
	"""
	event_df = pd.DataFrame(session_json['Events'])
	event_df['StartTime'] = event_df.Time
	event_df['Table'] = 'Events'
	# event_df
	screen_df = pd.DataFrame(session_json['Screens'])
	screen_df['num_gestures'] = [len(i) for i in screen_df.Gestures]
	screen_df['num_actions'] = [len(i) for i in screen_df.Actions]
	screen_df['Table'] = 'Screens'
	screen_df['screen_num'] = screen_df.index.values

	combined = pd.concat([event_df, screen_df])
	combined = combined.sort_values('StartTime').reset_index(drop=True)
	combined.screen_num = combined.screen_num.ffill().fillna(0)
	
	return combined
	
def process_appsee_sessions(sessions_json):
	return [process_appsee_session(session) for session in sessions_json['Sessions']]