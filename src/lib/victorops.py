import requests
import logging
from urllib.parse import quote

class VictorOps:

	def __init__(self, API_ID, API_KEY):
		self.api_id = API_ID
		self.api_key = API_KEY
		self.api_base_url ='https://api.victorops.com/api-public'
		self.log = logging.getLogger(__name__)

	def call_api(self, endpoint, params=None):
		headers = {
			'X-VO-Api-Id': self.api_id,
			'X-VO-Api-Key': self.api_key
		}
		# craft the url + encode
		url = "%s%s" % (self.api_base_url, quote(endpoint))
		request = requests.get(url, params=params, headers=headers)

		if request.status_code == 200:
			return request.json()
		else:
			raise Exception("Call to VictorOps API failed: %s" % request.status_code)

	def get_oncall_schedule(self, team, daysForward=7, step=0):
		try:
			slug = self.get_team_slug(team)
			endpoint = "/v2/team/%s/oncall/schedule" % slug
			params = {
				'daysForward': daysForward,
				'step': step
			}
			return self.call_api(endpoint=endpoint, params=params)
		except Exception as e:
			raise Exception("Can't get oncall schedule for team %s: %s" % (team, e))

	def get_teams(self):
		endpoint = "/v1/team"
		try:
			return self.call_api(endpoint=endpoint)
		except Exception as e:
			raise Exception("Can't get teams: %s" % e)

	def get_team_slug(self, team):
		for t in self.get_teams():
			if t['name'] == team:
				return t['slug']
		raise Exception("Unknown team '%s'" % team)
