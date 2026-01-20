## ERPNext France

App to hold regional code and localization for France, built on top of ERPNext.

### Introduction

ERPNext France aims to support regional customizations for France. The app is built on Frappe, a full-stack, meta-data driven, web framework, and integrates seamlessly with ERPNext, the most agile ERP software.

Some customizations include:
- Transaction Logs -
In order to be compliant with the latest finance law applicable to POS software, ERPNext France automatically registers all sales and payment transactions in a chained log. Additionally, the deletion of sales and payment transactions will also not be permitted, even if the appropriate permissions are given to the user.

- Le Fichier des Écritures Comptables [FEC] -
Since 2014, a legal requirement makes it mandatory for companies operating in France to provide a file of their general accounting postings by fiscal year corresponding to an electronic accounting journal.

For ERPNext France users this file can be generated using this report called Le Fichier des Écritures Comptables FEC.
Manage number of "0" at the end of account code in FEC

- Check VAT customer and supplier code from [European VIES](https://europa.eu/youreurope/business/taxation/vat/check-vat-number-vies/index_fr.htm)

- Manage Deposit Invoice (Facture d'acompte) that is a real invoice with a % of total paiement that need to be deducted as payment after

- Export for CIEL and Sage Accountancy journal for Sales and Buying only

- EcoTax management

- Easier Customer and Supplier creation with [API Sinene](https://api.gouv.fr/les-api/sirene_v3)

- Easier Item Taxe Template creation from company card

- Easier Deposit Item creation from company card

- Header and Footer for document "Francisé"

- Cannot delete invoices

- Payment terms before invoice (example 30% deposit invoice, 70% delivery)

- Codes NAF/APE (for customer and supplier)

- Company type from INSEE (for customer and supplier)


### Installation

Using bench, [install ERPNext](https://github.com/frappe/bench#installation) as mentioned here.

Once ERPNext is installed, add ERPNext France app to your bench by running

```sh
$ bench get-app https://github.com/scopen-coop/erpnext_france.git
```

After that, you can install the app on required site (let's say demo.com )by running

```sh
$ bench --site demo.com install-app erpnext_france
```

#### License

GNU General Public License V3

#### History
This app is originally a fork from https://github.com/britlog/erpnext_france.

And Scopen put some salt in it.

And Scopen manually merge feature from https://github.com/frappe/erpnext_france the is actually (version-14) still in the core but may be remove one day

The feature for VAT check is highly inspirated from erpnext_germany https://github.com/alyf-de/erpnext_germany
