# ATL03 Glossary

This file records important ATL03 terms while reading the User Guide and Data Dictionary.

### Term

* Simple meaning: A short explanation of the word in plain English.
* Technical meaning: The official or more detailed meaning from the ATL03 document.
* Source document: Where I found the definition.
* Page/section: The page number or HDF5 group where the term appears.
* Example question: A question someone might ask the RAG system about this term.

---

### ATL03

* Simple meaning: ATL03 is the ICESat-2 dataset that stores individual laser photon measurements from Earth.
* Technical meaning: ATL03 is a Level 2A data product that contains height, latitude, longitude, and time for photons downlinked by the ATLAS instrument on ICESat-2.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-1, Data Dictionary attributes
* Example question: What kind of information does the ATL03 dataset contain?

### ICESat-2

* Simple meaning: ICESat-2 is NASA’s satellite mission that measures Earth’s surface using laser light.
* Technical meaning: ICESat-2 is the satellite platform that carries the ATLAS instrument, which collects the photon measurements used in ATL03.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-1, dataset description
* Example question: What satellite produces the ATL03 dataset?

### ATLAS

* Simple meaning: ATLAS is the laser instrument on ICESat-2 that sends light pulses toward Earth and records returning photons.
* Technical meaning: ATLAS stands for Advanced Topographic Laser Altimeter System. It is the instrument on ICESat-2 that produces the photon measurements used in ATL03.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-1, dataset description
* Example question: What instrument collects the photon data in ATL03?

### photon

* Simple meaning: A photon is a tiny packet of light that returns to the satellite after the laser pulse hits Earth or the atmosphere.
* Technical meaning: In ATL03, each photon is an individual detected laser return event. The dataset stores information such as its height, latitude, longitude, time, and quality flags.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-35 to 1-36, Group `/gtx/heights`
* Example question: What does a photon mean in the ATL03 dataset?

### h_ph

* Simple meaning: h_ph is the height of each photon above the WGS-84 ellipsoid, in meters.
* Technical meaning: `h_ph` stores the height of each received photon relative to the WGS-84 ellipsoid, in meters. Some geophysical corrections are included, but geoid, ocean tide, and dynamic atmosphere corrections are not applied to the ellipsoidal heights.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-36, Group `/gtx/heights`
* Example question: Which ATL03 variable gives the height of each photon?

### lat_ph

* Simple meaning: `lat_ph` is the latitude location of each received photon.
* Technical meaning: `lat_ph` stores the latitude of each received photon in degrees north. It is computed from the ECF Cartesian coordinates of the photon bounce point.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-36, Group `/gtx/heights`
* Example question: Which ATL03 variable gives the latitude of each photon?

### lon_ph

* Simple meaning: `lon_ph` is the longitude location of each received photon.
* Technical meaning: `lon_ph` stores the longitude of each received photon in degrees east. It is computed from the ECF Cartesian coordinates of the photon bounce point.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-36, Group `/gtx/heights`
* Example question: Which ATL03 variable gives the longitude of each photon?

### delta_time

* Simple meaning: `delta_time` tells when a photon was transmitted, measured as seconds from a special ATLAS time starting point.
* Technical meaning: `delta_time` is the transmit time of a given photon, measured in seconds from the ATLAS Standard Data Product Epoch. It is not a normal calendar timestamp. To compute GPS seconds, the offset stored in `/ancillary_data/atlas_sdp_gps_epoch` must be added.
* Source document: ATL03 Data Dictionary V07
* Page/section: Page 1-35, Group `/gtx/heights`
* Example question: Is `delta_time` a normal UTC timestamp, or is it measured from a special epoch?
