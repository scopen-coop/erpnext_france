from erpnext_france.regional.france.pappers.api import PappersAPI


class PappersRecherche(PappersAPI):
	def __init__(self):
		super(PappersRecherche, self).__init__()
		self.url = "https://suggestions.pappers.fr/v2"
