# Copyright (c) 2025, scopen.fr and contributors
# For license information, please see license.txt
import frappe
from frappe import _


def _extract_code(v14_value):
	"""
	Extrait le code Incoterm depuis une valeur v14
	"""
	if not v14_value:
		return None
	code = v14_value.strip()[:3].upper()
	return code if code else None


# Étape 1 - Mise à jour des title des Incoterms existants
def _update_incoterm_titles(dry_run):
	for incoterm in frappe.get_all("Incoterm", fields=["name", "description"]):
		if incoterm.description:
			if dry_run:
				frappe.logger().info(f"[DRY RUN] Incoterm {incoterm.name} → title : {incoterm.description}")
			else:
				frappe.db.set_value(
					"Incoterm", incoterm.name, "title", incoterm.description, update_modified=False
				)


# Étape 2 - Création des incoterms obsolètes
def _create_obsolete_incoterms(dry_run):
	# Codes existants en v15+
	existing_codes = {r.name for r in frappe.get_all("Incoterm", fields=["name"])}

	# Valeurs distinctes utilisées en v14
	v14_values = frappe.db.get_all(
		"Customer",
		filters={"incoterm": ["not in", ["", None]]},
		fields=["incoterm"],
		distinct=True,
	)

	for row in v14_values:
		code = row.incoterm.strip()[:3].upper()
		if code and code not in existing_codes:
			# Code absent en v15 -> obsolète
			if dry_run:
				frappe.logger().info(f"[DRY RUN] Incoterm obsolète à créer : {code}")
			else:
				frappe.get_doc(
					{
						"doctype": "Incoterm",
						"name": code,
						"code": code,
						"title": f"[Obsolète] {code}",
						"description": f"{code} (Incoterms obsolète — migré depuis v14)",
					}
				).insert(ignore_permissions=True)
				frappe.logger().info(f"Incoterm obsolète créé : {code}")
			existing_codes.add(code)


# Étape 3 - Custom Field "incoterm" sur Supplier
def _create_supplier_incoterm_field(dry_run):
	if frappe.db.exists("Custom Field", {"dt": "Supplier", "fieldname": "incoterm"}):
		frappe.logger().info("Custom Field incoterm sur Supplier déjà existant - ignoré.")
		return

	if dry_run:
		frappe.logger().info("[DRY RUN] Custom Field incoterm à créer sur Supplier.")
		return

	custom_field = frappe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": "Supplier",
			"fieldname": "incoterm",
			"label": "Incoterm",
			"fieldtype": "Link",
			"options": "Incoterm",
			"insert_after": "supplier_type",
		}
	)
	custom_field.insert(ignore_permissions=True)
	frappe.logger().info("Custom Field incoterm créé sur Supplier.")


# Étape 4 - Migration des valeurs incoterm sur Customer
def _migrate_customer_incoterms(dry_run):
	# Vérifie que le custom field incoterm existe sur Customer
	if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "incoterm"}):
		frappe.logger().warning("Custom Field incoterm non trouvé sur Customer - migration ignorée.")
		return

	# Tous les customers avec un incoterm renseigné
	customers = frappe.db.get_all(
		"Customer",
		filters={"incoterm": ["!=", ""]},
		fields=["name", "incoterm"],
	)

	migrated = 0
	skipped = 0

	for customer in customers:
		v14_value = customer.get("incoterm")
		code = _extract_code(v14_value)

		if not code:
			frappe.logger().warning(
				f"Customer {customer.name} : valeur incoterm vide ou non parsable '{v14_value}' - ignoré."
			)
			skipped += 1
			continue

		# Vérifie que le code existe dans le doctype Incoterm (actif ou obsolète)
		if not frappe.db.exists("Incoterm", code):
			frappe.logger().warning(
				f"Customer {customer.name} : code '{code}' inexistant dans Incoterm - ignoré."
			)
			skipped += 1
			continue

		if dry_run:
			frappe.logger().info(f"[DRY RUN] Customer {customer.name} : '{v14_value}' → '{code}'")
		else:
			frappe.db.set_value("Customer", customer.name, "incoterm", code, update_modified=False)
		migrated += 1

	prefix = "[DRY RUN] " if dry_run else ""
	frappe.logger().info(f"{prefix}Migration incoterm Customer : {migrated} à migrer, {skipped} ignorés.")


# Point d'entrée du patch
def execute(dry_run=False):
	frappe.logger().info(f"=== Patch migrate_incoterm : démarrage {'(DRY RUN)' if dry_run else ''} ===")

	_update_incoterm_titles(dry_run)
	frappe.logger().info("# Étape 1 : titles Incoterms mis à jour")

	_create_obsolete_incoterms(dry_run)
	frappe.logger().info("# Étape 2 : incoterms obsolètes créés")

	_create_supplier_incoterm_field(dry_run)
	frappe.logger().info("# Étape 3 : custom field Supplier créé")

	_migrate_customer_incoterms(dry_run)
	frappe.logger().info("# Étape 4 : valeurs Customer migrées")

	if not dry_run:
		frappe.db.commit()

	frappe.logger().info(f"=== Patch migrate_incoterm : terminé {'(DRY RUN)' if dry_run else ''} ===")
