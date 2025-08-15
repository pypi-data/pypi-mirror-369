# NIST parser
#
# Initial author: Pascal Bourgault
# Contributing author: Leonardo Di Schiavi Trotta
#
# Downloads attenuation data from the Nist website
# Uses the HTML Table Parser class, Credits below:

# -----------------------------------------------------------------------------
# Name:        HTMLTablePasrer
# Purpose:     Simple class for parsing an (x)html string to extract tables.
#              Written in python3
#
# Author:      Josua Schmid
#
# Created:     05.03.2014
# Copyright:   (c) Josua Schmid 2014
# Licence:     AGPLv3
# -----------------------------------------------------------------------------

"""
Module used to download and present attenuation and composition data
from the NIST website.
"""

import time
from html import unescape
from html.parser import HTMLParser
from math import ceil
from typing import Dict, List, Sequence, Union
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from periodictable import elements, formula
    from periodictable.formulas import Formula
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "This module requires the periodictable optional dependency. Install with: "
        "`pip install pygrpm[periodictable]` or `pip install pygrpm[all]`"
    ) from exc

from .materials_enum import NISTMaterials

MAX_NETWORK_TRIES = 30
WAIT_TIME = 0.1
MAX_ENERGY_LENGTH = 50
POST_DATA = {
    "NumAdd": "1",
    "WindowXmin": "0.001",
    "WindowXmax": "1000",
    "ResizeFlag": "on",
}


def get_atomic_number(composition: str) -> int:
    """
    Returns the atomic number equivalent to the first element
    match in the provided string
    Parameters
    ----------
    composition : string
        The key representing the element, e.g: "H"

    Returns
    -------
    int
        The atomic number
    """
    element = formula(composition)
    element_list = [elem.number for elem, numFrac in element.atoms.items()]

    if len(element_list) > 1:
        print(
            f"Warning, submitted more than one element, only returning {list(element.atoms)[0]}"
        )
    return [elem.number for elem, numFrac in element.atoms.items()][0]


def get_electronic_cross_sections(
    composition: Union[int, str],
    energies: Sequence[float],
    option: str = "total",
    verbose: int = 0,
) -> List:
    """Retrieves the electronic cross sections of an element
    at given energies on the NIST website
    in (barns/electron), barn=10^-24cm^2.

    Parameters
    ----------
    composition : str or int (atomic number) representing the desired element
    energies : sequence of float
        The energies at which the attenuations are computed, given in keV
    option : string
        One of: "total", "ph", "comp", or "ray" indicating attenuation type
    verbose : int, optional
        The verbose level  of the  function.
        If it is greater than 0, prints at each step.

    Raises
    ------
    URLError
        If the data request failed more than `NISTparser.MAX_NETWORK_TRIES`
        times. At each fail, it waits `NISTparser.WAIT_TIME` seconds
        before trying again.
    ValueError
        If `composition` is not of a known type
        (dict, str or periodictable.formulas.Formula)

    Returns
    -------
    list of float
        The total electronic cross section values for the material
        at each energies, (barns/electron), barn=10^-24cm^2
    """
    atomic_number = (
        composition if isinstance(composition, int) else get_atomic_number(composition)
    )
    cross_section = get_cross_sections(
        composition, energies, option=option, verbose=verbose
    )
    return [cross / atomic_number for cross in cross_section]


def get_cross_sections(
    composition: Union[int, str],
    energies: Sequence[float],
    option: str = "total",
    verbose: int = 0,
) -> List:
    """Retrieves the desired cross sections of an element at given energies
     on the NIST website in (barns/electron), barn=10^-24cm^2.

    Parameters
    ----------
    composition : str or int (atomic number) representing the desired element
    energies : sequence of float
        The energies at which the attenuations are computed, given in keV
    option : string
        One of: "total", "ph", "comp", or "ray" indicating attenuation type
    verbose : int, optional
        The verbose level  of the  function.
        If it is greater than 0, prints at each step.

    Raises
    ------
    URLError
        If the data request failed more than `NISTparser.MAX_NETWORK_TRIES`
        times. At each fail, it waits `NISTparser.WAIT_TIME` seconds
        before trying again.
    ValueError
        If `composition` is not of a known type
        (dict, str or periodictable.formulas.Formula)

    Returns
    -------
    list of float
        The desired type of cross section values for the material
         at each energies, (barns/electron), barn=10^-24cm^2

    """
    atomic_number = (
        composition if isinstance(composition, int) else get_atomic_number(composition)
    )
    return get_attenuations(
        atomic_number, energies, option=option, verbose=verbose, outopt="CSBA"
    )


