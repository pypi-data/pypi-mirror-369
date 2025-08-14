from time import sleep

from elemental_tools.scripts.google_synchronization import GoogleSync
from elemental_tools.api.controllers.user import UserController


def start(sub):

	results = []

	def run_sync(sub):
		nonlocal results

		_this_user = GoogleSync(sub)
		sleep(5)
		results.append({'statementSync': _this_user.sync_statement()})
		sleep(5)
		results.append({'transactionSync': _this_user.sync_transaction()})
		sleep(5)

	user_db = UserController()
	_all_google_sync_users = user_db.query_all({'google_sync': True})

	for user in _all_google_sync_users:

		try:
			run_sync(str(user.get('_id')))
		except Exception as e:
			if "quota_limit" in str(e):
				sleep(15)
				try:
					run_sync(str(user.get('_id')))
				except:
					pass

			print(str(e))

	return str(results)


if __name__ == "__main__":
	start("root")

