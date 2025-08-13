import logging
import os  # to determine files path

import pandas as pd
import numpy as np
from .util import Singleton
from opticalglass import glass
from opticalglass.spectral_lines import get_wavelength


logger = logging.getLogger('PyRFTL_opticalglass_schott')


class SchottCatalog(metaclass=Singleton):
    def __init__(self, fname=None):
        if fname is None:
            file_dir = os.path.dirname(os.path.realpath(__file__))
            fname = os.path.join(file_dir, r'data\schott-optical-glasses-preferred-and-inquiry-en.AGF')

        # Open AGF schott file, extract data about dispersion formula

        # create a dataframe to stock data. Each line = one material
        self.df = pd.DataFrame(columns=['formula_number',
                                        'c0','c1','c2','c3','c4','c5','c6','c7','c8','c9',
                                        'wvl_min_nm', 'wvl_max_nm'])
        # glass name => index

        # open the agf file and read it line by line
        # fill the dataframe self.df with informations about materials
        with open(fname) as agf_file :
            cur_mat = None
            suppress_mat = []  # materials to delete because error when import them
            for line in agf_file :
                line_elements = line.split(' ')

                match line_elements[0] :
                    case 'NM':
                        # self.df add a line (new material)
                        cur_mat = line_elements[1]
                        self.df.loc[cur_mat, 'formula_number'] = line_elements[2]

                    case 'CD':
                        # self.df add diffusion coefficients to current line = last material added
                        nb_elts = len(line_elements)
                        number_last_coeff = str(nb_elts - 2 )
                        try :
                            self.df.loc[cur_mat, 'c0' : 'c'+number_last_coeff] = [float(coeff) for coeff in
                                                                                  line_elements[1:nb_elts]]

                        except Exception as exception :
                            # wrong import of coefficients
                            self.df.loc[cur_mat, 'c0': 'c' + number_last_coeff] = [np.nan]*(nb_elts-1)
                            # logger.error('Error when import materials from file : ' + fname +
                            #              '\nError with material ' + cur_mat + '. When try to import its coefficients : '
                            #              + str(exception))
                            if cur_mat not in suppress_mat :
                                suppress_mat.append(cur_mat)

                    case 'LD':
                        try :
                            self.df.loc[cur_mat, 'wvl_min_nm'] = float(line_elements[0]) * 1e3
                            self.df.loc[cur_mat, 'wvl_max_nm'] = float(line_elements[1]) * 1e3
                        except:
                            pass

                    case _ :
                        pass

            # delete materials with bad import
            for mat_to_delete in suppress_mat :
                self.df = self.df.drop(mat_to_delete)

        # some values
        self.name = 'Schott'

        # build an alphabetical list of decoded glass names
        gnames = self.df.index.array
        glass_list = [(glass.decode_glass_name(gn), gn, self.name)
                      for gn in gnames]
        glass_list = sorted(glass_list, key=lambda glass: glass[0][0])
        # build a lookup dict of the glass defs keyed to decoded glass names
        glass_lookup = {gn_decode: (gn, gc)
                        for gn_decode, gn, gc in glass_list}
        # attach these 'static' lists to class variables
        self.__class__.glass_list = glass_list
        self.__class__.glass_lookup = glass_lookup

    def get_glass_names(self):
        """ returns a list of glass names """
        return self.df.index.array

    def get_column_names(self):
        """ returns a list of column headers """
        return self.df.columns.levels[0]

    def glass_index(self, gname):
        """ returns the glass index (row) for glass name `gname`
        Args:
            gname (str): glass name
        Returns:
            int: the 0-based index (row) of the requested glass
        """
        return self.df.index.get_loc(gname)

    def glass_coefs_zmx(self, gname):
        """ returns an array of glass coefficients for the glass at *gname*
        coefficients order is the one of the zmx file (line CD) """
        glas = self.df.loc[gname]
        coefs = glas['c0':'c9'].to_numpy(dtype=float)
        return coefs

    def glass_coefs(self, gname):
        """ returns an array of glass coefficients for the glass at *gname*
        coefficient order is the same than used by rayoptics schott function based on xls file, for compatibility"""
        c = self.glass_coefs_zmx(gname)
        coefs = [c[0], c[2], c[4], c[1], c[3], c[5], c[6], c[7], c[8], c[9]]
        return coefs

    def create_glass(self, gname: str, gcat: str) -> 'SchottGlass':
        """ Create an instance of the glass `gname`. """
        return SchottGlass(gname)

    def catalog_name(self):
        return self.name


class SchottGlass():
    catalog = None

    def initialize_catalog(self):
        if SchottGlass.catalog is None:
            SchottGlass.catalog = SchottCatalog()

    def __init__(self, gname):
        self.initialize_catalog()
        self.gname = gname
        self.coefs = self.catalog.glass_coefs(gname)  # coeff order of RayOptics SchottGlass class using xls file
        self.coefs_zmx = self.catalog.glass_coefs_zmx(gname)  # coeff order of zemax file line CD

    def calc_rindex(self, wv_nm):
        # return the refractive index of the medium for the wavelength wv_nm (should be in nm)

        if not hasattr(self, 'coefs_zmx'):
            # compatibility with medium created with unmodified version of opticalglass
            # if the medium is a schott glass of an unmodified version, change it to the modified SchottGlass
            # can be useful in rayoptics when open a roa file
            self = SchottGlass(self.gname)

        wv = 0.001 * wv_nm  # convert in um
        wv2 = wv * wv
        c = self.coefs_zmx
        n2 = 1. + (c[0] * wv2 / (wv2 - c[1])) + (c[2] * wv2 / (wv2 - c[3])) + (c[4] * wv2 / (wv2 - c[5]))
        return np.sqrt(n2)

    def rindex(self, wvl) -> float:
        """ returns the interpolated refractive index at wvl

        Args:
            wvl: either the wavelength in nm or a string with a spectral line
                 identifier. for the refractive index query

        Returns:
            float: the refractive index at wv_nm
        """
        return self.calc_rindex(get_wavelength(wvl))

    def name(self):
        """ returns the glass name, :attr:`gname` """
        return self.gname

    def __repr__(self):
        return "{!s}('{}')".format(type(self).__name__, self.gname)

    def catalog_name(self):
        """ returns the glass name, :attr:`gname` """
        return self.catalog.catalog_name()


sc = SchottCatalog()
