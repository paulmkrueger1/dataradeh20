from .amplitude_export_helpers import run_historical_job
import sys

if __name__ == '__main__':
	print(sys.argv)
	if len(sys.argv) > 0:
		if len(sys.argv) > 1:
			if sys.argv[1] == 'corn':
				now = datetime.now() - timedelta(hours=1)
				last_hour = now - timedelta(hours=1)
				start_list = [int(i) for i in str(last_hour).split(':')[0].replace(' ','-').split('-')] # [Y, M, D, h]
				end_list = [int(i) for i in str(now).split(':')[0].replace(' ','-').split('-')] # [Y, M, D, h]
			else:
				start_str = sys.argv[1]
				end_str = sys.argv[2]
				start_list = [int(i) for i in start_str.split(':')[0].replace(' ','-').split('-')] # [Y, M, D, h]
				end_list = [int(i) for i in end_str.split(':')[0].replace(' ','-').split('-')] # [Y, M, D, h]

			run_historical_job(start_list, end_list)
		else:
			print("Must pass start and end-date arguments (e.g., '2018-09-01-15' '2018-09-02-15')")