def get_attenuations(
    composition: Union[str, Dict, int, Formula],
    energies: Sequence[float],
    option: str = "total",
    verbose: int = 0,
    outopt: str = "PIC",
) -> List:
    """Retrieves the attenuation of a material in cm^2/g
    at given energies on the NIST website.

    Parameters
    ----------
    composition : dict or str or periodictable.formulas.Formula
        The composition of the material. If it is a dict,
        it must be of the form {"formula": Relative weight}.
            Ex : `{"Cu":0.5, "H2O":0.3, "C6H12O6":0.2}`
        if it is a string, it must be a formula. Ex: `"C6H12O6"`
        if it is a `periodictable.formulas.Formula`, the mass fraction of each
        composing elements is extracted.
    energies : sequence of float
        The energies at which the attenuations are computed, given in keV
    option : string
        One of: "total", "ph", "comp", or "ray" indicating attenuation type
    verbose : int, optional
        The verbose level  of the  function.
        If it is greater than 0, prints at each step.
    outopt: str, optional
        If atomic number is chosen then Mass Attenuation Coefficient
            is returned by default (PIC),
        if "CSBA", then atomic cross section is returned instead.

    Raises
    ------
    URLError
        If the data request failed more than `NISTparser.MAX_NETWORK_TRIES`
        times. At each fail, it waits `NISTparser.WAIT_TIME` seconds
        before trying again.
    ValueError
        If `composition` is not of a known type
        (dict, str or periodictable.formulas.Formula)

    Returns
    -------
    list of float
        The total mass-attenuation with coherent scattering values
        for the material at each energies, in cm^2/g
    """
    # Selects attenuation component:
    # ph: photoelectric; comp: compton; total: total
    options_dict = {
        "ph": {
            "value": 4,
            "type": "Photoelectric",
        },
        "comp": {
            "value": 3,
            "type": "Compton (incoherent)",
        },
        "ray": {"value": 2, "type": "Rayleigh (coherent)"},
        "total": {
            "value": -2,
            "type": "Total",
        },
    }

    # Select our index for NIST query and print details if required
    component_index = options_dict[option]["value"]
    if verbose > 0:
        print(f"{options_dict[option]['type']} component selected")

    # NIST has a limit at approx 112 energies
    if len(energies) > MAX_ENERGY_LENGTH:
        if verbose > 0:
            print(
                f"NIST Parser: Too many energies ({len(energies)} >"
                f"{MAX_ENERGY_LENGTH}), dividing."
            )
        all_mus = []
        for index in range(ceil(len(energies) / MAX_ENERGY_LENGTH)):
            all_mus += get_attenuations(
                composition,
                energies[index * MAX_ENERGY_LENGTH : (index + 1) * MAX_ENERGY_LENGTH],
                option=option,
                verbose=verbose,
                outopt=outopt,
            )
        return all_mus

    # Mixture dict (Formula : Relative weight)
    if isinstance(composition, dict):
        url = "https://physics.nist.gov/cgi-bin/Xcom/xcom3_3"
        post_data = dict(
            POST_DATA,
            Formulae="\n".join([f"{k} {v:.6f}" for k, v in composition.items()]),
            Energies="\n".join([f"{e / 1000:0.4f}" for e in energies]),
        )
    elif isinstance(composition, str):  # Formula string
        url = "https://physics.nist.gov/cgi-bin/Xcom/xcom3_2"
        post_data = dict(
            POST_DATA,
            Formula=composition,
            Energies="\n".join([f"{e / 1000:0.4f}" for e in energies]),
        )

    # Periodicttable.formulas.Formula object
    elif isinstance(composition, Formula):
        return get_attenuations(
            {
                elem.symbol: massFrac
                for elem, massFrac in composition.mass_fraction.items()
            },
            energies,
            option=option,
            verbose=verbose,
        )

    elif isinstance(composition, int):  # Atomic number of element
        url = "https://physics.nist.gov/cgi-bin/Xcom/xcom3_1"
        post_data = dict(
            POST_DATA,
            ZNum=composition,
            Energies="\n".join([f"{e / 1000:0.4f}" for e in energies]),
            OutOpt=outopt,
        )
    else:
        raise ValueError(f"Composition value of type {type(composition)} invalid.")

    html = _perform_request(url, post_data, verbose)

    nist_parser = HTMLTableParser()
    nist_parser.feed(html)
    try:
        return [
            float(muOverRho[component_index]) for muOverRho in nist_parser.tables[0][3:]
        ]
    except IndexError:
        raise (
            URLError(f"There was a problem getting the data. We received:\n{html}")
        ) from IndexError


