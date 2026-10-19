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


def _log(msg):
	print(msg)
	frappe.logger().info(msg)


def _table_exists(table):
	# Comparaison sensible à la casse : sous Linux (lower_case_table_names=0),
	# "tabCategorie comptable Tiers" et "tabCategorie Comptable Tiers" sont deux tables distinctes
	return bool(
		frappe.db.sql(
			"""
			SELECT 1 FROM information_schema.tables
			WHERE table_schema = DATABASE() AND BINARY table_name = %s
			""",
			table,
		)
	)


def _count(table):
	return frappe.db.sql(f"SELECT COUNT(*) FROM `{table}`")[0][0]


def _delete_old_metadata(old_name, dry_run):
	# BINARY : sans ça, la collation insensible à la casse supprime aussi le nouveau DocType
	if dry_run:
		_log(f"[DRY RUN] Suppression métadonnées DocType '{old_name}' (casse exacte)")
		return

	frappe.db.sql("DELETE FROM `tabDocType` WHERE BINARY name = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocField` WHERE BINARY parent = %s", old_name)
	frappe.db.sql("DELETE FROM `tabDocPerm` WHERE BINARY parent = %s", old_name)
	frappe.db.commit()
	_log(f"Métadonnées DocType '{old_name}' supprimées")


def _rename_table(old_table, new_table, dry_run):
	if dry_run:
		_log(f"[DRY RUN] RENAME TABLE `{old_table}` -> `{new_table}`")
		return

	frappe.db.commit()
	frappe.db.sql(f"RENAME TABLE `{old_table}` TO `{new_table}`")
	frappe.db.commit()
	_log(f"RENAME TABLE `{old_table}` -> `{new_table}` OK")


def _merge_and_drop(old_table, new_table, dry_run):
	old_cols = [r[0] for r in frappe.db.sql(f"SHOW COLUMNS FROM `{old_table}`")]
	new_cols = {r[0] for r in frappe.db.sql(f"SHOW COLUMNS FROM `{new_table}`")}

	common = [c for c in old_cols if c in new_cols]
	lost = [c for c in old_cols if c not in new_cols]
	if lost:
		_log(f"ATTENTION : colonnes absentes de `{new_table}`, non copiées : {lost}")

	cols = ", ".join(f"`{c}`" for c in common)
	old_count = _count(old_table)
	new_count = _count(new_table)
	_log(f"`{old_table}` : {old_count} lignes | `{new_table}` : {new_count} lignes")

	if dry_run:
		_log(f"[DRY RUN] INSERT IGNORE {old_count} lignes de `{old_table}` -> `{new_table}`")
		_log(f"[DRY RUN] DROP TABLE `{old_table}` si toutes les lignes sont présentes")
		return

	frappe.db.sql(
		f"""
		INSERT IGNORE INTO `{new_table}` ({cols})
		SELECT {cols} FROM `{old_table}`
		"""
	)
	frappe.db.commit()

	missing = frappe.db.sql(
		f"""
		SELECT COUNT(*) FROM `{old_table}` o
		WHERE NOT EXISTS (SELECT 1 FROM `{new_table}` n WHERE n.name = o.name)
		"""
	)[0][0]

	_log(f"Après fusion : `{new_table}` = {_count(new_table)} lignes, {missing} lignes manquantes")

	if missing:
		_log(f"STOP : {missing} lignes non copiées, `{old_table}` conservée. À vérifier à la main.")
		return False

	frappe.db.sql(f"DROP TABLE `{old_table}`")
	frappe.db.commit()
	_log(f"DROP TABLE `{old_table}` OK")
	return True


def execute(dry_run=False):
	_log(f"=== Patch migrate_categorie_comptable_tiers : démarrage {'(DRY RUN)' if dry_run else ''} ===")

	for old_name, new_name in RENAMES:
		old_table = f"tab{old_name}"
		new_table = f"tab{new_name}"

		old_exists = _table_exists(old_table)
		new_exists = _table_exists(new_table)
		_log(f"`{old_table}` exists={old_exists} | `{new_table}` exists={new_exists}")

		if not old_exists:
			_log(f"`{old_table}` inexistante, rien à faire.")
			continue

		if not new_exists:
			_rename_table(old_table, new_table, dry_run)
			_delete_old_metadata(old_name, dry_run)
		else:
			ok = _merge_and_drop(old_table, new_table, dry_run)
			if ok or dry_run:
				_delete_old_metadata(old_name, dry_run)

	if not dry_run:
		frappe.db.commit()

	_log(f"=== Patch migrate_categorie_comptable_tiers : terminé {'(DRY RUN)' if dry_run else ''} ===")