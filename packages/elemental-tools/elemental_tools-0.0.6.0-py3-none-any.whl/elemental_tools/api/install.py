from elemental_tools.api.settings import SettingsInstaller


class api:

	def install(self):
		SettingsInstaller().check()


if __name__ == '__main__':
	api().install()



