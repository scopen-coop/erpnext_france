from erpnext_france.regional.france.pappers.api import PappersAPI


class PappersEntreprise(PappersAPI):
	def __init__(self):
		super(PappersEntreprise, self).__init__()
		self.url = f"{self.base_url.rstrip('/')}/entreprise"
