# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt


import frappe


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            for tabName in ["tabCompany", "tabCustomer", "tabSupplier"]:
                frappe.db.sql(
                    """update {} set code_naf='0111Z' WHERE code_naf='1'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0123Z' WHERE code_naf='10'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1310Z' WHERE code_naf='100'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1320Z' WHERE code_naf='101'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1330Z' WHERE code_naf='102'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1391Z' WHERE code_naf='103'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1392Z' WHERE code_naf='104'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1393Z' WHERE code_naf='105'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1394Z' WHERE code_naf='106'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1395Z' WHERE code_naf='107'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1396Z' WHERE code_naf='108'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1399Z' WHERE code_naf='109'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0124Z' WHERE code_naf='11'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1411Z' WHERE code_naf='110'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1412Z' WHERE code_naf='111'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1413Z' WHERE code_naf='112'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1414Z' WHERE code_naf='113'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1419Z' WHERE code_naf='114'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1420Z' WHERE code_naf='115'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1431Z' WHERE code_naf='116'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1439Z' WHERE code_naf='117'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1511Z' WHERE code_naf='118'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1512Z' WHERE code_naf='119'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0125Z' WHERE code_naf='12'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1520Z' WHERE code_naf='120'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1610A' WHERE code_naf='121'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1610B' WHERE code_naf='122'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1621Z' WHERE code_naf='123'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1622Z' WHERE code_naf='124'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1623Z' WHERE code_naf='125'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1624Z' WHERE code_naf='126'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1629Z' WHERE code_naf='127'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1711Z' WHERE code_naf='128'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1712Z' WHERE code_naf='129'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0126Z' WHERE code_naf='13'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721A' WHERE code_naf='130'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721B' WHERE code_naf='131'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721C' WHERE code_naf='132'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1722Z' WHERE code_naf='133'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1723Z' WHERE code_naf='134'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1724Z' WHERE code_naf='135'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1729Z' WHERE code_naf='136'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1811Z' WHERE code_naf='137'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1812Z' WHERE code_naf='138'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1813Z' WHERE code_naf='139'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0127Z' WHERE code_naf='14'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1814Z' WHERE code_naf='140'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1820Z' WHERE code_naf='141'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1910Z' WHERE code_naf='142'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1920Z' WHERE code_naf='143'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2011Z' WHERE code_naf='144'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2012Z' WHERE code_naf='145'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2013A' WHERE code_naf='146'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2013B' WHERE code_naf='147'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2014Z' WHERE code_naf='148'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2015Z' WHERE code_naf='149'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0128Z' WHERE code_naf='15'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2016Z' WHERE code_naf='150'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2017Z' WHERE code_naf='151'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2020Z' WHERE code_naf='152'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2030Z' WHERE code_naf='153'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2041Z' WHERE code_naf='154'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2042Z' WHERE code_naf='155'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2051Z' WHERE code_naf='156'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2052Z' WHERE code_naf='157'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2053Z' WHERE code_naf='158'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2059Z' WHERE code_naf='159'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0129Z' WHERE code_naf='16'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2060Z' WHERE code_naf='160'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2110Z' WHERE code_naf='161'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2120Z' WHERE code_naf='162'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2211Z' WHERE code_naf='163'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2219Z' WHERE code_naf='164'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2221Z' WHERE code_naf='165'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2222Z' WHERE code_naf='166'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2223Z' WHERE code_naf='167'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2229A' WHERE code_naf='168'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2229B' WHERE code_naf='169'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0130Z' WHERE code_naf='17'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2311Z' WHERE code_naf='170'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2312Z' WHERE code_naf='171'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2313Z' WHERE code_naf='172'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2314Z' WHERE code_naf='173'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2319Z' WHERE code_naf='174'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2320Z' WHERE code_naf='175'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2331Z' WHERE code_naf='176'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2332Z' WHERE code_naf='177'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2341Z' WHERE code_naf='178'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2342Z' WHERE code_naf='179'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0141Z' WHERE code_naf='18'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2343Z' WHERE code_naf='180'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2344Z' WHERE code_naf='181'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2349Z' WHERE code_naf='182'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2351Z' WHERE code_naf='183'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2352Z' WHERE code_naf='184'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2361Z' WHERE code_naf='185'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2362Z' WHERE code_naf='186'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2363Z' WHERE code_naf='187'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2364Z' WHERE code_naf='188'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2365Z' WHERE code_naf='189'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0142Z' WHERE code_naf='19'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2369Z' WHERE code_naf='190'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2370Z' WHERE code_naf='191'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2391Z' WHERE code_naf='192'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2399Z' WHERE code_naf='193'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2410Z' WHERE code_naf='194'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2420Z' WHERE code_naf='195'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2431Z' WHERE code_naf='196'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2432Z' WHERE code_naf='197'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2433Z' WHERE code_naf='198'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2434Z' WHERE code_naf='199'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0112Z' WHERE code_naf='2'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0143Z' WHERE code_naf='20'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2441Z' WHERE code_naf='200'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2442Z' WHERE code_naf='201'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2443Z' WHERE code_naf='202'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2444Z' WHERE code_naf='203'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2445Z' WHERE code_naf='204'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2446Z' WHERE code_naf='205'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2451Z' WHERE code_naf='206'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2452Z' WHERE code_naf='207'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2453Z' WHERE code_naf='208'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2454Z' WHERE code_naf='209'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0144Z' WHERE code_naf='21'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2511Z' WHERE code_naf='210'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2512Z' WHERE code_naf='211'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2521Z' WHERE code_naf='212'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2529Z' WHERE code_naf='213'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2530Z' WHERE code_naf='214'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2540Z' WHERE code_naf='215'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2550A' WHERE code_naf='216'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2550B' WHERE code_naf='217'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2561Z' WHERE code_naf='218'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2562A' WHERE code_naf='219'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0145Z' WHERE code_naf='22'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2562B' WHERE code_naf='220'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2571Z' WHERE code_naf='221'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2572Z' WHERE code_naf='222'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2573A' WHERE code_naf='223'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2573B' WHERE code_naf='224'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2591Z' WHERE code_naf='225'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2592Z' WHERE code_naf='226'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2593Z' WHERE code_naf='227'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2594Z' WHERE code_naf='228'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2599A' WHERE code_naf='229'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0146Z' WHERE code_naf='23'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2599B' WHERE code_naf='230'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2611Z' WHERE code_naf='231'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2612Z' WHERE code_naf='232'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2620Z' WHERE code_naf='233'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2630Z' WHERE code_naf='234'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2640Z' WHERE code_naf='235'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2651A' WHERE code_naf='236'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2651B' WHERE code_naf='237'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2652Z' WHERE code_naf='238'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2660Z' WHERE code_naf='239'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0147Z' WHERE code_naf='24'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2670Z' WHERE code_naf='240'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2680Z' WHERE code_naf='241'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2711Z' WHERE code_naf='242'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2712Z' WHERE code_naf='243'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2720Z' WHERE code_naf='244'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2731Z' WHERE code_naf='245'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2732Z' WHERE code_naf='246'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2733Z' WHERE code_naf='247'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2740Z' WHERE code_naf='248'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2751Z' WHERE code_naf='249'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0149Z' WHERE code_naf='25'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2752Z' WHERE code_naf='250'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2790Z' WHERE code_naf='251'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2811Z' WHERE code_naf='252'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2812Z' WHERE code_naf='253'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2813Z' WHERE code_naf='254'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2814Z' WHERE code_naf='255'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2815Z' WHERE code_naf='256'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2821Z' WHERE code_naf='257'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2822Z' WHERE code_naf='258'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2823Z' WHERE code_naf='259'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0150Z' WHERE code_naf='26'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2824Z' WHERE code_naf='260'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2825Z' WHERE code_naf='261'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2829A' WHERE code_naf='262'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2829B' WHERE code_naf='263'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2830Z' WHERE code_naf='264'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2841Z' WHERE code_naf='265'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2849Z' WHERE code_naf='266'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2891Z' WHERE code_naf='267'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2892Z' WHERE code_naf='268'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2893Z' WHERE code_naf='269'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0161Z' WHERE code_naf='27'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2894Z' WHERE code_naf='270'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2895Z' WHERE code_naf='271'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2896Z' WHERE code_naf='272'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2899A' WHERE code_naf='273'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2899B' WHERE code_naf='274'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2910Z' WHERE code_naf='275'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2920Z' WHERE code_naf='276'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2931Z' WHERE code_naf='277'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2932Z' WHERE code_naf='278'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3011Z' WHERE code_naf='279'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0162Z' WHERE code_naf='28'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3012Z' WHERE code_naf='280'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3020Z' WHERE code_naf='281'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3030Z' WHERE code_naf='282'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3040Z' WHERE code_naf='283'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3091Z' WHERE code_naf='284'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3092Z' WHERE code_naf='285'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3099Z' WHERE code_naf='286'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3101Z' WHERE code_naf='287'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3102Z' WHERE code_naf='288'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3103Z' WHERE code_naf='289'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0163Z' WHERE code_naf='29'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3109A' WHERE code_naf='290'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3109B' WHERE code_naf='291'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3211Z' WHERE code_naf='292'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3212Z' WHERE code_naf='293'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3213Z' WHERE code_naf='294'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3220Z' WHERE code_naf='295'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3230Z' WHERE code_naf='296'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3240Z' WHERE code_naf='297'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3250A' WHERE code_naf='298'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3250B' WHERE code_naf='299'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0113Z' WHERE code_naf='3'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0164Z' WHERE code_naf='30'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3291Z' WHERE code_naf='300'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3299Z' WHERE code_naf='301'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3311Z' WHERE code_naf='302'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3312Z' WHERE code_naf='303'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3313Z' WHERE code_naf='304'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3314Z' WHERE code_naf='305'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3315Z' WHERE code_naf='306'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3316Z' WHERE code_naf='307'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3317Z' WHERE code_naf='308'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3319Z' WHERE code_naf='309'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0170Z' WHERE code_naf='31'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320A' WHERE code_naf='310'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320B' WHERE code_naf='311'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320C' WHERE code_naf='312'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320D' WHERE code_naf='313'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3511Z' WHERE code_naf='314'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3512Z' WHERE code_naf='315'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3513Z' WHERE code_naf='316'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3514Z' WHERE code_naf='317'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3521Z' WHERE code_naf='318'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3522Z' WHERE code_naf='319'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0210Z' WHERE code_naf='32'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3523Z' WHERE code_naf='320'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3530Z' WHERE code_naf='321'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3600Z' WHERE code_naf='322'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3700Z' WHERE code_naf='323'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3811Z' WHERE code_naf='324'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3812Z' WHERE code_naf='325'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3821Z' WHERE code_naf='326'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3822Z' WHERE code_naf='327'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3831Z' WHERE code_naf='328'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3832Z' WHERE code_naf='329'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0220Z' WHERE code_naf='33'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3900Z' WHERE code_naf='330'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110A' WHERE code_naf='331'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110B' WHERE code_naf='332'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110C' WHERE code_naf='333'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110D' WHERE code_naf='334'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4120A' WHERE code_naf='335'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4120B' WHERE code_naf='336'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4211Z' WHERE code_naf='337'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4212Z' WHERE code_naf='338'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4213A' WHERE code_naf='339'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0230Z' WHERE code_naf='34'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4213B' WHERE code_naf='340'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4221Z' WHERE code_naf='341'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4222Z' WHERE code_naf='342'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4291Z' WHERE code_naf='343'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4299Z' WHERE code_naf='344'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4311Z' WHERE code_naf='345'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4312A' WHERE code_naf='346'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4312B' WHERE code_naf='347'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4313Z' WHERE code_naf='348'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4321A' WHERE code_naf='349'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0240Z' WHERE code_naf='35'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4321B' WHERE code_naf='350'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4322A' WHERE code_naf='351'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4322B' WHERE code_naf='352'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4329A' WHERE code_naf='353'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4329B' WHERE code_naf='354'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4331Z' WHERE code_naf='355'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332A' WHERE code_naf='356'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332B' WHERE code_naf='357'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332C' WHERE code_naf='358'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4333Z' WHERE code_naf='359'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0311Z' WHERE code_naf='36'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4334Z' WHERE code_naf='360'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4339Z' WHERE code_naf='361'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4391A' WHERE code_naf='362'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4391B' WHERE code_naf='363'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399A' WHERE code_naf='364'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399B' WHERE code_naf='365'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399C' WHERE code_naf='366'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399D' WHERE code_naf='367'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399E' WHERE code_naf='368'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4511Z' WHERE code_naf='369'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0312Z' WHERE code_naf='37'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4519Z' WHERE code_naf='370'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4520A' WHERE code_naf='371'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4520B' WHERE code_naf='372'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4531Z' WHERE code_naf='373'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4532Z' WHERE code_naf='374'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4540Z' WHERE code_naf='375'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4611Z' WHERE code_naf='376'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4612A' WHERE code_naf='377'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4612B' WHERE code_naf='378'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4613Z' WHERE code_naf='379'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0321Z' WHERE code_naf='38'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4614Z' WHERE code_naf='380'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4615Z' WHERE code_naf='381'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4616Z' WHERE code_naf='382'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4617A' WHERE code_naf='383'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4617B' WHERE code_naf='384'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4618Z' WHERE code_naf='385'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4619A' WHERE code_naf='386'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4619B' WHERE code_naf='387'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4621Z' WHERE code_naf='388'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4622Z' WHERE code_naf='389'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0322Z' WHERE code_naf='39'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4623Z' WHERE code_naf='390'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4624Z' WHERE code_naf='391'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4631Z' WHERE code_naf='392'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632A' WHERE code_naf='393'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632B' WHERE code_naf='394'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632C' WHERE code_naf='395'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4633Z' WHERE code_naf='396'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4634Z' WHERE code_naf='397'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4635Z' WHERE code_naf='398'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4636Z' WHERE code_naf='399'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0114Z' WHERE code_naf='4'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0510Z' WHERE code_naf='40'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4637Z' WHERE code_naf='400'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4638A' WHERE code_naf='401'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4638B' WHERE code_naf='402'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4639A' WHERE code_naf='403'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4639B' WHERE code_naf='404'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4641Z' WHERE code_naf='405'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4642Z' WHERE code_naf='406'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4643Z' WHERE code_naf='407'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4644Z' WHERE code_naf='408'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4645Z' WHERE code_naf='409'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0520Z' WHERE code_naf='41'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4646Z' WHERE code_naf='410'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4647Z' WHERE code_naf='411'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4648Z' WHERE code_naf='412'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4649Z' WHERE code_naf='413'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4651Z' WHERE code_naf='414'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4652Z' WHERE code_naf='415'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4661Z' WHERE code_naf='416'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4662Z' WHERE code_naf='417'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4663Z' WHERE code_naf='418'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4664Z' WHERE code_naf='419'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0610Z' WHERE code_naf='42'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4665Z' WHERE code_naf='420'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4666Z' WHERE code_naf='421'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669A' WHERE code_naf='422'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669B' WHERE code_naf='423'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669C' WHERE code_naf='424'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4671Z' WHERE code_naf='425'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4672Z' WHERE code_naf='426'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4673A' WHERE code_naf='427'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4673B' WHERE code_naf='428'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4674A' WHERE code_naf='429'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0620Z' WHERE code_naf='43'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4674B' WHERE code_naf='430'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4675Z' WHERE code_naf='431'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4676Z' WHERE code_naf='432'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4677Z' WHERE code_naf='433'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4690Z' WHERE code_naf='434'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711A' WHERE code_naf='435'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711B' WHERE code_naf='436'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711C' WHERE code_naf='437'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711D' WHERE code_naf='438'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711E' WHERE code_naf='439'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0710Z' WHERE code_naf='44'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711F' WHERE code_naf='440'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4719A' WHERE code_naf='441'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4719B' WHERE code_naf='442'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4721Z' WHERE code_naf='443'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4722Z' WHERE code_naf='444'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4723Z' WHERE code_naf='445'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4724Z' WHERE code_naf='446'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4725Z' WHERE code_naf='447'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4726Z' WHERE code_naf='448'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4729Z' WHERE code_naf='449'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0721Z' WHERE code_naf='45'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4730Z' WHERE code_naf='450'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4741Z' WHERE code_naf='451'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4742Z' WHERE code_naf='452'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4743Z' WHERE code_naf='453'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4751Z' WHERE code_naf='454'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4752A' WHERE code_naf='455'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4752B' WHERE code_naf='456'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4753Z' WHERE code_naf='457'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4754Z' WHERE code_naf='458'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4759A' WHERE code_naf='459'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0729Z' WHERE code_naf='46'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4759B' WHERE code_naf='460'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4761Z' WHERE code_naf='461'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4762Z' WHERE code_naf='462'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4763Z' WHERE code_naf='463'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4764Z' WHERE code_naf='464'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4765Z' WHERE code_naf='465'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4771Z' WHERE code_naf='466'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4772A' WHERE code_naf='467'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4772B' WHERE code_naf='468'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4773Z' WHERE code_naf='469'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0811Z' WHERE code_naf='47'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4774Z' WHERE code_naf='470'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4775Z' WHERE code_naf='471'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4776Z' WHERE code_naf='472'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4777Z' WHERE code_naf='473'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778A' WHERE code_naf='474'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778B' WHERE code_naf='475'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778C' WHERE code_naf='476'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4779Z' WHERE code_naf='477'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4781Z' WHERE code_naf='478'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4782Z' WHERE code_naf='479'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0812Z' WHERE code_naf='48'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4789Z' WHERE code_naf='480'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4791A' WHERE code_naf='481'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4791B' WHERE code_naf='482'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4799A' WHERE code_naf='483'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4799B' WHERE code_naf='484'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4910Z' WHERE code_naf='485'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4920Z' WHERE code_naf='486'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4931Z' WHERE code_naf='487'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4932Z' WHERE code_naf='488'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939A' WHERE code_naf='489'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0891Z' WHERE code_naf='49'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939B' WHERE code_naf='490'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939C' WHERE code_naf='491'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941A' WHERE code_naf='492'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941B' WHERE code_naf='493'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941C' WHERE code_naf='494'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4942Z' WHERE code_naf='495'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4950Z' WHERE code_naf='496'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5010Z' WHERE code_naf='497'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5020Z' WHERE code_naf='498'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5030Z' WHERE code_naf='499'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0115Z' WHERE code_naf='5'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0892Z' WHERE code_naf='50'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5040Z' WHERE code_naf='500'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5110Z' WHERE code_naf='501'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5121Z' WHERE code_naf='502'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5122Z' WHERE code_naf='503'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5210A' WHERE code_naf='504'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5210B' WHERE code_naf='505'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5221Z' WHERE code_naf='506'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5222Z' WHERE code_naf='507'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5223Z' WHERE code_naf='508'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5224A' WHERE code_naf='509'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0893Z' WHERE code_naf='51'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5224B' WHERE code_naf='510'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5229A' WHERE code_naf='511'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5229B' WHERE code_naf='512'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5310Z' WHERE code_naf='513'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5320Z' WHERE code_naf='514'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5510Z' WHERE code_naf='515'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5520Z' WHERE code_naf='516'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5530Z' WHERE code_naf='517'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5590Z' WHERE code_naf='518'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610A' WHERE code_naf='519'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0899Z' WHERE code_naf='52'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610B' WHERE code_naf='520'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610C' WHERE code_naf='521'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5621Z' WHERE code_naf='522'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5629A' WHERE code_naf='523'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5629B' WHERE code_naf='524'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5630Z' WHERE code_naf='525'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5811Z' WHERE code_naf='526'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5812Z' WHERE code_naf='527'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5813Z' WHERE code_naf='528'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5814Z' WHERE code_naf='529'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0910Z' WHERE code_naf='53'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5819Z' WHERE code_naf='530'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5821Z' WHERE code_naf='531'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829A' WHERE code_naf='532'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829B' WHERE code_naf='533'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829C' WHERE code_naf='534'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911A' WHERE code_naf='535'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911B' WHERE code_naf='536'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911C' WHERE code_naf='537'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5912Z' WHERE code_naf='538'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5913A' WHERE code_naf='539'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0990Z' WHERE code_naf='54'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5913B' WHERE code_naf='540'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5914Z' WHERE code_naf='541'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5920Z' WHERE code_naf='542'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6010Z' WHERE code_naf='543'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6020A' WHERE code_naf='544'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6020B' WHERE code_naf='545'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6110Z' WHERE code_naf='546'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6120Z' WHERE code_naf='547'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6130Z' WHERE code_naf='548'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6190Z' WHERE code_naf='549'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1011Z' WHERE code_naf='55'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6201Z' WHERE code_naf='550'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6202A' WHERE code_naf='551'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6202B' WHERE code_naf='552'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6203Z' WHERE code_naf='553'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6209Z' WHERE code_naf='554'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6311Z' WHERE code_naf='555'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6312Z' WHERE code_naf='556'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6391Z' WHERE code_naf='557'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6399Z' WHERE code_naf='558'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6411Z' WHERE code_naf='559'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1012Z' WHERE code_naf='56'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6419Z' WHERE code_naf='560'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6420Z' WHERE code_naf='561'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6430Z' WHERE code_naf='562'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6491Z' WHERE code_naf='563'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6492Z' WHERE code_naf='564'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6499Z' WHERE code_naf='565'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6511Z' WHERE code_naf='566'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6512Z' WHERE code_naf='567'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6520Z' WHERE code_naf='568'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6530Z' WHERE code_naf='569'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1013A' WHERE code_naf='57'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6611Z' WHERE code_naf='570'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6612Z' WHERE code_naf='571'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6619A' WHERE code_naf='572'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6619B' WHERE code_naf='573'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6621Z' WHERE code_naf='574'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6622Z' WHERE code_naf='575'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6629Z' WHERE code_naf='576'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6630Z' WHERE code_naf='577'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6810Z' WHERE code_naf='578'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6820A' WHERE code_naf='579'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1013B' WHERE code_naf='58'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6820B' WHERE code_naf='580'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6831Z' WHERE code_naf='581'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6832A' WHERE code_naf='582'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6832B' WHERE code_naf='583'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6910Z' WHERE code_naf='584'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6920Z' WHERE code_naf='585'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7010Z' WHERE code_naf='586'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7021Z' WHERE code_naf='587'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7022Z' WHERE code_naf='588'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7111Z' WHERE code_naf='589'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1020Z' WHERE code_naf='59'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7112A' WHERE code_naf='590'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7112B' WHERE code_naf='591'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7120A' WHERE code_naf='592'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7120B' WHERE code_naf='593'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7211Z' WHERE code_naf='594'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7219Z' WHERE code_naf='595'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7220Z' WHERE code_naf='596'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7311Z' WHERE code_naf='597'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7312Z' WHERE code_naf='598'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7320Z' WHERE code_naf='599'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0116Z' WHERE code_naf='6'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1031Z' WHERE code_naf='60'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7410Z' WHERE code_naf='600'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7420Z' WHERE code_naf='601'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7430Z' WHERE code_naf='602'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7490A' WHERE code_naf='603'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7490B' WHERE code_naf='604'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7500Z' WHERE code_naf='605'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7711A' WHERE code_naf='606'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7711B' WHERE code_naf='607'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7712Z' WHERE code_naf='608'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7721Z' WHERE code_naf='609'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1032Z' WHERE code_naf='61'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7722Z' WHERE code_naf='610'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7729Z' WHERE code_naf='611'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7731Z' WHERE code_naf='612'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7732Z' WHERE code_naf='613'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7733Z' WHERE code_naf='614'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7734Z' WHERE code_naf='615'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7735Z' WHERE code_naf='616'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7739Z' WHERE code_naf='617'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7740Z' WHERE code_naf='618'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7810Z' WHERE code_naf='619'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1039A' WHERE code_naf='62'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7820Z' WHERE code_naf='620'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7830Z' WHERE code_naf='621'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7911Z' WHERE code_naf='622'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7912Z' WHERE code_naf='623'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7990Z' WHERE code_naf='624'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8010Z' WHERE code_naf='625'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8020Z' WHERE code_naf='626'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8030Z' WHERE code_naf='627'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8110Z' WHERE code_naf='628'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8121Z' WHERE code_naf='629'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1039B' WHERE code_naf='63'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8122Z' WHERE code_naf='630'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8129A' WHERE code_naf='631'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8129B' WHERE code_naf='632'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8130Z' WHERE code_naf='633'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8211Z' WHERE code_naf='634'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8219Z' WHERE code_naf='635'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8220Z' WHERE code_naf='636'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8230Z' WHERE code_naf='637'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8291Z' WHERE code_naf='638'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8292Z' WHERE code_naf='639'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1041A' WHERE code_naf='64'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8299Z' WHERE code_naf='640'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8411Z' WHERE code_naf='641'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8412Z' WHERE code_naf='642'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8413Z' WHERE code_naf='643'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8421Z' WHERE code_naf='644'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8422Z' WHERE code_naf='645'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8423Z' WHERE code_naf='646'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8424Z' WHERE code_naf='647'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8425Z' WHERE code_naf='648'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430A' WHERE code_naf='649'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1041B' WHERE code_naf='65'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430B' WHERE code_naf='650'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430C' WHERE code_naf='651'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8510Z' WHERE code_naf='652'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8520Z' WHERE code_naf='653'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8531Z' WHERE code_naf='654'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8532Z' WHERE code_naf='655'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8541Z' WHERE code_naf='656'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8542Z' WHERE code_naf='657'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8551Z' WHERE code_naf='658'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8552Z' WHERE code_naf='659'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1042Z' WHERE code_naf='66'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8553Z' WHERE code_naf='660'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8559A' WHERE code_naf='661'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8559B' WHERE code_naf='662'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8560Z' WHERE code_naf='663'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8610Z' WHERE code_naf='664'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8621Z' WHERE code_naf='665'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622A' WHERE code_naf='666'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622B' WHERE code_naf='667'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622C' WHERE code_naf='668'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8623Z' WHERE code_naf='669'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051A' WHERE code_naf='67'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690A' WHERE code_naf='670'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690B' WHERE code_naf='671'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690C' WHERE code_naf='672'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690D' WHERE code_naf='673'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690E' WHERE code_naf='674'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690F' WHERE code_naf='675'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710A' WHERE code_naf='676'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710B' WHERE code_naf='677'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710C' WHERE code_naf='678'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8720A' WHERE code_naf='679'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051B' WHERE code_naf='68'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8720B' WHERE code_naf='680'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8730A' WHERE code_naf='681'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8730B' WHERE code_naf='682'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8790A' WHERE code_naf='683'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8790B' WHERE code_naf='684'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810A' WHERE code_naf='685'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810B' WHERE code_naf='686'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810C' WHERE code_naf='687'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8891A' WHERE code_naf='688'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8891B' WHERE code_naf='689'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051C' WHERE code_naf='69'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8899A' WHERE code_naf='690'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8899B' WHERE code_naf='691'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9001Z' WHERE code_naf='692'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9002Z' WHERE code_naf='693'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9003A' WHERE code_naf='694'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9003B' WHERE code_naf='695'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9004Z' WHERE code_naf='696'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9101Z' WHERE code_naf='697'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9102Z' WHERE code_naf='698'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9103Z' WHERE code_naf='699'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0119Z' WHERE code_naf='7'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051D' WHERE code_naf='70'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9104Z' WHERE code_naf='700'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9200Z' WHERE code_naf='701'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9311Z' WHERE code_naf='702'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9312Z' WHERE code_naf='703'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9313Z' WHERE code_naf='704'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9319Z' WHERE code_naf='705'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9321Z' WHERE code_naf='706'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9329Z' WHERE code_naf='707'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9411Z' WHERE code_naf='708'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9412Z' WHERE code_naf='709'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1052Z' WHERE code_naf='71'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9420Z' WHERE code_naf='710'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9491Z' WHERE code_naf='711'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9492Z' WHERE code_naf='712'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9499Z' WHERE code_naf='713'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9511Z' WHERE code_naf='714'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9512Z' WHERE code_naf='715'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9521Z' WHERE code_naf='716'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9522Z' WHERE code_naf='717'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9523Z' WHERE code_naf='718'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9524Z' WHERE code_naf='719'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1061A' WHERE code_naf='72'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9525Z' WHERE code_naf='720'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9529Z' WHERE code_naf='721'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9601A' WHERE code_naf='722'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9601B' WHERE code_naf='723'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9602A' WHERE code_naf='724'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9602B' WHERE code_naf='725'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9603Z' WHERE code_naf='726'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9604Z' WHERE code_naf='727'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9609Z' WHERE code_naf='728'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9700Z' WHERE code_naf='729'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1061B' WHERE code_naf='73'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9810Z' WHERE code_naf='730'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9820Z' WHERE code_naf='731'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9900Z' WHERE code_naf='732'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1062Z' WHERE code_naf='74'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071A' WHERE code_naf='75'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071B' WHERE code_naf='76'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071C' WHERE code_naf='77'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071D' WHERE code_naf='78'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1072Z' WHERE code_naf='79'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0121Z' WHERE code_naf='8'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1073Z' WHERE code_naf='80'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1081Z' WHERE code_naf='81'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1082Z' WHERE code_naf='82'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1083Z' WHERE code_naf='83'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1084Z' WHERE code_naf='84'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1085Z' WHERE code_naf='85'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1086Z' WHERE code_naf='86'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1089Z' WHERE code_naf='87'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1091Z' WHERE code_naf='88'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1092Z' WHERE code_naf='89'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0122Z' WHERE code_naf='9'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1101Z' WHERE code_naf='90'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1102A' WHERE code_naf='91'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1102B' WHERE code_naf='92'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1103Z' WHERE code_naf='93'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1104Z' WHERE code_naf='94'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1105Z' WHERE code_naf='95'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1106Z' WHERE code_naf='96'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1107A' WHERE code_naf='97'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1107B' WHERE code_naf='98'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1200Z' WHERE code_naf='99'""".format(
                        tabName
                    )
                )

        except Exception:
            frappe.log_error("Failed to migrate Code Naf.")
