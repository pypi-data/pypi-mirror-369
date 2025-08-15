# Gallica

**URL:** <https://gallica.bnf.fr/>

**Corresponding Library:** [Bibliothèque nationale de France](https://en.wikipedia.org/wiki/Biblioth%C3%A8que_nationale_de_France).

**Official API:**
- [Search API](https://api.bnf.fr/api-gallica-de-recherche): for searching the digital holdings.
    - Note that when using multiple filtering conditions in a URL, only French search terms function as expected.
        - For example, <https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&maximumRecords=10&startRecord=1&query=dc.title%20all%20%22cartes%20figurative%22%20and%20dc.type%20any%20image> only returns two records
- [Document API](https://api.bnf.fr/api-document-de-gallica): for retrieving the metadata.
- [Image API](https://api.bnf.fr/api-iiif-de-recuperation-des-images-de-gallica): for retrieving and manipulating image with [IIIF](https://iiif.io/) standard.

**Term of Use:**
> The non-commercial reuse of these contents is free and free in compliance with the legislation in force and in particular the maintenance of the source mention of the contents as specified below: "Source gallica.bnf.fr / Bibliothèque nationale de France" or "Source gallica.bnf.fr / BnF"... The metadata are subject to the EtaLab license, which authorizes free and open use provided the source is mentioned (BnF / Gallica). ([Source](https://gallica.bnf.fr/edit/conditions-dutilisation-des-contenus-de-gallica))

## Additional Notes

### Structure of a Query URL

Example query URL to be used as an entry in `queries` of `querier.fetch_metadata(queries=queries)`: `https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&maximumRecords=10&startRecord=1&query=+dc.title+all+%22{keyword}%22`.

- The parameter `{keyword}` is to be replaced with the keyword to be searched.
- The URL parameter `maximumRecords` denotes the maximum number of records to be returned. When `maximumRecords` is not explicitly specified, its default value is 10.
- The URL parameter `startRecord` denotes the index of the start record (starting from 1). For examine

Additional query URL example: <https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&maximumRecords=10&startRecord=11&query=dc.title+all+%22cartes+figurative%22>.
This URL returns the 11th to 20th records whose title includes the word "cartes figurative".

Each query URL returns a list of XML records (with identifier stored in `dc:identifier`).
An example record is: <https://gallica.bnf.fr/ark:/12148/btv1b525109845>.

### Obtaining Image Information

Each record returned by a query URL may contain one or multiple images.
For example, the record <https://gallica.bnf.fr/ark:/12148/btv1b525109845> has 16 images.

The image information for the record can be obtained with the URL `https://gallica.bnf.fr/services/Pagination?ark={ark_identifier}`.
For example, the `ark_identifier` of <https://gallica.bnf.fr/ark:/12148/btv1b525109845> is `btv1b525109845`. We can retrieve its corresponding image information at <https://gallica.bnf.fr/services/Pagination?ark=btv1b525109845>.