def _perform_request(url: str, post_data: Union[Dict, None], verbose: int) -> str:
    """
    Internal method used to perform the html request to the NIST website
    Parameters
    ----------
    url : string
        The url to target
    post_data : dictionary or None
        The dictionary containing the info to pass as a POST parameter
    verbose : int
        Verbosity of the method

    Returns
    -------
    string
        The raw html of the webpage as a string
    """
    if verbose > 0:
        print("NIST Parser: Requesting attenuation data from physics.nist.gov.")
    if post_data is not None:
        request = Request(url, urlencode(post_data).encode())
    else:
        request = Request(url)

    for attempt in range(MAX_NETWORK_TRIES):
        try:
            with urlopen(request) as html:
                html = html.read().decode()
                break
        except URLError:
            if verbose > 0:
                if attempt == 0:
                    print("NIST Parser: WARNING: Connection known to be fragile.")
                print(
                    "NIST Parser :"
                    "Failed to connect to NIST, trying again:"
                    f"{attempt} out of {MAX_NETWORK_TRIES}."
                )
            time.sleep(WAIT_TIME)
    else:  # Never called "break" == All tries failed
        raise (
            URLError(
                "NIST Parser :"
                f"Max number of tries ({MAX_NETWORK_TRIES}) reached. "
                "NIST Request failed."
            )
        ) from URLError

    return html


def get_composition(material: NISTMaterials, verbose: int = 0) -> Dict:
    """
    Method used to obtain the material composition listed at
    https://physics.nist.gov/cgi-bin/Star/compos.pl?refer=ap
    This method expects an enum object from the NISTMaterial class
    in ./materials_enum.py
    Parameters
    ----------
    material : enum
        An enum option from the NISTMaterials class of the material
        whose composition and details should be looked up
    verbose : int, optional
        The verbose level  of the  function.
        If it is greater than 0, prints at each step.

    Raises
    ------
    URLError
        If the data request failed more than `NISTparser.MAX_NETWORK_TRIES`
        times. At each fail, it waits `NISTparser.WAIT_TIME` seconds
        before trying again.
    ValueError
        If `material` is not of type NISTMaterials

    Returns
    -------
    dictionary
        Itemized relative mass, mass density,
        mean excitation energy, and reference url
    """

    if isinstance(material, NISTMaterials) is False:
        raise ValueError("Material parameter is not an instance of NISTMaterial")

    url = (
        f"https://physics.nist.gov/cgi-bin/Star/"
        f"compos.pl?refer=ap&matno={material.value}"
    )
    html = _perform_request(url, None, verbose)

    nist_parser = HTMLTableParser()
    nist_parser.feed(html)

    # in g/cm^3 & eV respectively
    density, mean_excitation_energy = [val[1] for val in nist_parser.tables[0]]

    comp_table = nist_parser.tables[1][2:]
    # The first entry contains both the header and entries, so purge that
    comp_table[0] = comp_table[0][2:]

    # Nasty way of getting number to symbol
    symbol_conversion = {el.number: el.symbol for el in elements}

    # Replace atomic number with text representation
    comp_table = [
        (symbol_conversion[int(key)], float(value)) for key, value in comp_table
    ]

    composition = dict(comp_table)

    return {
        "relative mass": composition,
        "mass density": float(density),
        "mean excitation energy": float(mean_excitation_energy),
        "reference url": url,
    }


class HTMLTableParser(HTMLParser):
    """This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    """

    # pylint: disable=abstract-method
    # pylint has issues with the ParserBase.error() method,
    # which is not relevant here

    # pylint: disable=too-many-instance-attributes
    # The 8 instances are assumed to be meaningful here
    def __init__(self, decode_html_entities=False, data_separator=" "):
        HTMLParser.__init__(self)

        self._parse_html_entities = decode_html_entities
        self._data_separator = data_separator

        self._in_td = False
        self._in_th = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []

    def handle_starttag(self, tag, attrs):
        """We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        if tag == "td":
            self._in_td = True
        if tag == "th":
            self._in_th = True

    def handle_data(self, data):
        """This is where we save content to a cell"""
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())

    def handle_charref(self, name):
        """Handle HTML encoded characters"""

        if self._parse_html_entities:
            self.handle_data(unescape(f"&#{name};"))

    def handle_endtag(self, tag):
        """Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        if tag == "td":
            self._in_td = False
        elif tag == "th":
            self._in_th = False

        if tag in ["td", "th"]:
            final_cell = self._data_separator.join(self._current_cell).strip()
            self._current_row.append(final_cell)
            self._current_cell = []
        elif tag == "tr":
            self._current_table.append(self._current_row)
            self._current_row = []
        elif tag == "table":
            self.tables.append(self._current_table)
            self._current_table = []
