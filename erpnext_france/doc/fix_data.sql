
### tout sauf les spécifique

SELECT inv.name,dest.item_name,itm.description, dest.income_account, src.compte_de_produits FROM
`tabSales Invoice Item` as dest, `tabSales Invoice` as inv, tabCustomer as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
WHERE dest.item_code=itm.name
 AND src.parent='Special Item Accountancy Code Default'
AND dest.parent=inv.name
AND inv.customer=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.income_account<>src.compte_de_produits
AND dest.item_name NOT LIKE 'ZPORT%';

UPDATE `tabSales Invoice Item` as dest, `tabSales Invoice` as inv, tabCustomer as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
    SET dest.income_account=src.compte_de_produits
    WHERE dest.item_code=itm.name
 AND src.parent='Special Item Accountancy Code Default'
AND dest.parent=inv.name
AND inv.customer=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.income_account<>src.compte_de_produits
AND dest.item_name NOT LIKE 'ZPORT%';

## seulement les spécifiques

SELECT inv.name,dest.item_name,itm.description, dest.income_account, src.compte_de_produits FROM
`tabSales Invoice Item` as dest, `tabSales Invoice` as inv, tabCustomer as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
WHERE dest.item_code=itm.name
 AND src.parent=dest.item_code
AND dest.parent=inv.name
AND inv.customer=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.income_account<>src.compte_de_produits;

UPDATE `tabSales Invoice Item` as dest, `tabSales Invoice` as inv, tabCustomer as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
    SET dest.income_account=src.compte_de_produits
WHERE dest.item_code=itm.name
 AND src.parent=dest.item_code
AND dest.parent=inv.name
AND inv.customer=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.income_account<>src.compte_de_produits;



### tout sauf les spécifiques

SELECT inv.name,dest.item_code, dest.expense_account, src.compte_de_charges FROM
`tabPurchase Invoice Item` as dest, `tabPurchase Invoice` as inv, tabSupplier as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
WHERE dest.item_code=itm.name
AND src.parent='Special Item Accountancy Code Default'
AND dest.parent=inv.name
AND inv.supplier=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.expense_account<>src.compte_de_charges
AND dest.item_name NOT LIKE 'ZPORT%';

UPDATE `tabPurchase Invoice Item` as dest, `tabPurchase Invoice` as inv, tabSupplier as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
SET dest.expense_account=src.compte_de_charges
WHERE dest.item_code=itm.name
AND src.parent='Special Item Accountancy Code Default'
AND dest.parent=inv.name
AND inv.supplier=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.expense_account<>src.compte_de_charges
AND dest.item_name NOT LIKE 'ZPORT%';

## seulement les spécifiques
SELECT inv.name,dest.item_code, dest.expense_account, src.compte_de_charges FROM
`tabPurchase Invoice Item` as dest, `tabPurchase Invoice` as inv, tabSupplier as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
WHERE dest.item_code=itm.name
AND src.parent=dest.item_code
AND dest.parent=inv.name
AND inv.supplier=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.expense_account<>src.compte_de_charges;

UPDATE `tabPurchase Invoice Item` as dest, `tabPurchase Invoice` as inv, tabSupplier as cust,
    `tabCategorie comptable Tiers et code comptable Produit` as src,
    tabItem as itm
SET dest.expense_account=src.compte_de_charges
WHERE dest.item_code=itm.name
AND src.parent=dest.item_code
AND dest.parent=inv.name
AND inv.supplier=cust.name
AND cust.categorie_comptable_tiers=src.categorie_comptable_tiers
AND dest.expense_account<>src.compte_de_charges;