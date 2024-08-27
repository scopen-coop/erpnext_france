# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt


import frappe


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            for tabName in ["tabCompany", "tabCustomer", "tabSupplier"]:
                frappe.db.sql(
                    """update {} set code_naf='0111Z' WHERE naf_code='1'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0123Z' WHERE naf_code='10'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1310Z' WHERE naf_code='100'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1320Z' WHERE naf_code='101'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1330Z' WHERE naf_code='102'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1391Z' WHERE naf_code='103'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1392Z' WHERE naf_code='104'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1393Z' WHERE naf_code='105'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1394Z' WHERE naf_code='106'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1395Z' WHERE naf_code='107'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1396Z' WHERE naf_code='108'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1399Z' WHERE naf_code='109'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0124Z' WHERE naf_code='11'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1411Z' WHERE naf_code='110'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1412Z' WHERE naf_code='111'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1413Z' WHERE naf_code='112'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1414Z' WHERE naf_code='113'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1419Z' WHERE naf_code='114'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1420Z' WHERE naf_code='115'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1431Z' WHERE naf_code='116'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1439Z' WHERE naf_code='117'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1511Z' WHERE naf_code='118'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1512Z' WHERE naf_code='119'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0125Z' WHERE naf_code='12'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1520Z' WHERE naf_code='120'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1610A' WHERE naf_code='121'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1610B' WHERE naf_code='122'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1621Z' WHERE naf_code='123'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1622Z' WHERE naf_code='124'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1623Z' WHERE naf_code='125'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1624Z' WHERE naf_code='126'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1629Z' WHERE naf_code='127'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1711Z' WHERE naf_code='128'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1712Z' WHERE naf_code='129'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0126Z' WHERE naf_code='13'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721A' WHERE naf_code='130'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721B' WHERE naf_code='131'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1721C' WHERE naf_code='132'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1722Z' WHERE naf_code='133'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1723Z' WHERE naf_code='134'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1724Z' WHERE naf_code='135'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1729Z' WHERE naf_code='136'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1811Z' WHERE naf_code='137'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1812Z' WHERE naf_code='138'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1813Z' WHERE naf_code='139'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0127Z' WHERE naf_code='14'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1814Z' WHERE naf_code='140'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1820Z' WHERE naf_code='141'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1910Z' WHERE naf_code='142'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1920Z' WHERE naf_code='143'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2011Z' WHERE naf_code='144'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2012Z' WHERE naf_code='145'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2013A' WHERE naf_code='146'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2013B' WHERE naf_code='147'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2014Z' WHERE naf_code='148'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2015Z' WHERE naf_code='149'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0128Z' WHERE naf_code='15'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2016Z' WHERE naf_code='150'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2017Z' WHERE naf_code='151'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2020Z' WHERE naf_code='152'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2030Z' WHERE naf_code='153'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2041Z' WHERE naf_code='154'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2042Z' WHERE naf_code='155'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2051Z' WHERE naf_code='156'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2052Z' WHERE naf_code='157'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2053Z' WHERE naf_code='158'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2059Z' WHERE naf_code='159'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0129Z' WHERE naf_code='16'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2060Z' WHERE naf_code='160'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2110Z' WHERE naf_code='161'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2120Z' WHERE naf_code='162'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2211Z' WHERE naf_code='163'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2219Z' WHERE naf_code='164'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2221Z' WHERE naf_code='165'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2222Z' WHERE naf_code='166'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2223Z' WHERE naf_code='167'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2229A' WHERE naf_code='168'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2229B' WHERE naf_code='169'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0130Z' WHERE naf_code='17'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2311Z' WHERE naf_code='170'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2312Z' WHERE naf_code='171'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2313Z' WHERE naf_code='172'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2314Z' WHERE naf_code='173'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2319Z' WHERE naf_code='174'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2320Z' WHERE naf_code='175'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2331Z' WHERE naf_code='176'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2332Z' WHERE naf_code='177'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2341Z' WHERE naf_code='178'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2342Z' WHERE naf_code='179'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0141Z' WHERE naf_code='18'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2343Z' WHERE naf_code='180'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2344Z' WHERE naf_code='181'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2349Z' WHERE naf_code='182'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2351Z' WHERE naf_code='183'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2352Z' WHERE naf_code='184'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2361Z' WHERE naf_code='185'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2362Z' WHERE naf_code='186'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2363Z' WHERE naf_code='187'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2364Z' WHERE naf_code='188'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2365Z' WHERE naf_code='189'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0142Z' WHERE naf_code='19'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2369Z' WHERE naf_code='190'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2370Z' WHERE naf_code='191'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2391Z' WHERE naf_code='192'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2399Z' WHERE naf_code='193'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2410Z' WHERE naf_code='194'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2420Z' WHERE naf_code='195'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2431Z' WHERE naf_code='196'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2432Z' WHERE naf_code='197'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2433Z' WHERE naf_code='198'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2434Z' WHERE naf_code='199'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0112Z' WHERE naf_code='2'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0143Z' WHERE naf_code='20'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2441Z' WHERE naf_code='200'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2442Z' WHERE naf_code='201'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2443Z' WHERE naf_code='202'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2444Z' WHERE naf_code='203'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2445Z' WHERE naf_code='204'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2446Z' WHERE naf_code='205'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2451Z' WHERE naf_code='206'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2452Z' WHERE naf_code='207'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2453Z' WHERE naf_code='208'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2454Z' WHERE naf_code='209'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0144Z' WHERE naf_code='21'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2511Z' WHERE naf_code='210'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2512Z' WHERE naf_code='211'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2521Z' WHERE naf_code='212'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2529Z' WHERE naf_code='213'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2530Z' WHERE naf_code='214'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2540Z' WHERE naf_code='215'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2550A' WHERE naf_code='216'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2550B' WHERE naf_code='217'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2561Z' WHERE naf_code='218'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2562A' WHERE naf_code='219'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0145Z' WHERE naf_code='22'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2562B' WHERE naf_code='220'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2571Z' WHERE naf_code='221'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2572Z' WHERE naf_code='222'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2573A' WHERE naf_code='223'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2573B' WHERE naf_code='224'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2591Z' WHERE naf_code='225'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2592Z' WHERE naf_code='226'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2593Z' WHERE naf_code='227'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2594Z' WHERE naf_code='228'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2599A' WHERE naf_code='229'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0146Z' WHERE naf_code='23'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2599B' WHERE naf_code='230'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2611Z' WHERE naf_code='231'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2612Z' WHERE naf_code='232'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2620Z' WHERE naf_code='233'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2630Z' WHERE naf_code='234'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2640Z' WHERE naf_code='235'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2651A' WHERE naf_code='236'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2651B' WHERE naf_code='237'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2652Z' WHERE naf_code='238'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2660Z' WHERE naf_code='239'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0147Z' WHERE naf_code='24'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2670Z' WHERE naf_code='240'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2680Z' WHERE naf_code='241'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2711Z' WHERE naf_code='242'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2712Z' WHERE naf_code='243'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2720Z' WHERE naf_code='244'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2731Z' WHERE naf_code='245'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2732Z' WHERE naf_code='246'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2733Z' WHERE naf_code='247'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2740Z' WHERE naf_code='248'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2751Z' WHERE naf_code='249'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0149Z' WHERE naf_code='25'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2752Z' WHERE naf_code='250'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2790Z' WHERE naf_code='251'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2811Z' WHERE naf_code='252'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2812Z' WHERE naf_code='253'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2813Z' WHERE naf_code='254'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2814Z' WHERE naf_code='255'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2815Z' WHERE naf_code='256'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2821Z' WHERE naf_code='257'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2822Z' WHERE naf_code='258'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2823Z' WHERE naf_code='259'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0150Z' WHERE naf_code='26'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2824Z' WHERE naf_code='260'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2825Z' WHERE naf_code='261'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2829A' WHERE naf_code='262'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2829B' WHERE naf_code='263'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2830Z' WHERE naf_code='264'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2841Z' WHERE naf_code='265'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2849Z' WHERE naf_code='266'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2891Z' WHERE naf_code='267'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2892Z' WHERE naf_code='268'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2893Z' WHERE naf_code='269'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0161Z' WHERE naf_code='27'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2894Z' WHERE naf_code='270'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2895Z' WHERE naf_code='271'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2896Z' WHERE naf_code='272'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2899A' WHERE naf_code='273'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2899B' WHERE naf_code='274'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2910Z' WHERE naf_code='275'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2920Z' WHERE naf_code='276'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2931Z' WHERE naf_code='277'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='2932Z' WHERE naf_code='278'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3011Z' WHERE naf_code='279'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0162Z' WHERE naf_code='28'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3012Z' WHERE naf_code='280'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3020Z' WHERE naf_code='281'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3030Z' WHERE naf_code='282'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3040Z' WHERE naf_code='283'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3091Z' WHERE naf_code='284'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3092Z' WHERE naf_code='285'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3099Z' WHERE naf_code='286'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3101Z' WHERE naf_code='287'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3102Z' WHERE naf_code='288'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3103Z' WHERE naf_code='289'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0163Z' WHERE naf_code='29'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3109A' WHERE naf_code='290'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3109B' WHERE naf_code='291'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3211Z' WHERE naf_code='292'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3212Z' WHERE naf_code='293'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3213Z' WHERE naf_code='294'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3220Z' WHERE naf_code='295'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3230Z' WHERE naf_code='296'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3240Z' WHERE naf_code='297'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3250A' WHERE naf_code='298'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3250B' WHERE naf_code='299'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0113Z' WHERE naf_code='3'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0164Z' WHERE naf_code='30'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3291Z' WHERE naf_code='300'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3299Z' WHERE naf_code='301'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3311Z' WHERE naf_code='302'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3312Z' WHERE naf_code='303'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3313Z' WHERE naf_code='304'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3314Z' WHERE naf_code='305'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3315Z' WHERE naf_code='306'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3316Z' WHERE naf_code='307'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3317Z' WHERE naf_code='308'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3319Z' WHERE naf_code='309'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0170Z' WHERE naf_code='31'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320A' WHERE naf_code='310'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320B' WHERE naf_code='311'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320C' WHERE naf_code='312'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3320D' WHERE naf_code='313'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3511Z' WHERE naf_code='314'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3512Z' WHERE naf_code='315'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3513Z' WHERE naf_code='316'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3514Z' WHERE naf_code='317'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3521Z' WHERE naf_code='318'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3522Z' WHERE naf_code='319'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0210Z' WHERE naf_code='32'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3523Z' WHERE naf_code='320'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3530Z' WHERE naf_code='321'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3600Z' WHERE naf_code='322'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3700Z' WHERE naf_code='323'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3811Z' WHERE naf_code='324'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3812Z' WHERE naf_code='325'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3821Z' WHERE naf_code='326'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3822Z' WHERE naf_code='327'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3831Z' WHERE naf_code='328'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3832Z' WHERE naf_code='329'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0220Z' WHERE naf_code='33'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='3900Z' WHERE naf_code='330'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110A' WHERE naf_code='331'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110B' WHERE naf_code='332'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110C' WHERE naf_code='333'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4110D' WHERE naf_code='334'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4120A' WHERE naf_code='335'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4120B' WHERE naf_code='336'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4211Z' WHERE naf_code='337'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4212Z' WHERE naf_code='338'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4213A' WHERE naf_code='339'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0230Z' WHERE naf_code='34'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4213B' WHERE naf_code='340'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4221Z' WHERE naf_code='341'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4222Z' WHERE naf_code='342'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4291Z' WHERE naf_code='343'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4299Z' WHERE naf_code='344'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4311Z' WHERE naf_code='345'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4312A' WHERE naf_code='346'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4312B' WHERE naf_code='347'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4313Z' WHERE naf_code='348'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4321A' WHERE naf_code='349'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0240Z' WHERE naf_code='35'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4321B' WHERE naf_code='350'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4322A' WHERE naf_code='351'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4322B' WHERE naf_code='352'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4329A' WHERE naf_code='353'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4329B' WHERE naf_code='354'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4331Z' WHERE naf_code='355'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332A' WHERE naf_code='356'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332B' WHERE naf_code='357'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4332C' WHERE naf_code='358'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4333Z' WHERE naf_code='359'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0311Z' WHERE naf_code='36'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4334Z' WHERE naf_code='360'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4339Z' WHERE naf_code='361'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4391A' WHERE naf_code='362'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4391B' WHERE naf_code='363'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399A' WHERE naf_code='364'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399B' WHERE naf_code='365'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399C' WHERE naf_code='366'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399D' WHERE naf_code='367'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4399E' WHERE naf_code='368'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4511Z' WHERE naf_code='369'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0312Z' WHERE naf_code='37'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4519Z' WHERE naf_code='370'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4520A' WHERE naf_code='371'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4520B' WHERE naf_code='372'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4531Z' WHERE naf_code='373'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4532Z' WHERE naf_code='374'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4540Z' WHERE naf_code='375'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4611Z' WHERE naf_code='376'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4612A' WHERE naf_code='377'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4612B' WHERE naf_code='378'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4613Z' WHERE naf_code='379'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0321Z' WHERE naf_code='38'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4614Z' WHERE naf_code='380'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4615Z' WHERE naf_code='381'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4616Z' WHERE naf_code='382'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4617A' WHERE naf_code='383'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4617B' WHERE naf_code='384'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4618Z' WHERE naf_code='385'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4619A' WHERE naf_code='386'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4619B' WHERE naf_code='387'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4621Z' WHERE naf_code='388'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4622Z' WHERE naf_code='389'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0322Z' WHERE naf_code='39'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4623Z' WHERE naf_code='390'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4624Z' WHERE naf_code='391'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4631Z' WHERE naf_code='392'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632A' WHERE naf_code='393'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632B' WHERE naf_code='394'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4632C' WHERE naf_code='395'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4633Z' WHERE naf_code='396'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4634Z' WHERE naf_code='397'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4635Z' WHERE naf_code='398'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4636Z' WHERE naf_code='399'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0114Z' WHERE naf_code='4'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0510Z' WHERE naf_code='40'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4637Z' WHERE naf_code='400'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4638A' WHERE naf_code='401'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4638B' WHERE naf_code='402'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4639A' WHERE naf_code='403'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4639B' WHERE naf_code='404'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4641Z' WHERE naf_code='405'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4642Z' WHERE naf_code='406'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4643Z' WHERE naf_code='407'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4644Z' WHERE naf_code='408'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4645Z' WHERE naf_code='409'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0520Z' WHERE naf_code='41'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4646Z' WHERE naf_code='410'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4647Z' WHERE naf_code='411'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4648Z' WHERE naf_code='412'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4649Z' WHERE naf_code='413'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4651Z' WHERE naf_code='414'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4652Z' WHERE naf_code='415'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4661Z' WHERE naf_code='416'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4662Z' WHERE naf_code='417'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4663Z' WHERE naf_code='418'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4664Z' WHERE naf_code='419'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0610Z' WHERE naf_code='42'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4665Z' WHERE naf_code='420'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4666Z' WHERE naf_code='421'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669A' WHERE naf_code='422'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669B' WHERE naf_code='423'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4669C' WHERE naf_code='424'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4671Z' WHERE naf_code='425'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4672Z' WHERE naf_code='426'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4673A' WHERE naf_code='427'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4673B' WHERE naf_code='428'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4674A' WHERE naf_code='429'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0620Z' WHERE naf_code='43'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4674B' WHERE naf_code='430'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4675Z' WHERE naf_code='431'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4676Z' WHERE naf_code='432'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4677Z' WHERE naf_code='433'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4690Z' WHERE naf_code='434'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711A' WHERE naf_code='435'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711B' WHERE naf_code='436'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711C' WHERE naf_code='437'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711D' WHERE naf_code='438'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711E' WHERE naf_code='439'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0710Z' WHERE naf_code='44'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4711F' WHERE naf_code='440'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4719A' WHERE naf_code='441'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4719B' WHERE naf_code='442'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4721Z' WHERE naf_code='443'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4722Z' WHERE naf_code='444'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4723Z' WHERE naf_code='445'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4724Z' WHERE naf_code='446'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4725Z' WHERE naf_code='447'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4726Z' WHERE naf_code='448'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4729Z' WHERE naf_code='449'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0721Z' WHERE naf_code='45'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4730Z' WHERE naf_code='450'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4741Z' WHERE naf_code='451'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4742Z' WHERE naf_code='452'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4743Z' WHERE naf_code='453'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4751Z' WHERE naf_code='454'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4752A' WHERE naf_code='455'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4752B' WHERE naf_code='456'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4753Z' WHERE naf_code='457'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4754Z' WHERE naf_code='458'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4759A' WHERE naf_code='459'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0729Z' WHERE naf_code='46'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4759B' WHERE naf_code='460'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4761Z' WHERE naf_code='461'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4762Z' WHERE naf_code='462'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4763Z' WHERE naf_code='463'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4764Z' WHERE naf_code='464'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4765Z' WHERE naf_code='465'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4771Z' WHERE naf_code='466'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4772A' WHERE naf_code='467'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4772B' WHERE naf_code='468'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4773Z' WHERE naf_code='469'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0811Z' WHERE naf_code='47'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4774Z' WHERE naf_code='470'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4775Z' WHERE naf_code='471'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4776Z' WHERE naf_code='472'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4777Z' WHERE naf_code='473'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778A' WHERE naf_code='474'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778B' WHERE naf_code='475'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4778C' WHERE naf_code='476'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4779Z' WHERE naf_code='477'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4781Z' WHERE naf_code='478'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4782Z' WHERE naf_code='479'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0812Z' WHERE naf_code='48'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4789Z' WHERE naf_code='480'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4791A' WHERE naf_code='481'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4791B' WHERE naf_code='482'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4799A' WHERE naf_code='483'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4799B' WHERE naf_code='484'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4910Z' WHERE naf_code='485'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4920Z' WHERE naf_code='486'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4931Z' WHERE naf_code='487'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4932Z' WHERE naf_code='488'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939A' WHERE naf_code='489'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0891Z' WHERE naf_code='49'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939B' WHERE naf_code='490'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4939C' WHERE naf_code='491'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941A' WHERE naf_code='492'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941B' WHERE naf_code='493'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4941C' WHERE naf_code='494'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4942Z' WHERE naf_code='495'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='4950Z' WHERE naf_code='496'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5010Z' WHERE naf_code='497'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5020Z' WHERE naf_code='498'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5030Z' WHERE naf_code='499'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0115Z' WHERE naf_code='5'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0892Z' WHERE naf_code='50'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5040Z' WHERE naf_code='500'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5110Z' WHERE naf_code='501'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5121Z' WHERE naf_code='502'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5122Z' WHERE naf_code='503'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5210A' WHERE naf_code='504'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5210B' WHERE naf_code='505'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5221Z' WHERE naf_code='506'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5222Z' WHERE naf_code='507'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5223Z' WHERE naf_code='508'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5224A' WHERE naf_code='509'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0893Z' WHERE naf_code='51'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5224B' WHERE naf_code='510'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5229A' WHERE naf_code='511'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5229B' WHERE naf_code='512'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5310Z' WHERE naf_code='513'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5320Z' WHERE naf_code='514'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5510Z' WHERE naf_code='515'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5520Z' WHERE naf_code='516'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5530Z' WHERE naf_code='517'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5590Z' WHERE naf_code='518'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610A' WHERE naf_code='519'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0899Z' WHERE naf_code='52'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610B' WHERE naf_code='520'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5610C' WHERE naf_code='521'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5621Z' WHERE naf_code='522'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5629A' WHERE naf_code='523'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5629B' WHERE naf_code='524'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5630Z' WHERE naf_code='525'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5811Z' WHERE naf_code='526'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5812Z' WHERE naf_code='527'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5813Z' WHERE naf_code='528'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5814Z' WHERE naf_code='529'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0910Z' WHERE naf_code='53'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5819Z' WHERE naf_code='530'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5821Z' WHERE naf_code='531'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829A' WHERE naf_code='532'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829B' WHERE naf_code='533'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5829C' WHERE naf_code='534'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911A' WHERE naf_code='535'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911B' WHERE naf_code='536'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5911C' WHERE naf_code='537'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5912Z' WHERE naf_code='538'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5913A' WHERE naf_code='539'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0990Z' WHERE naf_code='54'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5913B' WHERE naf_code='540'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5914Z' WHERE naf_code='541'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='5920Z' WHERE naf_code='542'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6010Z' WHERE naf_code='543'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6020A' WHERE naf_code='544'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6020B' WHERE naf_code='545'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6110Z' WHERE naf_code='546'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6120Z' WHERE naf_code='547'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6130Z' WHERE naf_code='548'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6190Z' WHERE naf_code='549'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1011Z' WHERE naf_code='55'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6201Z' WHERE naf_code='550'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6202A' WHERE naf_code='551'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6202B' WHERE naf_code='552'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6203Z' WHERE naf_code='553'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6209Z' WHERE naf_code='554'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6311Z' WHERE naf_code='555'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6312Z' WHERE naf_code='556'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6391Z' WHERE naf_code='557'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6399Z' WHERE naf_code='558'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6411Z' WHERE naf_code='559'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1012Z' WHERE naf_code='56'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6419Z' WHERE naf_code='560'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6420Z' WHERE naf_code='561'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6430Z' WHERE naf_code='562'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6491Z' WHERE naf_code='563'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6492Z' WHERE naf_code='564'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6499Z' WHERE naf_code='565'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6511Z' WHERE naf_code='566'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6512Z' WHERE naf_code='567'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6520Z' WHERE naf_code='568'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6530Z' WHERE naf_code='569'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1013A' WHERE naf_code='57'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6611Z' WHERE naf_code='570'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6612Z' WHERE naf_code='571'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6619A' WHERE naf_code='572'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6619B' WHERE naf_code='573'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6621Z' WHERE naf_code='574'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6622Z' WHERE naf_code='575'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6629Z' WHERE naf_code='576'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6630Z' WHERE naf_code='577'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6810Z' WHERE naf_code='578'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6820A' WHERE naf_code='579'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1013B' WHERE naf_code='58'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6820B' WHERE naf_code='580'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6831Z' WHERE naf_code='581'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6832A' WHERE naf_code='582'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6832B' WHERE naf_code='583'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6910Z' WHERE naf_code='584'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='6920Z' WHERE naf_code='585'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7010Z' WHERE naf_code='586'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7021Z' WHERE naf_code='587'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7022Z' WHERE naf_code='588'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7111Z' WHERE naf_code='589'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1020Z' WHERE naf_code='59'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7112A' WHERE naf_code='590'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7112B' WHERE naf_code='591'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7120A' WHERE naf_code='592'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7120B' WHERE naf_code='593'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7211Z' WHERE naf_code='594'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7219Z' WHERE naf_code='595'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7220Z' WHERE naf_code='596'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7311Z' WHERE naf_code='597'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7312Z' WHERE naf_code='598'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7320Z' WHERE naf_code='599'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0116Z' WHERE naf_code='6'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1031Z' WHERE naf_code='60'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7410Z' WHERE naf_code='600'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7420Z' WHERE naf_code='601'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7430Z' WHERE naf_code='602'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7490A' WHERE naf_code='603'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7490B' WHERE naf_code='604'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7500Z' WHERE naf_code='605'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7711A' WHERE naf_code='606'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7711B' WHERE naf_code='607'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7712Z' WHERE naf_code='608'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7721Z' WHERE naf_code='609'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1032Z' WHERE naf_code='61'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7722Z' WHERE naf_code='610'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7729Z' WHERE naf_code='611'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7731Z' WHERE naf_code='612'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7732Z' WHERE naf_code='613'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7733Z' WHERE naf_code='614'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7734Z' WHERE naf_code='615'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7735Z' WHERE naf_code='616'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7739Z' WHERE naf_code='617'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7740Z' WHERE naf_code='618'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7810Z' WHERE naf_code='619'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1039A' WHERE naf_code='62'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7820Z' WHERE naf_code='620'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7830Z' WHERE naf_code='621'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7911Z' WHERE naf_code='622'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7912Z' WHERE naf_code='623'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='7990Z' WHERE naf_code='624'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8010Z' WHERE naf_code='625'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8020Z' WHERE naf_code='626'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8030Z' WHERE naf_code='627'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8110Z' WHERE naf_code='628'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8121Z' WHERE naf_code='629'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1039B' WHERE naf_code='63'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8122Z' WHERE naf_code='630'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8129A' WHERE naf_code='631'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8129B' WHERE naf_code='632'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8130Z' WHERE naf_code='633'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8211Z' WHERE naf_code='634'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8219Z' WHERE naf_code='635'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8220Z' WHERE naf_code='636'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8230Z' WHERE naf_code='637'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8291Z' WHERE naf_code='638'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8292Z' WHERE naf_code='639'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1041A' WHERE naf_code='64'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8299Z' WHERE naf_code='640'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8411Z' WHERE naf_code='641'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8412Z' WHERE naf_code='642'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8413Z' WHERE naf_code='643'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8421Z' WHERE naf_code='644'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8422Z' WHERE naf_code='645'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8423Z' WHERE naf_code='646'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8424Z' WHERE naf_code='647'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8425Z' WHERE naf_code='648'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430A' WHERE naf_code='649'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1041B' WHERE naf_code='65'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430B' WHERE naf_code='650'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8430C' WHERE naf_code='651'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8510Z' WHERE naf_code='652'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8520Z' WHERE naf_code='653'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8531Z' WHERE naf_code='654'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8532Z' WHERE naf_code='655'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8541Z' WHERE naf_code='656'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8542Z' WHERE naf_code='657'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8551Z' WHERE naf_code='658'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8552Z' WHERE naf_code='659'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1042Z' WHERE naf_code='66'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8553Z' WHERE naf_code='660'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8559A' WHERE naf_code='661'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8559B' WHERE naf_code='662'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8560Z' WHERE naf_code='663'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8610Z' WHERE naf_code='664'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8621Z' WHERE naf_code='665'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622A' WHERE naf_code='666'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622B' WHERE naf_code='667'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8622C' WHERE naf_code='668'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8623Z' WHERE naf_code='669'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051A' WHERE naf_code='67'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690A' WHERE naf_code='670'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690B' WHERE naf_code='671'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690C' WHERE naf_code='672'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690D' WHERE naf_code='673'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690E' WHERE naf_code='674'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8690F' WHERE naf_code='675'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710A' WHERE naf_code='676'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710B' WHERE naf_code='677'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8710C' WHERE naf_code='678'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8720A' WHERE naf_code='679'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051B' WHERE naf_code='68'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8720B' WHERE naf_code='680'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8730A' WHERE naf_code='681'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8730B' WHERE naf_code='682'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8790A' WHERE naf_code='683'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8790B' WHERE naf_code='684'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810A' WHERE naf_code='685'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810B' WHERE naf_code='686'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8810C' WHERE naf_code='687'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8891A' WHERE naf_code='688'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8891B' WHERE naf_code='689'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051C' WHERE naf_code='69'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8899A' WHERE naf_code='690'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='8899B' WHERE naf_code='691'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9001Z' WHERE naf_code='692'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9002Z' WHERE naf_code='693'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9003A' WHERE naf_code='694'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9003B' WHERE naf_code='695'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9004Z' WHERE naf_code='696'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9101Z' WHERE naf_code='697'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9102Z' WHERE naf_code='698'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9103Z' WHERE naf_code='699'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0119Z' WHERE naf_code='7'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1051D' WHERE naf_code='70'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9104Z' WHERE naf_code='700'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9200Z' WHERE naf_code='701'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9311Z' WHERE naf_code='702'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9312Z' WHERE naf_code='703'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9313Z' WHERE naf_code='704'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9319Z' WHERE naf_code='705'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9321Z' WHERE naf_code='706'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9329Z' WHERE naf_code='707'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9411Z' WHERE naf_code='708'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9412Z' WHERE naf_code='709'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1052Z' WHERE naf_code='71'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9420Z' WHERE naf_code='710'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9491Z' WHERE naf_code='711'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9492Z' WHERE naf_code='712'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9499Z' WHERE naf_code='713'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9511Z' WHERE naf_code='714'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9512Z' WHERE naf_code='715'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9521Z' WHERE naf_code='716'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9522Z' WHERE naf_code='717'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9523Z' WHERE naf_code='718'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9524Z' WHERE naf_code='719'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1061A' WHERE naf_code='72'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9525Z' WHERE naf_code='720'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9529Z' WHERE naf_code='721'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9601A' WHERE naf_code='722'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9601B' WHERE naf_code='723'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9602A' WHERE naf_code='724'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9602B' WHERE naf_code='725'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9603Z' WHERE naf_code='726'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9604Z' WHERE naf_code='727'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9609Z' WHERE naf_code='728'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9700Z' WHERE naf_code='729'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1061B' WHERE naf_code='73'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9810Z' WHERE naf_code='730'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9820Z' WHERE naf_code='731'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='9900Z' WHERE naf_code='732'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1062Z' WHERE naf_code='74'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071A' WHERE naf_code='75'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071B' WHERE naf_code='76'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071C' WHERE naf_code='77'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1071D' WHERE naf_code='78'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1072Z' WHERE naf_code='79'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0121Z' WHERE naf_code='8'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1073Z' WHERE naf_code='80'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1081Z' WHERE naf_code='81'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1082Z' WHERE naf_code='82'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1083Z' WHERE naf_code='83'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1084Z' WHERE naf_code='84'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1085Z' WHERE naf_code='85'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1086Z' WHERE naf_code='86'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1089Z' WHERE naf_code='87'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1091Z' WHERE naf_code='88'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1092Z' WHERE naf_code='89'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='0122Z' WHERE naf_code='9'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1101Z' WHERE naf_code='90'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1102A' WHERE naf_code='91'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1102B' WHERE naf_code='92'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1103Z' WHERE naf_code='93'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1104Z' WHERE naf_code='94'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1105Z' WHERE naf_code='95'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1106Z' WHERE naf_code='96'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1107A' WHERE naf_code='97'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1107B' WHERE naf_code='98'""".format(
                        tabName
                    )
                )
                frappe.db.sql(
                    """update {} set code_naf='1200Z' WHERE naf_code='99'""".format(
                        tabName
                    )
                )

        except Exception:
            frappe.log_error("Failed to migrate Code Naf.")
