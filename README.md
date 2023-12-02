# degiro_analyser
De Giro is a popular Dutch investment broker offering a wide range of securities. The account export generates .xls, or .csv files containing the various transactions over time, which can be analysed with this code. Presently, only stocks and ETFs are considered.

# Berekeningen
Onderstaande overzicht weergeeft hoe grootheden berekend worden in de overzichten.
 - AANTAL = Totaal aantal gekochte shares
 - GAK = AANTAL / Total gekocht (EUR)
 - WAARDE = AANTAL * GAK
 - Uitbetaalde dividend = (DIVIDEND - DEGIRO Corporate Action Kosten) / Valuta Debitering
 
Het overzicht is gesorteerd op de Datum. De Corporate Action Kosten, die bebehoren bij de Dividend, komen overeen met de Valutadatum. Voor een custody-account zijn de kosten voor dividend verwerking: 1.00E + 3.00% van het dividend. Voor VWRL moeten de kosten eerst naar dollars worden omgezet. Hierbij behoort de wisselkoers (FX = Foreign eXchange) van de Valutadatum van de Dividend. Let op: voor 2022 Q1 en Q2

