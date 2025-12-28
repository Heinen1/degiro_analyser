*English follows Dutch*

*Dutch*

# Introductie

Disclaimer: dit notebook gebasseerd op mijn eigen, beperkte portfolio en zal niet alle effecten kunnen analyseren 
- Basisvaluta is in EUR
- Portefeuille bevat 1 x ETF (EUR), 1 x aandeel (USD), 1 x staatsobligatie (EUR)
- Accounttype: Custody (bestaat niet meer na 2021)
- AutoFX staat aan voor valuta-omrekening 

De Giro is een populaire Nederlandse, online broker die een breed scala aan effecten (e.g. aandelen, indexfondsen, obligaties, etc.) aanbiedt. Dit Jupyter notebook analyseert het Account.csv-bestand van het Rekeningoverzicht, wat vanuit het De Giro-account gedownload kan worden. 

Opmerkelijkheden in het rekeningoverzicht[^1]:
- De DEGIRO Corporate Action Kosten voor de dividendverwerking voor Q4-2021 en heel 2022 ontbreken. Rond deze periode wordt het Custody-account ook niet meer aangeboden.
- Voor een dividendverwerking in 2023 zijn de DEGIRO Corporate Action Kosten verwerkt 3 maanden nadat het dividend is uitgekeerd. 

---

*English*

# Introduction

Disclaimer: this notebook is based on my own limited portfolio and will not be able to analyse all securities 
- Base currency is in EUR
- Portfolio contains 1 x ETF (EUR), 1 x stock (USD), 1 x government bond (EUR)
- Account type: Custody (does not exists anymore after 2021)
- AutoFX is enabled for exchange currencies

De Giro is a popular Dutch, online broker offering a wide range of securities (e.g. stocks, index funds, bonds, etc. etc.). This Jupyter notebook analyses the Account.csv file from the account statement, which can be downloaded from a De Giro account.

Notable features from the account statement[^1]
- The DEGIRO Corporate Action Kosten for processing dividend are missing for Q4-2021 and all of 2022. Around this time, the Custody account was nolonger being offered.
- For processing of dividends in 2023, the DEGIRO Corporate Action Kosten are incured 3 months after the dividend was paid out

[^1]: There could be a specific reason for this which have been communicated with DEGIRO customers (unknown at this point).
