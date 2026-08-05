# Copyright (c) 2026, scopen.fr and contributors
# For license information, please see license.txt
import frappe

RENAMES = [
	(
		"Categorie comptable Tiers",
		"Categorie Comptable Tiers",
	),
	(
		"Categorie comptable Tiers et code comptable Produit",
		"Categorie Comptable Tiers Et Code Comptable Produit",
	),
]


def _rename_doctype(old_name, new_name, dry_run):
	old_table = f"tab{old_name}"
	new_table = f"tab{new_name}"

	if dry_run:
		frappe.logger().info(f"[DRY RUN] RENAME TABLE `{old_table}` -> `{new_table}`")
		frappe.logger().info(f"[DRY RUN] Suppression métadonnées DocType '{old_name}'")
		return

	# Renommer la table
	frappe.db.commit()
	frappe.db.sql(f"ALTER TABLE `{old_table}` RENAME TO `{new_table}`", auto_commit=True)

	# Supprimer les métadonnées de l'ancien DocType
	# Le bench migrate recrée les nouvelles depuis les fichiers JSON
	frappe.db.sql("DELETE FROM `tabDocType` WHERE name = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocField` WHERE parent = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocPerm` WHERE parent = %s", old_name)
	frappe.db.commit()


def _merge_and_drop(old_name, new_name, dry_run):
	old_table = f"tab{old_name}"
	new_table = f"tab{new_name}"

	count = frappe.db.sql(f"SELECT COUNT(*) FROM `{old_table}`")[0][0]

	if dry_run:
		frappe.logger().info(
			f"[DRY RUN] Fusion : {count} lignes de `{old_table}` -> `{new_table}` (INSERT IGNORE)"
		)
		frappe.logger().info(f"[DRY RUN] DROP TABLE `{old_table}`")
		frappe.logger().info(f"[DRY RUN] Suppression métadonnées DocType '{old_name}'")
		return

	# Copier les lignes manquantes
	frappe.db.sql(f"INSERT IGNORE INTO `{new_table}` SELECT * FROM `{old_table}`")
	inserted = frappe.db.sql("SELECT ROW_COUNT()")[0][0]
	frappe.logger().info(f"Fusion : {inserted}/{count} lignes copiées")

	# Commiter avant le DROP TABLE (DDL = implicit commit dans MariaDB)
	frappe.db.commit()

	# Supprimer l'ancienne table
	frappe.db.sql(f"DROP TABLE `{old_table}`", auto_commit=True)
	frappe.logger().info(f"DROP TABLE `{old_table}` OK")

	# Supprimer uniquement les métadonnées de l'ancien DocType en base
	frappe.db.sql("DELETE FROM `tabDocType` WHERE name = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocField` WHERE parent = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocPerm` WHERE parent = %s", old_name)
	frappe.db.commit()
	frappe.logger().info(f"Métadonnées DocType '{old_name}' supprimées")


def execute(dry_run=False):
	frappe.logger().info(
		f"=== Patch migrate_categorie_comptable_tiers : démarrage {'(DRY RUN)' if dry_run else ''} ==="
	)

	for old_name, new_name in RENAMES:
		old_exists = frappe.db.exists("DocType", old_name)
		new_exists = frappe.db.exists("DocType", new_name)

		frappe.logger().info(f"DocType '{old_name}' exists={old_exists} | '{new_name}' exists={new_exists}")

		if not old_exists:
			frappe.logger().info(f"'{old_name}' inexistant - rien à faire.")
			continue

		if old_exists and not new_exists:
			# Cas propre : renommage direct
			_rename_doctype(old_name, new_name, dry_run)

		elif old_exists and new_exists:
			# Migration partielle : fusion
			frappe.logger().info("Les deux DocTypes coexistent - fusion en cours.")
			_merge_and_drop(old_name, new_name, dry_run)

	if not dry_run:
		frappe.db.commit()

	frappe.logger().info(
		f"=== Patch migrate_categorie_comptable_tiers : terminé {'(DRY RUN)' if dry_run else ''} ==="
	)
