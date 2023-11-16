from erpnext_france.regional.france.pappers.api import PappersAPI


class PappersDocument(PappersAPI):
	def __init__(self):
		super(PappersDocument, self).__init__()
		self.url = f"{self.base_url.rstrip('/')}/document"

	def get_extrait_pappers(self, siren):
		self.url = f"{self.url}/extrait_pappers"
		return self.get_document(siren)

	def get_extrait_inpi(self, siren):
		self.url = f"{self.url}/extrait_inpi"
		return self.get_document(siren)

	def get_extrait_insee(self, siren):
		self.url = f"{self.url}/avis_situation_insee"
		return self.get_document(siren)

	def get_document(self, siren):
		return self.session.get(
			self.url, headers=self.headers, params={"api_token": self.token, "siren": siren}
		)
